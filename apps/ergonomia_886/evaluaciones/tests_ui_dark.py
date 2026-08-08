"""Recorrido HTML del módulo integrado en el backoffice oscuro."""

from pathlib import Path

from django.contrib.auth import get_user_model
from django.conf import settings
from django.test import TestCase
from django.urls import reverse

from apps.ergonomia_886.evaluaciones.catalog import FACTOR_DEFINITIONS
from apps.ergonomia_886.evaluaciones.models import RiskEvaluation
from apps.ergonomia_886.planillas.models import Evaluacion, Planilla3


class DarkThemeJourneyTests(TestCase):
    """Cubre las 30 pantallas y sus slugs contextuales efectivos."""

    @classmethod
    def setUpTestData(cls):
        cls.user = get_user_model().objects.create_professional(
            email="recorrido-oscuro@example.com",
            username="recorrido-oscuro",
            password="test-password",
        )
        cls.evaluacion = Evaluacion.objects.create(
            usuario=cls.user,
            razon_social="Empresa Recorrido Oscuro S.A.",
            cuit="30-55555555-5",
            direccion_establecimiento="Domicilio Recorrido",
            provincia="Buenos Aires",
        )
        cls.risk_eval = RiskEvaluation.objects.create(
            evaluacion=cls.evaluacion,
            creado_por=cls.user,
            factores_requeridos=[
                definition.slug for definition in FACTOR_DEFINITIONS
            ],
        )
        Planilla3.objects.create(evaluacion=cls.evaluacion)

    def setUp(self):
        self.client.force_login(self.user)

    def _pantallas(self):
        evaluacion_id = self.evaluacion.pk
        risk_eval_id = self.risk_eval.pk
        pantallas = [
            ("01-listado", reverse("ergonomia_886:evaluacion_list"), "dashboard"),
            ("02-crear", reverse("planillas:crear_evaluacion"), "crear"),
            (
                "03-detalle",
                reverse("planillas:detalle_evaluacion", args=[evaluacion_id]),
                "menu_planillas",
            ),
            ("04-planilla1", reverse("planillas:planilla1", args=[evaluacion_id]), "planilla1"),
        ]
        pantallas.extend(
            (
                f"{numero:02d}-planilla2{letra}",
                reverse(f"planillas:planilla2{letra}", args=[evaluacion_id]),
                f"planilla2{letra}",
            )
            for numero, letra in enumerate("abcdefghi", start=5)
        )
        pantallas.extend(
            [
                ("14-planilla3", reverse("planillas:planilla3", args=[evaluacion_id]), "planilla3"),
                ("15-planilla4", reverse("planillas:planilla4", args=[evaluacion_id]), "planilla4"),
            ]
        )
        pantallas.extend(
            (
                f"{numero:02d}-{definition.slug}",
                reverse(
                    f"evaluaciones:{definition.route_name_by_eval}",
                    args=[risk_eval_id],
                ),
                definition.help_slug,
            )
            for numero, definition in enumerate(FACTOR_DEFINITIONS, start=16)
        )
        pantallas.extend(
            [
                (
                    "29-wizard",
                    reverse("evaluaciones:wizard_resumen_by_eval", args=[risk_eval_id]),
                    "wizard_resumen",
                ),
                (
                    "30-documentos",
                    reverse("exportaciones:panel", args=[evaluacion_id]),
                    "exportaciones",
                ),
            ]
        )
        return pantallas

    def test_recorrido_de_30_pantallas_y_slugs_de_ayuda(self):
        pantallas = self._pantallas()
        self.assertEqual(len(pantallas), 30)

        for nombre, url, help_slug in pantallas:
            with self.subTest(pantalla=nombre, slug=help_slug):
                response = self.client.get(url)
                self.assertEqual(response.status_code, 200)
                self.assertContains(response, 'data-bs-theme="dark"')
                self.assertContains(
                    response,
                    f'data-page-slug="{help_slug}"',
                    html=False,
                )
                self.assertNotContains(response, 'data-page-slug="home"')

    def test_inventario_de_templates_con_contraste_y_23_bloques_de_ayuda(self):
        raiz = Path(settings.BASE_DIR) / "apps" / "ergonomia_886"
        templates = sorted(
            path
            for path in raiz.rglob("*.html")
            if "templates" in path.parts
        )
        self.assertEqual(len(templates), 25)

        contenidos = {path: path.read_text(encoding="utf-8") for path in templates}
        con_help_slug = [
            path
            for path, contenido in contenidos.items()
            if "{% block help_slug %}" in contenido
        ]
        self.assertEqual(len(con_help_slug), 23)

        for path, contenido in contenidos.items():
            with self.subTest(template=path.name):
                self.assertNotIn("bg-white", contenido)
                self.assertNotIn("bg-light", contenido)
                self.assertNotIn("table-light", contenido)
                self.assertNotIn("text-gray-800", contenido)

    def test_los_cinco_scripts_interactivos_se_renderizan(self):
        rutas_y_marcadores = [
            (
                reverse("evaluaciones:lmc_form_by_eval", args=[self.risk_eval.pk]),
                "Generando informe",
            ),
            (
                reverse("evaluaciones:vibracion_mano_brazo_form_by_eval", args=[self.risk_eval.pk]),
                "toggleBlocks",
            ),
            (
                reverse("evaluaciones:posturas_forzadas_form_by_eval", args=[self.risk_eval.pk]),
                "updateLogic",
            ),
            (
                reverse("evaluaciones:bipedestacion_form_by_eval", args=[self.risk_eval.pk]),
                "campo-mov-mph",
            ),
            (
                reverse("evaluaciones:vibracion_cuerpo_entero_form_by_eval", args=[self.risk_eval.pk]),
                "TOTAL_FORMS",
            ),
        ]

        for url, marcador in rutas_y_marcadores:
            with self.subTest(url=url, marcador=marcador):
                response = self.client.get(url)
                self.assertEqual(response.status_code, 200)
                self.assertContains(response, marcador)
                self.assertContains(response, "<script nonce=", html=False)
