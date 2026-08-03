"""Pruebas del motor de superposición y de los builders oficiales."""

from __future__ import annotations

import io

from django.test import TestCase
from pypdf import PdfReader

from exportaciones.official.catalog import (
    OFFICIAL_PAGESIZE,
    PLANILLA_DEFINITIONS,
    official_pdf_bytes,
)
from exportaciones.official.overlay import DrawOp, PageOps, stamp_official_pdf
from exportaciones import serializers
from exportaciones.official.builders import (
    build_planilla1_pages, build_planilla2_pages, build_planilla4_pages,
)
from django.contrib.auth import get_user_model
from planillas.models import Evaluacion, FactorRiesgo, Planilla1


class PlantillaOficialTests(TestCase):
    """La plantilla oficial versionada debe conservar sus invariantes."""

    def test_la_plantilla_tiene_doce_paginas_tamano_carta(self):
        lector = PdfReader(io.BytesIO(official_pdf_bytes()))
        self.assertEqual(len(lector.pages), 12)
        for pagina in lector.pages:
            caja = pagina.mediabox
            self.assertAlmostEqual(float(caja.width), OFFICIAL_PAGESIZE[0], places=1)
            self.assertAlmostEqual(float(caja.height), OFFICIAL_PAGESIZE[1], places=1)

    def test_la_plantilla_no_tiene_formulario_ni_anotaciones(self):
        lector = PdfReader(io.BytesIO(official_pdf_bytes()))
        self.assertIsNone(lector.get_fields())
        for pagina in lector.pages:
            self.assertFalse(pagina.get("/Annots"))

    def test_el_catalogo_cubre_las_doce_paginas_sin_repetir(self):
        indices = sorted(d.page_index for d in PLANILLA_DEFINITIONS)
        self.assertEqual(indices, list(range(12)))

    def test_la_curva_de_fanger_sobrevive_a_la_superposicion(self):
        """La página 9 (2H) tiene 4 imágenes; superponer no debe perderlas."""
        original = PdfReader(io.BytesIO(official_pdf_bytes()))
        imagenes_originales = len(original.pages[8]["/Resources"].get("/XObject", {}))
        self.assertEqual(imagenes_originales, 4)

        salida = stamp_official_pdf([
            PageOps(page_index=8, ops=[DrawOp(text="X", x=449.5, y=400.0)])
        ])
        resultado = PdfReader(io.BytesIO(salida))
        nombres = resultado.pages[0]["/Resources"].get("/XObject", {})
        self.assertGreaterEqual(len(nombres), 4)


class OverlayTests(TestCase):

    def test_estampa_solo_las_paginas_pedidas_y_en_orden(self):
        salida = stamp_official_pdf([
            PageOps(page_index=11),
            PageOps(page_index=0),
        ])
        lector = PdfReader(io.BytesIO(salida))
        self.assertEqual(len(lector.pages), 2)
        self.assertIn("Planilla 4", lector.pages[0].extract_text())
        self.assertIn("Planilla 1", lector.pages[1].extract_text())

    def test_una_misma_pagina_puede_repetirse_sin_contaminarse(self):
        salida = stamp_official_pdf([
            PageOps(page_index=1, ops=[DrawOp(text="TAREA-UNO", x=100, y=700)]),
            PageOps(page_index=1, ops=[DrawOp(text="TAREA-DOS", x=100, y=700)]),
        ])
        lector = PdfReader(io.BytesIO(salida))
        primera = lector.pages[0].extract_text()
        segunda = lector.pages[1].extract_text()
        self.assertIn("TAREA-UNO", primera)
        self.assertNotIn("TAREA-DOS", primera)
        self.assertIn("TAREA-DOS", segunda)
        self.assertNotIn("TAREA-UNO", segunda)

    def test_pagina_sin_operaciones_queda_en_blanco(self):
        salida = stamp_official_pdf([PageOps(page_index=0)])
        texto = PdfReader(io.BytesIO(salida)).pages[0].extract_text()
        self.assertIn("Planilla 1", texto)
        self.assertNotIn("ACME", texto)

    def test_indice_de_pagina_invalido_falla(self):
        with self.assertRaises(ValueError):
            stamp_official_pdf([PageOps(page_index=99)])

    def test_texto_largo_se_recorta_y_no_invade_la_celda_vecina(self):
        salida = stamp_official_pdf([
            PageOps(page_index=0, ops=[DrawOp(
                text="X" * 500, x=118.0, y=699.8, max_width=200.0,
            )])
        ])
        texto = PdfReader(io.BytesIO(salida)).pages[0].extract_text()
        self.assertIn("…", texto)


