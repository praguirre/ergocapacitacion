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
        self.trainee = User.objects.create_trainee(
            cuil='20-12345678-9',
            email='trainee-dashboard@test.com',
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

    def test_footer_interno_atribuye_el_desarrollo_a_iainsane(self):
        """Todas las páginas internas heredan el crédito institucional único."""
        self.client.force_login(self.professional)

        response = self.client.get(reverse('dashboard:home'))

        self.assertContains(response, '© 2026 ErgoSolutions. Desarrollado por')
        self.assertContains(
            response,
            '<strong class="text-white">IAinsane</strong>',
            html=True,
        )
        self.assertNotContains(response, 'Lic. Pablo Aguirre')
        self.assertNotContains(response, 'MN 10.027')

    def test_tarjeta_evaluaciones_esta_disponible_y_navega_al_modulo(self):
        self.client.force_login(self.professional)
        response = self.client.get(reverse('dashboard:home'))

        self.assertContains(response, 'Evaluaciones')
        self.assertContains(response, 'Disponible')
        self.assertContains(response, reverse('dashboard:evaluaciones_menu'))
        self.assertNotContains(response, 'Próximamente')
        self.assertNotContains(response, 'iluminación')
        self.assertNotContains(response, 'ruido')
        self.assertContains(response, reverse('dashboard:capacitaciones_menu'))

    def test_menu_evaluaciones_lista_disponibles_y_proximamente(self):
        self.client.force_login(self.professional)

        response = self.client.get(reverse('dashboard:evaluaciones_menu'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'dashboard/evaluaciones_menu.html')
        self.assertContains(response, 'Ergonomía')
        self.assertContains(response, reverse('ergonomia_886:evaluacion_list'))
        self.assertContains(response, 'Disponible')
        self.assertContains(response, 'Próximamente')
        self.assertContains(response, 'aria-disabled="true"', count=5)
        self.assertContains(response, 'data-module-active="true"', count=1)
        self.assertNotContains(response, 'href=""')

    def test_menu_evaluaciones_requiere_backoffice(self):
        self.client.force_login(self.trainee)

        response = self.client.get(reverse('dashboard:evaluaciones_menu'))

        self.assertEqual(response.status_code, 403)

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

    def test_entrada_sin_ref_limpia_una_atribucion_anterior(self):
        session = self.client.session
        session["capacitacion_ref"] = str(self.link.id)
        session.save()

        response = self.client.get("/c/test-module/")

        self.assertEqual(response.status_code, 302)
        self.assertNotIn("capacitacion_ref", self.client.session)


@override_settings(STORAGES=TEST_STORAGES)
class PersonalizedTrainingAccessTests(TestCase):
    """Tests de visibilidad y acceso para capacitaciones personalizadas."""

    def setUp(self):
        self.client = Client()
        self.professional_a = User.objects.create_professional(
            email="proa@test.com",
            password="testpass123",
            username="proauser",
            first_name="Profesional",
            last_name="A",
        )
        self.professional_b = User.objects.create_professional(
            email="prob@test.com",
            password="testpass123",
            username="probuser",
            first_name="Profesional",
            last_name="B",
        )
        self.general_module = TrainingModule.objects.create(
            slug="general-module",
            title="Módulo General",
            youtube_id="general123",
            is_active=True,
            is_personalized=False,
            icon="bi-book",
            color="#28a745",
            order=1,
        )
        self.personalized_module = TrainingModule.objects.create(
            slug="personalized-module",
            title="Módulo Personalizado",
            youtube_id="personal123",
            is_active=True,
            is_personalized=True,
            requested_by=self.professional_a,
            company_name_custom="Acme S.A.",
            icon="bi-shield-lock",
            color="#17a2b8",
            order=2,
        )
        self.personalized_module.assigned_professionals.add(self.professional_a)

    def test_professional_a_sees_general_and_personalized_modules(self):
        self.client.force_login(self.professional_a)

        response = self.client.get(reverse("dashboard:capacitaciones_menu"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Módulo General")
        self.assertContains(response, "Módulo Personalizado")
        self.assertContains(response, "Mis Capacitaciones Personalizadas")

    def test_professional_b_sees_only_general_modules(self):
        self.client.force_login(self.professional_b)

        response = self.client.get(reverse("dashboard:capacitaciones_menu"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Módulo General")
        self.assertNotContains(response, "Módulo Personalizado")
        self.assertNotContains(response, "Mis Capacitaciones Personalizadas")

    def test_professional_b_gets_403_on_personalized_modalidad_selector(self):
        self.client.force_login(self.professional_b)

        response = self.client.get(
            reverse("dashboard:modalidad_selector", args=[self.personalized_module.slug])
        )

        self.assertEqual(response.status_code, 403)

    def test_professional_a_can_access_personalized_modalidad_selector(self):
        self.client.force_login(self.professional_a)

        response = self.client.get(
            reverse("dashboard:modalidad_selector", args=[self.personalized_module.slug])
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Módulo Personalizado")

    def test_professional_b_gets_403_on_personalized_online_links(self):
        self.client.force_login(self.professional_b)

        response = self.client.get(
            reverse("dashboard:online_links", args=[self.personalized_module.slug])
        )

        self.assertEqual(response.status_code, 403)

    def test_professional_b_cannot_generate_link_for_unassigned_personalized_module(self):
        self.client.force_login(self.professional_b)

        response = self.client.post(
            reverse("dashboard:generate_link", args=[self.personalized_module.slug]),
            {"label": "Intento no autorizado"},
        )

        self.assertEqual(response.status_code, 403)
        self.assertFalse(
            CapacitacionLink.objects.filter(
                module=self.personalized_module,
                created_by=self.professional_b,
            ).exists()
        )
