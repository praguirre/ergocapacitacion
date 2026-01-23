# apps/ergobot_ai/agents.py
from django.conf import settings
from agents import Agent
from apps.training.models import TrainingModule
from .prompts import build_system_prompt


async def ergobot_agent(module_slug: str) -> Agent:
    """
    Crea el agente Ergobot con instrucciones específicas del módulo.
    Versión asíncrona para compatibilidad con vistas ASGI/SSE.
    """
    # ─────────────────────────────────────────────────────────────
    # IMPORTANTE: Usamos afirst() en lugar de first()
    # Django requiere métodos async del ORM dentro de vistas async
    # ─────────────────────────────────────────────────────────────
    module = await TrainingModule.objects.filter(slug=module_slug).afirst()

    if module:
        # Construimos las instrucciones dinámicas basadas en el contenido
        instructions = build_system_prompt(module)
    else:
        # Fallback de seguridad por si el slug no coincide
        instructions = (
            "Sos Ergobot, asistente docente experto en ergonomía. "
            "Tus respuestas deben ser claras, breves, concisas y amables "
            "Respondé solo temas de ergonomía laboral."
        )

    return Agent(
        name="Ergobot",
        instructions=instructions,
        model=getattr(settings, "OPENAI_MODEL", "gpt-4.1-mini-2025-04-14"),
    )