class MapasPlanilla2Tests(TestCase):
    """Los mapas deben corresponderse exactamente con los modelos."""

    SLUGS = [f"planilla2{letra}" for letra in "abcdefghi"]

    def _mapa(self, slug):
        from exportaciones.official.catalog import get_planilla_definition, load_page_map
        return load_page_map(get_planilla_definition(slug).map_file)

    def _modelo(self, slug):
        from django.utils.module_loading import import_string
        from exportaciones.serializers import PLANILLA2_MODELOS
        return import_string(PLANILLA2_MODELOS[slug])

    def test_cada_campo_del_mapa_existe_en_el_modelo(self):
        for slug in self.SLUGS:
            with self.subTest(slug=slug):
                modelo = self._modelo(slug)
                reales = {
                    c.name for c in modelo._meta.concrete_fields
                    if c.name.startswith(("p1_", "p2_"))
                }
                mapeados = {i["campo"] for i in self._mapa(slug)["items"]}
                self.assertEqual(
                    mapeados, reales,
                    f"{slug}: faltan {reales - mapeados}, sobran {mapeados - reales}",
                )

    def test_no_hay_campos_repetidos_en_un_mapa(self):
        for slug in self.SLUGS:
            with self.subTest(slug=slug):
                items = self._mapa(slug)["items"]
                campos = [i["campo"] for i in items]
                self.assertEqual(len(campos), len(set(campos)))

    def test_las_coordenadas_caen_dentro_de_la_pagina(self):
        for slug in self.SLUGS:
            with self.subTest(slug=slug):
                mapa = self._mapa(slug)
                for item in mapa["items"]:
                    self.assertTrue(40.0 < item["y"] < 760.0, f"{slug}: {item}")
                for clave in ("si", "no"):
                    x = mapa["checkbox"]["columnas"][clave]
                    self.assertTrue(300.0 < x < 570.0, f"{slug}/{clave}: {x}")

    def test_la_columna_no_esta_a_la_derecha_de_la_columna_si(self):
        for slug in self.SLUGS:
            with self.subTest(slug=slug):
                columnas = self._mapa(slug)["checkbox"]["columnas"]
                self.assertGreater(columnas["no"], columnas["si"])

    def test_los_items_de_cada_paso_van_de_arriba_hacia_abajo(self):
        for slug in self.SLUGS:
            with self.subTest(slug=slug):
                grupos: dict[tuple, list[float]] = {}
                for item in self._mapa(slug)["items"]:
                    clave = (item.get("bloque", ""), item["paso"])
                    grupos.setdefault(clave, []).append(item["y"])
                for clave, ys in grupos.items():
                    self.assertEqual(
                        ys, sorted(ys, reverse=True),
                        f"{slug} {clave}: los y deben decrecer",
                    )

    def test_cada_mapa_apunta_a_su_pagina_oficial(self):
        from exportaciones.official.catalog import get_planilla_definition
        for slug in self.SLUGS:
            with self.subTest(slug=slug):
                self.assertEqual(
                    self._mapa(slug)["page_index"],
                    get_planilla_definition(slug).page_index,
                )


