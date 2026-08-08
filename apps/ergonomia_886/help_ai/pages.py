"""Identidad humana de cada pantalla del módulo SRT 886/15.

El slug es un identificador técnico: el modelo no puede deducir de él en qué
pantalla está parado el usuario. Este registro le da a cada slug un título y
una ruta reales, que el preámbulo del prompt afirma como hecho.

Regla dura: este módulo NO lee la base de datos ni el request. Sólo traduce
un slug del catálogo a texto estático. Toda entrada debe existir en
``ALLOWED_HELP_SLUGS`` y viceversa; el test de cobertura lo verifica.
"""

from __future__ import annotations

from dataclasses import dataclass

from apps.ergonomia_886.evaluaciones.catalog import FACTOR_DEFINITIONS


@dataclass(frozen=True)
class PageInfo:
    """Título, ruta y propósito de una pantalla, en lenguaje de usuario."""

    titulo: str
    ruta: str
    proposito: str


# Rutas verificadas contra el resolvedor de URLs en el commit ef6ef4e.
# Los tramos variables se muestran como <id> a propósito: el prompt no debe
# afirmar un identificador concreto que no conoce.
PAGE_INFO: dict[str, PageInfo] = {
    "dashboard": PageInfo(
        "Evaluaciones ergonómicas",
        "/evaluacion-ergonomica/",
        "listado de todas las evaluaciones del usuario, con acceso a crear, "
        "ver, editar y eliminar",
    ),
    "menu_planillas": PageInfo(
        "Menú de planillas de la evaluación",
        "/evaluacion-ergonomica/protocolo/<id>/",
        "centro de comando de una evaluación: estado de cada planilla del "
        "protocolo y acceso a completarlas",
    ),
    "crear": PageInfo(
        "Crear una evaluación nueva",
        "/evaluacion-ergonomica/protocolo/crear/",
        "formulario de datos del establecimiento a evaluar",
    ),
    "planilla1": PageInfo(
        "Planilla 1 — Identificación de factores de riesgo",
        "/evaluacion-ergonomica/protocolo/<id>/planilla1/",
        "relevamiento del puesto y matriz de factores A a I",
    ),
    "planilla2a": PageInfo(
        "Planilla 2A — Levantamiento y descenso de cargas",
        "/evaluacion-ergonomica/protocolo/<id>/planilla2a/",
        "evaluación inicial del factor A",
    ),
    "planilla2b": PageInfo(
        "Planilla 2B — Empuje y arrastre",
        "/evaluacion-ergonomica/protocolo/<id>/planilla2b/",
        "evaluación inicial del factor B",
    ),
    "planilla2c": PageInfo(
        "Planilla 2C — Transporte manual de cargas",
        "/evaluacion-ergonomica/protocolo/<id>/planilla2c/",
        "evaluación inicial del factor C",
    ),
    "planilla2d": PageInfo(
        "Planilla 2D — Bipedestación",
        "/evaluacion-ergonomica/protocolo/<id>/planilla2d/",
        "evaluación inicial del factor D",
    ),
    "planilla2e": PageInfo(
        "Planilla 2E — Movimientos repetitivos de miembros superiores",
        "/evaluacion-ergonomica/protocolo/<id>/planilla2e/",
        "evaluación inicial del factor E",
    ),
    "planilla2f": PageInfo(
        "Planilla 2F — Posturas forzadas",
        "/evaluacion-ergonomica/protocolo/<id>/planilla2f/",
        "evaluación inicial del factor F",
    ),
    "planilla2g": PageInfo(
        "Planilla 2G — Vibraciones",
        "/evaluacion-ergonomica/protocolo/<id>/planilla2g/",
        "evaluación inicial del factor G, mano-brazo y cuerpo entero",
    ),
    "planilla2h": PageInfo(
        "Planilla 2H — Confort térmico",
        "/evaluacion-ergonomica/protocolo/<id>/planilla2h/",
        "evaluación inicial del factor H",
    ),
    "planilla2i": PageInfo(
        "Planilla 2I — Estrés de contacto",
        "/evaluacion-ergonomica/protocolo/<id>/planilla2i/",
        "evaluación inicial del factor I",
    ),
    "planilla3": PageInfo(
        "Planilla 3 — Medidas correctivas y preventivas",
        "/evaluacion-ergonomica/protocolo/<id>/planilla3/",
        "carga de medidas generales y específicas para los riesgos detectados",
    ),
    "planilla4": PageInfo(
        "Planilla 4 — Seguimiento de medidas",
        "/evaluacion-ergonomica/protocolo/<id>/planilla4/",
        "matriz de seguimiento e implementación de las medidas de la Planilla 3",
    ),
    "wizard_resumen": PageInfo(
        "Resumen de la evaluación de riesgos",
        "/evaluacion-ergonomica/factores/<id>/resumen/",
        "consolidado de los factores cuantitativos evaluados y su nivel de riesgo",
    ),
    "factor": PageInfo(
        "Formulario de evaluación de un factor",
        "/evaluacion-ergonomica/factores/<id>/<factor>/",
        "carga de los datos cuantitativos de un factor de riesgo",
    ),
    "exportaciones": PageInfo(
        "Documentos de la evaluación",
        "/evaluacion-ergonomica/documentos/<id>/",
        "descarga de planillas oficiales, protocolo completo, informes y paquete ZIP",
    ),
    "home": PageInfo(
        "Módulo de Ergonomía SRT 886/15",
        "/evaluacion-ergonomica/",
        "ayuda general del módulo; esta entrada es el respaldo que se usa "
        "cuando una pantalla no declara su propia guía",
    ),
}

# Los 13 factores cuantitativos derivan su ficha del catálogo canónico, que ya
# tiene label y ruta. Duplicarlos a mano garantizaría que se desincronicen.
for _definition in FACTOR_DEFINITIONS:
    PAGE_INFO.setdefault(
        _definition.help_slug,
        PageInfo(
            _definition.label,
            f"/evaluacion-ergonomica/factores/<id>/{_definition.route.rstrip('/')}/",
            "formulario de cálculo del nivel de riesgo de este factor",
        ),
    )


def page_info(slug: str) -> PageInfo:
    """Ficha de la pantalla. Falla cerrado: un slug sin ficha es un error."""
    try:
        return PAGE_INFO[slug]
    except KeyError as exc:
        raise KeyError(
            f"El slug {slug!r} no tiene ficha de pantalla en pages.PAGE_INFO. "
            "Toda página habilitada debe declarar título, ruta y propósito."
        ) from exc
