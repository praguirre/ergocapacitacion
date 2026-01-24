# apps/quiz/views.py

import json
from django.contrib.auth.decorators import login_required
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
    """
    module = get_object_or_404(TrainingModule, slug=module_slug, is_active=True)
    data = _json_body(request)
    attempt_id = data.get("attempt_id")
    if not attempt_id:
        return JsonResponse({"error": "missing_attempt_id"}, status=400)

    attempt = get_object_or_404(QuizAttempt, id=attempt_id, user=request.user, module=module)
    
    # Si ya se envió antes, solo devolvemos el resultado previo
    if attempt.is_submitted:
        return JsonResponse({
            "score": attempt.score,
            "passed": attempt.passed,
            "result_url": reverse("quiz_result", kwargs={"module_slug": module.slug, "attempt_id": attempt.id}),
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

    return JsonResponse({
        "score": score,
        "passed": passed,
        "result_url": reverse("quiz_result", kwargs={"module_slug": module.slug, "attempt_id": attempt.id}),
    })

@login_required
@require_http_methods(["GET"])
def result_page(request, module_slug, attempt_id: int):
    """Renderiza la pantalla final de resultados (HTML)."""
    module = get_object_or_404(TrainingModule, slug=module_slug, is_active=True)
    attempt = get_object_or_404(QuizAttempt, id=attempt_id, user=request.user, module=module)
    state = ensure_state(request.user, module)

    locked_now = is_locked(state)
    attempts_left = max(0, 3 - int(state.attempts_used or 0))

    return render(request, "quiz/result.html", {
        "module": module,
        "attempt": attempt,
        "state": state,
        "locked_now": locked_now,
        "attempts_left": attempts_left,
    })

@login_required
@require_http_methods(["POST"])
def retake(request, module_slug):
    """
    Permite reiniciar el examen si las reglas lo permiten.
    Resetea contadores si ya pasó el tiempo de bloqueo.
    """
    module = get_object_or_404(TrainingModule, slug=module_slug, is_active=True)

    with transaction.atomic():
        state = QuizState.objects.select_for_update().filter(user=request.user, module=module).first()
        if not state:
            state = ensure_state(request.user, module)

        if is_locked(state):
            return JsonResponse({
                "locked": True,
                "lockout_until": state.lockout_until,
                "retake_available_at": state.retake_available_at,
            }, status=403)

        # Si estaba bloqueado pero ya pasó el tiempo, reseteamos para permitir nuevo intento
        state.attempts_used = 0
        state.lockout_until = None
        state.retake_available_at = None
        state.last_passed = None
        state.save(update_fields=["attempts_used", "lockout_until", "retake_available_at", "last_passed"])

        attempt = QuizAttempt.objects.create(user=request.user, module=module)

    return JsonResponse({
        "attempt_id": attempt.id,
        "next": next_question_payload(module, 1),
    })
