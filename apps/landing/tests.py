"""Pruebas de contenido público de la landing de ErgoSolutions."""

from django.test import TestCase
from django.urls import reverse


class LandingContentTests(TestCase):
    """Protege la oferta vigente y la atribución institucional del sitio."""

    def test_evaluaciones_figura_como_disponible(self):
        response = self.client.get(reverse("landing:home"))

        self.assertContains(
            response,
            '<span class="badge bg-success">Disponible</span>',
            count=4,
            html=True,
        )
        self.assertNotContains(response, "Próximamente")

    def test_footer_atribuye_el_desarrollo_a_iainsane(self):
        response = self.client.get(reverse("landing:home"))

        self.assertContains(response, "Desarrollado por")
        self.assertContains(
            response,
            '<strong class="text-white">IAinsane</strong>',
            html=True,
        )
        self.assertNotContains(response, "Lic. Pablo Aguirre")
        self.assertNotContains(response, "MN 10.027")
