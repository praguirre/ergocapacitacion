"""Pruebas de autorización, respuesta y auditoría de exportaciones."""

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from apps.ergonomia_886.planillas.models import Evaluacion


class PermisosTests(TestCase):

    def setUp(self):
        User = get_user_model()
        self.duenio = User.objects.create_user(
            email="duenio@example.com", username="duenio", password="x",
            user_type="professional",
        )
        self.intruso = User.objects.create_user(
            email="intruso@example.com", username="intruso", password="x",
            user_type="professional",
        )
        self.evaluacion = Evaluacion.objects.create(
            usuario=self.duenio,
            razon_social="ACME",
            cuit="30-1-9",
            direccion_establecimiento="X",
            provincia="Buenos Aires",
        )
        self.url = reverse(
            "exportaciones:planilla_oficial",
            args=[self.evaluacion.pk, "planilla1"],
        )

    def test_sin_sesion_redirige_al_login(self):
        respuesta = self.client.get(self.url)
        self.assertEqual(respuesta.status_code, 302)

    def test_otro_usuario_recibe_404_y_no_403(self):
        self.client.force_login(self.intruso)
        self.assertEqual(self.client.get(self.url).status_code, 404)

    def test_el_duenio_descarga_un_pdf_valido(self):
        self.client.force_login(self.duenio)
        respuesta = self.client.get(self.url)
        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(respuesta["Content-Type"], "application/pdf")
        self.assertIn("attachment;", respuesta["Content-Disposition"])
        self.assertEqual(respuesta["X-Content-Type-Options"], "nosniff")
        self.assertTrue(respuesta.content.startswith(b"%PDF-"))
        self.assertTrue(respuesta.content.rstrip().endswith(b"%%EOF"))

    def test_la_descarga_no_se_cachea(self):
        self.client.force_login(self.duenio)
        respuesta = self.client.get(self.url)
        self.assertEqual(respuesta["Cache-Control"], "private, no-store")

    def test_slug_de_planilla_invalido_da_404(self):
        self.client.force_login(self.duenio)
        url = reverse(
            "exportaciones:planilla_oficial",
            args=[self.evaluacion.pk, "planilla-inexistente"],
        )
        self.assertEqual(self.client.get(url).status_code, 404)

    def test_el_protocolo_completo_entrega_doce_o_mas_paginas(self):
        from io import BytesIO
        from pypdf import PdfReader
        self.client.force_login(self.duenio)
        url = reverse("exportaciones:protocolo_completo", args=[self.evaluacion.pk])
        respuesta = self.client.get(url)
        self.assertEqual(respuesta.status_code, 200)
        lector = PdfReader(BytesIO(respuesta.content))
        self.assertGreaterEqual(len(lector.pages), 12)

    def test_cada_descarga_queda_auditada(self):
        from apps.ergonomia_886.exportaciones.models import ExportAudit
        self.client.force_login(self.duenio)
        self.client.get(self.url)
        registro = ExportAudit.objects.get()
        self.assertEqual(registro.evaluacion_id, self.evaluacion.pk)
        self.assertEqual(registro.usuario, self.duenio)
        self.assertGreater(registro.bytes_entregados, 1000)

    def test_las_doce_planillas_responden_para_su_dueno(self):
        from apps.ergonomia_886.exportaciones.official.catalog import PLANILLA_DEFINITIONS
        self.client.force_login(self.duenio)
        for definicion in PLANILLA_DEFINITIONS:
            with self.subTest(slug=definicion.slug):
                url = reverse(
                    "exportaciones:planilla_oficial",
                    args=[self.evaluacion.pk, definicion.slug],
                )
                respuesta = self.client.get(url)
                self.assertEqual(respuesta.status_code, 200)
                self.assertTrue(respuesta.content.startswith(b"%PDF-"))

    def test_el_panel_enlaza_a_la_evaluacion_correcta(self):
        """Riesgo H-7: Evaluacion.pk y RiskEvaluation.pk no son el mismo numero."""
        from apps.ergonomia_886.evaluaciones.models import RiskEvaluation
        risk = RiskEvaluation.objects.create(evaluacion=self.evaluacion)
        self.assertNotEqual(risk.pk, self.evaluacion.pk + 1000)
        self.client.force_login(self.duenio)
        respuesta = self.client.get(
            reverse("evaluaciones:wizard_resumen_by_eval", args=[risk.pk])
        )
        self.assertContains(
            respuesta,
            reverse("exportaciones:panel", args=[self.evaluacion.pk]),
        )


