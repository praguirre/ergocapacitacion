"""Contrato de la ayuda contextual del área de Capacitaciones.

Estas pruebas protegen tres cosas distintas y hay que mantener las tres:

  1. El CONTRATO DEL SLUG: catálogo, ficha, perfil y documento sincronizados.
  2. El AISLAMIENTO respecto del módulo 886: ninguna plantilla de esta área
     puede declarar `{% block help_slug %}`, porque la suite del 886 barre todo
     el proyecto y exige que ese bloque pertenezca a SU catálogo.
  3. La POSTURA DE SEGURIDAD: acceso, transporte, límites y versionado.
"""

import re
from pathlib import Path

from django.conf import settings
from django.test import SimpleTestCase

from .catalog import (
    GLOBAL_HELP_SLUGS,
    MODULOS_CON_FICHA,
    PAGE_HELP_SLUGS,
    PARTES_DEL_GLOBAL,
)
from .pages import PAGE_INFO, page_info
from .profiles import ANEXOS, documentos_modulo
from .prompts import HELP_TEXTS_PATH, HelpContentError, md, page_help_context


# Slugs que ninguna pantalla declara, a propósito.
SLUGS_DE_RESPALDO = frozenset({"home"})

# Pantallas con ayuda y la URL que hay que pedir para renderizarlas.
PANTALLAS = (
    ("capacitaciones_menu", "dashboard:capacitaciones_menu", ()),
    ("modalidad_selector", "dashboard:modalidad_selector", ("ergonomia",)),
    ("online_links", "dashboard:online_links", ("ergonomia",)),
    ("presencial_capacitacion", "dashboard:presencial:capacitacion", ("ergonomia",)),
    ("presencial_quiz", "dashboard:presencial:quiz", ("ergonomia",)),
    ("presencial_historial", "dashboard:presencial:historial", ()),
)


def _plantillas_del_proyecto():
    raiz = Path(settings.BASE_DIR)
    return list(raiz.glob("templates/**/*.html")) + list(
        raiz.glob("apps/**/templates/**/*.html")
    )


# ===========================================================================
# 1. Contrato del slug
# ===========================================================================

class ContratoDelSlugTests(SimpleTestCase):

    def test_todo_slug_tiene_documento_no_vacio(self):
        for slug in GLOBAL_HELP_SLUGS + PAGE_HELP_SLUGS + PARTES_DEL_GLOBAL:
            with self.subTest(slug=slug):
                ruta = HELP_TEXTS_PATH / f"{slug}.md"
                self.assertTrue(ruta.is_file(), f"Falta la ayuda {ruta.name}")
                self.assertTrue(
                    ruta.read_text(encoding="utf-8").strip(),
                    f"La ayuda {ruta.name} está vacía",
                )

    def test_toda_pantalla_tiene_ficha_y_ruta_absoluta(self):
        faltantes = set(PAGE_HELP_SLUGS) - set(PAGE_INFO)
        self.assertEqual(
            faltantes, set(),
            f"Slugs del catálogo sin ficha en pages.PAGE_INFO: {sorted(faltantes)}",
        )
        sobrantes = set(PAGE_INFO) - set(PAGE_HELP_SLUGS)
        self.assertEqual(
            sobrantes, set(),
            f"Fichas sin slug en el catálogo: {sorted(sobrantes)}",
        )
        for slug, info in PAGE_INFO.items():
            with self.subTest(slug=slug):
                self.assertTrue(info.titulo.strip(), "Título vacío")
                self.assertTrue(info.ruta.startswith("/"), "La ruta debe ser absoluta")
                self.assertTrue(info.proposito.strip(), "Propósito vacío")
                self.assertIsNone(
                    re.search(r"/\d+/", info.ruta),
                    f"La ruta de {slug} contiene un identificador concreto: {info.ruta}",
                )

    def test_page_info_falla_cerrado_ante_un_slug_desconocido(self):
        with self.assertRaises(KeyError):
            page_info("pantalla-que-no-existe")

    def test_todo_slug_tiene_perfil_declarado(self):
        sin_perfil = set(PAGE_HELP_SLUGS) - set(ANEXOS)
        self.assertEqual(
            sin_perfil, set(),
            f"Slugs sin perfil en profiles.ANEXOS: {sorted(sin_perfil)}. "
            "Sin perfil reciben el global completo: funciona, pero desperdicia "
            "contexto. Declaralos, aunque sea con una tupla vacía.",
        )

    def test_las_partes_reconstruyen_el_documento_maestro(self):
        reconstruido = "".join(md(nombre) for nombre in PARTES_DEL_GLOBAL)
        self.assertEqual(
            reconstruido, md("guia_capacitaciones_general"),
            "Las partes ya no reconstruyen guia_capacitaciones_general.md. "
            "Regeneralo con:\n"
            "  cat guia_capacitaciones_nucleo.md anexo_modalidades.md "
            "anexo_online.md anexo_presencial.md > guia_capacitaciones_general.md",
        )

    def test_markdown_loader_falla_cerrado(self):
        with self.assertRaises(HelpContentError):
            md("slug-que-no-existe")
        with self.assertRaises(HelpContentError):
            md("../../../etc/passwd")

    def test_guia_y_chat_comparten_version(self):
        for slug in PAGE_HELP_SLUGS:
            with self.subTest(slug=slug):
                uno = page_help_context(slug)
                otro = page_help_context(slug)
                self.assertEqual(uno.version, otro.version)
                self.assertEqual(len(uno.version), 64)

    def test_la_ficha_de_modulo_cambia_la_version(self):
        sin_modulo = page_help_context("modalidad_selector")
        con_modulo = page_help_context("modalidad_selector", "ergonomia")
        self.assertNotEqual(sin_modulo.version, con_modulo.version)
        self.assertTrue(con_modulo.module_markdown)
        self.assertFalse(sin_modulo.module_markdown)

    def test_la_ficha_de_modulo_solo_se_agrega_si_esta_declarada(self):
        self.assertEqual(documentos_modulo(None), ())
        self.assertEqual(documentos_modulo(""), ())
        self.assertEqual(documentos_modulo("modulo-inexistente"), ())
        for modulo in MODULOS_CON_FICHA:
            with self.subTest(modulo=modulo):
                self.assertEqual(documentos_modulo(modulo), (f"modulo_{modulo}",))


