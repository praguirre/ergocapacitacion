# help_ai/agents.py

import functools
from agents import Agent
from django.conf import settings

from .catalog import ALLOWED_HELP_SLUGS
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

    instructions = (
        "Eres un asistente experto en la Resolución SRT 886/15 y en el uso de ErgoApp. "
        "Responde en español, con claridad, y usa Markdown cuando ayude a la legibilidad. "
        "No tienes acceso a los valores del formulario, resultados, observaciones ni datos "
        "de la evaluación que el usuario está viendo. Nunca afirmes haber visto esos datos "
        "ni inventes por qué obtuvo un nivel. Si la respuesta depende de ellos, indícale "
        "qué valores debe copiar en la consulta o qué campo debe revisar. No solicites "
        "nombres de trabajadores, CUIT ni otros datos personales innecesarios.\n\n"
        f"### VERSIÓN DEL CONTEXTO\n{context.version}\n\n"
        f"### CONTEXTO GENERAL\n{context.global_markdown}\n\n"
        f"### GUÍA ESPECÍFICA ({slug})\n{context.specific_markdown}"
    )

    return Agent(
        name=f"Asistente de Ayuda ({slug})",
        instructions=instructions,
        model=settings.CHAT_AI_MODEL,
        tools=[],  # Importante: nada de dicts como {'type': 'web_search'} aquí
    )
