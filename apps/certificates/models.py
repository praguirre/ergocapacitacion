# apps/certificates/models.py

import uuid
from datetime import timedelta

from django.conf import settings
from django.db import models
from django.utils import timezone

from apps.training.models import TrainingModule
from apps.quiz.models import QuizAttempt


def default_valid_until():
    """Certificado válido por 1 año desde emisión."""
    return timezone.now() + timedelta(days=365)


class Certificate(models.Model):
    """
    Representa un certificado emitido cuando el usuario aprueba el quiz.
    
    Campos clave:
    - id: UUID único (para URLs seguras)
    - user: Usuario que recibe el certificado
    - module: Módulo de capacitación aprobado
    - attempt: Intento específico que generó la aprobación
    - pdf_file: Archivo PDF generado
    - issued_at: Fecha de emisión
    - valid_until: Fecha de vencimiento (1 año por defecto)
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="certificates"
    )
    module = models.ForeignKey(
        TrainingModule,
        on_delete=models.CASCADE,
        related_name="certificates"
    )
    attempt = models.OneToOneField(
        QuizAttempt,
        on_delete=models.CASCADE,
        related_name="certificate"
    )
    
    # El PDF se guarda en MEDIA_ROOT/certificates/
    pdf_file = models.FileField(upload_to="certificates/", blank=True, null=True)
    
    issued_at = models.DateTimeField(default=timezone.now)
    valid_until = models.DateTimeField(default=default_valid_until)
    
    # Metadatos opcionales
    email_sent = models.BooleanField(default=False)
    email_sent_at = models.DateTimeField(null=True, blank=True)
    email_error = models.TextField(blank=True, default="")
    
    class Meta:
        ordering = ["-issued_at"]
        verbose_name = "Certificado"
        verbose_name_plural = "Certificados"
    
    def __str__(self) -> str:
        return f"Cert {self.id} - {self.user.email} - {self.module.slug}"
    
    @property
    def is_valid(self) -> bool:
        """Verifica si el certificado aún está vigente."""
        return timezone.now() < self.valid_until
    
    @property
    def days_until_expiry(self) -> int:
        """Días restantes hasta el vencimiento."""
        delta = self.valid_until - timezone.now()
        return max(0, delta.days)