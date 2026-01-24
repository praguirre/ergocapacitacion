# apps/quiz/models.py

from django.conf import settings
from django.db import models
from django.utils import timezone
from apps.training.models import TrainingModule

class Question(models.Model):
    module = models.ForeignKey(TrainingModule, on_delete=models.CASCADE, related_name="questions")
    order = models.PositiveSmallIntegerField()  # 1..10
    text = models.TextField()
    explanation_correct = models.TextField(blank=True, default="")

    class Meta:
        ordering = ["order"]
        constraints = [
            models.UniqueConstraint(fields=["module", "order"], name="uq_question_module_order"),
        ]

    def __str__(self) -> str:
        # Mostramos slug y primeros 50 caracteres
        return f"[{self.module.slug}] Q{self.order}: {self.text[:50]}"


class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name="choices")
    label = models.CharField(max_length=2)  # A, B, C, D
    text = models.TextField()
    is_correct = models.BooleanField(default=False)
    explanation_if_chosen = models.TextField(blank=True, default="")

    class Meta:
        ordering = ["label"]
        constraints = [
            models.UniqueConstraint(fields=["question", "label"], name="uq_choice_question_label"),
        ]

    def __str__(self) -> str:
        return f"Q{self.question.order} {self.label} ({'OK' if self.is_correct else 'NO'})"


class QuizAttempt(models.Model):
    """
    Representa UN intento de examen de un usuario.
    Guarda las respuestas en crudo (JSON) para auditoría.
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="quiz_attempts")
    module = models.ForeignKey(TrainingModule, on_delete=models.CASCADE, related_name="quiz_attempts")

    started_at = models.DateTimeField(default=timezone.now)
    submitted_at = models.DateTimeField(null=True, blank=True)

    score = models.PositiveSmallIntegerField(null=True, blank=True)
    passed = models.BooleanField(default=False)

    # Estructura esperada: { "question_id_str": "choice_id_str" }
    answers = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["-started_at"]
        indexes = [
            models.Index(fields=["user", "module", "-started_at"]),
        ]

    @property
    def is_submitted(self) -> bool:
        return self.submitted_at is not None

    def __str__(self) -> str:
        return f"Attempt #{self.id} {self.user_id} {self.module.slug} ({self.score})"


class QuizState(models.Model):
    """
    Controla el estado global del usuario respecto a un módulo.
    Maneja los bloqueos de 24h y el contador de intentos.
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="quiz_states")
    module = models.ForeignKey(TrainingModule, on_delete=models.CASCADE, related_name="quiz_states")

    attempts_used = models.PositiveSmallIntegerField(default=0)
    lockout_until = models.DateTimeField(null=True, blank=True)

    # Después de aprobar (o fallar 3 veces) recién permite “retake” a las 24h
    retake_available_at = models.DateTimeField(null=True, blank=True)

    last_completed_at = models.DateTimeField(null=True, blank=True)
    last_passed = models.BooleanField(null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["user", "module"], name="uq_quizstate_user_module"),
        ]

    def __str__(self) -> str:
        return f"State {self.user_id} {self.module.slug} used={self.attempts_used}"