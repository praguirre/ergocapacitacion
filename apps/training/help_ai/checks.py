"""Chequeos de arranque de la ayuda contextual de Capacitaciones.

CF-1 bis: esta app es un tercer asistente, independiente del paquete de ayuda
del módulo 886 y del asistente docente. Comparten proveedor de modelo y nada
más. Un import cruzado acoplaría el área de Capacitaciones a un módulo que el
proyecto trata como desmontable (ver apps/dashboard/views.py, que consulta
INSTALLED_APPS antes de importar los modelos del 886).

Técnica idéntica a la del chequeo homólogo del módulo 886: análisis por AST, de
modo que un comentario o un texto de documentación que mencione la otra app no
produzca un falso positivo.

⚠️ Los nombres prohibidos se componen en tiempo de ejecución, anteponiendo el
   prefijo del paquete raíz. No es un capricho de estilo: una prueba del propio
   módulo 886 barre como TEXTO PLANO todos los `.py` de `apps/training/` y falla
   si encuentra la ruta punteada completa, aunque esté dentro de una cadena o de
   un comentario. La semántica del chequeo es idéntica; sólo cambia cómo se
   escribe la constante.
"""

from __future__ import annotations

import ast
from pathlib import Path

from django.conf import settings
from django.core.checks import Error, register


_RAIZ_DE_APPS = "apps"

PROHIBIDOS = tuple(
    f"{_RAIZ_DE_APPS}.{paquete}"
    for paquete in ("ergonomia_886", "ergobot_ai")
)


def _imported_modules(path: Path) -> set[str]:
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
def check_cf1_bis_ayuda_capacitaciones(app_configs, **kwargs):
    """La ayuda de Capacitaciones no importa código de los otros asistentes."""
    base = Path(settings.BASE_DIR)
    directorio = base / "apps" / "training" / "help_ai"
    if not directorio.exists():
        return []

    problemas = []
    for archivo in directorio.rglob("*.py"):
        # Los módulos de prueba quedan fuera del barrido. CF-1 bis protege el
        # acoplamiento del código de PRODUCCIÓN: que este paquete no dependa de
        # otro asistente para funcionar. Una prueba que verifica justamente lo
        # contrario —que los leases de los dos sistemas NO colisionan— necesita
        # nombrar a los dos por diseño, y prohibírselo eliminaría la única
        # garantía automatizada de esa independencia.
        #
        # Es además la convención que el proyecto ya aplica: el barrido textual
        # de `evaluaciones/tests_sugerencias.py` sobre `apps/training/` excluye
        # los archivos cuyo nombre empieza con "test".
        if archivo.name.startswith("test"):
            continue
        try:
            imports = _imported_modules(archivo)
        except (OSError, SyntaxError) as exc:
            problemas.append(Error(
                f"No se pudo analizar CF-1 bis en {archivo.relative_to(base)}: {exc}",
                id="capacitaciones_help_ai.E001",
            ))
            continue
        for prohibido in PROHIBIDOS:
            if any(
                ruta == prohibido or ruta.startswith(f"{prohibido}.")
                for ruta in imports
            ):
                problemas.append(Error(
                    f"CF-1 bis violada: la ayuda de Capacitaciones importa "
                    f"{prohibido!r} en {archivo.relative_to(base)}.",
                    hint=(
                        "Los tres asistentes de IA del proyecto son productos "
                        "distintos. Duplicá lo que necesites o promové el código "
                        "común a un paquete neutral, pero no importes entre apps."
                    ),
                    id="capacitaciones_help_ai.E002",
                ))
    return problemas
