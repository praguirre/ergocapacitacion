"""No repetir N1: ninguna ruta del módulo devuelve 500 a un anónimo."""

from django.test import Client, TestCase
from django.urls import reverse


class AccesoAnonimoModuloTests(TestCase):
    """Todas las rutas del módulo deben redirigir o denegar, nunca romper."""

    def _rutas(self):
        return [
            reverse("planillas:crear_evaluacion"),
            reverse("planillas:detalle_evaluacion", args=[1]),
            reverse("planillas:planilla1", args=[1]),
            reverse("planillas:planilla2a", args=[1]),
            reverse("planillas:planilla3", args=[1]),
            reverse("planillas:planilla4", args=[1]),
            reverse("evaluaciones:lmc_form_by_eval", args=[1]),
            reverse("evaluaciones:wizard_resumen_by_eval", args=[1]),
            reverse("exportaciones:panel", args=[1]),
            reverse("exportaciones:protocolo_completo", args=[1]),
            reverse("exportaciones:paquete_zip", args=[1]),
            reverse("help_ai:help_guide", kwargs={"slug": "lmc"}),
        ]

    def test_ninguna_ruta_del_modulo_devuelve_500_a_un_anonimo(self):
        cliente = Client()
        for ruta in self._rutas():
            with self.subTest(ruta=ruta):
                respuesta = cliente.get(ruta)
                self.assertNotEqual(
                    respuesta.status_code,
                    500,
                    f"{ruta} devuelve HTTP 500 a un anonimo (regresion tipo N1)",
                )
                self.assertIn(respuesta.status_code, (302, 403, 404))
