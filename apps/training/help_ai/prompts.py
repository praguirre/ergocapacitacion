"""Carga estricta y versionada del contenido de ayuda de Capacitaciones."""

from __future__ import annotations

import hashlib
import logging
import re
from dataclasses import dataclass
from pathlib import Path

from django.conf import settings

from .profiles import documentos_globales, documentos_modulo


logger = logging.getLogger(__name__)

# Los documentos viven en los estáticos del proyecto, no dentro de la app.
# Se ancla a settings.BASE_DIR y no a la posición de este archivo: al anidar la
# app bajo apps/training/, un `parent.parent` apuntaría a un directorio
# inexistente y `md()` lanzaría HelpContentError en cada llamada, dejando el
# sistema de ayuda sin funcionar.
#
# Directorio PROPIO (DA-4): compartirlo con el corpus del módulo 886 provocaría
# colisión de nombres (`home.md`, `dashboard.md`, `crear.md`, `factor.md`).
HELP_TEXTS_PATH = (
    Path(settings.BASE_DIR) / "static" / "ayuda" / "capacitaciones" / "help_texts"
)
VALID_HELP_NAME = re.compile(r"^[a-z0-9_-]+$")


class HelpContentError(RuntimeError):
    """El contenido de ayuda requerido no existe o no es utilizable."""


@dataclass(frozen=True)
class PageHelpContext:
    slug: str
    modulo: str | None
    global_markdown: str
    module_markdown: str
    specific_markdown: str
    version: str

    @property
    def guide_markdown(self) -> str:
        """Lo que se muestra en la pestaña Guía.

        Cuando hay ficha de módulo, se agrega debajo del documento de la
        pantalla, separada por una regla horizontal. El chat recibe las dos
        piezas por separado; el usuario las lee como un solo texto.
        """
        if not self.module_markdown:
            return self.specific_markdown
        return f"{self.specific_markdown}\n\n---\n\n{self.module_markdown}"


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


def page_help_context(slug: str, modulo: str | None = None) -> PageHelpContext:
    """Construye el contexto y un hash común para la Guía y el Chat.

    La versión se calcula sobre la composición EFECTIVA —incluido el anexo de
    módulo— de modo que la Guía y el Chat comparten exactamente el mismo hash
    para el mismo par (slug, módulo). Si divergieran, el Chat respondería 409
    de forma permanente y el panel quedaría inutilizable.
    """
    global_markdown = "\n\n".join(
        md(nombre) for nombre in documentos_globales(slug)
    )
    module_markdown = "\n\n".join(
        md(nombre) for nombre in documentos_modulo(modulo)
    )
    specific_markdown = md(slug)

    version_payload = (
        f"slug:{slug}\n"
        f"modulo:{modulo or ''}\n"
        f"---global---\n{global_markdown}\n"
        f"---modulo---\n{module_markdown}\n"
        f"---specific---\n{specific_markdown}"
    )
    version = hashlib.sha256(version_payload.encode("utf-8")).hexdigest()

    return PageHelpContext(
        slug=slug,
        modulo=modulo,
        global_markdown=global_markdown,
        module_markdown=module_markdown,
        specific_markdown=specific_markdown,
        version=version,
    )
