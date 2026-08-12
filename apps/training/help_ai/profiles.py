"""Composición del contexto global según la pantalla.

Réplica del criterio adoptado en el módulo 886: enviar el documento global
completo en todas las pantallas hace que en las pantallas simples la mayor
parte del prompt sea material que no aplica, y ahoga la señal de la página.

Regla de degradación: un slug sin perfil declarado recibe el global COMPLETO.
Nunca menos contexto del que le corresponde. Un olvido acá degrada el costo, no
la calidad de la respuesta.
"""

from __future__ import annotations


# Documentos que forman el núcleo, presentes en TODAS las pantallas.
NUCLEO: tuple[str, ...] = (
    "guia_capacitaciones_usuario",
    "guia_capacitaciones_nucleo",
)

# Anexos por slug, en orden de inclusión. La tupla vacía significa
# "sólo el núcleo": es una decisión explícita, no un olvido.
ANEXOS: dict[str, tuple[str, ...]] = {
    "home": (),
    "capacitaciones_menu": (),
    "modalidad_selector": ("anexo_modalidades",),
    "online_links": ("anexo_modalidades", "anexo_online"),
    "share_link": ("anexo_modalidades", "anexo_online"),
    "presencial_capacitacion": ("anexo_modalidades", "anexo_presencial"),
    "presencial_quiz": ("anexo_modalidades", "anexo_presencial"),
    "presencial_historial": ("anexo_presencial",),
}

# Respaldo conservador para cualquier slug no contemplado.
GLOBAL_COMPLETO: tuple[str, ...] = (
    "guia_capacitaciones_usuario",
    "guia_capacitaciones_general",
)


def documentos_globales(slug: str) -> tuple[str, ...]:
    """Documentos globales que le corresponden a una pantalla."""
    if slug not in ANEXOS:
        return GLOBAL_COMPLETO
    return NUCLEO + ANEXOS[slug]


def documentos_modulo(modulo: str | None) -> tuple[str, ...]:
    """Anexo de módulo, si el módulo tiene ficha declarada (Fase 2).

    Degrada en silencio: un módulo desconocido —o uno personalizado, que nunca
    debe tener ficha— simplemente no aporta anexo. Nunca es un error.
    """
    from .catalog import MODULOS_CON_FICHA

    if not modulo or modulo not in MODULOS_CON_FICHA:
        return ()
    return (f"modulo_{modulo}",)
