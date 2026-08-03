"""Registro canónico de las plantillas oficiales de la SRT.

Sigue el mismo patrón declarativo que `evaluaciones/catalog.py`: es
deliberadamente independiente de Django y no importa modelos.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Mapping, Tuple

BASE_DIR = Path(__file__).resolve().parent
TEMPLATES_DIR = BASE_DIR / "templates_bin"
MAPS_DIR = BASE_DIR / "maps"

OFFICIAL_PDF = TEMPLATES_DIR / "res_srt_886_15-formulario.pdf"
OFFICIAL_PDF_SHA256 = "bc0d0753943888779abd0936f6c4dc2e128766c7cf6370a4a2fb19073aad59f4"
OFFICIAL_PAGESIZE = (612.0, 792.0)


class OfficialTemplateError(RuntimeError):
    """La plantilla oficial falta, está vacía o no coincide con el checksum."""


@dataclass(frozen=True)
class PlanillaDefinition:
    """Una planilla del protocolo y su ubicación en el PDF oficial."""

    slug: str
    label: str
    page_index: int
    map_file: str
    model_path: str
    multiple: bool


PLANILLA_DEFINITIONS: Tuple[PlanillaDefinition, ...] = (
    PlanillaDefinition(
        slug="planilla1",
        label="Planilla 1 — Identificación de factores de riesgo",
        page_index=0,
        map_file="planilla1.json",
        model_path="apps.ergonomia_886.planillas.models.Planilla1",
        multiple=False,
    ),
    PlanillaDefinition("planilla2a", "Planilla 2A — Levantamiento y descenso", 1, "planilla2a.json", "apps.ergonomia_886.planillas.models.Planilla2A", True),
    PlanillaDefinition("planilla2b", "Planilla 2B — Empuje y arrastre", 2, "planilla2b.json", "apps.ergonomia_886.planillas.models.Planilla2B", True),
    PlanillaDefinition("planilla2c", "Planilla 2C — Transporte manual", 3, "planilla2c.json", "apps.ergonomia_886.planillas.models.Planilla2C", True),
    PlanillaDefinition("planilla2d", "Planilla 2D — Bipedestación", 4, "planilla2d.json", "apps.ergonomia_886.planillas.models.Planilla2D", True),
    PlanillaDefinition("planilla2e", "Planilla 2E — Movimientos repetitivos", 5, "planilla2e.json", "apps.ergonomia_886.planillas.models.Planilla2E", True),
    PlanillaDefinition("planilla2f", "Planilla 2F — Posturas forzadas", 6, "planilla2f.json", "apps.ergonomia_886.planillas.models.Planilla2F", True),
    PlanillaDefinition("planilla2g", "Planilla 2G — Vibraciones", 7, "planilla2g.json", "apps.ergonomia_886.planillas.models.Planilla2G", True),
    PlanillaDefinition("planilla2h", "Planilla 2H — Confort térmico", 8, "planilla2h.json", "apps.ergonomia_886.planillas.models.Planilla2H", True),
    PlanillaDefinition("planilla2i", "Planilla 2I — Estrés de contacto", 9, "planilla2i.json", "apps.ergonomia_886.planillas.models.Planilla2I", True),
    PlanillaDefinition("planilla3", "Planilla 3 — Medidas correctivas y preventivas", 10, "planilla3.json", "apps.ergonomia_886.planillas.models.Planilla3", False),
    PlanillaDefinition("planilla4", "Planilla 4 — Matriz de seguimiento", 11, "planilla4.json", "apps.ergonomia_886.planillas.models.SeguimientoMedida", False),
)


def _build_catalog() -> Mapping[str, PlanillaDefinition]:
    catalog = {d.slug: d for d in PLANILLA_DEFINITIONS}
    if len(catalog) != len(PLANILLA_DEFINITIONS):
        raise RuntimeError("El catálogo de planillas contiene slugs duplicados.")
    pages = {d.page_index for d in PLANILLA_DEFINITIONS}
    if len(pages) != len(PLANILLA_DEFINITIONS):
        raise RuntimeError("Dos planillas apuntan a la misma página del oficial.")
    return catalog


PLANILLA_CATALOG = _build_catalog()


def get_planilla_definition(slug: str) -> PlanillaDefinition:
    try:
        return PLANILLA_CATALOG[str(slug)]
    except KeyError as exc:
        raise OfficialTemplateError(f"Planilla desconocida: {slug!r}") from exc


@lru_cache(maxsize=1)
def official_pdf_bytes() -> bytes:
    """Devuelve el PDF oficial verificando su integridad."""
    try:
        raw = OFFICIAL_PDF.read_bytes()
    except OSError as exc:
        raise OfficialTemplateError(
            f"No se pudo leer la plantilla oficial en {OFFICIAL_PDF}"
        ) from exc

    if not raw.startswith(b"%PDF-"):
        raise OfficialTemplateError("La plantilla oficial no es un PDF válido.")

    digest = hashlib.sha256(raw).hexdigest()
    if OFFICIAL_PDF_SHA256 != "REEMPLAZAR_CON_EL_SHA256_REAL" and digest != OFFICIAL_PDF_SHA256:
        raise OfficialTemplateError(
            "El checksum de la plantilla oficial no coincide con el declarado. "
            f"Esperado {OFFICIAL_PDF_SHA256}, obtenido {digest}."
        )
    return raw


@lru_cache(maxsize=None)
def load_page_map(map_file: str) -> dict:
    """Carga un mapa de calibración desde maps/."""
    import json

    path = MAPS_DIR / map_file
    try:
        with path.open("r", encoding="utf-8") as fh:
            return json.load(fh)
    except (OSError, ValueError) as exc:
        raise OfficialTemplateError(
            f"No se pudo cargar el mapa de calibración {map_file}"
        ) from exc


__all__ = (
    "OFFICIAL_PAGESIZE",
    "OFFICIAL_PDF",
    "OFFICIAL_PDF_SHA256",
    "OfficialTemplateError",
    "PLANILLA_CATALOG",
    "PLANILLA_DEFINITIONS",
    "PlanillaDefinition",
    "get_planilla_definition",
    "load_page_map",
    "official_pdf_bytes",
)
