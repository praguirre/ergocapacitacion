"""Pruebas de navegación compartida del backoffice."""

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from apps.company.models import CompanyProfile
from apps.ergonomia_886.planillas.models import Evaluacion


class EvaluacionesNavbarTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        User = get_user_model()
        cls.profesional = User.objects.create_professional(
            email="navbar-prof@example.com",
            username="navbar-prof",
            password="test-password",
        )
        cls.usuario_empresa = User.objects.create_company(
            email="navbar-empresa@example.com",
            username="navbar-empresa",
            password="test-password",
        )
        cls.empresa = CompanyProfile.objects.create(
            user=cls.usuario_empresa,
            razon_social="Empresa Navbar S.A.",
            cuit="30-33333333-3",
            contacto_nombre="Contacto Navbar",
        )
        cls.evaluacion = Evaluacion.objects.create(
            usuario=cls.profesional,
            empresa=cls.empresa,
            razon_social="Empresa Navbar S.A.",
            cuit="30-33333333-3",
            direccion_establecimiento="Domicilio Navbar",
            provincia="Buenos Aires",
        )

    def _assert_navbar(self, user):
        self.client.force_login(user)
        href = reverse("dashboard:evaluaciones_menu")

        dashboard = self.client.get(reverse("dashboard:home"))
        self.assertEqual(dashboard.status_code, 200)
        self.assertContains(dashboard, href)
        self.assertContains(dashboard, "Evaluaciones")

        for url in (
            href,
            reverse("planillas:crear_evaluacion"),
            reverse(
                "planillas:detalle_evaluacion", args=[self.evaluacion.pk]
            ),
        ):
            with self.subTest(user=user.user_type, url=url):
                response = self.client.get(url)
                self.assertNotEqual(response.status_code, 500)
                body = response.content.decode()
                before_href = body.split(f'href="{href}"', 1)[0][-180:]
                self.assertIn("nav-link active", before_href)

    def test_navbar_para_profesional(self):
        self._assert_navbar(self.profesional)

    def test_navbar_para_empresa(self):
        self._assert_navbar(self.usuario_empresa)
