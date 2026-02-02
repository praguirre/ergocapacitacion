# apps/quiz/views.py

import json
import logging

from django.contrib.auth.decorators import login_required
from django.core.files.base import ContentFile
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_http_methods

from apps.training.models import TrainingModule
from .models import QuizAttempt, QuizState, Question
from .services import (
    TOTAL_QUESTIONS, PASS_SCORE,
    ensure_state, is_locked,
    next_question_payload, check_answer, apply_submit_rules
)

logger = logging.getLogger(__name__)


def _json_body(request):
    """Helper para parsear el body JSON de la request."""
    try:
        return json.loads(request.body.decode("utf-8") or "{}")
    except Exception:
        return {}


@login_required
@require_http_methods(["POST"])
def start(request, module_slug):
    """
    Inicia un intento. Verifica bloqueos (24h) y crea el QuizAttempt.
    Retorna la primera pregunta.
    """
    module = get_object_or_404(TrainingModule, slug=module_slug, is_active=True)

    with transaction.atomic():
        # Usamos select_for_update para evitar condiciones de carrera si el usuario hace doble click
        state = QuizState.objects.select_for_update().filter(user=request.user, module=module).first()
        if not state:
            state = ensure_state(request.user, module)

        if is_locked(state):
            return JsonResponse({
                "locked": True,
                "lockout_until": state.lockout_until,
                "retake_available_at": state.retake_available_at,
                "attempts_used": state.attempts_used,
                "last_passed": state.last_passed,
            }, status=403)

        attempt = QuizAttempt.objects.create(user=request.user, module=module)
        return JsonResponse({
            "attempt_id": attempt.id,
            "next": next_question_payload(module, 1),
        })


@login_required
@require_http_methods(["GET"])
def question(request, module_slug, order: int):
    """Obtiene una pregunta específica (para recargar o navegar)."""
    module = get_object_or_404(TrainingModule, slug=module_slug, is_active=True)
    if order < 1 or order > TOTAL_QUESTIONS:
        return JsonResponse({"error": "order_out_of_range"}, status=400)
    return JsonResponse(next_question_payload(module, order))


@login_required
@require_http_methods(["POST"])
def answer(request, module_slug):
    """
    Recibe la respuesta a UNA pregunta.
    Retorna feedback inmediato (correcta/incorrecta + explicación).
    """
    module = get_object_or_404(TrainingModule, slug=module_slug, is_active=True)
    data = _json_body(request)

    attempt_id = data.get("attempt_id")
    question_id = data.get("question_id")
    choice_id = data.get("choice_id")

    if not attempt_id or not question_id or not choice_id:
        return JsonResponse({"error": "missing_fields"}, status=400)

    attempt = get_object_or_404(QuizAttempt, id=attempt_id, user=request.user, module=module)
    if attempt.is_submitted:
        return JsonResponse({"error": "attempt_already_submitted"}, status=400)

    q = get_object_or_404(Question, id=question_id, module=module)
    correct, title, text = check_answer(q.id, int(choice_id))

    # Persistimos la respuesta en el JSON del intento
    answers = attempt.answers or {}
    answers[str(q.id)] = int(choice_id)
    attempt.answers = answers
    attempt.save(update_fields=["answers"])

    done = q.order >= TOTAL_QUESTIONS
    return JsonResponse({
        "correct": correct,
        "feedback_title": title,
        "feedback_text": text,
        "next_order": (q.order + 1),
        "done": done,
    })


@login_required
@require_http_methods(["POST"])
def submit(request, module_slug):
    """
    Finaliza el examen. Calcula score y aplica reglas (bloqueo/aprobación).
    
    ✅ COMMIT 7: Si aprueba, genera certificado PDF y envía por email.
    """
    module = get_object_or_404(TrainingModule, slug=module_slug, is_active=True)
    data = _json_body(request)
    attempt_id = data.get("attempt_id")
    if not attempt_id:
        return JsonResponse({"error": "missing_attempt_id"}, status=400)

    attempt = get_object_or_404(QuizAttempt, id=attempt_id, user=request.user, module=module)
    
    # Si ya se envió antes, solo devolvemos el resultado previo
    if attempt.is_submitted:
        # Verificar si ya tiene certificado
        certificate_payload = None
        if hasattr(attempt, 'certificate') and attempt.certificate:
            cert = attempt.certificate
            certificate_payload = {
                "id": str(cert.id),
                "download_url": f"/certificados/{cert.id}/download/",
            }
        
        return JsonResponse({
            "score": attempt.score,
            "passed": attempt.passed,
            "result_url": reverse("quiz_result", kwargs={"module_slug": module.slug, "attempt_id": attempt.id}),
            "certificate": certificate_payload,
        })

    # Scoring: Calcular puntaje real desde la DB
    questions = Question.objects.filter(module=module).prefetch_related("choices")
    score = 0
    answers = attempt.answers or {}

    for q in questions:
        chosen_id = answers.get(str(q.id))
        if not chosen_id:
            continue
        correct_choice = next((c for c in q.choices.all() if c.is_correct), None)
        if correct_choice and int(chosen_id) == correct_choice.id:
            score += 1

    # Variable para el payload del certificado
    certificate_payload = None

    with transaction.atomic():
        state = QuizState.objects.select_for_update().filter(user=request.user, module=module).first()
        if not state:
            state = ensure_state(request.user, module)

        # Guardar attempt finalizado
        attempt.score = score
        attempt.passed = (score >= PASS_SCORE)
        attempt.submitted_at = timezone.now()
        attempt.save(update_fields=["score", "passed", "submitted_at"])

        # Aplicar reglas de negocio al estado global del usuario
        passed = apply_submit_rules(state, score)

    # =====================================================
    # ✅ COMMIT 7: Generación de Certificado (si aprobó)
    # =====================================================
    if passed:
        certificate_payload = _create_certificate(request.user, module, attempt)

    return JsonResponse({
        "score": score,
        "passed": passed,
        "result_url": reverse("quiz_result", kwargs={"module_slug": module.slug, "attempt_id": attempt.id}),
        "certificate": certificate_payload,
    })


