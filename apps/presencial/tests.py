# apps/presencial/tests.py
# ============================================================================
# COMMIT 28: Tests de modo presencial
# ============================================================================

import io

from django.contrib.auth import get_user_model
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from pypdf import PdfReader

from apps.training.models import TrainingModule

User = get_user_model()

TEST_STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {"BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"},
}


@override_settings(STORAGES=TEST_STORAGES)
class PresencialTests(TestCase):
    """Tests de capacitación presencial."""

    def setUp(self):
        self.client = Client()
        self.professional = User.objects.create_professional(
            email='pro@test.com',
            password='testpass123',
            username='prouser',
            full_name='Profesional Presencial Correcta',
            profession='Lic. en Higiene y Seguridad',
            license_number='MP 789',
        )
        self.module = TrainingModule.objects.create(
            slug='test-module',
            title='Módulo de Test',
            youtube_id='test123',
            is_active=True,
            icon='bi-book',
            color='#28a745',
            order=1,
        )

    def test_capacitacion_page(self):
        """Página de capacitación presencial carga correctamente."""
        self.client.force_login(self.professional)
        response = self.client.get(
            reverse('dashboard:presencial:capacitacion', args=['test-module'])
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Presencial')
        self.assertContains(
            response,
            'https://www.youtube-nocookie.com/embed/test123',
        )
        self.assertContains(
            response,
            'https://www.youtube.com/watch?v=test123',
        )

    def test_quiz_presencial_page(self):
        """Página del quiz presencial carga correctamente."""
        self.client.force_login(self.professional)
        response = self.client.get(
            reverse('dashboard:presencial:quiz', args=['test-module'])
        )
        self.assertEqual(response.status_code, 200)

    def test_planilla_pdf_download(self):
        """El PDF usa al profesional autenticado y no otra identidad."""
        User.objects.create_professional(
            email='intruso@test.com',
            password='testpass123',
            username='intruso',
            full_name='Profesional Incorrecta',
            profession='Otra profesión',
            license_number='MP 000',
        )
        self.client.force_login(self.professional)
        response = self.client.get(
            reverse('dashboard:presencial:planilla_pdf', args=['test-module'])
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/pdf')
        text = "\n".join(
            page.extract_text() or ""
            for page in PdfReader(io.BytesIO(response.content)).pages
        )
        self.assertIn('Profesional Presencial Correcta', text)
        self.assertIn('Lic. en Higiene y Seguridad', text)
        self.assertIn('MP 789', text)
        self.assertNotIn('Profesional Incorrecta', text)
