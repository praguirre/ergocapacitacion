"""Pruebas de persistencia, rate limit y contrato de correo."""

import tempfile
from pathlib import Path
from unittest.mock import patch

from django.conf import settings
from django.core import mail
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings

from apps.accounts.models import CustomUser
from apps.feedback.models import FeedbackReport
from apps.feedback.services import (
    FeedbackRateLimitExceeded,
    create_and_send_feedback,
    create_feedback_report,
    send_feedback_email,
)
from apps.feedback.storage import private_feedback_storage


def cleaned_data(**overrides):
    data = {
        "category": FeedbackReport.Category.BUG,
        "subject": "Falla controlada",
        "affected_screen": "/dashboard/",
        "description": "Descripción para reproducir.",
        "reproduction_steps": "Paso uno.",
        "expected_result": "Resultado esperado.",
        "attachments": [],
        "privacy_confirmed": True,
    }
    data.update(overrides)
    return data


class FeedbackMailTests(TestCase):
    """Comprueba que persistencia anteceda al SMTP y que no haya fugas."""

    def setUp(self):
        self.tempdir = tempfile.TemporaryDirectory()
        self.override = override_settings(PRIVATE_FEEDBACK_ROOT=Path(self.tempdir.name))
        self.override.enable()
        self.original_storage_location = private_feedback_storage._location
        private_feedback_storage._location = Path(self.tempdir.name)
        for key in ("base_location", "location", "base_url"):
            private_feedback_storage.__dict__.pop(key, None)
        self.user = CustomUser.objects.create_professional(
            email="reply@test.local",
            password="never-in-email",
            username="reply-professional",
            full_name="Profesional Remitente",
            profession="Ergónoma",
            license_number="MN 123",
        )

    def tearDown(self):
        private_feedback_storage._location = self.original_storage_location
        for key in ("base_location", "location", "base_url"):
            private_feedback_storage.__dict__.pop(key, None)
        self.override.disable()
        self.tempdir.cleanup()

    def test_success_uses_fixed_headers_body_and_identical_attachment(self):
        content = b"evidencia binaria"
        upload = SimpleUploadedFile(
            "evidencia.txt",
            content,
            content_type="application/octet-stream",
        )
        report, delivered = create_and_send_feedback(
            professional=self.user,
            cleaned_data=cleaned_data(attachments=[upload], subject="Asunto\r\ninyectado"),
            user_agent="Browser/1.0",
        )
        report.refresh_from_db()
        self.assertTrue(delivered)
        self.assertEqual(report.email_status, FeedbackReport.EmailStatus.SENT)
        self.assertEqual(report.email_attempts, 1)
        self.assertIsNotNone(report.emailed_at)
        self.assertEqual(len(mail.outbox), 1)
        message = mail.outbox[0]
        self.assertEqual(message.to, ["consultaergosolutions@gmail.com"])
        self.assertEqual(message.from_email, settings.DEFAULT_FROM_EMAIL)
        self.assertEqual(message.reply_to, [self.user.email])
        self.assertNotIn("\r", message.subject)
        self.assertNotIn("\n", message.subject)
        self.assertIn(report.tracking_code, message.body)
        self.assertIn("Descripción para reproducir", message.body)
        attached_content = message.attachments[0][1]
        if isinstance(attached_content, str):
            attached_content = attached_content.encode("utf-8")
        self.assertEqual(attached_content, content)
        self.assertEqual(message.attachments[0][2], "text/plain")
        for secret in ("never-in-email", "sessionid", "csrftoken"):
            self.assertNotIn(secret, message.body)

    @patch("apps.feedback.services.EmailMessage.send", side_effect=TimeoutError("secret smtp"))
    def test_smtp_exception_preserves_report_and_safe_error_code(self, mocked_send):
        report, delivered = create_and_send_feedback(
            professional=self.user,
            cleaned_data=cleaned_data(),
        )
        report.refresh_from_db()
        self.assertFalse(delivered)
        self.assertTrue(FeedbackReport.objects.filter(pk=report.pk).exists())
        self.assertEqual(report.email_status, FeedbackReport.EmailStatus.FAILED)
        self.assertEqual(report.email_error_code, "TimeoutError")
        self.assertNotIn("secret", report.email_error_code)
        mocked_send.assert_called_once_with(fail_silently=False)

    @patch("apps.feedback.services.EmailMessage.send", return_value=0)
    def test_zero_deliveries_is_failed(self, mocked_send):
        report = create_feedback_report(professional=self.user, cleaned_data=cleaned_data())
        self.assertFalse(send_feedback_email(report))
        report.refresh_from_db()
        self.assertEqual(report.email_status, FeedbackReport.EmailStatus.FAILED)
        self.assertEqual(report.email_error_code, "EmailDeliveryReturnedZero")

    def test_sent_report_is_idempotent(self):
        report = create_feedback_report(professional=self.user, cleaned_data=cleaned_data())
        report.email_status = FeedbackReport.EmailStatus.SENT
        report.save(update_fields=("email_status",))
        with patch("apps.feedback.services.EmailMessage.send") as mocked_send:
            self.assertTrue(send_feedback_email(report))
        mocked_send.assert_not_called()

    @override_settings(FEEDBACK_RATE_LIMIT=5, FEEDBACK_RATE_WINDOW_SECONDS=3600)
    def test_sixth_report_within_window_is_rejected(self):
        for _ in range(5):
            create_feedback_report(professional=self.user, cleaned_data=cleaned_data())
        with self.assertRaises(FeedbackRateLimitExceeded):
            create_feedback_report(professional=self.user, cleaned_data=cleaned_data())
        self.assertEqual(FeedbackReport.objects.filter(professional=self.user).count(), 5)
