"""Catálogo canónico de páginas habilitadas para la ayuda contextual."""

from apps.ergonomia_886.evaluaciones.catalog import FACTOR_DEFINITIONS


GLOBAL_HELP_SLUGS = (
    "guia_para_el_usuario",
    "guia_general",
)

PAGE_HELP_SLUGS = (
    "home",
    "dashboard",
    "menu_planillas",
    "crear",
    "planilla1",
    "planilla2a",
    "planilla2b",
    "planilla2c",
    "planilla2d",
    "planilla2e",
    "planilla2f",
    "planilla2g",
    "planilla2h",
    "planilla2i",
    "planilla3",
    "planilla4",
    "wizard_resumen",
    "factor",
    "exportaciones",
    "feedback",
) + tuple(definition.help_slug for definition in FACTOR_DEFINITIONS)

ALLOWED_HELP_SLUGS = frozenset(PAGE_HELP_SLUGS)
