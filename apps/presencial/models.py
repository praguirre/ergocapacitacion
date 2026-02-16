# apps/presencial/models.py
# ============================================================================
# COMMIT 21: Modelo PresencialSession para registro de sesiones
# ============================================================================

from django.conf import settings
from django.db import models

from apps.training.models import TrainingModule


class PresencialSession(models.Model):
    """Registro de sesiones de capacitación presencial."""

    module = models.ForeignKey(
        TrainingModule,
        on_delete=models.CASCADE,
        related_name='presencial_sessions',
        verbose_name='Módulo',
    )
    professional = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='presencial_sessions',
        verbose_name='Profesional',
    )
    session_date = models.DateField(verbose_name='Fecha de la sesión')
    location = models.CharField(
        max_length=200,
        blank=True,
        default='',
        verbose_name='Ubicación',
    )
    participants_count = models.PositiveIntegerField(
        default=0,
        verbose_name='Cantidad de participantes',
    )
    quiz_score = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name='Score del quiz',
    )
    quiz_passed = models.BooleanField(
        default=False,
        verbose_name='Quiz aprobado',
    )
    notes = models.TextField(
        blank=True,
        default='',
        verbose_name='Notas / Observaciones',
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-session_date', '-created_at']
        verbose_name = 'Sesión presencial'
        verbose_name_plural = 'Sesiones presenciales'

    def __str__(self):
        return f"{self.module.title} - {self.session_date} ({self.professional.display_name})"
