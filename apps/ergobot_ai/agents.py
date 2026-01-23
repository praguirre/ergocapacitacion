# apps/ergobot_ai/agents.py
from django.conf import settings
from agents import Agent
from apps.training.models import TrainingModule
from .prompts import build_system_prompt

def ergobot_agent(module_slug: str) -> Agent:
    # Buscamos el módulo específico para obtener su material y transcripción
    module = TrainingModule.objects.filter(slug=module_slug).first()

    if module:
        # Construimos las instrucciones dinámicas basadas en el contenido
        instructions = build_system_prompt(module)
    else:
        # Fallback de seguridad por si el slug no coincide
        instructions = (
            "Sos Ergobot, asistente docente experto en ergonomía. "
            "Respondé solo temas de ergonomía laboral."
        )

    return Agent(
        name="Ergobot",
        instructions=instructions,
        model=getattr(settings, "OPENAI_MODEL", "gpt-5-mini-2025-08-07"), #
    )