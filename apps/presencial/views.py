# apps/presencial/views.py
# ============================================================================
# COMMIT 18-19: Vistas de capacitación y quiz presencial
# ============================================================================

import json

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_POST

from apps.accounts.decorators import professional_required
from apps.quiz.models import Question
from apps.training.models import TrainingModule


@login_required
@professional_required
@ensure_csrf_cookie
def capacitacion_presencial(request, module_slug):
    """
    Página de capacitación para uso presencial.
    Incluye video + chat Ergobot, sin registro de trabajadores.
    """
    module = get_object_or_404(TrainingModule, slug=module_slug, is_active=True)

    return render(request, "presencial/capacitacion.html", {
        "module": module,
    })


@login_required
@professional_required
@ensure_csrf_cookie
def quiz_presencial(request, module_slug):
    """
    Quiz para modo presencial.
    Muestra las mismas preguntas pero sin reglas de intentos/bloqueo.
    """
    module = get_object_or_404(TrainingModule, slug=module_slug, is_active=True)
    questions = Question.objects.filter(module=module).prefetch_related("choices")

    questions_data = []
    for q in questions:
        choices = [{"id": c.id, "text": c.text} for c in q.choices.all()]
        questions_data.append(
            {
                "id": q.id,
                "text": q.text,
                "choices": choices,
            }
        )

    return render(
        request,
        "presencial/quiz.html",
        {
            "module": module,
            "questions_json": json.dumps(questions_data),
            "total_questions": len(questions_data),
        },
    )


@login_required
@professional_required
@require_POST
def quiz_presencial_submit(request, module_slug):
    """
    Corrige el quiz presencial. Retorna JSON con score.
    Sin guardar intentos ni generar certificados.
    """
    module = get_object_or_404(TrainingModule, slug=module_slug, is_active=True)

    try:
        body = json.loads(request.body)
        answers = body.get("answers", {})
    except (json.JSONDecodeError, AttributeError):
        return JsonResponse({"error": "Datos inválidos"}, status=400)

    questions = Question.objects.filter(module=module).prefetch_related("choices")

    correct = 0
    total = questions.count()
    details = []

    for q in questions:
        selected_id = answers.get(str(q.id))
        correct_choice = q.choices.filter(is_correct=True).first()
        is_correct = (str(selected_id) == str(correct_choice.id)) if correct_choice and selected_id else False

        if is_correct:
            correct += 1

        details.append(
            {
                "question_id": q.id,
                "question_text": q.text,
                "selected_id": selected_id,
                "correct_id": correct_choice.id if correct_choice else None,
                "correct_text": correct_choice.text if correct_choice else "",
                "is_correct": is_correct,
                "explanation": q.explanation if hasattr(q, "explanation") else "",
            }
        )

    passed = correct >= 8

    return JsonResponse(
        {
            "score": correct,
            "total": total,
            "passed": passed,
            "details": details,
            "module_slug": module_slug,
            "module_title": module.title,
        }
    )
