from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import Evaluacion


class Planilla2RouteSmokeTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = get_user_model().objects.create_user(
            username="planilla-route-user",
            password="test-password",
        )
        cls.evaluacion = Evaluacion.objects.create(
            usuario=cls.user,
            razon_social="Empresa de prueba",
            cuit="30-00000000-0",
            direccion_establecimiento="Dirección de prueba",
            provincia="Buenos Aires",
        )

    def test_every_planilla2_page_loads_and_links_an_evaluation(self):
        self.client.force_login(self.user)

        for suffix in "abcdefghi":
            route_name = f"planillas:planilla2{suffix}"
            with self.subTest(planilla=route_name):
                response = self.client.get(
                    reverse(route_name, args=[self.evaluacion.pk])
                )
                self.assertEqual(response.status_code, 200)
                self.assertTemplateUsed(
                    response,
                    "planillas/planilla2_structured_form.html",
                )
                self.assertTrue(response.context["evaluacion_factor_urls"])
