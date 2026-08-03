from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone

from apps.ergonomia_886.evaluaciones.models import LMC_Eval, RiskEvaluation
from apps.ergonomia_886.planillas.models import Evaluacion

from apps.ergonomia_886.exportaciones import serializers
from apps.ergonomia_886.exportaciones.reports.pdf import AVISO_LEGAL, build_factor_detail_pdf


class DetalleFactorPDFTests(TestCase):

    def setUp(self):
        self.usuario = get_user_model().objects.create_user("pdf", password="x")
        self.evaluacion = Evaluacion.objects.create(
            usuario=self.usuario, razon_social="ACME", cuit="30-1-9",
            direccion_establecimiento="X", provincia="Buenos Aires",
        )
        self.risk_eval = RiskEvaluation.objects.create(evaluacion=self.evaluacion)
        LMC_Eval.objects.create(
            risk_evaluation=self.risk_eval, factor_slug="lmc",
            nivel_riesgo="alto", peso_kg="18.50", duracion_h="6.00",
            frecuencia_h=20, v_altura="suelo_espinilla", h_dist="intermedio",
            giro_mayor_30=True,
            calc_data={
                "estado_resultado": "calculado",
                "limite_base_kg": 14.0,
                "agravantes_presentes": ["Giro mayor de 30°"],
                "requiere_revision_profesional": True,
                "calculation_trace": {"sources": [
                    {"archivo": "lmc_tablas.json", "data_version": "1.2.0",
                     "artifact_effective_date": "2026-07-31", "sha256": "f" * 64},
                ]},
            },
        )

    def _pdf(self):
        payload = serializers.build_factor_payload(self.risk_eval, "lmc")
        return build_factor_detail_pdf(
            cabecera=serializers.build_cabecera(self.evaluacion),
            factores=[payload],
            generado_en=timezone.localtime(),
            titulo="Detalle técnico — LMC",
        )

    def test_produce_un_pdf_valido(self):
        contenido = self._pdf()
        self.assertTrue(contenido.startswith(b"%PDF-"))
        self.assertTrue(contenido.rstrip().endswith(b"%%EOF"))
        self.assertGreater(len(contenido), 2000)

    def test_incluye_inputs_calc_data_y_fuentes(self):
        from io import BytesIO
        from pypdf import PdfReader
        texto = "".join(p.extract_text() or ""
                        for p in PdfReader(BytesIO(self._pdf())).pages)
        self.assertIn("18", texto)
        self.assertIn("limite_base_kg", texto)
        self.assertIn("lmc_tablas.json", texto)
        self.assertIn("ffffffffffff", texto)

    def test_incluye_el_aviso_legal(self):
        from io import BytesIO
        from pypdf import PdfReader
        texto = "".join(p.extract_text() or ""
                        for p in PdfReader(BytesIO(self._pdf())).pages)
        self.assertIn("no constituye", texto.lower())
        self.assertIn("homologación", AVISO_LEGAL)

    def test_un_factor_sin_iniciar_no_rompe_el_render(self):
        payload = serializers.build_factor_payload(self.risk_eval, "transporte")
        contenido = build_factor_detail_pdf(
            cabecera=serializers.build_cabecera(self.evaluacion),
            factores=[payload], generado_en=timezone.localtime(),
            titulo="Detalle técnico — Transporte",
        )
        self.assertTrue(contenido.startswith(b"%PDF-"))


class RenderDelInformeTests(TestCase):

    def setUp(self):
        self.usuario = get_user_model().objects.create_user("informe", password="x")
        self.evaluacion = Evaluacion.objects.create(
            usuario=self.usuario, razon_social="ACME", cuit="30-1-9",
            direccion_establecimiento="X", provincia="Buenos Aires",
        )
        self.risk_eval = RiskEvaluation.objects.create(evaluacion=self.evaluacion)
        LMC_Eval.objects.create(
            risk_evaluation=self.risk_eval, factor_slug="lmc",
            nivel_riesgo="alto", peso_kg="18.50", duracion_h="6.00",
            frecuencia_h=20, v_altura="suelo_espinilla", h_dist="intermedio",
            calc_data={
                "estado_resultado": "calculado",
                "limite_base_kg": 14.0,
            },
        )

    def _contenido(self):
        from apps.ergonomia_886.exportaciones.reports.pdf import build_professional_report_pdf
        payload = serializers.build_factor_payload(self.risk_eval, "lmc")
        return build_professional_report_pdf(
            cabecera=serializers.build_cabecera(self.evaluacion),
            payload=payload,
            markdown_llm="## 1. Objeto y alcance\nTexto de prueba.",
            metadatos={"modelo_llm": "modelo-de-prueba", "prompt_version": "1.0.0",
                       "inputs_hash": "a" * 64, "duracion_ms": 1234},
            generado_en=timezone.localtime(),
        )

    def test_el_markdown_del_modelo_no_puede_inyectar_marcado(self):
        from apps.ergonomia_886.exportaciones.reports.pdf import _markdown_a_flowables, _estilos
        peligroso = '## Titulo <font color="red">rojo</font> & <b>negrita</b>'
        flowables = _markdown_a_flowables(peligroso, _estilos())
        texto = " ".join(getattr(f, "text", "") for f in flowables)
        self.assertIn("&lt;font", texto)
        self.assertIn("&amp;", texto)

    def test_se_conservan_negrita_cursiva_y_vinetas(self):
        from apps.ergonomia_886.exportaciones.reports.pdf import _markdown_a_flowables, _estilos
        fuente = "- **fuerte** y *enfasis*"
        texto = " ".join(
            getattr(f, "text", "")
            for f in _markdown_a_flowables(fuente, _estilos())
        )
        self.assertIn("<b>fuerte</b>", texto)
        self.assertIn("<i>enfasis</i>", texto)
        self.assertIn("•", texto)

    def test_el_informe_incluye_el_anexo_de_datos_y_la_trazabilidad(self):
        from io import BytesIO
        from pypdf import PdfReader
        texto = "".join(p.extract_text() or ""
                        for p in PdfReader(BytesIO(self._contenido())).pages)
        self.assertIn("Anexo", texto)
        self.assertIn("modelo-de-prueba", texto)
        self.assertIn("limite_base_kg", texto)

    def test_declara_que_los_niveles_no_provienen_del_modelo(self):
        from io import BytesIO
        from pypdf import PdfReader
        texto = "".join(p.extract_text() or ""
                        for p in PdfReader(BytesIO(self._contenido())).pages)
        self.assertIn("motor de cálculo", texto.lower())
