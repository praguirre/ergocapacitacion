# apps/dashboard/tests.py
# ============================================================================
# COMMIT 28: Tests del dashboard y flujos de capacitaciones
# ============================================================================

from django.contrib.auth import get_user_model
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from apps.training.models import CapacitacionLink, TrainingModule

User = get_user_model()

TEST_STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {"BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"},
}


@override_settings(STORAGES=TEST_STORAGES)
class DashboardTests(TestCase):
    """Tests del dashboard de profesionales."""

    def setUp(self):
        self.client = Client()
        self.professional = User.objects.create_professional(
            email='pro@test.com',
            password='testpass123',
            username='prouser',
            first_name='Test',
            last_name='Pro',
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

    def test_dashboard_home(self):
        """Dashboard muestra correctamente."""
        self.client.force_login(self.professional)
        response = self.client.get(reverse('dashboard:home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Dashboard')

    def test_capacitaciones_menu(self):
        """Menú de capacitaciones lista los módulos."""
        self.client.force_login(self.professional)
        response = self.client.get(reverse('dashboard:capacitaciones_menu'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Módulo de Test')

    def test_modalidad_selector(self):
        """Selector de modalidad muestra presencial y online."""
        self.client.force_login(self.professional)
        response = self.client.get(
            reverse('dashboard:modalidad_selector', args=['test-module'])
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Módulo de Test')
        self.assertContains(response, reverse('dashboard:presencial:capacitacion', args=['test-module']))

    def test_generate_link(self):
        """Generación de link de capacitación."""
        self.client.force_login(self.professional)
        response = self.client.post(
            reverse('dashboard:generate_link', args=['test-module']),
            {'label': 'Test Link'}
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            CapacitacionLink.objects.filter(
                module=self.module,
                created_by=self.professional,
                label='Test Link',
            ).exists()
        )

    def test_online_links_list(self):
        """Lista de links muestra links creados."""
        self.client.force_login(self.professional)
        CapacitacionLink.objects.create(
            module=self.module,
            created_by=self.professional,
            label='Mi Link',
        )
        response = self.client.get(
            reverse('dashboard:online_links', args=['test-module'])
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Mi Link')


@override_settings(STORAGES=TEST_STORAGES)
class PublicLinkTests(TestCase):
    """Tests de acceso público vía links."""

    def setUp(self):
        self.client = Client()
        self.professional = User.objects.create_professional(
            email='pro@test.com',
            password='testpass123',
            username='prouser',
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
        self.link = CapacitacionLink.objects.create(
            module=self.module,
            created_by=self.professional,
            is_active=True,
        )

    def test_public_link_redirects(self):
        """Link público redirige al login de trainees."""
        url = f"/c/test-module/?ref={self.link.id}"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith('/acceso/'))

    def test_public_link_increments_counter(self):
        """Link público incrementa el contador de accesos."""
        url = f"/c/test-module/?ref={self.link.id}"
        self.client.get(url)
        self.link.refresh_from_db()
        self.assertEqual(self.link.access_count, 1)
