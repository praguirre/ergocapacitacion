"""Persistencia, rate limit y entrega de reportes por correo."""

from __future__ import annotations

import hashlib
import logging
from datetime import timedelta

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.mail import EmailMessage, get_connection
from django.db import transaction
from django.utils import timezone

from .models import FeedbackAttachment, FeedbackReport
from .validators import safe_content_type, sanitized_original_name, validate_feedback_attachment


logger = logging.getLogger("apps.feedback")


class FeedbackRateLimitExceeded(ValidationError):
    """Señala que el profesional agotó su cuota durable por ventana."""


def enforce_rate_limit(professional) -> None:
    """Permite una cantidad configurable de reportes por profesional."""
    window_start = timezone.now() - timedelta(seconds=settings.FEEDBACK_RATE_WINDOW_SECONDS)
    recent = FeedbackReport.objects.filter(
        professional=professional,
        created_at__gte=window_start,
    ).count()
    if recent >= settings.FEEDBACK_RATE_LIMIT:
        raise FeedbackRateLimitExceeded(
            "Alcanzaste el límite temporal de comentarios. Intentá nuevamente más tarde."
        )


def create_feedback_report(*, professional, cleaned_data, user_agent="") -> FeedbackReport:
    """Guarda reporte y adjuntos atómicamente, limpiando archivos ante error."""
    attachments = cleaned_data.get("attachments", [])
    for upload in attachments:
        validate_feedback_attachment(upload)
    stored_files = []
    try:
        with transaction.atomic():
            locked_professional = (
                get_user_model().objects.select_for_update().get(pk=professional.pk)
            )
            enforce_rate_limit(locked_professional)
            report = FeedbackReport.objects.create(
                professional=locked_professional,
                reporter_name=locked_professional.display_name,
                reporter_email=locked_professional.email,
                reporter_profession=locked_professional.profession,
                reporter_license_number=locked_professional.license_number,
                category=cleaned_data["category"],
                subject=cleaned_data["subject"],
                affected_screen=cleaned_data.get("affected_screen", ""),
                description=cleaned_data["description"],
                reproduction_steps=cleaned_data.get("reproduction_steps", ""),
                expected_result=cleaned_data.get("expected_result", ""),
                user_agent=(user_agent or "")[:500],
            )
            for upload in attachments:
                upload.seek(0)
                digest = hashlib.sha256()
                for chunk in upload.chunks():
                    digest.update(chunk)
                upload.seek(0)
                safe_name = getattr(upload, "_feedback_safe_name", None)
                if safe_name is None:
                    safe_name = sanitized_original_name(upload.name)
                attachment = FeedbackAttachment(
                    report=report,
                    original_name=safe_name,
                    content_type=safe_content_type(upload._feedback_extension),
                    size_bytes=upload.size,
                    sha256=digest.hexdigest(),
                )
                attachment.file.save(safe_name, upload, save=False)
                stored_files.append((attachment.file.storage, attachment.file.name))
                attachment.save()
    except Exception:
        for storage, name in stored_files:
            storage.delete(name)
        raise

    logger.info(
        "feedback_created report_id=%s user_id=%s attachments=%s bytes=%s",
        report.pk,
        professional.pk,
        len(attachments),
        sum(attachment.size for attachment in attachments),
    )
    return report


def create_and_send_feedback(*, professional, cleaned_data, user_agent=""):
    """Persiste primero y luego intenta SMTP fuera de la transacción."""
    report = create_feedback_report(
        professional=professional,
        cleaned_data=cleaned_data,
        user_agent=user_agent,
    )
    return report, send_feedback_email(report)


def send_feedback_email(report: FeedbackReport) -> bool:
    """Entrega una sola vez; un reporte enviado es un no-op idempotente."""
    report.refresh_from_db()
    if report.email_status == FeedbackReport.EmailStatus.SENT:
        return True

    attempt_time = timezone.now()
    attempt_number = report.email_attempts + 1
    try:
        message = _build_email(report)
        sent_count = message.send(fail_silently=False)
        if sent_count != 1:
            raise EmailDeliveryReturnedZero("El backend devolvió cero entregas.")
    except Exception as exc:
        report.email_status = FeedbackReport.EmailStatus.FAILED
        report.email_attempts = attempt_number
        report.email_error_code = exc.__class__.__name__[:120]
        report.last_email_attempt_at = attempt_time
        report.save(
            update_fields=(
                "email_status",
                "email_attempts",
                "email_error_code",
                "last_email_attempt_at",
                "updated_at",
            )
        )
        logger.info(
            "feedback_email_failed report_id=%s attempts=%s error_class=%s",
            report.pk,
            attempt_number,
            exc.__class__.__name__,
        )
        return False

    report.email_status = FeedbackReport.EmailStatus.SENT
    report.email_attempts = attempt_number
    report.email_error_code = ""
    report.last_email_attempt_at = attempt_time
    report.emailed_at = attempt_time
    report.save(
        update_fields=(
            "email_status",
            "email_attempts",
            "email_error_code",
            "last_email_attempt_at",
            "emailed_at",
            "updated_at",
        )
    )
    logger.info("feedback_email_sent report_id=%s attempts=%s", report.pk, attempt_number)
    return True


class EmailDeliveryReturnedZero(RuntimeError):
    """Código seguro para backends que no confirman ninguna entrega."""


def _build_email(report: FeedbackReport) -> EmailMessage:
    safe_subject = report.subject.replace("\r", " ").replace("\n", " ").strip()
    category = report.get_category_display().upper()
    attachments = list(report.attachments.filter(purged_at__isnull=True))
    total_bytes = sum(attachment.size_bytes for attachment in attachments)
    body = "\n".join(
        (
            f"Código de seguimiento: {report.tracking_code}",
            f"Categoría: {report.get_category_display()}",
            f"Fecha: {report.created_at.isoformat()}",
            f"Profesional: {report.reporter_name}",
            f"Email profesional: {report.reporter_email}",
            f"Profesión: {report.reporter_profession}",
            f"Matrícula: {report.reporter_license_number}",
            f"Pantalla afectada: {report.affected_screen}",
            f"Asunto: {report.subject}",
            "",
            "Descripción:",
            report.description,
            "",
            "Pasos para reproducir:",
            report.reproduction_steps,
            "",
            "Resultado esperado:",
            report.expected_result,
            "",
            f"User agent: {report.user_agent}",
            f"Adjuntos: {len(attachments)} archivo(s), {total_bytes} bytes",
        )
    )
    connection = get_connection(
        backend=settings.EMAIL_BACKEND,
        fail_silently=False,
        timeout=settings.FEEDBACK_EMAIL_TIMEOUT_SECONDS,
    )
    message = EmailMessage(
        subject=f"[ErgoSolutions Beta][{category}][{report.tracking_code}] {safe_subject}",
        body=body,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[settings.FEEDBACK_RECIPIENT_EMAIL],
        reply_to=[report.reporter_email],
        connection=connection,
    )
    for attachment in attachments:
        with attachment.file.open("rb") as stored_file:
            content = stored_file.read()
        message.attach(attachment.original_name, content, attachment.content_type)
    return message
