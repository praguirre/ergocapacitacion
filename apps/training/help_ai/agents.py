"""Construcción del agente de ayuda contextual de Capacitaciones.

⚠️ CF-1 bis: este módulo no importa nada del paquete de ayuda del módulo 886 ni
   del asistente docente. Ver `checks.py`.
"""

from __future__ import annotations

import functools

from agents import Agent
from django.conf import settings

from .catalog import ALLOWED_HELP_SLUGS
from .pages import page_info
from .preamble import build_preamble
from .prompts import HelpContentError, page_help_context


@functools.lru_cache(maxsize=settings.CHAT_AI_AGENT_CACHE_SIZE)
def page_agent(slug: str, content_version: str, modulo: str | None = None) -> Agent:
    """Agente por pantalla, SIN guardrails ni tools, optimizado para streaming.

    La clave de caché incluye `content_version`: editar un .md invalida el
    agente automáticamente, sin reiniciar el proceso. Incluye también `modulo`
    porque la ficha de módulo forma parte de las instrucciones.
    """
    if slug not in ALLOWED_HELP_SLUGS:
        raise ValueError(f"Slug de ayuda no habilitado: {slug}")

    context = page_help_context(slug, modulo)
    if context.version != content_version:
        raise HelpContentError(
            "La versión solicitada de la ayuda ya no coincide con los documentos."
        )

    info = page_info(slug)

    partes = [
        build_preamble(slug=slug, info=info, modulo=context.modulo),
        f"### VERSIÓN DEL CONTEXTO\n{context.version}\n",
        f"### CONTEXTO GENERAL\n{context.global_markdown}\n",
    ]
    if context.module_markdown:
        partes.append(f"### FICHA DEL MÓDULO ({context.modulo})\n{context.module_markdown}\n")
    partes.append(f"### GUÍA ESPECÍFICA ({slug})\n{context.specific_markdown}")

    nombre = f"Ayuda de Capacitaciones ({slug})"
    if context.modulo:
        nombre = f"Ayuda de Capacitaciones ({slug}/{context.modulo})"

    return Agent(
        name=nombre,
        instructions="\n".join(partes),
        model=settings.CHAT_AI_MODEL,
        tools=[],  # Importante: nada de dicts como {'type': 'web_search'} acá.
    )
