# apps/quiz/services.py

from datetime import timedelta
from django.utils import timezone
from .models import QuizState, Question, Choice

# Constantes de reglas de negocio
TOTAL_QUESTIONS = 10
PASS_SCORE = 8
MAX_ATTEMPTS = 3
LOCK_HOURS = 24

def reset_if_unlocked(state: QuizState) -> None:
    """
    Si venció el lockout, resetea la ventana de intentos.
    Si pasó el tiempo de retake tras aprobar, libera el retake.
    """
    now = timezone.now()
    changed = False

    # 1. Verificar si el bloqueo por intentos fallidos ya expiró
    if state.lockout_until and now >= state.lockout_until:
        state.lockout_until = None
        state.attempts_used = 0
        changed = True

    # 2. Verificar si el tiempo de espera tras aprobar (cool-off) ya expiró
    # Si había retake tras aprobar, cuando llega el tiempo lo liberamos
    if state.last_passed and state.retake_available_at and now >= state.retake_available_at:
        state.retake_available_at = None
        changed = True

    if changed:
        state.save(update_fields=["lockout_until", "attempts_used", "retake_available_at"])

def is_locked(state: QuizState) -> bool:
    """
    Verifica si el usuario puede rendir AHORA mismo.
    """
    # Primero intentamos desbloquear si ya pasó el tiempo
    reset_if_unlocked(state)
    now = timezone.now()

    # Si sigue teniendo fecha de bloqueo futura, está bloqueado
    if state.lockout_until and now < state.lockout_until:
        return True

    # Si aprobó, no puede hacer retake hasta 24h (cool-off)
    if state.last_passed and state.retake_available_at and now < state.retake_available_at:
        return True

    return False

def ensure_state(user, module) -> QuizState:
    """
    Obtiene o crea el estado del usuario para un módulo específico.
    """
    state, _ = QuizState.objects.get_or_create(user=user, module=module)
    return state

def next_question_payload(module, order: int) -> dict:
    """
    Prepara el JSON de la pregunta para el Frontend.
    Oculta cuál es la correcta, solo envía IDs y Textos.
    """
    q = Question.objects.get(module=module, order=order)
    return {
        "order": q.order,
        "question_id": q.id,
        "text": q.text,
        # List comprehension para serializar las opciones
        "choices": [{"choice_id": c.id, "label": c.label, "text": c.text} for c in q.choices.all()],
    }

def check_answer(question_id: int, choice_id: int):
    """
    Valida una respuesta individual (feedback inmediato).
    Retorna: (es_correcta, titulo_feedback, texto_explicacion)
    """
    # Usamos select_related para traer la pregunta en la misma consulta y optimizar
    choice = Choice.objects.select_related("question").get(id=choice_id, question_id=question_id)
    q = choice.question
    
    if choice.is_correct:
        return True, "¡Así es!", (q.explanation_correct or "Respuesta correcta.")
    
    return False, "No exactamente", (choice.explanation_if_chosen or "Respuesta incorrecta.")

def apply_submit_rules(state: QuizState, score: int) -> bool:
    """
    Lógica al finalizar el examen (SUBMIT).
    - Si aprueba: setea retake_available_at a +24h (para que no rinda mil veces seguidas).
    - Si falla: incrementa attempts_used. 
      Si llega a 3 fallos: lockout_until +24h y retake_available_at = lockout_until.
    """
    now = timezone.now()
    passed = score >= PASS_SCORE

    state.last_completed_at = now
    state.last_passed = passed

    # CASO 1: APROBÓ
    if passed:
        # Se bloquea "positivamente" por 24h (cool-off period)
        state.retake_available_at = now + timedelta(hours=LOCK_HOURS)
        state.save(update_fields=["last_completed_at", "last_passed", "retake_available_at"])
        return True

    # CASO 2: FALLÓ
    state.attempts_used += 1

    # Verificar si agotó los intentos (Regla: 3 intentos por ventana)
    if state.attempts_used >= MAX_ATTEMPTS:
        state.lockout_until = now + timedelta(hours=LOCK_HOURS)
        # Sincronizamos el retake con el desbloqueo
        state.retake_available_at = state.lockout_until

    state.save(update_fields=[
        "attempts_used", "lockout_until", "retake_available_at", "last_completed_at", "last_passed"
    ])
    return False