# ===========================================================================
# 2. Aislamiento respecto del módulo 886  ← el bloque más importante
# ===========================================================================

class AislamientoDelModulo886Tests(SimpleTestCase):
    """La suite del 886 barre TODO el proyecto buscando `help_slug`.

    Si una plantilla del área de Capacitaciones declara ese bloque, tres
    pruebas del módulo 886 fallan. Esta clase convierte ese acoplamiento en un
    fallo local y explícito, en vez de un fallo remoto y desconcertante.
    """

    PLANTILLAS_DE_CAPACITACIONES = (
        "templates/base_capacitacion_help.html",
        "templates/capacitaciones/_help_widget_body.html",
        "templates/dashboard/capacitaciones_menu.html",
        "templates/dashboard/modalidad_selector.html",
        "templates/dashboard/online_links.html",
        "templates/dashboard/share_link.html",
        "templates/presencial/capacitacion.html",
        "templates/presencial/quiz.html",
        "templates/presencial/historial.html",
    )

    def test_ninguna_plantilla_de_capacitaciones_declara_help_slug(self):
        raiz = Path(settings.BASE_DIR)
        problemas = []
        for relativa in self.PLANTILLAS_DE_CAPACITACIONES:
            contenido = (raiz / relativa).read_text(encoding="utf-8")
            if re.search(r"{%\s*block\s+help_slug\s*%}", contenido):
                problemas.append(relativa)
        self.assertEqual(
            problemas, [],
            "Estas plantillas declaran `help_slug`, que pertenece al catálogo "
            f"del módulo 886: {problemas}. Usá `capacitacion_help_slug`.",
        )

    def _slugs_declarados(self):
        patron = re.compile(
            r"{%\s*block\s+capacitacion_help_slug\s*%}\s*([a-z0-9_-]+)\s*{%\s*endblock\s*%}"
        )
        encontrados = set()
        for plantilla in _plantillas_del_proyecto():
            encontrados.update(patron.findall(plantilla.read_text(encoding="utf-8")))
        return encontrados

    def test_todo_bloque_declarado_pertenece_al_catalogo(self):
        huerfanos = self._slugs_declarados() - set(PAGE_HELP_SLUGS)
        self.assertEqual(
            huerfanos, set(),
            f"Bloques con slug sin registrar: {sorted(huerfanos)}. "
            "Agregalos a catalog.PAGE_HELP_SLUGS y creá su .md.",
        )

    def test_todo_slug_del_catalogo_lo_declara_alguna_pantalla(self):
        huerfanos = set(PAGE_HELP_SLUGS) - self._slugs_declarados() - SLUGS_DE_RESPALDO
        self.assertEqual(
            huerfanos, set(),
            f"Slugs que ninguna pantalla declara: {sorted(huerfanos)}. "
            "Si es un respaldo deliberado, agregalo a SLUGS_DE_RESPALDO con un "
            "comentario que lo justifique.",
        )

    def test_el_barrido_de_plantillas_encuentra_las_de_capacitaciones(self):
        """Guarda del guardián: si el barrido no encuentra nada, no prueba nada."""
        self.assertGreaterEqual(len(self._slugs_declarados()), 6)

    def test_ninguna_plantilla_usa_manejadores_inline_ni_cdn(self):
        raiz = Path(settings.BASE_DIR)
        for relativa in self.PLANTILLAS_DE_CAPACITACIONES:
            contenido = (raiz / relativa).read_text(encoding="utf-8")
            with self.subTest(plantilla=relativa):
                self.assertNotIn("cdn.jsdelivr.net", contenido)
                self.assertNotRegex(
                    contenido, r"\son(?:click|change|submit|load|error)\s*="
                )
