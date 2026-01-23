# apps/ergobot_ai/prompts.py
from pathlib import Path

# Localizamos la carpeta de prompts relativa a este archivo
PROMPTS_DIR = Path(__file__).resolve().parent / "prompts"
SYSTEM_BASE_PATH = PROMPTS_DIR / "system_base.md"
MODULES_DIR = PROMPTS_DIR / "modules"

def _read_text(path: Path) -> str:
    """Lee un archivo de texto de forma segura."""
    try:
        return path.read_text(encoding="utf-8").strip()
    except FileNotFoundError:
        return ""

def build_system_prompt(module) -> str:
    """
    Arma el system prompt combinando:
    - prompts/system_base.md
    - campos markdown del TrainingModule (intro, material, transcript)
    - prompts/modules/<slug>.md (instrucciones extra por módulo)
    """
    base = _read_text(SYSTEM_BASE_PATH)

    # Extraemos el contenido del modelo TrainingModule definido en apps/training/models.py
    intro = (getattr(module, "intro_md", "") or "").strip()
    material = (getattr(module, "material_md", "") or "").strip()
    transcript = (getattr(module, "transcript_md", "") or "").strip()

    # Buscamos si existe un archivo de instrucciones extra para este slug específico
    module_slug = getattr(module, "slug", "") or ""
    per_module = _read_text(MODULES_DIR / f"{module_slug}.md") if module_slug else ""

    parts = [base]

    # Agregamos secciones solo si tienen contenido
    if intro:
        parts.append("## Introducción del módulo\n" + intro)
    if material:
        parts.append("## Material del módulo\n" + material)
    if transcript:
        parts.append("## Transcripción del módulo\n" + transcript)
    if per_module:
        parts.append("## Instrucciones específicas del módulo\n" + per_module)

    # Unimos todo con separadores claros para que la IA entienda la estructura
    return "\n\n".join([p for p in parts if p]).strip()