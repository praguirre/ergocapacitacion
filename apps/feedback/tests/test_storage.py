"""Pruebas del modelo inicial y del almacenamiento privado."""

import tempfile
from pathlib import Path

from django.core.files.base import ContentFile
from django.test import TestCase, override_settings

from apps.accounts.models import CustomUser
from apps.feedback.models import (
    FeedbackAttachment,
    FeedbackReport,
    feedback_attachment_upload_to,
)
from apps.feedback.storage import PrivateFeedbackStorage


class FeedbackModelTests(TestCase):
    """Congela snapshots, tracking, índices y ruta física opaca."""

    @classmethod
    def setUpTestData(cls):
        cls.user = CustomUser.objects.create_professional(
            email="feedback-professional@test.local",
            password="test-password",
            username="feedback-professional",
            full_name="Profesional Beta",
        )

    def make_report(self):
        return FeedbackReport.objects.create(
            professional=self.user,
            reporter_name="Profesional Beta",
            reporter_email=self.user.email,
            category=FeedbackReport.Category.BUG,
            subject="No guarda",
            description="Descripción reproducible",
        )

    def test_tracking_code_and_safe_string(self):
        report = self.make_report()
        self.assertRegex(report.tracking_code, r"^FB-[0-9A-F]{8}$")
        self.assertEqual(str(report), report.tracking_code)

    def test_required_indexes_are_declared(self):
        index_fields = {tuple(index.fields) for index in FeedbackReport._meta.indexes}
        self.assertEqual(
            index_fields,
            {
                ("professional", "-created_at"),
                ("email_status", "created_at"),
                ("category", "-created_at"),
            },
        )

    def test_upload_path_uses_uuids_not_client_directories(self):
        report = self.make_report()
        attachment = FeedbackAttachment(report=report)
        path = feedback_attachment_upload_to(attachment, "../../captura.PDF")
        self.assertEqual(path, f"feedback/{report.pk}/{attachment.pk}.pdf")
        self.assertNotIn("captura", path)
        self.assertNotIn("..", path)


class PrivateFeedbackStorageTests(TestCase):
    """Verifica fallo cerrado de URL y aislamiento respecto de MEDIA_ROOT."""

    def test_url_is_never_public(self):
        storage = PrivateFeedbackStorage()
        with self.assertRaisesRegex(ValueError, "no tiene URL pública"):
            storage.url("feedback/report/file.pdf")

    def test_physical_path_is_private_and_outside_media_root(self):
        with tempfile.TemporaryDirectory() as root:
            private_root = Path(root) / "private-feedback"
            media_root = Path(root) / "public-media"
            with override_settings(
                PRIVATE_FEEDBACK_ROOT=private_root,
                MEDIA_ROOT=media_root,
            ):
                storage = PrivateFeedbackStorage()
                name = storage.save("feedback/report/file.txt", ContentFile(b"ok"))
                physical = Path(storage.path(name)).resolve()
                self.assertTrue(physical.is_relative_to(private_root.resolve()))
                self.assertFalse(physical.is_relative_to(media_root.resolve()))
