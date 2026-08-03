"""Carga estricta y versionada del contenido de ayuda contextual."""

from __future__ import annotations

import hashlib
import logging
import re
from dataclasses import dataclass
from pathlib import Path

from django.conf import settings


logger = logging.getLogger(__name__)

# Los 33 documentos de ayuda viven en los estáticos del proyecto, no dentro
# de la app. Se ancla a settings.BASE_DIR y no a la posición de este archivo:
# al anidar la app bajo apps/ergonomia_886/, un `parent.parent` apuntaría a
# un directorio inexistente y `md()` lanzaría HelpContentError en cada
# llamada, dejando el sistema de ayuda sin funcionar (B6).
HELP_TEXTS_PATH = Path(settings.BASE_DIR) / "static" / "ayuda" / "help_texts"
VALID_HELP_NAME = re.compile(r"^[a-z0-9_-]+$")


class HelpContentError(RuntimeError):
    """El contenido de ayuda requerido no existe o no es utilizable."""


@dataclass(frozen=True)
class PageHelpContext:
    slug: str
    global_markdown: str
    specific_markdown: str
    version: str


def md(name: str) -> str:
    """Lee un Markdown requerido; nunca reemplaza una ausencia por texto vacío."""
    if not VALID_HELP_NAME.fullmatch(name):
        raise HelpContentError(f"Nombre de ayuda inválido: {name!r}")

    file_path = HELP_TEXTS_PATH / f"{name}.md"
    try:
        content = file_path.read_text(encoding="utf-8")
    except (FileNotFoundError, UnicodeDecodeError, OSError) as exc:
        logger.error("No se pudo leer el documento de ayuda %s", file_path)
        raise HelpContentError(
            f"No se pudo cargar el documento de ayuda {name}.md"
        ) from exc

    if not content.strip():
        logger.error("El documento de ayuda está vacío: %s", file_path)
        raise HelpContentError(f"El documento de ayuda {name}.md está vacío")
    return content


def page_help_context(slug: str) -> PageHelpContext:
    """Construye el contexto y un hash común para la Guía y el Chat."""
    global_markdown = md("guia_para_el_usuario") + "\n\n" + md("guia_general")
    specific_markdown = md(slug)
    version_payload = (
        f"slug:{slug}\n"
        f"---global---\n{global_markdown}\n"
        f"---specific---\n{specific_markdown}"
    )
    version = hashlib.sha256(version_payload.encode("utf-8")).hexdigest()
    return PageHelpContext(
        slug=slug,
        global_markdown=global_markdown,
        specific_markdown=specific_markdown,
        version=version,
    )
