"""Composición del contexto global según la pantalla.

Hallazgo 4: enviar los 27.241 caracteres del global en todas las páginas hace
que en `crear`, `dashboard` y `home` el 98 % del prompt sea normativa que no
aplica, y ahoga la señal de la página.

Regla de degradación: un slug sin perfil declarado recibe el global COMPLETO.
Nunca menos contexto del que recibe hoy. Un olvido acá degrada el costo, no
la calidad de la respuesta.
"""

from __future__ import annotations

from apps.ergonomia_886.evaluaciones.catalog import FACTOR_DEFINITIONS

# Documentos que forman el núcleo, presentes en TODAS las páginas.
NUCLEO: tuple[str, ...] = ("guia_para_el_usuario", "guia_general_nucleo")

# Anexos por slug, en orden de inclusión. La tupla vacía significa
# "sólo el núcleo": es una decisión explícita, no un olvido.
ANEXOS: dict[str, tuple[str, ...]] = {
    "home": (),
    "dashboard": (),
    "menu_planillas": (),
    "crear": (),
    "exportaciones": (),
    "planilla1": ("guia_general_paso1",),
    "planilla2a": ("guia_general_paso2", "guia_general_paso2a"),
    "planilla2b": ("guia_general_paso2", "guia_general_paso2b"),
    "planilla2c": ("guia_general_paso2", "guia_general_paso2c"),
    "planilla2d": ("guia_general_paso2", "guia_general_paso2d"),
    "planilla2e": ("guia_general_paso2", "guia_general_paso2e"),
    "planilla2f": ("guia_general_paso2", "guia_general_paso2f"),
    "planilla2g": ("guia_general_paso2", "guia_general_paso2g"),
    "planilla2h": ("guia_general_paso2", "guia_general_paso2h"),
    "planilla2i": ("guia_general_paso2", "guia_general_paso2i"),
    "planilla3": ("guia_general_paso4",),
    "planilla4": ("guia_general_paso5",),
    "wizard_resumen": ("guia_general_paso3",),
    "factor": ("guia_general_paso3",),
}

# Los 13 factores cuantitativos comparten el PASO 3.
for _definition in FACTOR_DEFINITIONS:
    ANEXOS.setdefault(_definition.help_slug, ("guia_general_paso3",))

# Respaldo conservador para cualquier slug no contemplado.
GLOBAL_COMPLETO: tuple[str, ...] = ("guia_para_el_usuario", "guia_general")


def documentos_globales(slug: str) -> tuple[str, ...]:
    """Documentos globales que le corresponden a una pantalla."""
    if slug not in ANEXOS:
        return GLOBAL_COMPLETO
    return NUCLEO + ANEXOS[slug]
