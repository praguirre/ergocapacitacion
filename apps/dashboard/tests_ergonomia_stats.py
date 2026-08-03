"""Regresiones para la stat opcional del módulo de Ergonomía."""

from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.urls import reverse

from apps.ergonomia_886.planillas.models import Evaluacion


APPS_SIN_ERGONOMIA = [
    app
    for app in settings.INSTALLED_APPS
    if not app.startswith("apps.ergonomia_886.")
]


class EvaluacionesErgonomicasStatTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        User = get_user_model()
        cls.profesional = User.objects.create_professional(
            email="stat-886@example.com",
            username="stat-886",
            password="test-password",
        )
        cls.otro_profesional = User.objects.create_professional(
            email="stat-886-otro@example.com",
            username="stat-886-otro",
            password="test-password",
        )
        for usuario in (
            cls.profesional,
            cls.profesional,
            cls.otro_profesional,
        ):
            Evaluacion.objects.create(
                usuario=usuario,
                razon_social="Empresa Stat S.A.",
                cuit="30-44444444-4",
                direccion_establecimiento="Domicilio Stat",
                provincia="Buenos Aires",
            )

    def setUp(self):
        self.client.force_login(self.profesional)

    def test_muestra_solo_las_evaluaciones_del_profesional(self):
        response = self.client.get(reverse("dashboard:home"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["stats"]["evaluaciones_ergonomicas"], 2)
        self.assertContains(response, "Evaluaciones ergonómicas")

    @override_settings(INSTALLED_APPS=APPS_SIN_ERGONOMIA)
    def test_dashboard_funciona_si_el_modulo_esta_desinstalado(self):
        response = self.client.get(reverse("dashboard:home"))

        self.assertEqual(response.status_code, 200)
        self.assertIsNone(response.context["stats"]["evaluaciones_ergonomicas"])
        self.assertNotContains(response, "Evaluaciones ergonómicas")
