"""Evidencia privada de Vibración de Cuerpo Entero (commit 5.1)."""

from io import BytesIO
import zipfile

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse

from apps.ergonomia_886.evaluaciones.models import RiskEvaluation, VibracionCE_Eval
from apps.ergonomia_886.exportaciones.packaging import build_evaluation_package
from apps.ergonomia_886.exportaciones.reports.llm import sanitize_payload
from apps.ergonomia_886.planillas.models import Evaluacion


class EvidenciaVCETests(TestCase):
    @classmethod
    def setUpTestData(cls):
        User = get_user_model()
        cls.duenio = User.objects.create_professional(
            email="evidencia-duenio@test.local",
            username="evidencia-duenio",
            password="prueba",
        )
        cls.intruso = User.objects.create_professional(
            email="evidencia-intruso@test.local",
            username="evidencia-intruso",
            password="prueba",
        )
        cls.evaluacion = Evaluacion.objects.create(
            usuario=cls.duenio,
            razon_social="ACME",
            cuit="30-1-9",
            direccion_establecimiento="Depósito",
            provincia="Buenos Aires",
        )
        cls.risk = RiskEvaluation.objects.create(evaluacion=cls.evaluacion)

    def setUp(self):
        self.foto_bytes = (
            b"GIF89a\x01\x00\x01\x00\x80\x00\x00\x00\x00\x00"
            b"\xff\xff\xff!\xf9\x04\x01\x00\x00\x00\x00,\x00\x00"
            b"\x00\x00\x01\x00\x01\x00\x00\x02\x02D\x01\x00;"
        )
        self.certificado_bytes = b"certificado-calibracion-de-prueba"
        self.vce = VibracionCE_Eval.objects.create(
            risk_evaluation=self.risk,
            foto_montaje=SimpleUploadedFile(
                "montaje.gif", self.foto_bytes, content_type="image/gif"
            ),
            certificado_calibracion=SimpleUploadedFile(
                "calibracion.pdf",
                self.certificado_bytes,
                content_type="application/pdf",
            ),
        )

    def tearDown(self):
        self.vce.foto_montaje.delete(save=False)
        self.vce.certificado_calibracion.delete(save=False)

    def _url(self, tipo):
        return reverse(
            "exportaciones:evidencia_vce",
            args=[self.evaluacion.pk, self.vce.pk, tipo],
        )

    def test_se_pueden_cargar_una_foto_y_un_certificado(self):
        self.assertTrue(self.vce.foto_montaje.storage.exists(self.vce.foto_montaje.name))
        self.assertTrue(
            self.vce.certificado_calibracion.storage.exists(
                self.vce.certificado_calibracion.name
            )
        )
        with self.assertRaises(ValueError):
            _ = self.vce.foto_montaje.url

    def test_el_duenio_puede_descargar_por_la_vista_privada(self):
        self.client.force_login(self.duenio)
        respuesta = self.client.get(self._url("foto-montaje"))
        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(b"".join(respuesta.streaming_content), self.foto_bytes)
        self.assertEqual(respuesta["Cache-Control"], "private, no-store")

    def test_un_usuario_ajeno_no_puede_descargar_la_evidencia(self):
        self.client.force_login(self.intruso)
        self.assertEqual(self.client.get(self._url("foto-montaje")).status_code, 404)
        self.assertEqual(
            self.client.get(f"/media/{self.vce.foto_montaje.name}").status_code,
            404,
        )

    def test_el_zip_incluye_la_foto_y_el_certificado(self):
        paquete = build_evaluation_package(self.evaluacion)
        with zipfile.ZipFile(BytesIO(paquete)) as zf:
            nombres = zf.namelist()
            foto = next(n for n in nombres if "foto-montaje-montaje" in n)
            certificado = next(
                n for n in nombres if "certificado-calibracion-calibracion" in n
            )
            self.assertEqual(zf.read(foto), self.foto_bytes)
            self.assertEqual(zf.read(certificado), self.certificado_bytes)

    def test_cf4_el_saneamiento_excluye_las_dos_evidencias(self):
        limpio = sanitize_payload(
            {
                "factor": "vibracion_cuerpo_entero",
                "foto_montaje": self.vce.foto_montaje.name,
                "certificado_calibracion": self.vce.certificado_calibracion.name,
                "inputs": {"a_wx": "0.500"},
            }
        )
        self.assertNotIn("foto_montaje", limpio)
        self.assertNotIn("certificado_calibracion", limpio)
        self.assertEqual(limpio["inputs"]["a_wx"], "0.500")