def _create_certificate(user, module, attempt) -> dict | None:
    """
    Crea el certificado, genera el PDF, lo guarda y envía por email.
    
    Retorna el payload del certificado o None si hay error.
    No lanza excepciones para no romper la aprobación.
    """
    # Importaciones locales para evitar import circular
    from apps.certificates.models import Certificate
    from apps.certificates.pdf import build_certificate_pdf
    from apps.certificates.emailer import send_certificate_emails
    
    try:
        # 1. Crear registro del certificado
        cert = Certificate.objects.create(
            user=user,
            module=module,
            attempt=attempt,
        )
        logger.info(f"Certificado creado: {cert.id} para {user.email}")
        
        # 2. Generar PDF
        pdf_bytes = build_certificate_pdf(
            user=user,
            module=module,
            issued_at=cert.issued_at,
            valid_until=cert.valid_until,
        )
        
        # 3. Guardar PDF en FileField (usa UUID para evitar colisiones)
        filename = f"certificado_{cert.id}.pdf"
        cert.pdf_file.save(filename, ContentFile(pdf_bytes), save=True)
        logger.info(f"PDF guardado: {filename}")
        
        # 4. Enviar por email (non-blocking)
        try:
            # ✅ FIX: Usar full_name del modelo TraineeUser
            user_name = getattr(user, 'full_name', None) or None
            
            # ✅ FIX: Nombre del archivo para el email (con nombre del usuario)
            if user_name:
                safe_name = "".join(c if c.isalnum() or c in (' ', '-', '_') else '' for c in user_name)
                safe_name = safe_name.replace(' ', '_').strip('_') or 'usuario'
                email_filename = f"certificado_{safe_name}.pdf"
            else:
                email_filename = filename  # Fallback al UUID
            
            send_certificate_emails(
                to_email=user.email,
                pdf_bytes=pdf_bytes,
                filename=email_filename,
                user_name=user_name,
                module_title=module.title,
            )
            # Marcar como enviado
            cert.email_sent = True
            cert.email_sent_at = timezone.now()
            cert.save(update_fields=["email_sent", "email_sent_at"])
            logger.info(f"Email enviado a {user.email}")
            
        except Exception as email_error:
            # NO romper la aprobación, solo registrar el error
            logger.error(f"Error enviando email: {email_error}")
            cert.email_error = str(email_error)[:500]
            cert.save(update_fields=["email_error"])
        
        # 5. Retornar payload para el frontend
        return {
            "id": str(cert.id),
            "download_url": f"/certificados/{cert.id}/download/",
        }
        
    except Exception as e:
        # Error crítico en la creación del certificado
        # Loguear pero NO romper la aprobación
        logger.exception(f"Error creando certificado para {user.email}: {e}")
        return None



@login_required
@require_http_methods(["GET"])
def result_page(request, module_slug, attempt_id: int):
    """Renderiza la pantalla final de resultados (HTML)."""
    module = get_object_or_404(TrainingModule, slug=module_slug, is_active=True)
    attempt = get_object_or_404(QuizAttempt, id=attempt_id, user=request.user, module=module)
    state = ensure_state(request.user, module)

    locked_now = is_locked(state)
    attempts_left = max(0, 3 - int(state.attempts_used or 0))
    
    # ✅ COMMIT 7: Obtener certificado si existe
    certificate = None
    if hasattr(attempt, 'certificate'):
        certificate = attempt.certificate

    return render(request, "quiz/result.html", {
        "module": module,
        "attempt": attempt,
        "state": state,
        "locked_now": locked_now,
        "attempts_left": attempts_left,
        "certificate": certificate,  # ✅ Nuevo
    })


@login_required
@require_http_methods(["POST"])
def retake(request, module_slug):
    """
    Permite reiniciar el examen si las reglas lo permiten.
    Delega el reset de contadores a reset_if_unlocked() via is_locked().
    """
    module = get_object_or_404(TrainingModule, slug=module_slug, is_active=True)

    with transaction.atomic():
        state = QuizState.objects.select_for_update().filter(user=request.user, module=module).first()
        if not state:
            state = ensure_state(request.user, module)

        # is_locked() internamente llama a reset_if_unlocked() 
        # Si el tiempo expiró, los contadores ya se resetearon automáticamente
        if is_locked(state):
            return JsonResponse({
                "locked": True,
                "lockout_until": state.lockout_until,
                "retake_available_at": state.retake_available_at,
            }, status=403)

        # Si llegamos aquí, el usuario está desbloqueado y puede rendir
        # No hacemos reset manual - reset_if_unlocked() ya lo hizo si era necesario
        attempt = QuizAttempt.objects.create(user=request.user, module=module)

    return JsonResponse({
        "attempt_id": attempt.id,
        "next": next_question_payload(module, 1),
    })
