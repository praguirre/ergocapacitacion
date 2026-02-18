# apps/accounts/tests.py
# ============================================================================
# COMMIT 28: Tests de autenticación dual
# ============================================================================

from django.contrib.auth import get_user_model
from django.test import Client, TestCase, override_settings
from django.urls import reverse

User = get_user_model()

TEST_STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {"BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"},
}


@override_settings(STORAGES=TEST_STORAGES)
class TraineeAuthTests(TestCase):
    """Tests de autenticación de trabajadores (trainees)."""

    def setUp(self):
        self.client = Client()
        self.trainee = User.objects.create_trainee(
            cuil='20123456789',
            email='trainee@test.com',
            full_name='Test Trainee',
        )

    def test_trainee_login_with_cuil_email(self):
        """Login de trainee con CUIL y email."""
        response = self.client.post(reverse('login_post'), {
            'cuil': '20123456789',
            'email': 'trainee@test.com',
        })
        self.assertEqual(response.status_code, 302)

    def test_trainee_cannot_access_dashboard(self):
        """Trainee no puede acceder al dashboard de profesionales."""
        self.client.force_login(self.trainee)
        response = self.client.get(reverse('dashboard:home'))
        # Debería redirigir o devolver 403
        self.assertIn(response.status_code, [302, 403])


@override_settings(STORAGES=TEST_STORAGES)
class ProfessionalAuthTests(TestCase):
    """Tests de autenticación de profesionales."""

    def setUp(self):
        self.client = Client()
        self.professional = User.objects.create_professional(
            email='pro@test.com',
            password='testpass123',
            username='prouser',
            first_name='Test',
            last_name='Professional',
        )

    def test_professional_login(self):
        """Login de profesional con username y password."""
        response = self.client.post(reverse('accounts_professional:professional_login'), {
            'username': 'prouser',
            'password': 'testpass123',
        })
        self.assertEqual(response.status_code, 302)

    def test_professional_login_with_email(self):
        """Login de profesional con email y password."""
        response = self.client.post(reverse('accounts_professional:professional_login'), {
            'username': 'pro@test.com',
            'password': 'testpass123',
        })
        self.assertEqual(response.status_code, 302)

    def test_professional_can_access_dashboard(self):
        """Profesional puede acceder al dashboard."""
        self.client.force_login(self.professional)
        response = self.client.get(reverse('dashboard:home'))
        self.assertEqual(response.status_code, 200)

    def test_professional_register(self):
        """Registro de nuevo profesional."""
        response = self.client.post(reverse('accounts_professional:professional_register'), {
            'first_name': 'Nuevo',
            'last_name': 'Pro',
            'dni': '30123456',
            'email': 'nuevo@test.com',
            'profession': 'Lic. en Higiene y Seguridad',
            'license_number': 'MN 99999',
            'username': 'nuevopro',
            'password1': 'securepass123',
            'password2': 'securepass123',
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(username='nuevopro').exists())
