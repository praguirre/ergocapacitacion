"""Modelos durables para reportes y adjuntos privados de la beta."""

import uuid
from pathlib import Path

from django.conf import settings
from django.db import models

from .storage import private_feedback_storage


def feedback_attachment_upload_to(instance, filename):
    """Genera una ruta física opaca sin reutilizar el nombre del cliente."""
    extension = Path(filename).suffix.lower()
    return f"feedback/{instance.report_id}/{instance.id}{extension}"


class FeedbackReport(models.Model):
    """Comentario persistido antes de cualquier intento de entrega SMTP."""

    class Category(models.TextChoices):
        BUG = "bug", "Error"
        IMPROVEMENT = "improvement", "Mejora"
        QUESTION = "question", "Consulta"
        OTHER = "other", "Otro"

    class EmailStatus(models.TextChoices):
        PENDING = "pending", "Pendiente"
        SENT = "sent", "Enviado"
        FAILED = "failed", "Fallido"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    professional = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="feedback_reports",
    )
    reporter_name = models.CharField(max_length=200)
    reporter_email = models.EmailField()
    reporter_profession = models.CharField(max_length=100, blank=True)
    reporter_license_number = models.CharField(max_length=50, blank=True)
    category = models.CharField(max_length=20, choices=Category.choices)
    subject = models.CharField(max_length=160)
    affected_screen = models.CharField(max_length=300, blank=True)
    description = models.TextField()
    reproduction_steps = models.TextField(blank=True)
    expected_result = models.TextField(blank=True)
    user_agent = models.CharField(max_length=500, blank=True)
    email_status = models.CharField(
        max_length=20,
        choices=EmailStatus.choices,
        default=EmailStatus.PENDING,
    )
    email_attempts = models.PositiveSmallIntegerField(default=0)
    email_error_code = models.CharField(max_length=120, blank=True)
    last_email_attempt_at = models.DateTimeField(null=True, blank=True)
    emailed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-created_at",)
        indexes = (
            models.Index(fields=("professional", "-created_at")),
            models.Index(fields=("email_status", "created_at")),
            models.Index(fields=("category", "-created_at")),
        )
        verbose_name = "Reporte de feedback"
        verbose_name_plural = "Reportes de feedback"

    @property
    def tracking_code(self):
        """Código breve y no secuencial para mostrar al profesional."""
        return f"FB-{str(self.pk).split('-')[0].upper()}"

    def __str__(self):
        return self.tracking_code


class FeedbackAttachment(models.Model):
    """Metadatos e identidad privada de un archivo asociado al reporte."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    report = models.ForeignKey(
        FeedbackReport,
        on_delete=models.CASCADE,
        related_name="attachments",
    )
    file = models.FileField(
        storage=private_feedback_storage,
        upload_to=feedback_attachment_upload_to,
        max_length=500,
    )
    original_name = models.CharField(max_length=255)
    content_type = models.CharField(max_length=120)
    size_bytes = models.PositiveBigIntegerField()
    sha256 = models.CharField(max_length=64)
    purged_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("created_at",)
        verbose_name = "Adjunto de feedback"
        verbose_name_plural = "Adjuntos de feedback"

    def __str__(self):
        return f"Adjunto {self.pk}"
