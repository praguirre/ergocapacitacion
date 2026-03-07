# apps/company/tests.py
# ============================================================================
# COMMIT 48: Tests integrales de Etapa 3
# ============================================================================

from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from .models import AgendaEvent, CompanyProfile, CompanyWorker, ContactRequest

User = get_user_model()

TEST_STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {"BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"},
}


@override_settings(STORAGES=TEST_STORAGES)
class CompanyRegistrationTests(TestCase):
    """Tests de registro y autenticación de empresas."""

    def setUp(self):
        self.client = Client()

    def test_company_register_creates_user_and_profile(self):
        """Registrar empresa crea CustomUser + CompanyProfile."""
        data = {
            'razon_social': 'Acme S.A.',
            'nombre_comercial': 'Acme',
            'cuit': '20-12345678-9',
            'rubro': 'Servicios',
            'cantidad_trabajadores': 20,
            'contacto_nombre': 'Juan Perez',
            'contacto_cargo': 'RRHH',
            'contacto_telefono': '11223344',
            'domicilio': 'Calle 123',
            'provincia': 'Buenos Aires',
            'email': 'acme@test.com',
            'password1': 'testpass123',
            'password2': 'testpass123',
        }
        response = self.client.post(
            reverse('accounts_company:company_register'),
            data,
        )
        self.assertEqual(response.status_code, 302)

        user = User.objects.get(email='acme@test.com')
        self.assertTrue(user.is_company)
        self.assertTrue(user.is_backoffice_user)
        self.assertFalse(user.is_professional)
        self.assertTrue(CompanyProfile.objects.filter(user=user).exists())
        self.assertEqual(user.company_profile.razon_social, 'Acme S.A.')

    def test_company_can_access_dashboard_backoffice(self):
        """Empresa autenticada puede acceder al dashboard."""
        user = User.objects.create_company(
            email='company@test.com',
            password='testpass123',
            username='companyuser',
        )
        CompanyProfile.objects.create(
            user=user,
            razon_social='Empresa Test',
            cuit='20111111111',
            contacto_nombre='Admin',
        )
        self.client.force_login(user)
        response = self.client.get(reverse('dashboard:home'))
        self.assertEqual(response.status_code, 200)

    def test_trainee_cannot_access_dashboard(self):
        """Trainee no puede acceder al dashboard de backoffice."""
        trainee = User.objects.create_trainee(
            cuil='20999999999',
            email='worker@test.com',
            full_name='Worker Test',
        )
        self.client.force_login(trainee)
        response = self.client.get(reverse('dashboard:home'))
        self.assertIn(response.status_code, [302, 403])


@override_settings(STORAGES=TEST_STORAGES)
class CompanyNominaTests(TestCase):
    """Tests de nómina de trabajadores."""

    def setUp(self):
        self.client = Client()
        self.company_user = User.objects.create_company(
            email='co@test.com',
            password='testpass123',
            username='companynomina',
        )
        self.cp = CompanyProfile.objects.create(
            user=self.company_user,
            razon_social='Test Co',
            cuit='20222222222',
            contacto_nombre='Admin',
        )
        self.trainee = User.objects.create_trainee(
            cuil='20333333333',
            email='worker@test.com',
            full_name='Worker Test',
            first_name='Worker',
            last_name='Test',
        )
        self.client.force_login(self.company_user)

    def test_add_existing_trainee_to_nomina(self):
        """Agregar trainee existente a nómina."""
        data = {
            'cuil': '20-33333333-3',
            'email': 'worker@test.com',
            'full_name': 'Worker Test',
            'job_title': 'Operario',
            'employee_code': 'LEG001',
            'department': 'Produccion',
            'position': 'Linea',
            'notes': 'Alta inicial',
        }
        response = self.client.post(
            reverse('dashboard:company:nomina_add_worker'),
            data,
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            CompanyWorker.objects.filter(
                company=self.cp, worker=self.trainee
            ).exists()
        )

    def test_cannot_add_duplicate_worker(self):
        """No permite agregar duplicado en nómina."""
        CompanyWorker.objects.create(company=self.cp, worker=self.trainee)
        data = {
            'cuil': '20-33333333-3',
            'email': 'worker@test.com',
            'full_name': 'Worker Test',
        }
        response = self.client.post(
            reverse('dashboard:company:nomina_add_worker'),
            data,
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            CompanyWorker.objects.filter(
                company=self.cp, worker=self.trainee
            ).count(),
            1,
        )

    def test_professional_cannot_access_nomina(self):
        """Profesional no empresa no accede a nómina de empresa."""
        professional = User.objects.create_professional(
            email='pro@test.com',
            password='testpass123',
            username='prouser',
        )
        self.client.force_login(professional)
        response = self.client.get(reverse('dashboard:company:nomina_list'))
        self.assertIn(response.status_code, [302, 403])


