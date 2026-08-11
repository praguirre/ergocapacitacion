import io
import tempfile
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from pypdf import PdfReader

from apps.quiz.models import QuizAttempt
from apps.quiz.views import _create_certificate
from apps.training.models import CapacitacionLink, TrainingModule

from .models import Certificate
from .pdf import build_certificate_pdf


class CertificateResponsibleTests(TestCase):
    """El certificado congela al creador profesional del link de origen."""

    def setUp(self):
        self.media_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.media_dir.cleanup)
        self.settings_override = override_settings(MEDIA_ROOT=self.media_dir.name)
        self.settings_override.enable()
        self.addCleanup(self.settings_override.disable)

        User = get_user_model()
        self.professional = User.objects.create_professional(
            email="cert-responsable@test.local",
            username="cert-responsable",
            password="prueba",
            full_name="Andrea Responsable",
            profession="Lic. en Seguridad e Higiene",
            license_number="MP 2468",
        )
        self.other_professional = User.objects.create_professional(
            email="cert-otro@test.local",
            username="cert-otro",
            password="prueba",
            full_name="Bruno Incorrecto",
            profession="Otra profesión",
            license_number="MP 9999",
        )
        self.trainee = User.objects.create_trainee(
            cuil="20-30000000-3",
            email="cert-trainee@test.local",
            full_name="Trabajador Certificado",
        )
        self.module = TrainingModule.objects.create(
            slug="cert-attrib",
            title="Capacitación atribuida",
            youtube_id="cert123",
            is_active=True,
        )
        self.link = CapacitacionLink.objects.create(
            module=self.module,
            created_by=self.professional,
        )
        self.attempt = QuizAttempt.objects.create(
            user=self.trainee,
            module=self.module,
            capacitacion_link=self.link,
            score=10,
            passed=True,
        )

    @patch("apps.certificates.emailer.send_certificate_emails")
    def test_emision_persiste_snapshot_y_pdf_del_responsable_real(self, send_email):
        payload = _create_certificate(self.trainee, self.module, self.attempt)

        self.assertIsNotNone(payload)
        cert = Certificate.objects.get(attempt=self.attempt)
        self.assertEqual(cert.responsible_professional, self.professional)
        self.assertEqual(cert.responsible_name, "Andrea Responsable")
        self.assertEqual(cert.responsible_profession, "Lic. en Seguridad e Higiene")
        self.assertEqual(cert.responsible_license_number, "MP 2468")

        with cert.pdf_file.open("rb") as pdf_file:
            text = "\n".join(
                page.extract_text() or ""
                for page in PdfReader(io.BytesIO(pdf_file.read())).pages
            )
        self.assertIn("Andrea Responsable", text)
        self.assertIn("Lic. en Seguridad e Higiene", text)
        self.assertIn("MP 2468", text)
        self.assertNotIn("Bruno Incorrecto", text)
        send_email.assert_called_once()

    @patch("apps.certificates.emailer.send_certificate_emails")
    def test_cambiar_el_perfil_no_reescribe_snapshot_ni_pdf(self, _send_email):
        _create_certificate(self.trainee, self.module, self.attempt)
        cert = Certificate.objects.get(attempt=self.attempt)
        with cert.pdf_file.open("rb") as pdf_file:
            original_pdf = pdf_file.read()

        self.professional.full_name = "Nombre Posterior"
        self.professional.profession = "Profesión Posterior"
        self.professional.license_number = "MP 0000"
        self.professional.save()
        cert.refresh_from_db()

        self.assertEqual(cert.responsible_name, "Andrea Responsable")
        self.assertEqual(cert.responsible_profession, "Lic. en Seguridad e Higiene")
        self.assertEqual(cert.responsible_license_number, "MP 2468")
        with cert.pdf_file.open("rb") as pdf_file:
            self.assertEqual(pdf_file.read(), original_pdf)

    def test_generador_rechaza_responsable_incompleto(self):
        with self.assertRaisesRegex(ValueError, "responsable profesional completo"):
            build_certificate_pdf(
                user=self.trainee,
                module=self.module,
                issued_at=self.attempt.started_at,
                valid_until=self.attempt.started_at,
                responsible_name="Andrea Responsable",
                responsible_profession="",
                responsible_license_number="MP 2468",
            )
