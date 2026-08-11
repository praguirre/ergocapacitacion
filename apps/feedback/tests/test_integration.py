"""Integración punta a punta del canal profesional, retry y retención."""

import io
import tempfile
from datetime import timedelta
from pathlib import Path
from unittest.mock import patch

from django.core import mail
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.management import call_command
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone
from pypdf import PdfWriter

from apps.accounts.models import CustomUser
from apps.feedback.models import FeedbackAttachment, FeedbackReport
from apps.feedback.storage import private_feedback_storage


def minimal_pdf_upload():
    """Crea un PDF mínimo en memoria sin incorporar fixtures binarias."""
    buffer = io.BytesIO()
    writer = PdfWriter()
    writer.add_blank_page(width=10, height=10)
    writer.write(buffer)
    return SimpleUploadedFile(
        "captura.pdf",
        buffer.getvalue(),
        content_type="text/html",
    )


class FeedbackEndToEndTests(TestCase):
    """Recorre POST → storage → email y los caminos operativos de falla."""

    def setUp(self):
        self.tempdir = tempfile.TemporaryDirectory()
        self.override = override_settings(PRIVATE_FEEDBACK_ROOT=Path(self.tempdir.name))
        self.override.enable()
        self.original_storage_location = private_feedback_storage._location
        private_feedback_storage._location = Path(self.tempdir.name)
        for key in ("base_location", "location", "base_url"):
            private_feedback_storage.__dict__.pop(key, None)
        self.professional = CustomUser.objects.create_professional(
            email="integration-feedback@test.local",
            password="test-password",
            username="integration-feedback",
            full_name="Profesional Integración",
            profession="Ergónoma",
            license_number="MN 789",
        )
        self.url = reverse("dashboard:feedback:create")
        self.client.force_login(self.professional)

    def tearDown(self):
        private_feedback_storage._location = self.original_storage_location
        for key in ("base_location", "location", "base_url"):
            private_feedback_storage.__dict__.pop(key, None)
        self.override.disable()
        self.tempdir.cleanup()

    def payload(self, **overrides):
        data = {
            "category": "bug",
            "subject": "Integración completa",
            "affected_screen": "/dashboard/comentarios/",
            "description": "Descripción suficiente para reproducir.",
            "reproduction_steps": "Abrir, completar y enviar.",
            "expected_result": "Confirmación con código.",
            "privacy_confirmed": "on",
        }
        data.update(overrides)
        return data

    def test_professional_post_persists_private_file_and_sends_identical_email(self):
        upload = minimal_pdf_upload()
        expected = upload.read()
        upload.seek(0)
        response = self.client.post(self.url, self.payload(attachments=upload))
        self.assertEqual(response.status_code, 302)

        report = FeedbackReport.objects.get()
        attachment = report.attachments.get()
        self.assertEqual(report.email_status, FeedbackReport.EmailStatus.SENT)
        self.assertEqual(report.professional, self.professional)
        self.assertEqual(attachment.content_type, "application/pdf")
        self.assertTrue(Path(attachment.file.path).is_relative_to(Path(self.tempdir.name)))
        with attachment.file.open("rb") as stored:
            self.assertEqual(stored.read(), expected)
        self.assertEqual(mail.outbox[0].attachments[0][1], expected)
        self.assertEqual(mail.outbox[0].to, ["consultaergosolutions@gmail.com"])

    @patch("apps.feedback.services.EmailMessage.send", side_effect=TimeoutError("smtp"))
    def test_smtp_failure_is_durable_then_retry_marks_sent(self, failed_send):
        response = self.client.post(self.url, self.payload())
        self.assertEqual(response.status_code, 302)
        report = FeedbackReport.objects.get()
        self.assertEqual(report.email_status, FeedbackReport.EmailStatus.FAILED)
        self.assertEqual(report.email_attempts, 1)

        with patch("apps.feedback.services.EmailMessage.send", return_value=1):
            call_command("retry_feedback_emails", report=str(report.pk), stdout=io.StringIO())
        report.refresh_from_db()
        self.assertEqual(report.email_status, FeedbackReport.EmailStatus.SENT)
        self.assertEqual(report.email_attempts, 2)

    def test_dry_run_then_real_purge_preserves_metadata(self):
        self.client.post(self.url, self.payload(attachments=minimal_pdf_upload()))
        attachment = FeedbackAttachment.objects.get()
        original_name = attachment.original_name
        sha256 = attachment.sha256
        stored_name = attachment.file.name
        FeedbackAttachment.objects.filter(pk=attachment.pk).update(
            created_at=timezone.now() - timedelta(days=91)
        )
        attachment.refresh_from_db()

        call_command(
            "purge_feedback_attachments",
            older_than_days=90,
            dry_run=True,
            stdout=io.StringIO(),
        )
        self.assertTrue(attachment.file.storage.exists(stored_name))

        call_command("purge_feedback_attachments", older_than_days=90, stdout=io.StringIO())
        attachment.refresh_from_db()
        self.assertFalse(attachment.file.storage.exists(stored_name))
        self.assertEqual(attachment.file.name, "")
        self.assertEqual(attachment.original_name, original_name)
        self.assertEqual(attachment.sha256, sha256)
        self.assertIsNotNone(attachment.purged_at)
