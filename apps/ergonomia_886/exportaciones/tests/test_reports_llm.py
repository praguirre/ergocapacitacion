"""Pruebas del informe con LLM. Nunca se llama al proveedor real."""

from __future__ import annotations

from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.urls import reverse

from evaluaciones.models import LMC_Eval, RiskEvaluation
from planillas.models import Evaluacion

from exportaciones import serializers
from exportaciones.models import EstadoInforme
from exportaciones.reports.llm import (
    CLAVES_PROHIBIDAS,
    ReportResult,
    get_or_create_report,
    sanitize_payload,
)
from exportaciones.reports.prompts import PROMPT_VERSION, SYSTEM_PROMPT

MARKDOWN_FALSO = """\
## 1. Objeto y alcance
Se analiza el factor de levantamiento manual de cargas.
## 2. Metodología aplicada
Se aplicó la tabla correspondiente.
## 3. Datos relevados
Peso: 18,5 kg.
## 4. Resultado de la evaluación
Nivel de riesgo: Alto.
## 5. Análisis técnico
El peso supera el límite de tabla.
## 6. Medidas correctivas y preventivas sugeridas
Reducir la carga unitaria.
## 7. Limitaciones del presente análisis
Requiere revisión y firma profesional.
"""


class SanitizacionTests(TestCase):

    def test_se_eliminan_todas_las_claves_prohibidas(self):
        sucio = {
            "factor_slug": "lmc",
            "nombres_trabajadores": "Juan Pérez",
            "cuit": "30-12345678-9",
            "direccion": "Ruta 8",
            "inputs": {"peso_kg": 18.5, "salud_columna": "hernia L4-L5"},
            "calc_data": {"revisado_por": {"username": "jperez"}},
        }
        limpio = sanitize_payload(sucio)
        texto = str(limpio)
        for clave in CLAVES_PROHIBIDAS:
            self.assertNotIn(clave, texto)
        self.assertNotIn("Juan Pérez", texto)
        self.assertNotIn("hernia", texto)
        self.assertEqual(limpio["inputs"]["peso_kg"], 18.5)

    def test_el_contexto_se_reduce_a_cuatro_campos(self):
        limpio = sanitize_payload({
            "contexto": {
                "razon_social": "ACME",
                "puesto_trabajo": "Preparador",
                "area_sector": "Depósito",
                "provincia": "Buenos Aires",
                "cuit": "30-1-9",
                "telefono": "011-0000",
            }
        })
        self.assertEqual(
            set(limpio["contexto"]),
            {"razon_social", "area_sector", "puesto_trabajo", "provincia"},
        )

from exportaciones.reports.prompts import SYSTEM_PROMPT


class PromptTests(TestCase):

    def test_el_system_prompt_declara_las_prohibiciones_criticas(self):
        for fragmento in (
            "NO inventes",
            "NO recalcules",
            "NO afirmes",
            "homologación",
            "única fuente de verdad",
        ):
            self.assertIn(fragmento, SYSTEM_PROMPT)

    def test_el_system_prompt_exige_las_siete_secciones(self):
        for seccion in (
            "## 1. Objeto y alcance",
            "## 2. Metodología aplicada",
            "## 3. Datos relevados",
            "## 4. Resultado de la evaluación",
            "## 5. Análisis técnico",
            "## 6. Medidas correctivas y preventivas sugeridas",
            "## 7. Limitaciones del presente análisis",
        ):
            self.assertIn(seccion, SYSTEM_PROMPT)