class BuildersTests(TestCase):

    def setUp(self):
        self.usuario = get_user_model().objects.create_user("builder", password="x")
        self.evaluacion = Evaluacion.objects.create(
            usuario=self.usuario, razon_social="ACME LOGÍSTICA S.A.",
            cuit="30-12345678-9", ciiu="5210",
            direccion_establecimiento="Ruta 8 km 60, Pilar", provincia="Buenos Aires",
        )

    def test_planilla1_vacia_produce_una_pagina_sin_operaciones(self):
        paginas = build_planilla1_pages(serializers.build_planilla1_payload(self.evaluacion))
        self.assertEqual(len(paginas), 1)
        self.assertEqual(paginas[0].ops, [])

    def test_planilla1_completa_dibuja_la_matriz(self):
        planilla1 = Planilla1.objects.create(
            evaluacion=self.evaluacion, area_sector="Depósito",
            puesto_trabajo="Preparador", nro_trabajadores=14,
        )
        FactorRiesgo.objects.create(
            planilla1=planilla1, tipo_factor="A", presente=True,
            tiempo_exposicion="4 h", riesgo_tarea1=3,
        )
        paginas = build_planilla1_pages(serializers.build_planilla1_payload(self.evaluacion))
        textos = [op.text for op in paginas[0].ops]
        self.assertIn("ACME LOGÍSTICA S.A.", textos)
        self.assertIn("4 h", textos)
        self.assertIn("3", textos)

    def test_planilla2a_sin_instancia_no_marca_nada(self):
        payloads = serializers.build_planilla2_payloads(self.evaluacion, "planilla2a")
        paginas = build_planilla2_pages("planilla2a", payloads)
        self.assertEqual(len(paginas), 1)
        self.assertEqual(paginas[0].ops, [])

    def test_planilla2a_guardada_marca_si_y_no(self):
        from planillas.models import Planilla2A
        Planilla2A.objects.create(
            evaluacion=self.evaluacion, tarea_nro="1",
            p1_levanta_2_a_25kg=True, p1_ciclico_diario=False,
        )
        paginas = build_planilla2_pages(
            "planilla2a", serializers.build_planilla2_payloads(self.evaluacion, "planilla2a"))
        self.assertEqual(len([op for op in paginas[0].ops if op.text == "X"]), 9)

    def test_planilla2a_con_varias_tareas_produce_varias_paginas(self):
        from planillas.models import Planilla2A
        Planilla2A.objects.create(evaluacion=self.evaluacion, tarea_nro="1")
        Planilla2A.objects.create(evaluacion=self.evaluacion, tarea_nro="2")
        paginas = build_planilla2_pages(
            "planilla2a", serializers.build_planilla2_payloads(self.evaluacion, "planilla2a"))
        self.assertEqual(len(paginas), 2)

    def test_las_nueve_planillas_marcan_todos_sus_items(self):
        from django.utils.module_loading import import_string
        from exportaciones.official.catalog import get_planilla_definition, load_page_map
        for slug, ruta in serializers.PLANILLA2_MODELOS.items():
            with self.subTest(slug=slug):
                modelo = import_string(ruta)
                modelo.objects.create(evaluacion=self.evaluacion, tarea_nro="1")
                paginas = build_planilla2_pages(
                    slug, serializers.build_planilla2_payloads(self.evaluacion, slug))
                esperados = len(load_page_map(get_planilla_definition(slug).map_file)["items"])
                self.assertEqual(len([op for op in paginas[0].ops if op.text == "X"]), esperados)
                modelo.objects.filter(evaluacion=self.evaluacion).delete()

    def test_planilla4_pagina_cuando_hay_mas_filas_que_capacidad(self):
        from planillas.models import MedidaEspecifica, Planilla3, SeguimientoMedida
        planilla3 = Planilla3.objects.create(evaluacion=self.evaluacion)
        for i in range(20):
            medida = MedidaEspecifica.objects.create(
                planilla3=planilla3, descripcion=f"Medida {i}"
            )
            SeguimientoMedida.objects.create(
                medida_especifica=medida, nombre_puesto="Preparador"
            )
        payload = serializers.build_planilla4_payload(self.evaluacion)
        paginas = build_planilla4_pages(payload)
        self.assertEqual(len(paginas), 2)

    def test_el_protocolo_completo_tiene_al_menos_doce_paginas(self):
        from exportaciones.official.builders import build_protocolo_pages
        payload = serializers.build_evaluacion_payload(self.evaluacion)
        paginas = build_protocolo_pages(payload)
        self.assertGreaterEqual(len(paginas), 12)
        self.assertEqual(paginas[0].page_index, 0)
        self.assertEqual(paginas[-1].page_index, 11)

    def test_planilla3_pagina_cuando_hay_mas_de_29_medidas(self):
        from exportaciones.official.builders import build_planilla3_pages
        from planillas.models import MedidaEspecifica, Planilla3
        planilla3 = Planilla3.objects.create(evaluacion=self.evaluacion)
        for i in range(35):
            MedidaEspecifica.objects.create(planilla3=planilla3, descripcion=f"M{i}")
        payload = serializers.build_planilla3_payload(self.evaluacion)
        self.assertEqual(len(build_planilla3_pages(payload)), 2)
