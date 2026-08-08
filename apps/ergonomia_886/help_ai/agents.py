# help_ai/agents.py

import functools
from agents import Agent
from django.conf import settings

from .catalog import ALLOWED_HELP_SLUGS
from .pages import page_info
from .preamble import build_preamble
from .prompts import HelpContentError, page_help_context


@functools.lru_cache(maxsize=settings.CHAT_AI_AGENT_CACHE_SIZE)
def page_agent(slug: str, content_version: str) -> Agent:
    """
    Agente principal por página SIN guardrails ni tools, optimizado para streaming.
    """
    if slug not in ALLOWED_HELP_SLUGS:
        raise ValueError(f"Slug de ayuda no habilitado: {slug}")

    context = page_help_context(slug)
    if context.version != content_version:
        raise HelpContentError(
            "La versión solicitada de la ayuda ya no coincide con los documentos."
        )

    info = page_info(slug)
    instructions = (
        build_preamble(slug=slug, info=info)
        + f"### VERSIÓN DEL CONTEXTO\n{context.version}\n\n"
        f"### CONTEXTO GENERAL\n{context.global_markdown}\n\n"
        f"### GUÍA ESPECÍFICA ({slug})\n{context.specific_markdown}"
    )

    return Agent(
        name=f"Asistente de Ayuda ({slug})",
        instructions=instructions,
        model=settings.CHAT_AI_MODEL,
        tools=[],  # Importante: nada de dicts como {'type': 'web_search'} aquí
    )
