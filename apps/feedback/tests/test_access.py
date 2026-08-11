"""Pruebas de permisos, identidad y render del formulario profesional."""

from django.core import mail
from django.test import TestCase
from django.urls import reverse

from apps.accounts.models import CustomUser
from apps.feedback.models import FeedbackReport


class FeedbackAccessTests(TestCase):
    """Congela la matriz anónimo/trainee/company/professional."""

    @classmethod
    def setUpTestData(cls):
        cls.professional = CustomUser.objects.create_professional(
            email="owner@test.local",
            password="test-password",
            username="feedback-owner",
            full_name="Profesional Real",
            profession="Lic. en Higiene",
            license_number="MN 456",
        )
        cls.trainee = CustomUser.objects.create_trainee(
            cuil="20123456789",
            email="trainee-feedback@test.local",
        )
        cls.company = CustomUser.objects.create_company(
            email="company-feedback@test.local",
            password="test-password",
            username="company-feedback",
        )
        cls.inactive = CustomUser.objects.create_professional(
            email="inactive-feedback@test.local",
            password="test-password",
            username="inactive-feedback",
            is_active=False,
        )
        cls.url = reverse("dashboard:feedback:create")

    def test_anonymous_get_and_post_redirect_to_login(self):
        self.assertEqual(self.client.get(self.url).status_code, 302)
        self.assertEqual(self.client.post(self.url).status_code, 302)

    def test_non_professional_and_inactive_users_are_forbidden(self):
        for user in (self.trainee, self.company, self.inactive):
            with self.subTest(user=user.user_type):
                self.client.force_login(user)
                self.assertEqual(self.client.get(self.url).status_code, 403)
                self.assertEqual(self.client.post(self.url).status_code, 403)
                self.client.logout()

    def test_active_professional_gets_form(self):
        self.client.force_login(self.professional)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Comentarios de la beta")
        self.assertContains(response, 'enctype="multipart/form-data"')
        self.assertContains(response, "12 MiB")
        self.assertContains(response, "DNI")
        self.assertContains(response, 'data-page-slug="feedback"')
        self.assertContains(response, "ayuda/js/help_widget.js")
        self.assertNotContains(response, "js/planilla_logic.js")

    def test_post_uses_authenticated_identity_and_prg(self):
        other = CustomUser.objects.create_professional(
            email="forged@test.local",
            password="test-password",
            username="forged-feedback",
        )
        self.client.force_login(self.professional)
        response = self.client.post(
            self.url,
            {
                "category": "bug",
                "subject": "No guarda",
                "description": "Descripción válida",
                "privacy_confirmed": "on",
                "user_id": other.pk,
                "email": other.email,
                "recipient": "attacker@test.local",
            },
            HTTP_USER_AGENT="Browser seguro/1.0",
        )
        self.assertRedirects(response, self.url, fetch_redirect_response=False)
        report = FeedbackReport.objects.get()
        self.assertEqual(report.professional, self.professional)
        self.assertEqual(report.reporter_email, self.professional.email)
        self.assertEqual(report.reporter_name, self.professional.display_name)
        self.assertEqual(report.user_agent, "Browser seguro/1.0")
        self.assertEqual(mail.outbox[0].to, ["consultaergosolutions@gmail.com"])
        self.assertContains(self.client.get(self.url), report.tracking_code)

    def test_no_attachment_download_route_exists(self):
        self.client.force_login(self.professional)
        response = self.client.get(
            "/dashboard/comentarios/adjuntos/00000000-0000-0000-0000-000000000000/"
        )
        self.assertEqual(response.status_code, 404)

    def test_886_page_still_loads_planilla_logic(self):
        self.client.force_login(self.professional)
        response = self.client.get(reverse("ergonomia_886:evaluacion_list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "js/planilla_logic.js")
        self.assertContains(response, "ayuda/js/help_widget.js")


class FeedbackDashboardTests(TestCase):
    """La tarjeta pertenece exclusivamente al dashboard profesional."""

    def test_professional_dashboard_has_feedback_card(self):
        professional = CustomUser.objects.create_professional(
            email="dashboard-feedback@test.local",
            password="test-password",
            username="dashboard-feedback",
        )
        self.client.force_login(professional)
        response = self.client.get(reverse("dashboard:home"))
        self.assertContains(response, "Comentarios de la beta")
        self.assertContains(response, reverse("dashboard:feedback:create"))

    def test_company_dashboard_does_not_have_feedback_card(self):
        company = CustomUser.objects.create_company(
            email="dashboard-company@test.local",
            password="test-password",
            username="dashboard-company-feedback",
        )
        self.client.force_login(company)
        response = self.client.get(reverse("dashboard:home"))
        self.assertNotContains(response, "Comentarios de la beta")
        self.assertNotContains(response, reverse("dashboard:feedback:create"))
