"""Pruebas de comandos manuales de reintento y purga."""

import io
import tempfile
from datetime import timedelta
from pathlib import Path
from unittest.mock import patch

from django.core.files.base import ContentFile
from django.core.management import call_command
from django.test import TestCase, override_settings
from django.utils import timezone

from apps.accounts.models import CustomUser
from apps.feedback.models import FeedbackAttachment, FeedbackReport
from apps.feedback.storage import private_feedback_storage


class FeedbackCommandTests(TestCase):
    """Los comandos respetan estados, máximos y retención segura."""

    def setUp(self):
        self.tempdir = tempfile.TemporaryDirectory()
        self.override = override_settings(PRIVATE_FEEDBACK_ROOT=Path(self.tempdir.name))
        self.override.enable()
        self.original_storage_location = private_feedback_storage._location
        private_feedback_storage._location = Path(self.tempdir.name)
        for key in ("base_location", "location", "base_url"):
            private_feedback_storage.__dict__.pop(key, None)
        self.user = CustomUser.objects.create_professional(
            email="commands@test.local",
            password="test-password",
            username="commands-professional",
        )

    def tearDown(self):
        private_feedback_storage._location = self.original_storage_location
        for key in ("base_location", "location", "base_url"):
            private_feedback_storage.__dict__.pop(key, None)
        self.override.disable()
        self.tempdir.cleanup()

    def make_report(self, status=FeedbackReport.EmailStatus.PENDING):
        return FeedbackReport.objects.create(
            professional=self.user,
            reporter_name="Profesional",
            reporter_email=self.user.email,
            category=FeedbackReport.Category.BUG,
            subject="Asunto",
            description="Descripción",
            email_status=status,
        )

    @patch("apps.feedback.services.EmailMessage.send", return_value=1)
    def test_retry_sends_failed_report_without_sensitive_output(self, mocked_send):
        report = self.make_report(FeedbackReport.EmailStatus.FAILED)
        output = io.StringIO()
        call_command("retry_feedback_emails", report=str(report.pk), stdout=output)
        report.refresh_from_db()
        self.assertEqual(report.email_status, FeedbackReport.EmailStatus.SENT)
        self.assertIn(f"report_id={report.pk} status=sent", output.getvalue())
        self.assertNotIn(report.reporter_email, output.getvalue())

    def test_retry_skips_maximum_attempts(self):
        report = self.make_report(FeedbackReport.EmailStatus.FAILED)
        report.email_attempts = 5
        report.save(update_fields=("email_attempts",))
        output = io.StringIO()
        call_command("retry_feedback_emails", stdout=output)
        self.assertIn("processed=0", output.getvalue())

    def test_purge_dry_run_preserves_file_and_pending_is_never_purged(self):
        sent = self.make_report(FeedbackReport.EmailStatus.SENT)
        pending = self.make_report(FeedbackReport.EmailStatus.PENDING)
        sent_attachment = self._old_attachment(sent)
        pending_attachment = self._old_attachment(pending)
        output = io.StringIO()
        call_command(
            "purge_feedback_attachments",
            older_than_days=90,
            dry_run=True,
            stdout=output,
        )
        self.assertIn("candidates=1", output.getvalue())
        self.assertTrue(sent_attachment.file.storage.exists(sent_attachment.file.name))

        call_command("purge_feedback_attachments", older_than_days=90, stdout=io.StringIO())
        sent_attachment.refresh_from_db()
        pending_attachment.refresh_from_db()
        self.assertEqual(sent_attachment.file.name, "")
        self.assertIsNotNone(sent_attachment.purged_at)
        self.assertTrue(pending_attachment.file.storage.exists(pending_attachment.file.name))
        self.assertIsNone(pending_attachment.purged_at)

    def _old_attachment(self, report):
        attachment = FeedbackAttachment(
            report=report,
            original_name="evidencia.txt",
            content_type="text/plain",
            size_bytes=2,
            sha256="0" * 64,
        )
        attachment.file.save("evidencia.txt", ContentFile(b"ok"), save=True)
        FeedbackAttachment.objects.filter(pk=attachment.pk).update(
            created_at=timezone.now() - timedelta(days=91)
        )
        attachment.refresh_from_db()
        return attachment
