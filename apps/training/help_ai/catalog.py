"""Catálogo canónico de pantallas habilitadas para la ayuda de Capacitaciones.

Es un conjunto CERRADO. Un slug que no esté acá produce HTTP 404 antes de que
se construya el agente: es la primera línea de defensa del endpoint.

⚠️ No confundir con `TrainingModule.slug` (`ergonomia`, `riesgo-electrico`, …).
   Aquél identifica un módulo de capacitación y vive en la base de datos; éste
   identifica una PANTALLA y vive en el código. Ver DA-7 del documento de
   auditoría.
"""

from __future__ import annotations


# Documentos globales del área. No son pantallas: nunca se sirven por
# `guide_view`, sólo alimentan el contexto general del modelo.
GLOBAL_HELP_SLUGS: tuple[str, ...] = (
    "guia_capacitaciones_usuario",
    "guia_capacitaciones_general",
)

# Partes del documento maestro. Su concatenación literal debe reconstruir
# `guia_capacitaciones_general.md`; hay una prueba que lo verifica.
PARTES_DEL_GLOBAL: tuple[str, ...] = (
    "guia_capacitaciones_nucleo",
    "anexo_modalidades",
    "anexo_online",
    "anexo_presencial",
)

# Una entrada por pantalla con ayuda contextual.
PAGE_HELP_SLUGS: tuple[str, ...] = (
    "home",                      # respaldo del bloque de la plantilla base
    "capacitaciones_menu",
    "modalidad_selector",
    "online_links",
    "share_link",
    "presencial_capacitacion",
    "presencial_quiz",
    "presencial_historial",
)

ALLOWED_HELP_SLUGS = frozenset(PAGE_HELP_SLUGS)

# --- Fichas de módulo (Fase 2) ---------------------------------------------
# Registro ESTÁTICO de los módulos que tienen anexo propio. Se valida contra
# este conjunto y no contra la base de datos, por tres motivos:
#   1. La composición del prompt no puede depender de la BD (regla dura).
#   2. Un módulo nuevo cargado desde el admin no debe romper la ayuda.
#   3. Los módulos PERSONALIZADOS llevan nombre de empresa cliente y no deben
#      tener ficha pública. Nunca se agregan acá.
MODULOS_CON_FICHA: frozenset[str] = frozenset({
    "ergonomia",
})
