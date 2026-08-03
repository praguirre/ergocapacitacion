"""Chequeos de arranque del módulo de Ergonomía SRT 886/15.

El módulo declara 48 rutas de importación como cadenas de texto. Una ruta mal
escrita no falla al arrancar: produce un HTTP 500 diferido al abrir la pantalla
que la resuelve. Estos chequeos convierten ese riesgo en errores de Django.
"""

from __future__ import annotations

import ast
import hashlib
import importlib
from pathlib import Path

from django.conf import settings
from django.core.checks import Error, Warning, register
from django.utils.module_loading import import_string


@register()
def check_rutas_declarativas(app_configs, **kwargs):
    """Verifica las 48 rutas declarativas del módulo."""
    from .evaluaciones.catalog import FACTOR_DEFINITIONS
    from .exportaciones.official.catalog import PLANILLA_DEFINITIONS
    from .exportaciones.serializers import PLANILLA2_MODELOS

    rutas = []
    for definicion in FACTOR_DEFINITIONS:
        rutas.append((definicion.form_path, f"catalog:{definicion.slug}.form_path"))
        rutas.append((definicion.model_path, f"catalog:{definicion.slug}.model_path"))
    for planilla in PLANILLA_DEFINITIONS:
        rutas.append((planilla.model_path, f"official:{planilla.slug}.model_path"))
    for slug, ruta in PLANILLA2_MODELOS.items():
        rutas.append((ruta, f"serializers:PLANILLA2_MODELOS[{slug}]"))

    errores = []
    for ruta, procedencia in rutas:
        try:
            import_string(ruta)
        except ImportError:
            errores.append(Error(
                f"Ruta declarativa no resoluble: {ruta!r}",
                hint=(
                    f"Declarada en {procedencia}. Verificar que el módulo y el "
                    "símbolo existan tras el trasplante a apps.ergonomia_886."
                ),
                id="ergonomia_886.E001",
            ))

    paquete_datos = "apps.ergonomia_886.evaluaciones.data"
    try:
        importlib.import_module(paquete_datos)
    except ImportError:
        errores.append(Error(
            f"Ruta declarativa no resoluble: {paquete_datos!r}",
            hint="Declarada en evaluaciones/calculators.py para cargar recursos.",
            id="ergonomia_886.E001",
        ))
    return errores


@register()
def check_artefactos_normativos(app_configs, **kwargs):
    """Verifica existencia, metadatos y checksum de los artefactos (CF-3)."""
    from .evaluaciones.calculators import data_file_sha256, load_json
    from .evaluaciones.catalog import FACTOR_DEFINITIONS

    problemas = []
    vistos = set()
    for definicion in FACTOR_DEFINITIONS:
        for archivo in definicion.data_files:
            if archivo in vistos:
                continue
            vistos.add(archivo)
            try:
                meta = load_json(archivo).get("meta")
                if not meta:
                    problemas.append(Error(
                        f"El artefacto {archivo!r} no declara bloque 'meta'.",
                        hint="CF-3 exige versión, fuente y trazabilidad por artefacto.",
                        id="ergonomia_886.E002",
                    ))
                    continue
                checksum = data_file_sha256(archivo)
                if len(checksum) != 64:
                    problemas.append(Error(
                        f"Checksum inválido para {archivo!r}.",
                        id="ergonomia_886.E003",
                    ))
                estado = meta.get("professional_approval", {}).get("status")
                if estado == "pending":
                    problemas.append(Warning(
                        f"El artefacto {archivo!r} tiene aprobación profesional pendiente.",
                        hint=(
                            "Los documentos generados con él no deberían presentarse "
                            "ante la ART o la SRT."
                        ),
                        id="ergonomia_886.W001",
                    ))
            except Exception as exc:  # noqa: BLE001
                problemas.append(Error(
                    f"No se pudo cargar el artefacto {archivo!r}: {exc}",
                    id="ergonomia_886.E004",
                ))
    return problemas


@register()
def check_plantilla_oficial(app_configs, **kwargs):
    """Verifica la integridad del PDF oficial de la SRT (CF-6)."""
    from .exportaciones.official.catalog import OFFICIAL_PDF, OFFICIAL_PDF_SHA256

    if not OFFICIAL_PDF.exists():
        return [Error(
            f"Falta la plantilla oficial de la SRT: {OFFICIAL_PDF}",
            hint=(
                "CF-6: los documentos oficiales sólo pueden generarse por "
                "superposición sobre este PDF. Está prohibido rellenar el .xls oficial."
            ),
            id="ergonomia_886.E005",
        )]

    real = hashlib.sha256(OFFICIAL_PDF.read_bytes()).hexdigest()
    if real != OFFICIAL_PDF_SHA256:
        return [Error(
            "El checksum de la plantilla oficial no coincide.",
            hint=(
                f"Esperado {OFFICIAL_PDF_SHA256}, obtenido {real}. "
                "El archivo fue alterado en el trasplante (CF-6)."
            ),
            id="ergonomia_886.E006",
        )]
    return []


def _imported_modules(path: Path) -> set[str]:
    """Devuelve imports estáticos; comentarios y documentación no acoplan apps."""
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    modules = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            modules.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            modules.add(node.module)
        elif (
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Name)
            and node.func.id == "import_string"
            and node.args
            and isinstance(node.args[0], ast.Constant)
            and isinstance(node.args[0].value, str)
        ):
            modules.add(node.args[0].value)
    return modules


@register()
def check_cf1_asistentes_separados(app_configs, **kwargs):
    """CF-1: help_ai y ergobot_ai no importan código entre sí."""
    base = Path(settings.BASE_DIR)
    problemas = []
    pares = (
        (base / "apps" / "ergonomia_886" / "help_ai", "apps.ergobot_ai", "help_ai"),
        (base / "apps" / "ergobot_ai", "apps.ergonomia_886.help_ai", "ergobot_ai"),
    )
    for directorio, prohibido, nombre in pares:
        if not directorio.exists():
            continue
        for archivo in directorio.rglob("*.py"):
            try:
                imports = _imported_modules(archivo)
            except (OSError, SyntaxError) as exc:
                problemas.append(Error(
                    f"No se pudo analizar CF-1 en {archivo.relative_to(base)}: {exc}",
                    id="ergonomia_886.E007",
                ))
                continue
            if any(ruta == prohibido or ruta.startswith(f"{prohibido}.") for ruta in imports):
                problemas.append(Error(
                    f"CF-1 violada: {nombre} importa {prohibido!r} en "
                    f"{archivo.relative_to(base)}.",
                    hint=(
                        "help_ai y ergobot_ai son productos distintos que comparten "
                        "proveedor. Ninguna puede importar código de la otra."
                    ),
                    id="ergonomia_886.E007",
                ))
    return problemas
