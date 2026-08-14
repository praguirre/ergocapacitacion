"""Pruebas de contenido público de la landing de ErgoSolutions."""

import re

from django.test import TestCase
from django.urls import reverse


IAINSANE_CREDIT_LINK_HTML = (
    '<strong>'
    '<a href="https://www.iainsane.com/" '
    'target="_blank" '
    'rel="noopener" '
    'class="text-white text-decoration-underline" '
    'aria-label="IAinsane (se abre en una pestaña nueva)">'
    'IAinsane'
    '</a>'
    '</strong>'
)


def assert_iainsane_credit_link(test_case, response):
    """El crédito institucional es un enlace externo con la marca IAinsane."""
    test_case.assertContains(response, "© 2026 ErgoSolutions. Desarrollado por")
    test_case.assertContains(response, IAINSANE_CREDIT_LINK_HTML, html=True)
    test_case.assertContains(response, 'href="https://www.iainsane.com/"')
    test_case.assertContains(response, 'rel="noopener"')
    test_case.assertContains(response, 'target="_blank"')
    test_case.assertNotContains(response, "Lic. Pablo Aguirre")
    test_case.assertNotContains(response, "MN 10.027")

    html = response.content.decode()
    matches = re.findall(
        r'<a\b[^>]*href="https://www.iainsane.com/"[^>]*>(.*?)</a>',
        html,
        flags=re.DOTALL,
    )
    test_case.assertEqual(len(matches), 1)
    visible = re.sub(r"<[^>]+>", "", matches[0]).strip()
    test_case.assertEqual(visible, "IAinsane")

    opening_tag = re.search(
        r'<a\b[^>]*href="https://www.iainsane.com/"[^>]*>',
        html,
    )
    test_case.assertIsNotNone(opening_tag)
    test_case.assertIn('rel="noopener"', opening_tag.group(0))
    test_case.assertIn('target="_blank"', opening_tag.group(0))


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
        self.assertContains(response, IAINSANE_CREDIT_LINK_HTML, html=True)
        self.assertNotContains(response, "Lic. Pablo Aguirre")
        self.assertNotContains(response, "MN 10.027")

    def test_footer_enlace_iainsane_abre_el_sitio_en_pestana_nueva(self):
        response = self.client.get(reverse("landing:home"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "base_landing.html")
        assert_iainsane_credit_link(self, response)