class DetalleEndpointTests(TestCase):

    def setUp(self):
        from apps.ergonomia_886.evaluaciones.models import RiskEvaluation
        User = get_user_model()
        self.duenio = User.objects.create_user(
            email="duenio_d@example.com", username="duenio_d", password="x",
            user_type="professional",
        )
        self.intruso = User.objects.create_user(
            email="intruso_d@example.com", username="intruso_d", password="x",
            user_type="professional",
        )
        self.evaluacion = Evaluacion.objects.create(
            usuario=self.duenio, razon_social="ACME", cuit="30-1-9",
            direccion_establecimiento="X", provincia="Buenos Aires",
        )
        self.risk_eval = RiskEvaluation.objects.create(evaluacion=self.evaluacion)
        self.url = reverse(
            "exportaciones:factor_detalle", args=[self.evaluacion.pk, "lmc"])

    def test_otro_usuario_recibe_404(self):
        self.client.force_login(self.intruso)
        self.assertEqual(self.client.get(self.url).status_code, 404)

    def test_factor_inexistente_da_404(self):
        self.client.force_login(self.duenio)
        url = reverse("exportaciones:factor_detalle",
                      args=[self.evaluacion.pk, "factor-que-no-existe"])
        self.assertEqual(self.client.get(url).status_code, 404)

    def test_los_trece_factores_responden(self):
        from apps.ergonomia_886.evaluaciones.catalog import FACTOR_DEFINITIONS
        self.client.force_login(self.duenio)
        for definicion in FACTOR_DEFINITIONS:
            with self.subTest(slug=definicion.slug):
                url = reverse("exportaciones:factor_detalle",
                              args=[self.evaluacion.pk, definicion.slug])
                respuesta = self.client.get(url)
                self.assertEqual(respuesta.status_code, 200)
                self.assertTrue(respuesta.content.startswith(b"%PDF-"))

    def test_sin_risk_evaluation_da_404(self):
        otra = Evaluacion.objects.create(
            usuario=self.duenio, razon_social="OTRA", cuit="30-2-8",
            direccion_establecimiento="Y", provincia="Córdoba",
        )
        self.client.force_login(self.duenio)
        url = reverse("exportaciones:factor_detalle", args=[otra.pk, "lmc"])
        self.assertEqual(self.client.get(url).status_code, 404)


class BotonEnPaginaDeFactorTests(TestCase):

    def setUp(self):
        from apps.ergonomia_886.evaluaciones.models import LMC_Eval, RiskEvaluation
        self.usuario = get_user_model().objects.create_user(
            email="boton@example.com", username="boton", password="x",
            user_type="professional",
        )
        self.evaluacion = Evaluacion.objects.create(
            usuario=self.usuario, razon_social="ACME", cuit="30-1-9",
            direccion_establecimiento="X", provincia="Buenos Aires",
        )
        self.risk_eval = RiskEvaluation.objects.create(evaluacion=self.evaluacion)
        LMC_Eval.objects.create(
            risk_evaluation=self.risk_eval, factor_slug="lmc",
            calc_data={"estado_resultado": "calculado"},
        )

    def test_la_pagina_del_factor_enlaza_al_detalle_de_su_evaluacion(self):
        """Riesgo H-7: debe usar Evaluacion.pk, no RiskEvaluation.pk."""
        self.client.force_login(self.usuario)
        respuesta = self.client.get(
            reverse("evaluaciones:lmc_form_by_eval", args=[self.risk_eval.pk])
        )
        self.assertEqual(respuesta.status_code, 200)
        self.assertContains(
            respuesta,
            reverse("exportaciones:factor_detalle",
                    args=[self.evaluacion.pk, "lmc"]),
        )

    def test_las_trece_paginas_traen_el_boton(self):
        from apps.ergonomia_886.evaluaciones.catalog import FACTOR_DEFINITIONS
        self.client.force_login(self.usuario)
        for definicion in FACTOR_DEFINITIONS:
            with self.subTest(slug=definicion.slug):
                respuesta = self.client.get(
                    reverse(f"evaluaciones:{definicion.route_name_by_eval}",
                            args=[self.risk_eval.pk])
                )
                self.assertContains(respuesta, "Documentación de esta evaluación")