@override_settings(STORAGES=TEST_STORAGES)
class CompanyAgendaTests(TestCase):
    """Tests de agenda y contacto empresa-profesional."""

    def setUp(self):
        self.client = Client()
        self.company_user = User.objects.create_company(
            email='coagenda@test.com',
            password='testpass123',
            username='companyagenda',
        )
        self.cp = CompanyProfile.objects.create(
            user=self.company_user,
            razon_social='Agenda Co',
            cuit='20444444444',
            contacto_nombre='Admin Agenda',
        )

    def test_create_agenda_event(self):
        """Crear evento de agenda."""
        self.client.force_login(self.company_user)
        data = {
            'title': 'Revision mensual',
            'description': 'Control interno',
            'event_type': 'reminder',
            'priority': 'medium',
            'due_at': (timezone.now() + timedelta(days=7)).strftime('%Y-%m-%dT%H:%M'),
        }
        response = self.client.post(
            reverse('dashboard:company:agenda_create'),
            data,
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            AgendaEvent.objects.filter(
                company=self.cp, title='Revision mensual'
            ).exists()
        )

    def test_complete_event(self):
        """Marcar evento como completado."""
        self.client.force_login(self.company_user)
        event = AgendaEvent.objects.create(
            company=self.cp,
            created_by=self.company_user,
            title='Evento test',
            due_at=timezone.now() + timedelta(days=1),
        )
        response = self.client.post(
            reverse('dashboard:company:agenda_complete', args=[event.id]),
        )
        self.assertEqual(response.status_code, 302)
        event.refresh_from_db()
        self.assertEqual(event.status, AgendaEvent.EventStatus.COMPLETED)

    def test_contact_request_flow_company_to_professional(self):
        """Empresa envía solicitud y profesional responde."""
        professional = User.objects.create_professional(
            email='procontact@test.com',
            password='testpass123',
            username='procontact',
            first_name='Ana',
            last_name='Perez',
            profession='Higiene',
            is_visible_in_directory=True,
        )

        self.client.force_login(self.company_user)
        send_response = self.client.post(
            reverse('dashboard:company:send_contact_request', args=[professional.id]),
            {'message': 'Hola, queremos contactarte.'},
        )
        self.assertEqual(send_response.status_code, 302)

        req = ContactRequest.objects.get(
            company=self.cp,
            professional=professional,
        )
        self.assertEqual(req.status, ContactRequest.RequestStatus.PENDING)

        self.client.force_login(professional)
        list_response = self.client.get(reverse('dashboard:my_contact_requests'))
        self.assertEqual(list_response.status_code, 200)
        self.assertContains(list_response, self.cp.display_name)

        respond_response = self.client.post(
            reverse('dashboard:respond_contact_request', args=[req.id]),
            {
                'response_action': 'accepted',
                'response_message': 'Acepto la solicitud.',
            },
        )
        self.assertEqual(respond_response.status_code, 302)
        req.refresh_from_db()
        self.assertEqual(req.status, ContactRequest.RequestStatus.ACCEPTED)
        self.assertIsNotNone(req.responded_at)