class CacheDeInformesTests(TestCase):

    def setUp(self):
        self.usuario = get_user_model().objects.create_user("tester", password="x")
        self.evaluacion = Evaluacion.objects.create(
            usuario=self.usuario, razon_social="ACME", cuit="30-1-9",
            direccion_establecimiento="X", provincia="Buenos Aires",
        )
        self.risk_eval = RiskEvaluation.objects.create(
            evaluacion=self.evaluacion, factores_requeridos=["lmc"],
        )
        LMC_Eval.objects.create(
            risk_evaluation=self.risk_eval, factor_slug="lmc",
            peso_kg="18.50", duracion_h="6.00", frecuencia_h=20,
            v_altura="suelo_espinilla", h_dist="intermedio",
            nivel_riesgo="alto",
            calc_data={"estado_resultado": "calculado", "limite_base_kg": 14.0},
        )

    def _resultado_falso(self, payload, **kwargs):
        from exportaciones.models import payload_fingerprint
        limpio = sanitize_payload(payload)
        return ReportResult(
            markdown=MARKDOWN_FALSO,
            modelo="modelo-de-prueba",
            prompt_version=PROMPT_VERSION,
            inputs_hash=payload_fingerprint(limpio),
            duracion_ms=1234,
            payload_enviado=limpio,
        )

    def test_el_segundo_pedido_no_vuelve_a_llamar_al_modelo(self):
        payload = serializers.build_factor_payload(self.risk_eval, "lmc")
        with patch(
            "exportaciones.reports.llm.build_professional_report",
            side_effect=self._resultado_falso,
        ) as llamada:
            primero = get_or_create_report(
                evaluacion=self.evaluacion, payload=payload,
                factor_slug="lmc", usuario=self.usuario,
            )
            segundo = get_or_create_report(
                evaluacion=self.evaluacion, payload=payload,
                factor_slug="lmc", usuario=self.usuario,
            )
        self.assertEqual(llamada.call_count, 1)
        self.assertEqual(primero.pk, segundo.pk)

    def test_si_cambian_los_datos_el_informe_previo_queda_obsoleto(self):
        payload = serializers.build_factor_payload(self.risk_eval, "lmc")
        with patch(
            "exportaciones.reports.llm.build_professional_report",
            side_effect=self._resultado_falso,
        ):
            primero = get_or_create_report(
                evaluacion=self.evaluacion, payload=payload,
                factor_slug="lmc", usuario=self.usuario,
            )
            payload["inputs"]["peso_kg"] = 25.0
            segundo = get_or_create_report(
                evaluacion=self.evaluacion, payload=payload,
                factor_slug="lmc", usuario=self.usuario,
            )
        primero.refresh_from_db()
        self.assertEqual(primero.estado, EstadoInforme.OBSOLETO)
        self.assertEqual(segundo.estado, EstadoInforme.LISTO)
        self.assertNotEqual(primero.inputs_hash, segundo.inputs_hash)

    def test_el_payload_enviado_queda_persistido_como_evidencia(self):
        payload = serializers.build_factor_payload(self.risk_eval, "lmc")
        with patch(
            "exportaciones.reports.llm.build_professional_report",
            side_effect=self._resultado_falso,
        ):
            informe = get_or_create_report(
                evaluacion=self.evaluacion, payload=payload,
                factor_slug="lmc", usuario=self.usuario,
            )
        self.assertEqual(informe.prompt_version, PROMPT_VERSION)
        self.assertIn("calc_data", informe.payload_json)
        self.assertNotIn("cuit", str(informe.payload_json))


class CuotasDeInformeTests(TestCase):

    def setUp(self):
        from django.core.cache import cache
        cache.clear()

    def test_el_lease_impide_dos_generaciones_simultaneas(self):
        from exportaciones.reports.limits import (
            ReportLimitExceeded, acquire_report_lease, release_report_lease,
        )
        lease = acquire_report_lease(1)
        with self.assertRaises(ReportLimitExceeded):
            acquire_report_lease(1)
        release_report_lease(lease)
        acquire_report_lease(1)  # ya liberado: no debe fallar

    @override_settings(REPORT_AI_RATE_LIMIT=2)
    def test_la_cuota_horaria_se_agota(self):
        from exportaciones.reports.limits import (
            ReportLimitExceeded, acquire_report_lease, release_report_lease,
        )
        for _ in range(2):
            release_report_lease(acquire_report_lease(7))
        with self.assertRaises(ReportLimitExceeded) as ctx:
            acquire_report_lease(7)
        self.assertGreater(ctx.exception.retry_after, 0)

    def test_las_cuotas_de_distintos_usuarios_son_independientes(self):
        from exportaciones.reports.limits import acquire_report_lease
        acquire_report_lease(10)
        acquire_report_lease(11)  # otro usuario: no debe bloquearse