class BotonDeInformeTests(TestCase):

    def setUp(self):
        from apps.ergonomia_886.evaluaciones.models import RiskEvaluation
        self.usuario = get_user_model().objects.create_user(
            email="boton_i@example.com", username="boton_i", password="x",
            user_type="professional",
        )
        self.evaluacion = Evaluacion.objects.create(
            usuario=self.usuario, razon_social="ACME", cuit="30-1-9",
            direccion_establecimiento="X", provincia="Buenos Aires",
        )
        self.risk_eval = RiskEvaluation.objects.create(evaluacion=self.evaluacion)

    def _abrir_lmc(self):
        return self.client.get(
            reverse("evaluaciones:lmc_form_by_eval", args=[self.risk_eval.pk])
        )

    def test_con_resultado_calculado_el_boton_esta_habilitado(self):
        from apps.ergonomia_886.evaluaciones.models import LMC_Eval
        LMC_Eval.objects.create(
            risk_evaluation=self.risk_eval, factor_slug="lmc",
            calc_data={"estado_resultado": "calculado"},
        )
        self.client.force_login(self.usuario)
        respuesta = self._abrir_lmc()
        self.assertContains(
            respuesta,
            reverse("exportaciones:informe_factor",
                    args=[self.evaluacion.pk, "lmc"]),
        )

    def test_en_borrador_el_boton_aparece_deshabilitado(self):
        from apps.ergonomia_886.evaluaciones.models import LMC_Eval
        LMC_Eval.objects.create(
            risk_evaluation=self.risk_eval, factor_slug="lmc",
            calc_data={"estado_resultado": "borrador"},
        )
        self.client.force_login(self.usuario)
        respuesta = self._abrir_lmc()
        self.assertContains(respuesta, "disabled")
        self.assertContains(respuesta, "Guardar y calcular")

    def test_desactualizado_pide_recalcular(self):
        from apps.ergonomia_886.evaluaciones.models import LMC_Eval
        LMC_Eval.objects.create(
            risk_evaluation=self.risk_eval, factor_slug="lmc",
            calc_data={"estado_resultado": "desactualizado"},
        )
        self.client.force_login(self.usuario)
        self.assertContains(self._abrir_lmc(), "Recalcul")


class PaqueteZipTests(TestCase):

    def setUp(self):
        User = get_user_model()
        self.duenio = User.objects.create_user(
            email="duenio_z@example.com", username="duenio_z", password="x",
            user_type="professional",
        )
        self.intruso = User.objects.create_user(
            email="intruso_z@example.com", username="intruso_z", password="x",
            user_type="professional",
        )
        self.evaluacion = Evaluacion.objects.create(
            usuario=self.duenio, razon_social="ACME", cuit="30-1-9",
            direccion_establecimiento="X", provincia="Buenos Aires",
        )

    def test_el_zip_contiene_leeme_y_protocolo(self):
        import io, zipfile
        self.client.force_login(self.duenio)
        respuesta = self.client.get(
            reverse("exportaciones:paquete_zip", args=[self.evaluacion.pk]))
        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(respuesta["Content-Type"], "application/zip")
        with zipfile.ZipFile(io.BytesIO(respuesta.content)) as zf:
            nombres = zf.namelist()
            self.assertIn("LEEME.txt", nombres)
            self.assertTrue(any(n.startswith("01-protocolo-oficial/") for n in nombres))
            leeme = zf.read("LEEME.txt").decode("utf-8")
            self.assertIn("no constituye", leeme.lower())
            self.assertIn("en blanco", leeme.lower())

    def test_el_zip_no_incluye_factores_sin_iniciar(self):
        import io, zipfile
        self.client.force_login(self.duenio)
        respuesta = self.client.get(
            reverse("exportaciones:paquete_zip", args=[self.evaluacion.pk]))
        with zipfile.ZipFile(io.BytesIO(respuesta.content)) as zf:
            detalles = [n for n in zf.namelist()
                        if n.startswith("02-detalle-tecnico/")]
        self.assertEqual(detalles, [])

    def test_otro_usuario_recibe_404(self):
        self.client.force_login(self.intruso)
        self.assertEqual(
            self.client.get(
                reverse("exportaciones:paquete_zip", args=[self.evaluacion.pk])
            ).status_code, 404)