class InformeEndpointTests(TestCase):

    def setUp(self):
        User = get_user_model()
        self.duenio = User.objects.create_user("duenio", password="x")
        self.intruso = User.objects.create_user("intruso", password="x")
        self.evaluacion = Evaluacion.objects.create(
            usuario=self.duenio, razon_social="ACME", cuit="30-1-9",
            direccion_establecimiento="X", provincia="Buenos Aires",
        )
        self.risk_eval = RiskEvaluation.objects.create(evaluacion=self.evaluacion)
        self.url = reverse(
            "exportaciones:informe_factor", args=[self.evaluacion.pk, "lmc"]
        )

    def _resultado_falso(self, payload, **kwargs):
        from exportaciones.models import payload_fingerprint
        limpio = sanitize_payload(payload)
        return ReportResult(
            markdown=MARKDOWN_FALSO,
            modelo="modelo-de-prueba",
            prompt_version=PROMPT_VERSION,
            inputs_hash=payload_fingerprint(limpio),
            duracion_ms=1234,
            payload_enviado=limpio,
        )

    def test_otro_usuario_recibe_404(self):
        self.client.force_login(self.intruso)
        self.assertEqual(self.client.post(self.url).status_code, 404)

    def test_get_no_esta_permitido(self):
        self.client.force_login(self.duenio)
        self.assertEqual(self.client.get(self.url).status_code, 405)

    def test_factor_sin_datos_no_llama_al_modelo(self):
        self.client.force_login(self.duenio)
        with patch("exportaciones.reports.llm.build_professional_report") as llamada:
            respuesta = self.client.post(self.url, follow=True)
        llamada.assert_not_called()
        self.assertEqual(respuesta.status_code, 200)

    @override_settings(REPORT_AI_RATE_LIMIT=0)
    def test_cuota_agotada_devuelve_429_con_retry_after(self):
        LMC_Eval.objects.create(
            risk_evaluation=self.risk_eval, factor_slug="lmc",
            nivel_riesgo="alto", calc_data={"estado_resultado": "calculado"},
        )
        self.client.force_login(self.duenio)
        respuesta = self.client.post(self.url)
        self.assertEqual(respuesta.status_code, 429)
        self.assertIn("Retry-After", respuesta)

    def test_un_factor_en_borrador_avisa_pero_no_bloquea_la_navegacion(self):
        LMC_Eval.objects.create(
            risk_evaluation=self.risk_eval, factor_slug="lmc",
            calc_data={"estado_resultado": "borrador"},
        )
        self.client.force_login(self.duenio)
        with patch("exportaciones.reports.llm.build_professional_report") as llamada:
            respuesta = self.client.post(self.url, follow=True)
        llamada.assert_not_called()
        self.assertEqual(respuesta.status_code, 200)

    def test_el_informe_generado_se_descarga_como_pdf(self):
        LMC_Eval.objects.create(
            risk_evaluation=self.risk_eval, factor_slug="lmc",
            nivel_riesgo="alto",
            calc_data={"estado_resultado": "calculado", "limite_base_kg": 14.0},
        )
        self.client.force_login(self.duenio)
        with patch("exportaciones.reports.llm.build_professional_report",
                   side_effect=self._resultado_falso):
            respuesta = self.client.post(self.url)
        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(respuesta["Content-Type"], "application/pdf")
        self.assertEqual(respuesta["X-Content-Type-Options"], "nosniff")
        self.assertIn("no-store", respuesta["Cache-Control"])
        self.assertTrue(respuesta.content.startswith(b"%PDF-"))
