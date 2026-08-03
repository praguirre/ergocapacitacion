# evaluaciones/calculators.py

from __future__ import annotations

import hashlib
import json
import logging
import math
import os
from dataclasses import dataclass, asdict
from decimal import Decimal
from functools import lru_cache
from typing import Any, Callable, Dict, List, Optional
from django.utils import timezone

from .catalog import FACTOR_CATALOG
from .choices import FactorSlug
from .models import VibracionCE_Eval


logger = logging.getLogger(__name__)

try:
    # Python 3.9+: acceso a archivos empaquetados como recursos
    from importlib import resources as importlib_resources  # type: ignore
except Exception:  # pragma: no cover
    import importlib_resources  # type: ignore

# --------------------------------------------------------------------------------------
# Resultados y registro
# --------------------------------------------------------------------------------------


@dataclass
class CalcResult:
    nivel: str  # "bajo" | "medio" | "alto" | "no_aplicable"
    detalle: Dict[str, Any]  # límites usados, penalizaciones/criterios, trazabilidad


REGISTRY: Dict[str, Callable[[Any], CalcResult]] = {}


def register(slug: str):
    """Decorador para registrar una función calculadora por 'slug' de factor."""
    def _wrap(fn: Callable[[Any], CalcResult]):
        REGISTRY[slug] = fn
        return fn
    return _wrap


# --------------------------------------------------------------------------------------
# Helpers comunes
# --------------------------------------------------------------------------------------


@lru_cache(maxsize=None)
def _data_dir() -> str:
    """Ubicación de /evaluaciones/data como path real (fallback si no está empaquetado)."""
    here = os.path.dirname(__file__)
    return os.path.join(here, "data")


@lru_cache(maxsize=None)
def load_json(name: str) -> Dict[str, Any]:
    """
    Carga un JSON desde evaluaciones/data/<name> con cache.
    Intenta primero como recurso empaquetado; si no, desde el filesystem.
    """
    # 1) Paquete como recurso
    try:
        data_pkg = importlib_resources.files("apps.ergonomia_886.evaluaciones.data")  # type: ignore
        with data_pkg.joinpath(name).open("r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        pass

    # 2) Filesystem (desarrollo)
    fs_path = os.path.join(_data_dir(), name)
    with open(fs_path, "r", encoding="utf-8") as f:
        return json.load(f)


@lru_cache(maxsize=None)
def data_file_sha256(name: str) -> str:
    """Devuelve el checksum del artefacto normativo exactamente cargado."""
    try:
        data_pkg = importlib_resources.files("apps.ergonomia_886.evaluaciones.data")  # type: ignore
        raw = data_pkg.joinpath(name).read_bytes()
    except Exception:
        fs_path = os.path.join(_data_dir(), name)
        with open(fs_path, "rb") as f:
            raw = f.read()
    return hashlib.sha256(raw).hexdigest()


def data_source_info(name: str, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Normaliza versión, fuente y checksum para persistirlos en ``calc_data``."""
    payload = data if data is not None else load_json(name)
    return {
        "archivo": name,
        **payload.get("meta", {}),
        "sha256": data_file_sha256(name),
    }


CALCULATION_TRACE_SCHEMA_VERSION = "1.0.0"
CALCULATION_ENGINE_VERSION = "1.0.0"


def calculation_trace(slug: str) -> Dict[str, Any]:
    """Describe motor y artefactos exactos usados por un factor."""
    definition = FACTOR_CATALOG.get(str(slug))
    return {
        "schema_version": CALCULATION_TRACE_SCHEMA_VERSION,
        "engine_version": CALCULATION_ENGINE_VERSION,
        "factor_slug": str(slug),
        "catalogued": definition is not None,
        "sources": (
            [
                data_source_info(data_file)
                for data_file in definition.data_files
            ]
            if definition is not None
            else []
        ),
    }


def _with_calculation_trace(slug: str, result: CalcResult) -> CalcResult:
    detail = dict(result.detalle or {})
    detail["calculation_trace"] = calculation_trace(str(slug))
    return CalcResult(nivel=result.nivel, detalle=detail)


def to_float(x: Any) -> float:
    if x is None:
        return float("nan")
    if isinstance(x, (int, float)):
        return float(x)
    if isinstance(x, Decimal):
        return float(x)
    try:
        return float(str(x))
    except Exception:
        return float("nan")


def bools_selected(d: Dict[str, bool]) -> Dict[str, bool]:
    """Filtra sólo los agravantes en True para trazabilidad."""
    return {k: v for k, v in d.items() if bool(v)}


def _nivel_binario(ok: bool) -> str:
    return "bajo" if ok else "alto"


def _nivel_por_relacion(valor: float, limite: float) -> str:
    """
    Regla simple v1: <= 1.0: bajo, 1.0-1.1: medio, > 1.1: alto.
    Útil si en el futuro queremos mapear bandas 'medio'.
    """
    if not math.isfinite(valor) or not math.isfinite(limite) or limite <= 0:
        return "no_aplicable"
    ratio = valor / limite
    if ratio <= 1.0:
        return "bajo"
    if ratio <= 1.1:
        return "medio"
    return "alto"

def _clamp(v: float, lo: float, hi: float) -> float:
    """Asegura que un valor esté dentro de un rango [lo, hi]."""
    return max(lo, min(hi, v))


# --------------------------------------------------------------------------------------
# LMC (Levantamiento Manual de Cargas)
# - Campos de entrada: peso_kg, duracion_h, frecuencia_h, v_altura (V), h_dist (H),
#   + agravantes (booleans). Ver formulario: peso/duración/frecuencia y V/H/agravantes.
# - Criterio (según instructivo Tablas 1, 2 y 3):
#   1) Seleccionar tabla por duración diaria (h) y frecuencia (lev/h).
#   2) Usar cruce V×H para obtener el valor límite base en kg.
#   3) Aplicar sólo penalizaciones con política profesional aprobada.
#   4) Comparar peso real vs límite ajustado → nivel bajo/medio/alto.
# --------------------------------------------------------------------------------------

def _seleccionar_tabla_lmc(duracion_h: float, frecuencia_h: int) -> int:
    """
    Implementa literalmente las condiciones de las Tablas 1, 2 y 3 del instructivo.

    Tabla 1:
      - Tareas con ≤ 2 h/día y ≤ 60 levantamientos/hora
        O
      - Tareas con > 2 h/día y ≤ 12 levantamientos/hora

    Tabla 2:
      - Tareas con > 2 h/día y > 12 y ≤ 30 levantamientos/hora
        O
      - Tareas con ≤ 2 h/día y > 60 y ≤ 360 levantamientos/hora

    Tabla 3:
      - Tareas con > 2 h/día y > 30 y ≤ 360 levantamientos/hora

    Devuelve 1, 2, 3 o 0 si la combinación queda fuera del rango de las tablas
    (por ejemplo > 360 lev/h).
    """
    # Normalización básica
    dur = max(0.0, float(duracion_h or 0.0))
    freq = max(0, int(frecuencia_h or 0))

    # Tabla 1
    cond1_a = (dur <= 2 and freq <= 60)
    cond1_b = (dur > 2 and freq <= 12)
    if cond1_a or cond1_b:
        return 1

    # Tabla 2
    cond2_a = (dur > 2 and 12 < freq <= 30)
    cond2_b = (dur <= 2 and 60 < freq <= 360)
    if cond2_a or cond2_b:
        return 2

    # Tabla 3
    if dur > 2 and 30 < freq <= 360:
        return 3

    # Fuera de rango de las tablas (p.ej. > 360 lev/h o valores 0)
    return 0


LMC_TABLA_LABELS = {
    1: "Tabla 1 (≤2 h y ≤60 lev/h; o >2 h y ≤12 lev/h)",
    2: "Tabla 2 (>2 h y 12–30 lev/h; o ≤2 h y 60–360 lev/h)",
    3: "Tabla 3 (>2 h y 30–360 lev/h)",
}

LMC_AGGRAVANT_LABELS = {
    "giro_mayor_30": "Giro mayor de 30°",
    "una_mano": "Levantamiento con una mano",
    "postura_agachada": "Postura agachada",
    "carga_inestable": "Carga inestable",
    "entorno_adverso": "Entorno adverso",
    "turnos_largos": "Turnos largos",
}


def _aplicar_agravantes_lmc(
    limite_base: float, instance: Any, cfg: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Implementa la decisión profesional vigente: los agravantes no modifican
    automáticamente el límite oficial. Si están presentes, conserva el límite
    base y exige que el profesional confirme o modifique la clasificación.
    """
    pens = cfg.get("penalizaciones", {})
    agravantes_selec: List[str] = []

    # Mapea booleanos del modelo → claves del JSON (si existen)
    mapa = {
        "giro_mayor_30": "giro_mayor_30",
        "una_mano": "una_mano",
        "postura_agachada": "postura_agachada",
        "carga_inestable": "carga_inestable",
        "entorno_adverso": "entorno_adverso",
        "turnos_largos": "turnos_largos",
    }

    for attr, key in mapa.items():
        if getattr(instance, attr, False):
            agravantes_selec.append(key)

    decision = pens.get("professional_decision", {})

    base_detail = {
        "factores": [],
        "agravantes": agravantes_selec,
        "agravantes_presentes": [
            LMC_AGGRAVANT_LABELS[key] for key in agravantes_selec
        ],
        "modo": "sin_ajuste_automatico",
        "politica_habilitada": False,
        "estado_politica": pens.get("policy_status", "missing"),
        "decision_profesional": decision,
    }

    if not agravantes_selec:
        return {
            **base_detail,
            "limite_ajustado": limite_base,
            "aplicada": False,
            "requiere_revision_profesional": False,
        }

    return {
        **base_detail,
        "limite_ajustado": None,
        "aplicada": False,
        "requiere_revision_profesional": True,
    }


@register(FactorSlug.LMC)
def calc_lmc(instance) -> CalcResult:
    """
    Calcula el nivel de riesgo de Levantamiento Manual de Cargas usando:

    - lmc_tablas.json:
        * "limites" → Tablas 1, 2 y 3 (altura V × distancia H → kg).
        * "penalizaciones" → política interna sujeta a aprobación profesional.
    - Criterio:
        1) Seleccionar tabla según duración/frecuencia (_seleccionar_tabla_lmc).
        2) Buscar límite base en data["limites"][tabla][v_altura][h_dist].
        3) Aplicar agravantes sólo si la política está aprobada.
        4) Comparar peso real vs límite ajustado → nivel bajo/medio/alto.
    """
    data = load_json("lmc_tablas.json")
    fuente = data_source_info("lmc_tablas.json", data)

    # Entradas principales. Se revalidan aquí porque el motor también puede
    # ejecutarse sobre datos históricos o sin pasar por un ModelForm.
    dur_h = to_float(getattr(instance, "duracion_h", None))
    freq_raw = to_float(getattr(instance, "frecuencia_h", None))
    peso = to_float(getattr(instance, "peso_kg", None))
    v_key = str(getattr(instance, "v_altura", "") or "")
    h_key = str(getattr(instance, "h_dist", "") or "")
    invalid = []
    if not math.isfinite(peso) or peso <= 0:
        invalid.append("peso_kg")
    if not math.isfinite(dur_h) or dur_h <= 0:
        invalid.append("duracion_h")
    if not math.isfinite(freq_raw) or freq_raw <= 0:
        invalid.append("frecuencia_h")
    if v_key not in {"suelo_espinilla", "espinilla_nudillos", "nudillos_hombro", "sobre_hombro"}:
        invalid.append("v_altura")
    if h_key not in {"proximo", "intermedio", "alejado"}:
        invalid.append("h_dist")
    if invalid:
        return CalcResult(
            nivel="no_aplicable",
            detalle={
                "motivo": "Faltan datos válidos para calcular LMC.",
                "campos_invalidos": invalid,
            },
        )
    freq_h = int(freq_raw)

    # Selección de tabla (1, 2 o 3)
    tabla_num = _seleccionar_tabla_lmc(dur_h, freq_h)

    if tabla_num == 0:
        # Fuera del rango de aplicación de las Tablas 1–3 (ej. > 360 lev/h).
        detalle = {
            "categoria": "Fuera de rango (ver instructivo Tablas 1–3)",
            "tabla": None,
            "duracion_h": dur_h,
            "frecuencia_h": freq_h,
            "peso_kg": peso,
            "motivo": (
                "Combinación de duración/frecuencia fuera del rango de las Tablas 1–3 "
                "para levantamientos repetidos."
            ),
            "fuente": fuente,
        }
        # Nivel conservador alto para que destaque en el resumen
        return CalcResult(nivel="alto", detalle=detalle)

    tabla_key = f"tabla{tabla_num}"

    # Claves de altura (V) y distancia (H) coinciden con los values de los choices
    # del modelo: 'suelo_espinilla', 'espinilla_nudillos', 'nudillos_hombro',
    # 'sobre_hombro' y 'proximo', 'intermedio', 'alejado'.
    try:
        limite_base = to_float(data["limites"][tabla_key][v_key][h_key])
    except KeyError:
        # Alguna combinación no está en el JSON → error de configuración, no del usuario.
        detalle = {
            "categoria": LMC_TABLA_LABELS.get(tabla_num, f"Tabla {tabla_num}"),
            "tabla": tabla_num,
            "duracion_h": dur_h,
            "frecuencia_h": freq_h,
            "peso_kg": peso,
            "v_altura": instance.v_altura,
            "h_dist": instance.h_dist,
            "motivo": "Combinación V/H no encontrada en lmc_tablas.json",
            "fuente": fuente,
            "keys_usadas": {"v_key": v_key, "h_key": h_key},
        }
        return CalcResult(nivel="no_aplicable", detalle=detalle)

    # Caso especial: 0 → “No se conoce un límite seguro para levantamientos repetidos”
    if limite_base <= 0:
        detalle = {
            "categoria": LMC_TABLA_LABELS.get(tabla_num, f"Tabla {tabla_num}"),
            "tabla": tabla_num,
            "duracion_h": dur_h,
            "frecuencia_h": freq_h,
            "limite_base_kg": limite_base,
            "limite_ajustado_kg": 0,
            "peso_kg": peso,
            "v_altura": instance.v_altura,
            "h_dist": instance.h_dist,
            "motivo": (
                "Zona sin límite seguro conocido en la tabla "
                "(no se conoce un límite seguro para levantamientos repetidos)."
            ),
            "fuente": fuente,
            "keys_usadas": {"v_key": v_key, "h_key": h_key},
        }
        return CalcResult(nivel="alto", detalle=detalle)

    # Aplicar agravantes según JSON
    ajuste = _aplicar_agravantes_lmc(limite_base, instance, data)
    nivel_base = _nivel_binario(peso <= limite_base)
    clasificacion_tabla = "tolerable" if nivel_base == "bajo" else "no_tolerable"
    if ajuste["requiere_revision_profesional"]:
        detalle = {
            "categoria": LMC_TABLA_LABELS.get(tabla_num, f"Tabla {tabla_num}"),
            "tabla": tabla_num,
            "limite_base_kg": limite_base,
            "limite_ajustado_kg": None,
            "peso_kg": peso,
            "duracion_h": dur_h,
            "frecuencia_h": freq_h,
            "v_altura": instance.v_altura,
            "h_dist": instance.h_dist,
            "keys_usadas": {"v_key": v_key, "h_key": h_key},
            "agravantes_true": bools_selected(
                {
                    "giro_mayor_30": instance.giro_mayor_30,
                    "una_mano": instance.una_mano,
                    "postura_agachada": instance.postura_agachada,
                    "carga_inestable": instance.carga_inestable,
                    "entorno_adverso": instance.entorno_adverso,
                    "turnos_largos": instance.turnos_largos,
                }
            ),
            "agravantes_presentes": ajuste["agravantes_presentes"],
            "penalizaciones": ajuste,
            "requiere_revision_profesional": True,
            "resultado_condicionado_por_agravantes": True,
            "clasificacion_base_nivel": nivel_base,
            "clasificacion_tabla": clasificacion_tabla,
            "motivo": (
                "La clasificación se obtuvo con el límite oficial base. Los "
                "agravantes no alteran automáticamente ese límite: el profesional "
                "debe considerarlos y confirmar o modificar la clasificación final."
            ),
            "fuente": fuente,
        }
        return CalcResult(nivel=nivel_base, detalle=detalle)

    limite_aj = to_float(ajuste["limite_ajustado"])

    # LMC se valora contra el máximo oficial: tolerable / no tolerable.
    nivel = _nivel_binario(peso <= limite_aj)

    detalle = {
        "categoria": LMC_TABLA_LABELS.get(tabla_num, f"Tabla {tabla_num}"),
        "tabla": tabla_num,
        "limite_base_kg": limite_base,
        "limite_ajustado_kg": limite_aj,
        "peso_kg": peso,
        "duracion_h": dur_h,
        "frecuencia_h": freq_h,
        "v_altura": instance.v_altura,
        "h_dist": instance.h_dist,
        "keys_usadas": {"v_key": v_key, "h_key": h_key},
        "agravantes_true": bools_selected(
            {
                "giro_mayor_30": instance.giro_mayor_30,
                "una_mano": instance.una_mano,
                "postura_agachada": instance.postura_agachada,
                "carga_inestable": instance.carga_inestable,
                "entorno_adverso": instance.entorno_adverso,
                "turnos_largos": instance.turnos_largos,
            }
        ),
        "penalizaciones": ajuste,
        "requiere_revision_profesional": False,
        "resultado_condicionado_por_agravantes": False,
        "clasificacion_base_nivel": nivel,
        "clasificacion_tabla": "tolerable" if nivel == "bajo" else "no_tolerable",
        "fuente": fuente,
    }
    return CalcResult(nivel=nivel, detalle=detalle)


# --------------------------------------------------------------------------------------
# Empuje / Tracción (Inicial y Sostenida)
#  - Campos del form: población (m/f), altura de agarre (64/95/144 cm),
#    distancia (2/8/15/30/45/60 m), frecuencia (8 opciones), fuerza medida en N.
#    【turn5file11†manual y formularios evaluaciones.md†L3-L16】【turn5file11†manual y formularios evaluaciones.md†L17-L28】
#    (Listado de frecuencias) 【turn5file10†formularios_evaluaciones.md†L1-L9】
# --------------------------------------------------------------------------------------

# --- INICIO CORRECCIÓN 2 (Empuje/Tracción) ---
FREQ_CAT_MAP = {
    "10_min": "muy_alta",
    "5_min": "alta",
    "4_min": "alta",
    "2_5_min": "media",
    "1_min": "media",
    "1_cada_2_min": "baja",
    "1_cada_5_min": "muy_baja",
    "1_cada_8_h": "muy_baja",
}
# --- FIN CORRECCIÓN 2 ---


def _lookup_fuerza_limite(
    json_name: str, pobl: str, altura_cm: int, dist_m: int, freq_slug: str
) -> Optional[float]:
    data = load_json(json_name)
    try:
        # Estructura esperada:
        # data["limites_N"][pobl][str(altura_cm)][str(dist_m)][freq_slug] -> N
        limite = data["limites_N"][pobl][str(altura_cm)][str(dist_m)][freq_slug]
        return to_float(limite)
    except KeyError:
        return None


def _calc_empuje_traccion_common(instance, tabla_json: str) -> CalcResult:
    
    # --- INICIO CORRECCIÓN 2 (Empuje/Tracción) ---
    freq_slug = str(instance.frecuencia_opcion)
    freq_key = FREQ_CAT_MAP.get(freq_slug, freq_slug)  # fallback por si ya viene categórico
    # --- FIN CORRECCIÓN 2 ---

    limite = _lookup_fuerza_limite(
        tabla_json,
        pobl=str(instance.poblacion),
        altura_cm=int(instance.altura_agarre_cm),
        dist_m=int(instance.distancia_m),
        # --- INICIO CORRECCIÓN 2 (Empuje/Tracción) ---
        freq_slug=freq_key,
        # --- FIN CORRECCIÓN 2 ---
    )
    if limite is None or not math.isfinite(limite):
        return CalcResult(
            nivel="no_aplicable",
            detalle={
                "motivo": "Combinación no encontrada en tablas",
                "poblacion": str(instance.poblacion),
                "altura_agarre_cm": int(instance.altura_agarre_cm),
                "distancia_m": int(instance.distancia_m),
                "frecuencia": str(instance.frecuencia_opcion),
                # --- INICIO CORRECCIÓN 2 (Empuje/Tracción) ---
                "frecuencia_key_usada": freq_key,
                # --- FIN CORRECCIÓN 2 ---
                "fuente": tabla_json,
            },
        )

    fuerza = to_float(instance.fuerza_n)
    nivel = _nivel_por_relacion(fuerza, limite)
    return CalcResult(
        nivel=nivel,
        detalle={
            "fuerza_medida_N": fuerza,
            "limite_N": limite,
            "poblacion": str(instance.poblacion),
            "altura_agarre_cm": int(instance.altura_agarre_cm),
            "distancia_m": int(instance.distancia_m),
            "frecuencia": str(instance.frecuencia_opcion),
            # --- INICIO CORRECCIÓN 2 (Empuje/Tracción) ---
            "frecuencia_key_usada": freq_key,
            # --- FIN CORRECCIÓN 2 ---
            "fuente": tabla_json,
        },
    )


def _map_altura_key(altura_int: int) -> str:
    """Mapea el valor numérico del modelo a la clave del JSON (alta/media/baja)."""
    if altura_int == 144:
        return "alta"
    elif altura_int == 95:
        return "media"
    else:
        return "baja" # Por defecto 64cm


def _validated_force_inputs(instance) -> tuple[Optional[Dict[str, Any]], Optional[CalcResult]]:
    """
    Contrato común de empuje/tracción. Evita que None, NaN, infinitos o
    valores fuera de los selectores lleguen a conversiones int o a tablas.
    """
    distance = to_float(getattr(instance, "distancia_m", None))
    height = to_float(getattr(instance, "altura_agarre_cm", None))
    force = to_float(getattr(instance, "fuerza_n", None))
    population = str(getattr(instance, "poblacion", "") or "")
    frequency = str(getattr(instance, "frecuencia_opcion", "") or "")
    scope = (
        ((getattr(instance, "calc_data", {}) or {}).get("input", {}) or {})
        .get("alcance_metodo", {})
    )
    scope_fields = (
        "alcance_una_persona",
        "alcance_de_pie",
        "alcance_ambas_manos",
        "alcance_objeto_frente",
    )
    missing_scope = [field for field in scope_fields if scope.get(field) is not True]
    if missing_scope:
        return None, CalcResult(
            nivel="no_aplicable",
            detalle={
                "motivo": (
                    "No se confirmó que la tarea cumpla todas las condiciones "
                    "de alcance del método de empuje/tracción."
                ),
                "condiciones_sin_confirmar": missing_scope,
            },
        )

    invalid = []
    if not math.isfinite(distance) or distance not in {2, 8, 15, 30, 45, 60}:
        invalid.append("distancia_m")
    if not math.isfinite(height) or height not in {64, 95, 144}:
        invalid.append("altura_agarre_cm")
    if not math.isfinite(force) or force < 0:
        invalid.append("fuerza_n")
    if population not in {"m", "f"}:
        invalid.append("poblacion")
    if frequency not in {
        "10_min",
        "5_min",
        "4_min",
        "2_5_min",
        "1_min",
        "1_cada_2_min",
        "1_cada_5_min",
        "1_cada_8_h",
    }:
        invalid.append("frecuencia_opcion")

    if invalid:
        return None, CalcResult(
            nivel="no_aplicable",
            detalle={
                "motivo": "Faltan datos válidos para calcular empuje/tracción.",
                "campos_invalidos": invalid,
            },
        )
    return {
        "distance": int(distance),
        "height": int(height),
        "force": force,
        "population": population,
        "frequency": frequency,
        "scope": scope,
    }, None

@register(FactorSlug.EMPUJE_INICIAL)
def calc_empuje_inicial(instance) -> CalcResult:
    """
    Calculadora directa para Empuje Inicial (Tabla 1 SRT 3345/15).
    Usa la estructura jerárquica: Distancia -> Frecuencia -> Altura -> Sexo.
    """
    values, error = _validated_force_inputs(instance)
    if error:
        return error

    # 1. Cargar datos limpios
    data = load_json("empuje_inicial.json")
    
    # 2. Obtener inputs del modelo (ya validados por el form)
    # Como el choice usa etiquetas de rango, el valor guardado (instance.distancia_m)
    # ya es el límite superior (ej: 8, 15), listo para usar como clave.
    dist_key = str(values["distance"])
    freq_key = values["frequency"] # Ej: "10_min", "1_cada_5_min"
    
    # Mapeo de altura (144 -> "alta") y población
    altura_key = _map_altura_key(values["height"])
    sexo_key = values["population"] # "m" o "f"

    # 3. Búsqueda en el JSON (Try/Except para manejo robusto de errores)
    try:
        # Navegación directa: Distancia -> Frecuencia -> Altura -> Sexo
        tabla_dist = data["limites_N"].get(dist_key)
        if not tabla_dist:
            raise KeyError(f"Distancia {dist_key}m no encontrada")

        tabla_freq = tabla_dist.get(freq_key)
        if not tabla_freq:
            # Caso común: Usuario eligió frecuencia "10 por min" en distancia "60m" (no existe en norma)
            return CalcResult(
                nivel="no_aplicable", 
                detalle={
                    "motivo": f"La combinación de {dist_key}m y frecuencia seleccionada no existe en la Tabla 1.",
                    "recomendacion": "Verifique si la frecuencia es compatible con la distancia recorrida."
                }
            )
            
        limite = to_float(tabla_freq[altura_key][sexo_key])

    except (KeyError, ValueError, TypeError) as e:
        return CalcResult(
            nivel="no_aplicable",
            detalle={"motivo": f"Error en búsqueda de datos: {str(e)}"}
        )

    # 4. Evaluación del Riesgo (Criterio Binario Estricto)
    fuerza_medida = values["force"]
    
    if fuerza_medida <= limite:
        nivel = "bajo" # Aceptable
    else:
        nivel = "alto" # No Aceptable / Riesgo

    # 5. Retorno con trazabilidad completa
    return CalcResult(
        nivel=nivel,
        detalle={
            "fuerza_medida_N": fuerza_medida,
            "limite_N": limite,
            "parametros_usados": {
                "distancia": f"{dist_key} m",
                "frecuencia": freq_key,
                "altura": altura_key,
                "sexo": sexo_key
            },
            "alcance_metodo": values["scope"],
            "fuente": "empuje_inicial.json (Tabla 1 SRT 3345/15)",
            "criterio": "Fuerza > Límite = Riesgo"
        }
    )


@register(FactorSlug.EMPUJE_SOSTENIDA)
def calc_empuje_sostenida(instance) -> CalcResult:
    """
    Calculadora directa para Empuje Sostenida (Tabla 2 SRT 3345/15).
    Estructura: Distancia -> Frecuencia -> Altura -> Sexo
    """
    values, error = _validated_force_inputs(instance)
    if error:
        return error

    data = load_json("empuje_sostenida.json")

    dist_key = str(values["distance"])               # 2/8/15/30/45/60
    freq_key = values["frequency"]             # "10_min", "1_cada_5_min", etc.
    altura_key = _map_altura_key(values["height"])  # "baja"/"media"/"alta"
    sexo_key = values["population"]

    try:
        tabla_dist = data["limites_N"].get(dist_key)
        if not tabla_dist:
            raise KeyError(f"Distancia {dist_key}m no encontrada")

        tabla_freq = tabla_dist.get(freq_key)
        if not tabla_freq:
            # combinación no existente en la norma para esa distancia
            validas = list(tabla_dist.keys())
            return CalcResult(
                nivel="no_aplicable",
                detalle={
                    "motivo": f"La frecuencia '{freq_key}' no aplica para {dist_key}m (Tabla 2).",
                    "recomendacion": f"Frecuencias válidas para {dist_key}m: {', '.join(validas)}",
                    "fuente": "empuje_sostenida.json (Tabla 2 SRT 3345/15)",
                },
            )

        limite = to_float(tabla_freq[altura_key][sexo_key])

    except (KeyError, ValueError, TypeError) as e:
        return CalcResult(
            nivel="no_aplicable",
            detalle={
                "motivo": f"Error en búsqueda de datos (Tabla 2): {str(e)}",
                "fuente": "empuje_sostenida.json (Tabla 2 SRT 3345/15)",
            },
        )

    fuerza_medida = values["force"]
    nivel = "bajo" if fuerza_medida <= limite else "alto"

    return CalcResult(
        nivel=nivel,
        detalle={
            "fuerza_medida_N": fuerza_medida,
            "limite_N": limite,
            "resultado": "ACEPTABLE" if nivel == "bajo" else "RIESGO ERGONÓMICO",
            "parametros_usados": {
                "distancia": f"{dist_key} m",
                "frecuencia": freq_key,
                "altura": altura_key,
                "sexo": sexo_key,
            },
            "alcance_metodo": values["scope"],
            "fuente": "empuje_sostenida.json (Tabla 2 SRT 3345/15)",
            "criterio": "Fuerza > Límite = Riesgo",
        },
    )

@register(FactorSlug.TRACCION_INICIAL)
def calc_traccion_inicial(instance) -> CalcResult:
    """
    Calculadora directa para Tracción Inicial (Tabla 3 SRT 3345/15).
    Lógica: Distancia (Rango) -> Frecuencia -> Altura -> Sexo.
    """
    values, error = _validated_force_inputs(instance)
    if error:
        return error

    # 1. Cargar Datos
    data = load_json("traccion_inicial.json")
    fuente = data_source_info("traccion_inicial.json", data)

    # 2. Obtener Inputs
    # instance.distancia_m es un entero (2, 8, 15...) gracias al Select de Rangos en forms.py/choices.py
    dist_key = str(values["distance"])
    
    # Frecuencia seleccionada (ej: "10_min")
    freq_key = values["frequency"]

    # Mapeo de altura (95 -> media) y sexo (mixto -> f)
    # Nota: _map_altura_key ya está definida en tu archivo (si no, avísame)
    altura_key = _map_altura_key(values["height"])
    sexo_input = values["population"]
    sexo_key = "m" if sexo_input == "m" else "f"

    # 3. Búsqueda y Validación
    try:
        # A. Validar Distancia
        tabla_dist = data["limites_N"].get(dist_key)
        if not tabla_dist:
            raise KeyError(f"Distancia {dist_key}m no encontrada (¿Rango inválido?)")

        # B. Validar Frecuencia para esa distancia
        tabla_freq = tabla_dist.get(freq_key)
        if not tabla_freq:
            # Combinación inválida (ej: 10_min en 60m)
            validas = data.get("frecuencias_validas_por_distancia", {}).get(dist_key, [])
            validas_str = ", ".join(validas) if validas else "Ninguna definida"
            
            return CalcResult(
                nivel="no_aplicable",
                detalle={
                    "motivo": f"La frecuencia '{freq_key}' no es válida para la distancia de {dist_key}m (Tabla 3).",
                    "recomendacion": f"Seleccione una frecuencia válida: {validas_str}",
                    "parametros": {"distancia": dist_key, "frecuencia": freq_key}
                }
            )

        # C. Obtener Límite
        limite = to_float(tabla_freq[altura_key][sexo_key])

    except (KeyError, ValueError, TypeError) as e:
        return CalcResult(
            nivel="no_aplicable",
            detalle={
                "motivo": f"Error técnico buscando límite: {str(e)}", 
                "fuente": "traccion_inicial.json"
            }
        )

    # 4. Evaluación del Riesgo
    fuerza_medida = values["force"]
    usa_celda_ajustada = (
        dist_key == "60"
        and freq_key == "1_cada_8_h"
        and altura_key == "alta"
        and sexo_key == "f"
    )
    
    if fuerza_medida <= limite:
        nivel = "bajo" # ACEPTABLE
    else:
        nivel = "alto" # RIESGO

    return CalcResult(
        nivel=nivel,
        detalle={
            "fuerza_medida_N": fuerza_medida,
            "limite_N": limite,
            "resultado": "ACEPTABLE" if nivel == "bajo" else "RIESGO ERGONÓMICO",
            "parametros_usados": {
                "distancia_rango_superior": f"{dist_key} m",
                "frecuencia": freq_key,
                "altura": altura_key,
                "sexo": sexo_key
            },
            "alcance_metodo": values["scope"],
            "requiere_revision_profesional": usa_celda_ajustada,
            "advertencia_fuente": (
                "La imagen oficial publica 1460 N para esta celda; ErgoApp usa "
                "140 N como corrección interna conservadora sin fe de erratas "
                "oficial localizada. El resultado requiere aprobación profesional."
                if usa_celda_ajustada
                else None
            ),
            "fuente": fuente,
        }
    )

@register(FactorSlug.TRACCION_SOSTENIDA)
def calc_traccion_sostenida(instance) -> CalcResult:
    """
    Calculadora para Tracción Sostenida (Tabla 4 SRT 3345/15).
    Usa el valor 'snapped' del selector de rangos (2, 8, 15, 30, 45, 60).
    """
    values, error = _validated_force_inputs(instance)
    if error:
        return error

    # 1. Cargar Datos
    data = load_json("traccion_sostenida.json")

    # 2. Obtener Inputs
    # Distancia viene del Select de rangos como entero (ej: 8, 15, 30)
    dist_key = str(values["distance"])
    
    # Frecuencia seleccionada (ej: "10_min")
    freq_key = values["frequency"]

    # Mapeo de altura y sexo (Mixto -> f)
    # Nota: _map_altura_key ya está definida en tu archivo
    altura_key = _map_altura_key(values["height"])
    
    # Población: Aseguramos que si viene vacío o mixto, use 'f'
    sexo_input = values["population"]
    sexo_key = "m" if sexo_input == "m" else "f"

    # 3. Búsqueda y Validación
    try:
        # A. Validar Distancia
        tabla_dist = data["limites_N"].get(dist_key)
        if not tabla_dist:
            raise KeyError(f"Distancia {dist_key}m no encontrada (¿Rango inválido?)")

        # B. Validar Frecuencia
        tabla_freq = tabla_dist.get(freq_key)
        if not tabla_freq:
            validas = data.get("frecuencias_validas_por_distancia", {}).get(dist_key, [])
            validas_str = ", ".join(validas) if validas else "Ninguna"
            
            return CalcResult(
                nivel="no_aplicable",
                detalle={
                    "motivo": f"La frecuencia '{freq_key}' no es válida para tracción sostenida a {dist_key}m.",
                    "recomendacion": f"Seleccione una frecuencia válida: {validas_str}",
                    "parametros": {"distancia": dist_key, "frecuencia": freq_key}
                }
            )

        # C. Obtener Límite
        limite = to_float(tabla_freq[altura_key][sexo_key])

    except (KeyError, ValueError, TypeError) as e:
        return CalcResult(
            nivel="no_aplicable",
            detalle={
                "motivo": f"Error técnico buscando límite: {str(e)}", 
                "fuente": "traccion_sostenida.json"
            }
        )

    # 4. Evaluación
    fuerza_medida = values["force"]
    
    if fuerza_medida <= limite:
        nivel = "bajo" # ACEPTABLE
    else:
        nivel = "alto" # RIESGO

    return CalcResult(
        nivel=nivel,
        detalle={
            "fuerza_medida_N": fuerza_medida,
            "limite_N": limite,
            "resultado": "ACEPTABLE" if nivel == "bajo" else "RIESGO ERGONÓMICO",
            "parametros_usados": {
                "distancia_rango": f"{dist_key} m",
                "frecuencia": freq_key,
                "altura": altura_key,
                "sexo": sexo_key
            },
            "alcance_metodo": values["scope"],
            "fuente": "Tabla 4 (SRT 3345/2015)"
        }
    )



# --------------------------------------------------------------------------------------
# Transporte Manual de Cargas (Masa acumulada)
# --------------------------------------------------------------------------------------

def _lookup_tramo_transporte(dist_m: float) -> Optional[Dict[str, Any]]:
    """
    Selecciona conservadoramente la primera distancia oficial mayor o igual que
    la medida. La Tabla 1 sólo llega a 20 m; no se extrapolan distancias mayores.
    """
    data = load_json("transporte_limites.json")
    rows = sorted(
        data.get("tabla_distancias", []),
        key=lambda row: to_float(row.get("distancia_m")),
    )
    previous_distance = 0.0
    for row in rows:
        table_distance = to_float(row.get("distancia_m"))
        if dist_m <= table_distance:
            return {
                "min_exclusive": previous_distance,
                "max_inclusive": table_distance,
                "distancia_tabla_m": table_distance,
                "frecuencia_max_referencia_15kg_min": to_float(
                    row.get("frecuencia_max_referencia_15kg_min")
                ),
                "masa_max_kg_min": to_float(row.get("masa_max_kg_min")),
                "masa_max_kg_h": to_float(row.get("masa_max_kg_h")),
                "limite_kg_jornada": to_float(row.get("limite_kg_jornada")),
            }
        previous_distance = table_distance
    return None


def _lookup_limite_transporte(dist_m: float) -> Optional[float]:
    tramo = _lookup_tramo_transporte(dist_m)
    return tramo["limite_kg_jornada"] if tramo else None

@register(FactorSlug.TRANSPORTE)
def calc_transporte(instance) -> CalcResult:
    data = load_json("transporte_limites.json")
    fuente = data_source_info("transporte_limites.json", data)
    m = to_float(getattr(instance, "masa_kg", None))
    f_min = to_float(getattr(instance, "frecuencia_max_minuto", None))
    f_h = to_float(getattr(instance, "frecuencia_max_hora", None))
    f = to_float(getattr(instance, "frecuencia_jornada", None))
    d = to_float(getattr(instance, "distancia_m", None))

    # --- Sección 2: condiciones de aplicabilidad (del formulario) ---
    s2 = {
        "plano_horizontal": getattr(instance, "en_plano_horizontal", None),
        "jornada_8h": getattr(instance, "jornada_8h", None),
        "velocidad_05a1_ms": getattr(instance, "velocidad_05a1_ms", None),
        "superficie_plana": getattr(instance, "superficie_plana", None),
    }
    # Si alguna fue respondida “No”, la norma no aplica
    fail = [k for k, v in s2.items() if v is False]
    if fail:
        return CalcResult(
            nivel="no_aplicable",
            detalle={
                "motivo": "Una o más condiciones de la Sección 2 no se cumplen.",
                "condiciones_fallidas": fail,
            },
        )
    if any(v is None for v in s2.values()):
        return CalcResult(
            nivel="no_aplicable",
            detalle={
                "motivo": "Faltan respuestas obligatorias en la Sección 2.",
                "condiciones_faltantes": [k for k, v in s2.items() if v is None],
            },
        )

    # Reglas mínimas de datos (Sección 1/3)
    if not math.isfinite(m) or m < 2.0:
        return CalcResult(nivel="no_aplicable",
                          detalle={"motivo": "Peso inválido o < 2 kg (condición mínima)."})
    if not math.isfinite(d) or d < 1.0:
        return CalcResult(nivel="no_aplicable",
                          detalle={"motivo": "Distancia inválida o < 1 m: fuera de alcance del método."})
    if not math.isfinite(f) or f <= 0 or not f.is_integer():
        return CalcResult(nivel="no_aplicable",
                          detalle={"motivo": "Frecuencia inválida: debe ser un entero positivo."})
    if not math.isfinite(f_min) or f_min <= 0 or not f_min.is_integer():
        return CalcResult(
            nivel="no_aplicable",
            detalle={"motivo": "Falta el máximo de traslados observado en un minuto."},
        )
    if not math.isfinite(f_h) or f_h <= 0 or not f_h.is_integer():
        return CalcResult(
            nivel="no_aplicable",
            detalle={"motivo": "Falta el máximo de traslados observado en una hora."},
        )
    if f_h < f_min or f < f_h:
        return CalcResult(
            nivel="no_aplicable",
            detalle={
                "motivo": (
                    "Frecuencias incoherentes: debe cumplirse máximo/minuto ≤ "
                    "máximo/hora ≤ total/jornada."
                )
            },
        )

    m_acum = m * f
    m_acum_min = m * f_min
    m_acum_h = m * f_h
    tramo = _lookup_tramo_transporte(d)
    limite = tramo["limite_kg_jornada"] if tramo else None
    if limite is None or not math.isfinite(limite):
        return CalcResult(
            nivel="no_aplicable",
            detalle={
                "motivo": "No hay límite definido para el tramo de distancia.",
                "masa_kg": m,
                "frecuencia_jornada": f,
                "distancia_m": d,
                "distancia_maxima_tabla_m": 20,
                "fuente": fuente,
                **s2,
            },
        )

    # La definición legal exige valorar masa acumulada a corto, mediano y largo
    # plazo. Se usan máximos observados, no promedios derivados de la jornada.
    verificaciones = {
        "masa_max_kg_min": m_acum_min <= tramo["masa_max_kg_min"],
        "masa_max_kg_h": m_acum_h <= tramo["masa_max_kg_h"],
        "masa_max_kg_jornada": m_acum <= limite,
    }
    nivel = _nivel_binario(all(verificaciones.values()))

    return CalcResult(
        nivel=nivel,
        detalle={
            "masa_kg": m,
            "frecuencia_jornada": f,
            "distancia_m": d,
            "masa_acumulada_kg_jornada": m_acum,
            "limite_kg_jornada": limite,
            "tramo_distancia_m": {
                "min_exclusive": tramo["min_exclusive"],
                "max_inclusive": tramo["max_inclusive"],
            },
            "distancia_tabla_m": tramo["distancia_tabla_m"],
            "frecuencia_max_referencia_15kg_min": tramo[
                "frecuencia_max_referencia_15kg_min"
            ],
            "masa_max_kg_min": tramo["masa_max_kg_min"],
            "masa_max_kg_h": tramo["masa_max_kg_h"],
            "frecuencia_max_minuto_observada": f_min,
            "frecuencia_max_hora_observada": f_h,
            "masa_acumulada_kg_minuto": m_acum_min,
            "masa_acumulada_kg_hora": m_acum_h,
            "verificaciones_tabla": verificaciones,
            "criterio": (
                "CUMPLE si las masas acumuladas máximas por minuto/hora y el total de 8 h "
                "no superan ningún máximo de la primera distancia oficial mayor "
                "o igual que la distancia medida."
            ),
            "fuente": fuente,
            **s2,
        },
    )


# --------------------------------------------------------------------------------------
# Stubs iniciales (a completar con sus tablas / criterios)
# --------------------------------------------------------------------------------------


# --- Helpers específicos Bipedestación ----------------------------------------

def _cat_por_duracion(minutos: float, bins: list[dict]) -> dict:
    """
    Devuelve {"idx": 0..2, "id": <str>, "rango": "<texto>"} según bins del JSON.
    bins: [
      {"id":"lt_2h", "max_min":120, "label":"<2 h"},
      {"id":"2a4h", "min_min":120, "max_min":240, "label":"2 a <4 h"},
      {"id":"ge_4h", "min_min":240, "max_min":null, "label":"≥4 h"}
    ]
    """
    for i, b in enumerate(bins):
        raw_min = b.get("min_min")
        raw_max = b.get("max_min")
        mn = float("-inf") if raw_min is None else to_float(raw_min)
        mx = float("inf") if raw_max is None else to_float(raw_max)
        if mn <= minutos < mx:
            return {"idx": i, "id": b.get("id"), "rango": b.get("label")}
    # fallback: última
    b = bins[-1]
    return {"idx": len(bins) - 1, "id": b.get("id"), "rango": b.get("label")}


def _count_true(d: dict) -> int:
    return sum(1 for v in d.values() if bool(v))


def _apply_controls_reduction(
    ag_count: int, controles: list[str], cfg: dict
) -> tuple[int, dict]:
    """Resta puntos de agravantes por controles existentes (no baja de 0)."""
    reducciones = cfg.get("controles_reduccion", {})
    usados = {}
    new = ag_count
    for c in controles or []:
        delta = int(reducciones.get(c, 0))
        if delta:
            new = max(0, new - delta)
            usados[c] = delta
    return new, usados


# --- Calculadora ---------------------------------------------------------------

@register(FactorSlug.BIPEDESTACION)
def calc_bipedestacion(instance) -> CalcResult:
    """
    Cribado v1 de Bipedestación:
    - Duración CONTINUA (min) → categoría (<2h / 2–4h / >4h), con ajuste por deambulación.
    - Conteo de AGRAVANTES (carga >2kg, calor, piso, calzado, posturas sostenidas, etc.)
    - Reducción por CONTROLES existentes.
    - Regla clínica: síntomas relevantes (diaria/semanal) ⇒ 'alto'.
    - Matriz (duración × agravantes) → nivel: bajo/medio/alto.
    """
    cfg = load_json("bipedestacion_limites.json")
    inp = (getattr(instance, "calc_data", {}) or {}).get("input", {})

    # ------------------ Duraciones (total y continua) ------------------
    total_h = to_float(
        getattr(instance, "horas_de_pie_total", inp.get("horas_total_h", 0))
    )
    cont_min_raw = to_float(
        getattr(instance, "tiempo_continuo_min", inp.get("tiempo_continuo_min", 0))
    )

    # Movilidad: si hay deambulación significativa, reducimos la duración efectiva
    movilidad_tipo = getattr(instance, "movilidad_tipo", inp.get("movilidad_tipo", ""))
    movilidad_mph = to_float(
        getattr(instance, "movilidad_m_por_h", inp.get("movilidad_m_por_h", 0))
    )

    invalid = []
    if not math.isfinite(total_h) or total_h <= 0:
        invalid.append("horas_de_pie_total")
    if not math.isfinite(cont_min_raw) or cont_min_raw <= 0:
        invalid.append("tiempo_continuo_min")
    if str(movilidad_tipo) not in {"estatica", "deambulacion"}:
        invalid.append("movilidad_tipo")
    if str(movilidad_tipo) == "deambulacion" and (
        not math.isfinite(movilidad_mph) or movilidad_mph < 0
    ):
        invalid.append("movilidad_m_por_h")
    if invalid:
        return CalcResult(
            nivel="no_aplicable",
            detalle={
                "motivo": "Faltan datos válidos para calcular Bipedestación.",
                "campos_invalidos": invalid,
            },
        )
    if not math.isfinite(movilidad_mph):
        movilidad_mph = 0.0

    mov_cfg = cfg.get(
        "movilidad", {"deambulacion_threshold_mph": 100, "factor_reduccion": 0.7}
    )

    cont_min_eff = cont_min_raw
    if (
        str(movilidad_tipo) == "deambulacion"
        and movilidad_mph > to_float(mov_cfg.get("deambulacion_threshold_mph", 100))
    ):
        cont_min_eff = cont_min_raw * to_float(mov_cfg.get("factor_reduccion", 0.7))

    # Categoría de duración (usa minutos EFECTIVOS)
    dur_cat = _cat_por_duracion(cont_min_eff, cfg["categorias_duracion_min"])

    # ------------------ Agravantes ------------------
    # Booleans ya modelados (con fallback a input_json para compatibilidad)
    agravantes = {
        "carga_mayor_2kg": bool(
            getattr(instance, "manipula_cargas_mayores_2kg", False)
            or inp.get("carga_mayor_2kg")
        ),
        "calor_ambiente": bool(
            getattr(instance, "ambiente_caluroso", False)
            or inp.get("ambiente_caluroso")
        ),

        # Piso y calzado
        "piso_duro": bool(
            getattr(instance, "piso_duro", False)
            or inp.get("piso_duro")
        ),
        "piso_irregular": bool(
            getattr(instance, "superficie_irregular", False)
            or inp.get("piso_irregular")
        ),
        "piso_resbaladizo": bool(
            getattr(instance, "piso_resbaladizo", False)
            or inp.get("piso_resbaladizo")
        ),
        "calzado_inadecuado": bool(
            getattr(instance, "calzado_inadecuado", False)
            or inp.get("calzado_inadecuado")
        ),

        # Posturas sostenidas (ISO 11226)
        "tronco_inclinado": bool(
            getattr(instance, "tronco_inclinado", False)
            or inp.get("tronco_inclinado")
        ),
        "brazos_elevados": bool(
            getattr(instance, "brazos_elevados", False)
            or inp.get("brazos_elevados")
        ),
        "cuello_giro_inclin": bool(
            getattr(instance, "cuello_giro_inclin", False)
            or inp.get("cuello_giro_inclin")
        ),
    }

    # Agravantes adicionales cargados desde input_json (si los hubiera)
    extra_agravantes = {
        k: bool(v)
        for k, v in (inp.get("extra_agravantes") or {}).items()
    }
    agravantes.update(extra_agravantes)

    ag_count_bruto = _count_true(agravantes)

    # ------------------ Controles existentes ------------------
    controles = list(getattr(instance, "controles_existentes_json", []))
    ag_count, controles_usados = _apply_controls_reduction(
        ag_count_bruto, controles, cfg
    )

    # Bucket de agravantes alineado a la matriz del manual:
    # col 0 = 0 agravantes, col 1 = 1 agravante, col 2 = >= 2
    buckets = cfg.get("agravantes_buckets", [0, 1])
    if ag_count <= buckets[0]:
        ag_col = 0
    elif ag_count <= buckets[1]:
        ag_col = 1
    else:
        ag_col = 2

    ag_bucket = {"count": ag_count, "col": ag_col}

    # ------------------ Reglas clínicas adicionales ------------------
    sintomas = getattr(instance, "sintomas_json", []) or inp.get("sintomas", [])
    freq = (
        getattr(instance, "sintomas_frecuencia", "")
        or inp.get("sintomas_frecuencia", "")
    )
    freq_norm = str(freq).strip().lower()

    sintomas_relevantes = bool(sintomas) and freq_norm in ("diaria", "semanal")

    razon_clinica = ""
    if sintomas_relevantes:
        razon_clinica = "Síntomas reportados con frecuencia diaria/semanal"
        nivel = "alto"
    else:
        # Matriz duración × agravantes
        matriz = cfg["matriz"]
        nivel = matriz[dur_cat["idx"]][ag_col]
        razon_clinica = ""

        # Regla de acumulación diaria: si total_h supera umbral, elevar al menos a 'medio'
        umbral_total = to_float(cfg.get("total_horas_al_menos_medio", 4))
        if total_h >= umbral_total and nivel == "bajo":
            nivel = "medio"

    # ------------------ Recomendaciones base ------------------
    # Sugerimos los controles que aún no están presentes (ordenados por prioridad del JSON)
    prioridades = cfg.get(
        "recomendaciones_control_order",
        ["alfombra", "banqueta", "footrest", "rotacion"],
    )
    sugerencias = [c for c in prioridades if c not in controles]

    detalle = {
        "duracion": {
            "total_h": total_h,
            "continuo_min_bruto": cont_min_raw,
            "continuo_min_efectivo": cont_min_eff,
            "categoria": dur_cat,
            "movilidad": {
                "tipo": movilidad_tipo,
                "m_por_h": movilidad_mph,
                "cfg": mov_cfg,
            },
        },
        "agravantes": {
            "seleccionados": bools_selected(agravantes),
            "conteo_bruto": ag_count_bruto,
            "conteo_ajustado_por_controles": ag_count,
            "bucket": ag_bucket,
        },
        "controles": {"aplicados": controles, "descuentos": controles_usados},
        "matriz_usada": "duración × agravantes",
        "reglas_adicionales": {
            "sintomas_relevantes": sintomas_relevantes,
            "sintomas_frecuencia": freq_norm or None,
            "motivo_clinico": razon_clinica,
            "total_horas_al_menos_medio": cfg.get("total_horas_al_menos_medio", 4),
        },
        "sugerencias_controles": sugerencias,
        "fuente": "bipedestacion_limites.json",
        "input": inp,
    }

    return CalcResult(nivel=nivel, detalle=detalle)


# --- Helpers específicos NAM/FPN ----------------------------------------------



def _as_points(seq):
    """
    Acepta [{"x":0,"y":7}, {"x":10,"y":0}] o [[0,7],[10,0]] y devuelve lista de (x,y) ordenada.
    """
    pts = []
    for item in seq:
        if isinstance(item, dict):
            pts.append((to_float(item["x"]), to_float(item["y"])))
        else:
            x, y = item
            pts.append((to_float(x), to_float(y)))
    pts.sort(key=lambda p: p[0])
    return pts


def _y_from_polyline(points, x: float) -> float:
    """
    Interpola linealmente sobre una polilínea definida por puntos ordenados.
    Si x queda fuera del rango, usa el extremo más cercano (clamp).
    """
    pts = _as_points(points)
    if not pts:
        return float("nan")
    if x <= pts[0][0]:
        return pts[0][1]
    if x >= pts[-1][0]:
        return pts[-1][1]
    for (x1, y1), (x2, y2) in zip(pts, pts[1:]):
        if x1 <= x <= x2 and x2 != x1:
            t = (x - x1) / (x2 - x1)
            return y1 + t * (y2 - y1)
    return float("nan")  # no debería ocurrir


# --- Calculadora NAM (repetitivos de MS) --------------------------------------


@register(FactorSlug.REPETITIVOS_MS)
def calc_repetitivos_ms(instance) -> CalcResult:
    """
    Método NAM: se posiciona el punto (NAM, FPN) y se compara contra:
      - VLU (Valor Límite Umbral) -> por encima => ALTO
      - LA (Límite de Acción)     -> entre LA y VLU => MEDIO
      - por debajo de LA         -> BAJO
    Reglas de aplicabilidad:
      - monotarea debe ser True
      - horas_dia >= 4
    Factores agravantes: exigen revisión profesional y reducir la exposición por
      debajo del LA. No escalan automáticamente porque la norma no prescribe
      un desplazamiento cuantitativo de las líneas.
    """
    data = load_json("repetitivos_ms_limites.json")

    # 1) Verificación de aplicabilidad
    monotarea = bool(getattr(instance, "monotarea", False))
    horas_dia = to_float(getattr(instance, "horas_dia", 0))
    if not monotarea or not (math.isfinite(horas_dia) and horas_dia >= 4.0):
        return CalcResult(
            nivel="no_aplicable",
            detalle={
                "motivo": "Método NAM no aplicable (monotarea=False o <4 h/día)",
                "monotarea": monotarea,
                "horas_dia": horas_dia,
                "requisito": "Monotarea y duración >= 4 h/día",
                "fuente": "repetitivos_ms_limites.json",
            },
        )

    # 2) Tomar valores NAM (X) y FPN (Y)
    nam = to_float(getattr(instance, "nam_x_valor", float("nan")))
    fpn = to_float(
        getattr(instance, "borg_y_valor", float("nan"))
    )  # ya viene discretizado (usar valor más alto si es rango)
    if not math.isfinite(nam) or not math.isfinite(fpn):
        return CalcResult(
            nivel="no_aplicable",
            detalle={
                "motivo": "Faltan valores válidos de NAM y/o FPN/Borg.",
                "NAM": None if not math.isfinite(nam) else nam,
                "FPN": None if not math.isfinite(fpn) else fpn,
                "fuente": "repetitivos_ms_limites.json",
            },
        )

    # Rango gráfico (default 0-10 si no se define en el JSON)
    rx = data.get("rango_nam", [0, 10])
    ry = data.get("rango_fpn", [0, 10])
    nam = _clamp(nam, to_float(rx[0]), to_float(rx[1]))
    fpn = _clamp(fpn, to_float(ry[0]), to_float(ry[1]))

    # 3) Obtener límites (líneas) para ese NAM
    vlu_line = data["lineas"]["vlu"]  # puntos de la polilínea VLU
    la_line = data["lineas"]["la"]  # puntos de la polilínea LA
    y_vlu = _y_from_polyline(vlu_line, nam)
    y_la = _y_from_polyline(la_line, nam)

    # 4) Clasificación
    #    y >= y_vlu -> ALTO
    #    y >= y_la  -> MEDIO
    #    y < y_la   -> BAJO
    # Para puntos exactamente sobre la línea, se considera el nivel superior.
    if not math.isfinite(y_vlu) or not math.isfinite(y_la):
        return CalcResult(
            nivel="no_aplicable",
            detalle={"motivo": "Límites no definidos/invalidos para NAM", "NAM": nam},
        )

    if fpn >= y_vlu:
        nivel = "alto"
        zona = "peligro (sobre VLU)"
    elif fpn >= y_la:
        nivel = "medio"
        zona = "zona de control (entre LA y VLU)"
    else:
        nivel = "bajo"
        zona = "zona de seguridad (bajo LA)"

    # 5) Factores agravantes → revisión profesional obligatoria.
    agravantes_dict = {
        "posturas_obligadas": bool(getattr(instance, "posturas_obligadas", False)),
        "estres_contacto": bool(getattr(instance, "estres_contacto", False)),
        "bajas_temperaturas": bool(getattr(instance, "bajas_temperaturas", False)),
        "vibraciones_mb": bool(getattr(instance, "vibraciones_mb", False)),
    }
    agravantes_true = bools_selected(agravantes_dict)
    aggravating_rule = data.get(
        "agravantes",
        {
            "rule": "professional_review_required",
            "automatic_level_change": False,
        },
    )
    requiere_revision_profesional = bool(agravantes_true)
    recomendaciones = []
    if requiere_revision_profesional:
        recomendaciones.append(
            "Aplicar juicio profesional y reducir la exposición por debajo del "
            "Límite de Acción (LA) debido a los factores agravantes."
        )

    # 6) Métricas útiles para el informe
    distancia_sobre_LA = fpn - y_la  # >0 si está por encima de LA
    distancia_sobre_VLU = fpn - y_vlu  # >0 si está por encima de VLU
    margen_hasta_LA = max(0.0, y_la - fpn)  # >0 si está por debajo de LA

    detalle = {
        "metodo": "NAM",
        "coordenadas": {"NAM": nam, "FPN": fpn},
        "limites": {"y_LA": y_la, "y_VLU": y_vlu},
        "zona": zona,
        "distancias": {
            "sobre_LA": distancia_sobre_LA,
            "sobre_VLU": distancia_sobre_VLU,
            "margen_hasta_LA": margen_hasta_LA,
        },
        "agravantes_true": agravantes_true,
        "requiere_revision_profesional": requiere_revision_profesional,
        "resultado_condicionado_por_agravantes": requiere_revision_profesional,
        "regla_agravantes": aggravating_rule,
        "recomendaciones": recomendaciones,
        "aplicabilidad": {"monotarea": monotarea, "horas_dia": horas_dia},
        "fuente": {
            "archivo": "repetitivos_ms_limites.json",
            **data.get("meta", {}),
        },
    }
    return CalcResult(nivel=nivel, detalle=detalle)


# --- Helpers REBA --------------------------------------------------------------


def _get_inputs(instance) -> Dict[str, Any]:
    """
    Espera que la vista ponga los valores del formulario en instance.calc_data["input"].
    Estructura esperada (booleans/int):
    {
      # Grupo A
      "cuello_base": 1|2,
      "cuello_torsion_inclin": bool,

      "piernas_base": 1|2,               # 1=bilateral/andando/sentado, 2=unilateral/ligero/inestable
      "piernas_flex_30_60": bool,      # +1
      "piernas_flex_mas_60": bool,     # +2 (salvo sedente)
      "piernas_sedente": bool,         # si True, ignora el +2

      "tronco_base": 1|2|3|4,            # 1=erguido; 2=0-20° flex/ext; 3=20-60° flex o >20° ext; 4=>60° flex
      "tronco_torsion_inclin": bool,   # +1

      "carga_categoria": 0|1|2,          # 0:<5 kg; 1:5-10; 2:>10
      "fuerza_rapida": bool,           # +1

      # Grupo B
      "brazo_base": 1|2|3|4,             # 1=0-20°; 2=>20° ext o 20-45° flex; 3=45-90°; 4=>90°
      "brazo_abduccion_rotacion": bool, # +1
      "brazo_hombro_elevado": bool,   # +1
      "brazo_apoyo": bool,             # -1 (a favor de gravedad)

      "antebrazo_base": 1|2,             # 1=60-100° flex; 2=<60° o >100°
      "muneca_base": 1|2,                # 1=0-15°; 2=>15°
      "muneca_torsion_desviacion": bool,# +1
      "agarre": 0|1|2|3,                 # 0=bueno, 1=regular, 2=malo, 3=inaceptable

      # Corrección por actividad (+1 si cualquiera es True)
      "actividad_estatica": bool,
      "actividad_repetitiva": bool,
      "actividad_inestable": bool
    }
    """
    data = getattr(instance, "calc_data", {}) or {}
    return dict(data.get("input", {}))


def _reba_lookup_tabla_a(neck: int, legs: int, trunk: int) -> int:
    data = load_json("posturas_forzadas_puntajes.json")
    arr = data["tabla_A"][str(legs)][str(neck)]  # lista idx 0..4 => tronco 1..5
    return int(arr[trunk - 1])


def _reba_lookup_tabla_b(forearm: int, wrist: int, upper_arm: int) -> int:
    data = load_json("posturas_forzadas_puntajes.json")
    arr = data["tabla_B"][str(forearm)][str(wrist)]  # lista idx 0..5 => brazo 1..6
    return int(arr[upper_arm - 1])


def _reba_lookup_tabla_c(punt_a: int, punt_b: int) -> int:
    data = load_json("posturas_forzadas_puntajes.json")
    return int(data["tabla_C"][punt_a - 1][punt_b - 1])


def _reba_nivel_accion(p_final: int) -> Dict[str, Any]:
    # Tabla de nivel de acción del manual
    if p_final <= 1:
        return {"accion": 0, "texto": "No necesario"}
    if 2 <= p_final <= 3:
        return {"accion": 1, "texto": "Puede ser necesario"}
    if 4 <= p_final <= 7:
        return {"accion": 2, "texto": "Necesario"}
    if 8 <= p_final <= 10:
        return {"accion": 3, "texto": "Necesario pronto"}
    return {"accion": 4, "texto": "Actuación inmediata"}  # 11–15


def _map_final_a_nivel_riesgo(p_final: int) -> str:
    # Mapa simple a bajo/medio/alto (para integrarse con el resto del sistema)
    if p_final <= 1:
        return "bajo"
    if 2 <= p_final <= 7:
        return "medio"
    return "alto"  # >= 8


@register(FactorSlug.POSTURAS_FORZADAS)
def calc_posturas_forzadas(instance) -> CalcResult:
    """
    Calcula REBA completo.
    Corrige: Lógica acumulativa de actividad y mapeo de Tabla C (max 12).
    """
    inp = _get_inputs(instance)

    numeric_ranges = {
        "cuello_base": (1, 2),
        "piernas_base": (1, 2),
        "tronco_base": (1, 5),
        "carga_categoria": (0, 2),
        "brazo_base": (1, 6),
        "antebrazo_base": (1, 2),
        "muneca_base": (1, 2),
        "agarre": (0, 3),
    }
    normalized = {}
    invalid = []
    for field, (minimum, maximum) in numeric_ranges.items():
        try:
            value = int(inp[field])
        except (KeyError, TypeError, ValueError):
            invalid.append(field)
            continue
        if not minimum <= value <= maximum:
            invalid.append(field)
        else:
            normalized[field] = value
    if inp.get("piernas_flex_30_60") and inp.get("piernas_flex_mas_60"):
        invalid.append("flexion_rodillas_incompatible")
    if inp.get("piernas_sedente") and (
        inp.get("piernas_flex_30_60") or inp.get("piernas_flex_mas_60")
    ):
        invalid.append("piernas_sedente_con_flexion")
    if invalid:
        return CalcResult(
            nivel="no_aplicable",
            detalle={
                "motivo": "Entradas REBA incompletas o incompatibles.",
                "campos_invalidos": invalid,
            },
        )
    inp = {**inp, **normalized}

    # --- Grupo A: Cuello, Piernas, Tronco ---
    cuello = inp["cuello_base"]
    if inp.get("cuello_torsion_inclin"):
        cuello += 1
    cuello = max(1, min(3, cuello))

    piernas = inp["piernas_base"]
    if inp.get("piernas_flex_30_60"):
        piernas += 1
    if inp.get("piernas_flex_mas_60") and not inp.get("piernas_sedente"):
        piernas += 2
    piernas = max(1, min(4, piernas))

    tronco = inp["tronco_base"]
    if inp.get("tronco_torsion_inclin"):
        tronco += 1
    tronco = max(1, min(5, tronco))

    # Lookup Tabla A: El JSON corregido espera [piernas][cuello][tronco]
    # Restamos 1 porque los índices de lista son base-0
    try:
        res_tabla_a = _reba_lookup_tabla_a(neck=cuello, legs=piernas, trunk=tronco)
    except (KeyError, IndexError, TypeError, ValueError):
        logger.exception("Tabla A de REBA inválida o inconsistente")
        return CalcResult(
            nivel="no_aplicable",
            detalle={
                "motivo": "No se pudo resolver la Tabla A de REBA.",
                "fuente": "posturas_forzadas_puntajes.json",
            },
        )

    # Carga / Fuerza
    carga = inp["carga_categoria"]
    if inp.get("fuerza_rapida"):
        carga += 1
    carga = max(0, min(3, carga))
    
    punt_a = res_tabla_a + carga

    # --- Grupo B: Brazo, Antebrazo, Muñeca ---
    brazo = inp["brazo_base"]
    if inp.get("brazo_abduccion_rotacion"):
        brazo += 1
    if inp.get("brazo_hombro_elevado"):
        brazo += 1
    if inp.get("brazo_apoyo"):
        brazo -= 1
    brazo = max(1, min(6, brazo))

    antebrazo = inp["antebrazo_base"]
    antebrazo = max(1, min(2, antebrazo))

    muneca = inp["muneca_base"]
    if inp.get("muneca_torsion_desviacion"):
        muneca += 1
    muneca = max(1, min(3, muneca))

    # Lookup Tabla B: El JSON corregido espera [antebrazo][muneca][brazo]
    try:
        res_tabla_b = _reba_lookup_tabla_b(forearm=antebrazo, wrist=muneca, upper_arm=brazo)
    except (KeyError, IndexError, TypeError, ValueError):
        logger.exception("Tabla B de REBA inválida o inconsistente")
        return CalcResult(
            nivel="no_aplicable",
            detalle={
                "motivo": "No se pudo resolver la Tabla B de REBA.",
                "fuente": "posturas_forzadas_puntajes.json",
            },
        )

    # Agarre
    agarre = inp["agarre"]
    agarre = max(0, min(3, agarre))
    
    punt_b = res_tabla_b + agarre

    # --- Tabla C ---
    # Manual: "Si el Resultado A es >12, usar valor 12. Igual para B."
    idx_a = max(1, min(12, punt_a))
    idx_b = max(1, min(12, punt_b))
    
    try:
        punt_c = _reba_lookup_tabla_c(idx_a, idx_b)
    except (KeyError, IndexError, TypeError, ValueError):
        logger.exception("Tabla C de REBA inválida o inconsistente")
        return CalcResult(
            nivel="no_aplicable",
            detalle={
                "motivo": "No se pudo resolver la Tabla C de REBA.",
                "fuente": "posturas_forzadas_puntajes.json",
            },
        )

    # --- Actividad (CORREGIDO: ACUMULATIVO) ---
    # Sumamos +1 por cada condición verdadera
    corr_actividad = 0
    if inp.get("actividad_estatica"):
        corr_actividad += 1
    if inp.get("actividad_repetitiva"):
        corr_actividad += 1
    if inp.get("actividad_inestable"):
        corr_actividad += 1
    
    punt_final = punt_c + corr_actividad

    # Determinación de Niveles
    nivel_accion_info = _reba_nivel_accion(punt_final)
    nivel_riesgo = _map_final_a_nivel_riesgo(punt_final)

    detalle = {
        # Estas claves coinciden con los campos del modelo PosturasForzadas_Eval
        # para que apply_result las guarde automáticamente en la BD:
        "puntaje_a": punt_a,
        "puntaje_b": punt_b,
        "puntaje_c": punt_c,
        "puntaje_final": punt_final,
        
        # Trazabilidad adicional (se guardará en calc_data)
        "grupo_A": {
             "cuello": cuello, "piernas": piernas, "tronco": tronco,
             "tabla_A_val": res_tabla_a, "carga_val": carga
        },
        "grupo_B": {
             "brazo": brazo, "antebrazo": antebrazo, "muneca": muneca,
             "tabla_B_val": res_tabla_b, "agarre_val": agarre
        },
        "actividad_sum": corr_actividad,
        "nivel_accion_texto": nivel_accion_info["texto"],
        "input": inp,
        "fuente": "posturas_forzadas_puntajes.json"
    }

    return CalcResult(nivel=nivel_riesgo, detalle=detalle)



# ----------------------- Helpers comunes de este bloque -----------------------


def _lookup_limit_by_time(hours, table_rows):
    """
    table_rows: lista de dicts con {"min_h": float|None, "max_h": float|None, "limite_m_s2": float, "action_fraction": float}
    Devuelve (limite, action_limite, fila_usada)
    """
    h = to_float(hours)
    chosen = None
    for row in table_rows:
        mn = row.get("min_h", None)
        mx = row.get("max_h", None)
        ok_min = (mn is None) or (h >= to_float(mn))
        ok_max = (mx is None) or (h < to_float(mx))
        if ok_min and ok_max:
            chosen = row
            break
    if chosen is None:
        chosen = table_rows[-1]  # cae en la última
    L = to_float(chosen["limite_m_s2"])
    frac = to_float(chosen.get("action_fraction", 0.5))
    return L, L * frac, chosen


def _bucket_3(n: float) -> str:
    # Conveniencia para >0, ==1, >=2
    if n <= 0:
        return "0"
    if n == 1:
        return "1"
    return "2p"


def _risk_from_value(value, action_limit, legal_limit):
    """
    Clasifica usando dos umbrales:
      - value < action_limit  → bajo
      - action_limit ≤ value ≤ legal_limit → medio
      - value  > legal_limit → alto
    """
    if value < action_limit:
        return "bajo"
    if value <= legal_limit:
        return "medio"
    return "alto"


# ============================================================================ #
#                              VIBRACIÓN MANO-BRAZO (VMB)
# ============================================================================ #

@register(FactorSlug.VIBRACION_MB)
@register("vibracion_mb")  # alias por si tu FactorSlug usa este valor
def calc_vibracion_mano_brazo(instance) -> CalcResult:
    if not getattr(instance, "aplicable", True):
        return CalcResult(nivel="no_aplicable", detalle={"motivo": "No aplicable"})

    data = load_json("vibracion_mano_brazo_limites.json")
    tipo = (getattr(instance, "tipo_exposicion", "simple") or "simple").lower()

    val_final = 0.0
    tiempo_total = 0.0
    eje_dominante = "N/A"
    detalle_calculo = {}

    # -------------------------
    # CASO 1: SIMPLE
    # -------------------------
    if tipo == "simple":
        t = to_float(getattr(instance, "duracion_h", 0))
        if not (t > 0 and math.isfinite(t)):
            return CalcResult(nivel="no_aplicable", detalle={"motivo": "Duración inválida (<=0).", "duracion_h": t})

        tiempo_total = t

        ax = to_float(getattr(instance, "ax_mps2", None))
        ay = to_float(getattr(instance, "ay_mps2", None))
        az = to_float(getattr(instance, "az_mps2", None))

        if math.isfinite(ax) and math.isfinite(ay) and math.isfinite(az):
            if any(value < 0 for value in (ax, ay, az)):
                return CalcResult(
                    nivel="no_aplicable",
                    detalle={"motivo": "Las aceleraciones por eje no pueden ser negativas."},
                )
            vals = {"X": ax, "Y": ay, "Z": az}
            eje_dominante = max(vals, key=vals.get)
            val_final = vals[eje_dominante]
            detalle_calculo = {"metodo": "Ejes (simple)", "valores": vals}
        else:
            ak = to_float(getattr(instance, "a_k_m_s2", None))
            if not math.isfinite(ak) or ak < 0:
                return CalcResult(nivel="no_aplicable", detalle={"motivo": "Aceleración legacy inválida.", "a_k_m_s2": ak})
            eje_dominante = "Legacy"
            val_final = ak
            detalle_calculo = {"metodo": "Valor único (legacy)"}

    # -------------------------
    # CASO 2: MÚLTIPLE
    # -------------------------
    else:
        items = getattr(instance, "exposiciones_json", None) or []
        if not items:
            return CalcResult(nivel="no_aplicable", detalle={"motivo": "Sin ítems de exposición (exposiciones_json vacío)."})

        sum_t = 0.0
        sum_e_x = sum_e_y = sum_e_z = 0.0
        sum_e_legacy = 0.0
        usando_ejes = False
        usando_legacy = False

        for it in items:
            ti = to_float((it or {}).get("Ti_h", 0))
            if not (math.isfinite(ti) and ti > 0):
                return CalcResult(
                    nivel="no_aplicable",
                    detalle={"motivo": "Todos los tramos deben tener un tiempo finito mayor a 0."},
                )

            sum_t += ti

            iax = to_float((it or {}).get("ax_mps2", float("nan")))
            iay = to_float((it or {}).get("ay_mps2", float("nan")))
            iaz = to_float((it or {}).get("az_mps2", float("nan")))

            if math.isfinite(iax) and math.isfinite(iay) and math.isfinite(iaz):
                if any(value < 0 for value in (iax, iay, iaz)):
                    return CalcResult(
                        nivel="no_aplicable",
                        detalle={"motivo": "Las aceleraciones de los tramos no pueden ser negativas."},
                    )
                usando_ejes = True
                sum_e_x += (iax ** 2) * ti
                sum_e_y += (iay ** 2) * ti
                sum_e_z += (iaz ** 2) * ti
            else:
                iaw = to_float((it or {}).get("awi_mps2", (it or {}).get("ak_mps2", float("nan"))))
                if not math.isfinite(iaw) or iaw < 0:
                    return CalcResult(
                        nivel="no_aplicable",
                        detalle={"motivo": "La aceleración escalar de cada tramo debe ser finita y no negativa."},
                    )
                usando_legacy = True
                sum_e_legacy += (iaw ** 2) * ti

        tiempo_total = sum_t
        if not (math.isfinite(tiempo_total) and tiempo_total > 0):
            return CalcResult(nivel="no_aplicable", detalle={"motivo": "Tiempo total inválido o 0.", "tiempo_total_h": tiempo_total})

        # Si hay mezcla (por edición manual), hacemos fallback conservador:
        # agregamos la energía escalar a todos los ejes para no subestimar.
        if usando_ejes:
            if usando_legacy and sum_e_legacy > 0:
                sum_e_x += sum_e_legacy
                sum_e_y += sum_e_legacy
                sum_e_z += sum_e_legacy

            a_eq_x = math.sqrt(sum_e_x / tiempo_total)
            a_eq_y = math.sqrt(sum_e_y / tiempo_total)
            a_eq_z = math.sqrt(sum_e_z / tiempo_total)

            vals = {"X": a_eq_x, "Y": a_eq_y, "Z": a_eq_z}
            eje_dominante = max(vals, key=vals.get)
            val_final = vals[eje_dominante]
            detalle_calculo = {
                "metodo": "Promedio energético (ISO 5349)",
                "A_eq_X": a_eq_x, "A_eq_Y": a_eq_y, "A_eq_Z": a_eq_z,
                "nota": "Si hubo tramos legacy mezclados, se sumaron de forma conservadora a todos los ejes."
            }
        else:
            if not usando_legacy:
                return CalcResult(nivel="no_aplicable", detalle={"motivo": "Ítems inválidos: sin ejes ni a_wi."})
            val_final = math.sqrt(sum_e_legacy / tiempo_total)
            eje_dominante = "Legacy (agrupado)"
            detalle_calculo = {"metodo": "Promedio energético escalar"}

    # -------------------------
    # Evaluación final vs tabla
    # -------------------------
    try:
        legal_limit, action_limit, fila_data = _lookup_limit_by_time(tiempo_total, data["tabla_limites"])
    except Exception as e:
        return CalcResult(nivel="no_aplicable", detalle={"motivo": f"Error leyendo tabla_limites: {e}"})

    nivel = _risk_from_value(val_final, action_limit, legal_limit)

    # A(8) informativo
    a_8_normalizado = val_final * math.sqrt(tiempo_total / 8.0)

    # ✅ claves alineadas al modelo (por si apply_result auto-mapea campos)
    detalle_final = {
        "eje_dominante_final": eje_dominante,
        "valor_final_mps2": val_final,

        "tiempo_total_h": tiempo_total,
        "valor_exposicion_mps2": val_final,
        "A_8_normalizado": a_8_normalizado,

        "limites_aplicados": {
            "limite_legal_mps2": legal_limit,
            "nivel_accion_mps2": action_limit,
            "rango_tabla": f"{fila_data.get('min_h')}h - {fila_data.get('max_h')}h"
        },
        "calculo_interno": detalle_calculo,
        "fuente": "vibracion_mano_brazo_limites.json",
    }

    # Si tu apply_result NO mapea campos automáticamente, esto igual deja trazabilidad:
    try:
        if hasattr(instance, "eje_dominante_final"):
            instance.eje_dominante_final = eje_dominante
        if hasattr(instance, "valor_final_mps2"):
            instance.valor_final_mps2 = val_final
    except Exception:
        pass

    return CalcResult(nivel=nivel, detalle=detalle_final)


# ============================================================================ #
#                            VIBRACIÓN CUERPO ENTERO (VCE)
# ============================================================================ #

@register(FactorSlug.VIBRACION_CE)
def calc_vibracion_cuerpo_entero(instance) -> CalcResult:
    """
    Soporta 2 modos (compatibles con tu estructura actual):

    1) NUEVO (prioritario): si existen tramos (instance.segmentos.*),
       calcula A(8) por integración energética en tramos y define el valor final
       como el MAX de los tres ejes ponderados (X,Y*1.4; Z*1.0).

    2) LEGACY: si no hay tramos, mantiene compatibilidad con calc_data["input"]
       (metodo2 / metodo1) y con campos legacy del modelo (a_wx/a_wy/a_wz, duracion_h, etc).
    """
    cfg = load_json("vibracion_cuerpo_entero_limites.json")

    accion_A8 = to_float(cfg.get("accion_A8", 0.5))
    limite_A8 = to_float(cfg.get("limite_A8", 1.15))
    crest_thr = to_float(cfg.get("crest_factor_threshold", 6.0))

    def _safe_num(x, default=0.0):
        """Evita NaN/inf en JSONB."""
        x = to_float(x)
        return x if (isinstance(x, (int, float)) and math.isfinite(x)) else default

    def _axis_label(axis_code: str) -> str:
        return {"X": "X (Antero-Posterior)", "Y": "Y (Lateral)", "Z": "Z (Vertical)"}.get(axis_code, axis_code)

    def _classify(val):
        return _risk_from_value(val, accion_A8, limite_A8)

    # ------------------------------------------------------------------
    # 1) NUEVO: cálculo por tramos (DB) si existen segmentos
    # ------------------------------------------------------------------
    # Verificamos si la instancia tiene el atributo 'segmentos' (relación reversa) y si hay datos
    if hasattr(instance, "segmentos") and instance.segmentos.exists():
        segmentos_qs = instance.segmentos.all().order_by("id")

        sum_t = 0.0
        sum_e_x = 0.0
        sum_e_y = 0.0
        sum_e_z = 0.0

        warnings = []
        crest_flag_any = False
        tramos_debug = []

        for seg in segmentos_qs:
            t = to_float(getattr(seg, "tiempo_horas", None))
            ax_raw = to_float(getattr(seg, "aw_x", None))
            ay_raw = to_float(getattr(seg, "aw_y", None))
            az_raw = to_float(getattr(seg, "aw_z", None))
            if not math.isfinite(t) or t <= 0 or any(
                not math.isfinite(value) or value < 0
                for value in (ax_raw, ay_raw, az_raw)
            ):
                return CalcResult(
                    nivel="no_aplicable",
                    detalle={
                        "motivo": "Todos los tramos VCE requieren tiempo positivo y aceleraciones no negativas.",
                        "tramo_id": getattr(seg, "pk", None),
                    },
                )

            # Factores k salud ISO 2631: X,Y * 1.4 ; Z * 1.0
            wx = ax_raw * 1.4
            wy = ay_raw * 1.4
            wz = az_raw * 1.0

            sum_t += t
            sum_e_x += (wx ** 2) * t
            sum_e_y += (wy ** 2) * t
            sum_e_z += (wz ** 2) * t

            # Crest factor (warning, no escalado automático)
            cf_x = getattr(seg, "cf_x", None)
            cf_y = getattr(seg, "cf_y", None)
            cf_z = getattr(seg, "cf_z", None)

            cfx = _safe_num(cf_x, 0.0) if cf_x is not None else None
            cfy = _safe_num(cf_y, 0.0) if cf_y is not None else None
            cfz = _safe_num(cf_z, 0.0) if cf_z is not None else None

            if (
                (cfx is not None and cfx > crest_thr)
                or (cfy is not None and cfy > crest_thr)
                or (cfz is not None and cfz > crest_thr)
            ):
                crest_flag_any = True
                vm = getattr(seg, "vehiculo_maquina", "Tramo")
                warnings.append(
                    f"Tramo '{vm}': Factor de cresta > {crest_thr}. El RMS puede subestimar; considerar método alternativo."
                )

            # Resonancias (warning)
            hz = getattr(seg, "pico_espectral_hz", None)
            if hz is not None:
                try:
                    hz_val = int(hz)
                except Exception:
                    hz_val = None

                if hz_val is not None:
                    vm = getattr(seg, "vehiculo_maquina", "Tramo")
                    if 4 <= hz_val <= 8:
                        warnings.append(
                            f"Tramo '{vm}': Pico en {hz_val}Hz coincide con resonancia vertical (4-8Hz)."
                        )
                    if 1 <= hz_val <= 2:
                        warnings.append(
                            f"Tramo '{vm}': Pico en {hz_val}Hz coincide con resonancia horizontal (1-2Hz)."
                        )

            # Debug (útil para auditoría)
            tramos_debug.append(
                {
                    "vehiculo_maquina": getattr(seg, "vehiculo_maquina", ""),
                    "tiempo_h": round(t, 3),
                    "aw_raw": {"x": round(ax_raw, 3), "y": round(ay_raw, 3), "z": round(az_raw, 3)},
                    "aw_ponderado_k": {"x": round(wx, 3), "y": round(wy, 3), "z": round(wz, 3)},
                    "pico_espectral_hz": getattr(seg, "pico_espectral_hz", None),
                    "cf": {
                        "x": float(cfx) if cfx is not None else None,
                        "y": float(cfy) if cfy is not None else None,
                        "z": float(cfz) if cfz is not None else None,
                    },
                }
            )

        if sum_t <= 0:
            return CalcResult(
                nivel="no_aplicable",
                detalle={"motivo": "No hay tramos válidos (tiempo_horas <= 0)."},
            )

        # A(8) por eje (integración energética): A8 = sqrt( Sum(aw^2 * t) / 8 )
        # Fórmula: A(8) = sqrt( (1/T0) * sum( (k*aw)^2 * t ) ) donde T0=8h
        # Nota: sum_e_x ya tiene (k*aw)^2 * t.
        a8_x = math.sqrt(max(sum_e_x, 0.0) / 8.0)
        a8_y = math.sqrt(max(sum_e_y, 0.0) / 8.0)
        a8_z = math.sqrt(max(sum_e_z, 0.0) / 8.0)

        # Global según tu modelo: MAX de ejes
        vals = {"X": a8_x, "Y": a8_y, "Z": a8_z}
        eje_dom = max(vals, key=vals.get)
        valor_final = vals[eje_dom]

        nivel = _classify(valor_final)

        calc_details = {
            "metodo": "tramos (integración energética ISO 2631)",
            "tiempo_total_h": round(sum_t, 3),
            "A8_x": round(a8_x, 3),
            "A8_y": round(a8_y, 3),
            "A8_z": round(a8_z, 3),
            "eje_dominante": _axis_label(eje_dom),
            "valor_final_a8": round(valor_final, 3),
            "umbrales": {"accion_A8": accion_A8, "limite_A8": limite_A8},
            "crest_factor_mayor_6": bool(crest_flag_any or getattr(instance, "factor_cresta_gt6", False)),
            "warnings": warnings,
            "tramos": tramos_debug,
            "fuente": "vibracion_cuerpo_entero_limites.json",
        }

        # ✅ CLAVES ALINEADAS AL MODELO:
        # Tu función apply_result actualizará instance.valor_final_a8, instance.eje_dominante, etc.
        detalle = {
            "valor_final_a8": round(valor_final, 3),
            "eje_dominante": eje_dom,  # Guardamos código corto ("X", "Y", "Z") o largo según tu modelo prefiera
            "calc_details": calc_details,
            # También devolvemos calc_data actualizado por si apply_result lo usa
            "calc_data": calc_details 
        }
        return CalcResult(nivel=nivel, detalle=detalle)

    # ------------------------------------------------------------------
    # 2) LEGACY: compatibilidad con inputs anteriores (sin tramos)
    # ------------------------------------------------------------------
    inp = (getattr(instance, "calc_data", {}) or {}).get("input", {})

    # Duración: primero input_json, luego campo legacy del modelo (duracion_h), default 8
    T = to_float(inp.get("duracion_h", getattr(instance, "duracion_h", None)))
    if not math.isfinite(T) or T <= 0:
        return CalcResult(
            nivel="no_aplicable",
            detalle={"motivo": "La duración VCE debe ser finita y mayor a 0."},
        )

    tipo_raw = inp.get("tipo_datos", None) or getattr(instance, "metodo", "") or "metodo2"
    tipo = str(tipo_raw).lower()
    # Map de tus choices legacy a los nombres históricos
    if tipo == "ponderadas":
        tipo = "metodo2"
    elif tipo == "espectral":
        tipo = "metodo1"

    # Crest factor legacy (warning, no escalado automático)
    crest_flag = bool(inp.get("crest_factor_mayor_6", False) or getattr(instance, "factor_cresta_gt6", False))
    legacy_warnings = []
    if crest_flag:
        legacy_warnings.append(
            f"Factor de cresta informado > {crest_thr}. El RMS puede subestimar; considerar método alternativo."
        )

    if tipo == "metodo2":
        Ax = to_float(inp.get("A_wx", getattr(instance, "a_wx", None)))
        Ay = to_float(inp.get("A_wy", getattr(instance, "a_wy", None)))
        Az = to_float(inp.get("A_wz", getattr(instance, "a_wz", None)))
        if any(not math.isfinite(value) or value < 0 for value in (Ax, Ay, Az)):
            return CalcResult(
                nivel="no_aplicable",
                detalle={"motivo": "Los tres ejes VCE deben ser finitos y no negativos."},
            )

        # A(8) por eje (MAX manda)
        a8_x = abs(1.4 * Ax) * math.sqrt(T / 8.0)
        a8_y = abs(1.4 * Ay) * math.sqrt(T / 8.0)
        a8_z = abs(1.0 * Az) * math.sqrt(T / 8.0)

        vals = {"X": a8_x, "Y": a8_y, "Z": a8_z}
        eje_dom = max(vals, key=vals.get)
        valor_final = vals[eje_dom]

        nivel = _classify(valor_final)

        calc_details = {
            "metodo": "2 (ponderado por eje) - legacy",
            "duracion_h": T,
            "Ax_raw": Ax,
            "Ay_raw": Ay,
            "Az_raw": Az,
            "A8_x": round(a8_x, 3),
            "A8_y": round(a8_y, 3),
            "A8_z": round(a8_z, 3),
            "eje_dominante": _axis_label(eje_dom),
            "valor_final_a8": round(valor_final, 3),
            "umbrales": {"accion_A8": accion_A8, "limite_A8": limite_A8},
            "crest_factor_mayor_6": crest_flag,
            "warnings": legacy_warnings,
            "fuente": "vibracion_cuerpo_entero_limites.json",
        }

        detalle = {
            "valor_final_a8": round(valor_final, 3),
            "eje_dominante": eje_dom,
            "calc_details": calc_details,
        }
        return CalcResult(nivel=nivel, detalle=detalle)

    # ---- método1 (screening con picos) ----
    spectrum = getattr(instance, "espectro_json", None) or {}
    # Compatibilidad para registros históricos: el campo modelado prevalece y
    # calc_data.input se conserva únicamente como fallback de lectura.
    spectral_input = {**inp, **spectrum}
    fx = to_float(spectral_input.get("pico_x_hz"))
    ax = to_float(spectral_input.get("pico_x_mps2"))
    fy = to_float(spectral_input.get("pico_y_hz"))
    ay = to_float(spectral_input.get("pico_y_mps2"))
    fz = to_float(spectral_input.get("pico_z_hz"))
    az = to_float(spectral_input.get("pico_z_mps2"))
    if any(
        not math.isfinite(value) or value < 0
        for value in (fx, ax, fy, ay, fz, az)
    ):
        return CalcResult(
            nivel="no_aplicable",
            detalle={"motivo": "El método espectral requiere picos y frecuencias no negativos en los tres ejes."},
        )

    # Treat pico≈RMS ponderado (aprox). Normalizo a A(8) por eje.
    a8_x = abs(1.4 * ax) * math.sqrt(T / 8.0)
    a8_y = abs(1.4 * ay) * math.sqrt(T / 8.0)
    a8_z = abs(1.0 * az) * math.sqrt(T / 8.0)

    vals = {"X": a8_x, "Y": a8_y, "Z": a8_z}
    eje_dom = max(vals, key=vals.get)
    valor_final = vals[eje_dom]

    nivel = _classify(valor_final)

    calc_details = {
        "metodo": "1 (espectral, screening aprox.) - legacy",
        "picos": {
            "x": {"hz": fx, "mps2": ax},
            "y": {"hz": fy, "mps2": ay},
            "z": {"hz": fz, "mps2": az},
        },
        "duracion_h": T,
        "A8_x": round(a8_x, 3),
        "A8_y": round(a8_y, 3),
        "A8_z": round(a8_z, 3),
        "eje_dominante": _axis_label(eje_dom),
        "valor_final_a8": round(valor_final, 3),
        "umbrales": {"accion_A8": accion_A8, "limite_A8": limite_A8},
        "crest_factor_mayor_6": crest_flag,
        "warnings": legacy_warnings + [
            "Sin curvas espectrales numéricas: se usa aproximación prudente (pico≈RMS ponderado). Preferir tramos o método 2."
        ],
        "fuente": "vibracion_cuerpo_entero_limites.json",
    }

    detalle = {
        "valor_final_a8": round(valor_final, 3),
        "eje_dominante": eje_dom,
        "calc_details": calc_details,
    }
    return CalcResult(nivel=nivel, detalle=detalle)



@register(FactorSlug.CONFORT_TERMICO)
def calc_confort_termico(instance) -> CalcResult:
    """
    Clasifica un punto (To °C, HR %) contra curvas aproximadas de Fanger
    definidas como polilíneas en JSON. Devuelve nivel: bajo/medio/alto + trazabilidad.
    Zonas: demasiado_frio, frio, confort, caliente, demasiado_caliente.
    """
    # --- INICIO CORRECCIÓN 3 (Confort Térmico) ---
    cfg = load_json("confort_termico_umbrales.json")  # ← nombre correcto
    # --- FIN CORRECCIÓN 3 ---
    inp = (getattr(instance, "calc_data", {}) or {}).get("input", {})

    # -------- inputs (desde modelo o payload del form) --------
    # --- INICIO CORRECCIÓN 3 (Confort Térmico) ---
    To = to_float(
        getattr(instance, "temperatura_operativa_c", inp.get("temp_operativa_c"))
    )
    HR = to_float(
        getattr(instance, "humedad_relativa_pct", inp.get("hr_pct"))
    )
    # --- FIN CORRECCIÓN 3 ---

    if (
        not math.isfinite(To)
        or not math.isfinite(HR)
        or not 15 <= To <= 40
        or not 0 <= HR <= 90
    ):
        return CalcResult(
            nivel="no_aplicable",
            detalle={
                "motivo": "Confort térmico requiere temperatura de 15–40 °C y humedad de 0–90 %.",
                "campos_invalidos": [
                    name
                    for name, valid in (
                        ("temperatura_operativa_c", math.isfinite(To) and 15 <= To <= 40),
                        ("humedad_relativa_pct", math.isfinite(HR) and 0 <= HR <= 90),
                    )
                    if not valid
                ],
            },
        )

    # -------- helpers internos --------

    def _y_at_x(poly_pts, x):
        """
        Interpola linealmente el valor Y (HR%) de una polilínea 'poly_pts' dada To=x.
        Si x cae fuera, usa el extremo más cercano.
        poly_pts: [[x0,y0],[x1,y1],...], se ordena por x para seguridad.
        """
        pts = sorted(poly_pts, key=lambda p: p[0])
        if x <= pts[0][0]:
            return pts[0][1]
        if x >= pts[-1][0]:
            return pts[-1][1]
        for i in range(len(pts) - 1):
            x0, y0 = pts[i]
            x1, y1 = pts[i + 1]
            if x0 <= x <= x1 or x1 <= x <= x0:
                if x1 == x0:
                    return (y0 + y1) / 2
                r = (x - x0) / (x1 - x0)
                return y0 + r * (y1 - y0)
        return pts[-1][1]

    # -------- normalización de entrada al dominio de la figura --------
    To_c = _clamp(To, cfg.get("x_min", 15.0), cfg.get("x_max", 40.0))
    HR_c = _clamp(HR, cfg.get("y_min", 0.0), cfg.get("y_max", 90.0))

    b = cfg["boundaries"]
    y_df_frio = _y_at_x(b["df_frio"], To_c)
    y_frio_confort = _y_at_x(b["frio_confort"], To_c)
    y_confort_calor = _y_at_x(b["confort_caliente"], To_c)
    y_calor_demasiado = _y_at_x(b["caliente_demasiado"], To_c)

    # -------- clasificación por bandas --------
    if HR_c <= y_df_frio:
        zona = "demasiado_frio"
    elif HR_c <= y_frio_confort:
        zona = "frio"
    elif HR_c <= y_confort_calor:
        zona = "confort"
    elif HR_c <= y_calor_demasiado:
        zona = "caliente"
    else:
        zona = "demasiado_caliente"

    # Mapeo zona → NivelRiesgo (editable en JSON)
    nivel = cfg.get("mapping", {}).get(zona, "medio")

    # Recomendaciones simples (puedes afinarlas o moverlas a JSON)
    recs = {
        "demasiado_frio": [
            "Incrementar To (calefacción) o reducir corrientes de aire.",
            "Aislar fuentes de frío y considerar ropa/EPP térmico.",
        ],
        "frio": ["Ajustar To o reducir ventilación; evaluar pausas activas y EPP."],
        "confort": ["Mantener condiciones; monitoreo periódico."],
        "caliente": [
            "Reducir To/HR (ventilación, deshumidificación), dar pausas y agua."
        ],
        "demasiado_caliente": [
            "Acción inmediata: enfriamiento/ventilación mecánica, limitar exposición."
        ],
    }

    detalle = {
        "input": {"temp_c": To, "hr_pct": HR},
        "clamped": {"temp_c": To_c, "hr_pct": HR_c},
        "umbrales_y_a_x": {
            "df_frio": y_df_frio,
            "frio_confort": y_frio_confort,
            "confort_caliente": y_confort_calor,
            "caliente_demasiado": y_calor_demasiado,
        },
        "zona": zona,
        "recomendaciones": recs.get(zona, []),
        # --- INICIO CORRECCIÓN 3 (Confort Térmico) ---
        "fuente": "confort_termico_umbrales.json",
        # --- FIN CORRECCIÓN 3 ---
        "nota": "Aproximación a curvas de Fanger (Fig. 4.6). Si necesitas PMV/PPD completo, lo añadimos como método alternativo.",
    }

    return CalcResult(nivel=nivel, detalle=detalle)


# ============================================================================ #
#                                ESTRÉS DE CONTACTO
# ============================================================================ #


def _level_bump(level: str, steps: int = 1) -> str:
    order = ["bajo", "medio", "alto"]
    try:
        i = order.index(level)
    except ValueError:
        i = 1
    return order[min(len(order) - 1, i + steps)]


def _level_drop(level: str, steps: int = 1) -> str:
    order = ["bajo", "medio", "alto"]
    try:
        i = order.index(level)
    except ValueError:
        i = 1
    return order[max(0, i - steps)]


def _band_from_value(v, brks):
    """
    brks = {"low_max": 30, "mid_max": 60} -> devuelve "bajo","medio" u "alto"
    """
    v = to_float(v)
    if v < 0:
        return "bajo"
    if v < to_float(brks.get("low_max", 30)):
        return "bajo"
    if v <= to_float(brks.get("mid_max", 60)):
        return "medio"
    return "alto"


def _bucket_0_1_2p(n: int) -> str:
    if n <= 0:
        return "0"
    if n == 1:
        return "1"
    return "2p"







@register(FactorSlug.ESTRES_CONTACTO)
def calc_estres_contacto(instance) -> CalcResult:
    """
    Clasificación del riesgo por Estrés de Contacto:
    - Overrides inmediatos por flags críticos (Sección 4).
    - Matriz base por % de tiempo en contacto (frecuencia_pct) vs. nº de agravantes.
    - Escalados por presión (kPa) y síntomas; mitigación opcional por controles.
    """
    cfg = load_json("estres_contacto_criterios.json")
    inp = (getattr(instance, "calc_data", {}) or {}).get("input", {})

    # --- 1. Inputs básicos ---
    borde_tipo = str(inp.get("borde_tipo", "")).lower()  # "afilado"/"duro"/"acolchado"
    dur_cont_min = to_float(
        inp.get("duracion_continua_min", getattr(instance, "duracion_continua_min", 0))
    )
    freq_pct = to_float(inp.get("frecuencia_pct", getattr(instance, "frecuencia_pct", 0)))
    
    fuerza_n = inp.get("fuerza_n", getattr(instance, "fuerza_n", None))
    area_cm2 = inp.get("area_cm2", getattr(instance, "area_cm2", None))
    borg = inp.get("borg", getattr(instance, "borg", None))

    invalid = []
    if borde_tipo not in {"afilado", "duro", "acolchado"}:
        invalid.append("tipo_borde")
    if not math.isfinite(dur_cont_min) or dur_cont_min <= 0:
        invalid.append("duracion_continua_min")
    if not math.isfinite(freq_pct) or not 0 <= freq_pct <= 100:
        invalid.append("frecuencia_exposicion")
    if (fuerza_n is None) != (area_cm2 is None):
        invalid.extend(["fuerza_n", "area_cm2"])
    elif fuerza_n is not None:
        force_value = to_float(fuerza_n)
        area_value = to_float(area_cm2)
        if not math.isfinite(force_value) or force_value < 0:
            invalid.append("fuerza_n")
        if not math.isfinite(area_value) or area_value <= 0:
            invalid.append("area_cm2")
    if borg is not None:
        borg_value = to_float(borg)
        if not math.isfinite(borg_value) or not 0 <= borg_value <= 10:
            invalid.append("borg")
    if invalid:
        return CalcResult(
            nivel="no_aplicable",
            detalle={
                "motivo": "Faltan datos válidos para calcular Estrés de Contacto.",
                "campos_invalidos": sorted(set(invalid)),
            },
        )

    # --- 2. Flags críticos (Sección 4) ---
    mano_martillo = bool(inp.get("mano_martillo", False))
    mango_inadecuado = bool(inp.get("mango_inadecuado", False))
    postura_forzada = bool(inp.get("postura_forzada", False))

    # --- 3. Corrección de lectura de SINTOMAS (Lista a Booleanos) ---
    sintomas_raw = inp.get("sintomas") or []
    # Normalizamos a lista de strings para verificación
    if isinstance(sintomas_raw, dict):
        sintomas_lista = [k for k, v in sintomas_raw.items() if v]
    elif isinstance(sintomas_raw, (list, tuple)):
        sintomas_lista = list(sintomas_raw)
    else:
        sintomas_lista = []

    sintomas = {
        "hormigueo": "hormigueo" in sintomas_lista,
        "adormecimiento": "adormecimiento" in sintomas_lista,
        "dolor": "dolor" in sintomas_lista,
        "marcas": "marcas" in sintomas_lista,
    }

    # --- 4. Corrección de lectura de CONTROLES (Lista a Booleanos) ---
    controles_raw = inp.get("controles") or []
    if isinstance(controles_raw, dict):
        controles_lista = [k for k, v in controles_raw.items() if v]
    elif isinstance(controles_raw, (list, tuple)):
        controles_lista = list(controles_raw)
    else:
        controles_lista = []

    controles = {
        "bordes_redondeados": "bordes_redondeados" in controles_lista,
        "herramientas_ergonomicas": "herramientas_ergonomicas" in controles_lista,
        "apoyos_muneca": "apoyos_muneca" in controles_lista,
        "rotacion_micropausas": "rotacion_micropausas" in controles_lista,
        "guantes_acolchados": "guantes_acolchados" in controles_lista,
    }

    # --- 5. Override inmediato por flags críticos ---
    immediate_flags = cfg.get(
        "immediate_high_flags",
        ["mano_martillo", "mango_inadecuado", "postura_forzada"],
    )
    
    overrides_activados = {
        "mano_martillo": mano_martillo,
        "mango_inadecuado": mango_inadecuado,
        "postura_forzada": postura_forzada,
    }

    if any(overrides_activados.get(k, False) for k in immediate_flags):
        detalle = {
            "motivo_override": "Flag crítico de Sección 4 activo",
            "flags": {k: bool(overrides_activados.get(k, False)) for k in immediate_flags},
            "input": {
                "borde_tipo": borde_tipo,
                "dur_cont_min": dur_cont_min,
                "frecuencia_pct": freq_pct,
            },
        }
        return CalcResult(nivel="alto", detalle=detalle)

    # --- 6. Cálculo de Presión e Intensidad ---
    # kPa = (N/cm^2) * 10
    pres_kpa = None
    if fuerza_n is not None and area_cm2 not in (None, 0, "0", 0.0):
        pres_kpa = to_float(fuerza_n) / to_float(area_cm2) * 10.0

    # Banda de presión
    pthr = cfg.get("pressure_kpa_thresholds", {"low_max": 100.0, "mid_max": 150.0})
    pres_band = None
    
    if pres_kpa is not None:
        if pres_kpa <= to_float(pthr.get("low_max", 100.0)):
            pres_band = "baja"
        elif pres_kpa <= to_float(pthr.get("mid_max", 150.0)):
            pres_band = "media"
        else:
            pres_band = "alta"

    # Intensidad subjetiva (si no hay presión válida, usa Borg o estima)
    borg_val = None
    if borg is not None:
        borg_val = _clamp(to_float(borg), 0.0, 10.0)
    else:
        # Estimación grosera desde presión si no hay Borg
        if pres_kpa is not None:
            if pres_kpa <= to_float(pthr.get("low_max", 100.0)):
                borg_val = 3.0
            elif pres_kpa <= to_float(pthr.get("mid_max", 150.0)):
                borg_val = 6.0
            else:
                borg_val = 8.0

    # --- 7. Matriz base (Frecuencia vs Agravantes) ---
    # Agravantes: borde afilado (+1), presión alta (+1), frecuencia alta (+1), postura forzada (+1)
    agravantes = 0
    if borde_tipo == "afilado":
        agravantes += 1
    if pres_band == "alta":
        agravantes += 1
    
    # Banda de frecuencia
    fbrks = cfg.get("frecuencia_pct_bands", {"low_max": 30, "mid_max": 60})
    freq_band = _band_from_value(freq_pct, fbrks)
    
    if freq_band == "alto":
        agravantes += 1
        
    # CORRECCIÓN AGREGADA: Sumar postura forzada al conteo
    if postura_forzada:
        agravantes += 1

    agrav_bucket = _bucket_0_1_2p(agravantes)

    # Lookup en Matriz
    matrix = cfg.get(
        "matrix",
        {
            "bajo": {"0": "bajo", "1": "bajo", "2p": "medio"},
            "medio": {"0": "bajo", "1": "medio", "2p": "alto"},
            "alto": {"0": "medio", "1": "alto", "2p": "alto"},
        },
    )
    base_nivel = matrix.get(freq_band, matrix["medio"]).get(agrav_bucket, "medio")

    # --- 8. Escalados por Presión y Síntomas ---
    nivel = base_nivel

    # Presión: media/alta puede escalar
    pres_rules = cfg.get("pressure_escalation", {"medium_add": 0, "high_add": 1})
    if pres_band == "media":
        add = int(pres_rules.get("medium_add", 0))
        if add:
            nivel = _level_bump(nivel, add)
    elif pres_band == "alta":
        add = int(pres_rules.get("high_add", 1))
        if add:
            nivel = _level_bump(nivel, add)

    # Síntomas: al menos "medio"; severos -> "alto"
    sym_rules = cfg.get(
        "symptom_escalation",
        {
            "any_to_at_least": "medio",
            "severe_keys": ["adormecimiento", "marcas"],
            "severe_to": "alto",
        },
    )
    
    any_sym = any(sintomas.values())
    severe_hit = any(sintomas.get(k, False) for k in sym_rules.get("severe_keys", []))

    if any_sym:
        min_lvl = sym_rules.get("any_to_at_least", "medio")
        order = {"bajo": 0, "medio": 1, "alto": 2}
        if order.get(nivel, 1) < order.get(min_lvl, 1):
            nivel = min_lvl

    if severe_hit and nivel != sym_rules.get("severe_to", "alto"):
        nivel = sym_rules.get("severe_to", "alto")

    # --- 9. Mitigación por Controles ---
    ctrl_rules = cfg.get(
        "controls_mitigation", {"min_count": 3, "minus": 1, "block_if_high": True}
    )
    ctrl_count = sum(1 for v in controles.values() if v)

    if ctrl_count >= int(ctrl_rules.get("min_count", 3)):
        if not (ctrl_rules.get("block_if_high", True) and nivel == "alto"):
            minus = int(ctrl_rules.get("minus", 1))
            if minus > 0:
                nivel = _level_drop(nivel, minus)

    # --- 10. Índice auxiliar (documental) ---
    dbrks = cfg.get("duracion_continua_min_bands", {"low_max": 5, "mid_max": 15})
    dur_band = _band_from_value(dur_cont_min, dbrks)
    
    dur_pct_est = (
        cfg.get("duracion_pct_estimate", {"bajo": 20, "medio": 45, "alto": 80}).get(
            dur_band, 45
        )
    )

    if borg_val is None:
        borg_val = 3.0
    
    stress_index = (dur_pct_est * max(0.0, min(100.0, freq_pct)) * borg_val) / 100.0

    detalle = {
        "input": {
            "borde_tipo": borde_tipo,
            "duracion_continua_min": dur_cont_min,
            "frecuencia_pct": freq_pct,
            "fuerza_n": fuerza_n,
            "area_cm2": area_cm2,
            "borg": borg,
        },
        "presion_kpa": pres_kpa,
        "presion_band": pres_band,
        "freq_band": freq_band,
        "dur_band": dur_band,
        "agravantes_contados": agravantes,
        "agravantes_bucket": agrav_bucket,
        "base_por_matriz": base_nivel,
        "sintomas": sintomas,
        "controles": controles,
        "indice_auxiliar": {
            "duracion_pct_estimado": dur_pct_est,
            "borg_usado": borg_val,
            "stress_index": stress_index,
            "formula": "(dur%_estimado * freq% * Borg) / 100",
        },
        "reglas_usadas": {
            "immediate_high_flags": immediate_flags,
            "pressure_thresholds_kpa": pthr,
            "matrix": matrix,
            "pressure_escalation": pres_rules,
            "symptom_escalation": sym_rules,
            "controls_mitigation": ctrl_rules,
        },
        "fuente": "estres_contacto_criterios.json",
        "nota": (
            "La presión alta (>150 kPa) agrega un agravante y eleva un nivel "
            "según pressure_escalation; los agravantes inmediatos se aplican "
            "conforme a la matriz parametrizada."
        ),
    }

    return CalcResult(nivel=nivel, detalle=detalle)



# --------------------------------------------------------------------------------------
# Utilidad opcional: ejecutar una calculadora a partir de la instancia del modelo
# --------------------------------------------------------------------------------------


def run_for_instance(instance: Any) -> CalcResult:
    """
    Ejecuta la calculadora según instance.factor_slug.
    Útil desde views/signals. No persiste nada: sólo retorna el CalcResult.
    """
    slug = getattr(instance, "factor_slug", "") or getattr(
        instance, "FACTOR_SLUG", ""
    )
    if not getattr(instance, "aplicable", True):
        return _with_calculation_trace(
            str(slug),
            CalcResult(
                nivel="no_aplicable",
                detalle={
                    "motivo": "La evaluación fue marcada como no aplicable.",
                    "estado_resultado": "calculado",
                },
            ),
        )

    fn = REGISTRY.get(str(slug))
    if not fn:
        return _with_calculation_trace(
            str(slug),
            CalcResult(
                nivel="no_aplicable",
                detalle={"motivo": f"No hay calculadora para '{slug}'"},
            ),
        )
    return _with_calculation_trace(str(slug), fn(instance))


def apply_result(instance: Any, result: CalcResult) -> None:
    """
    Persiste el resultado en la instancia de modelo del factor.
    MEJORA: Detecta si el 'detalle' trae claves que coinciden con campos reales 
    del modelo (como puntaje_a, puntaje_final) y los actualiza.
    """
    slug = getattr(instance, "factor_slug", "") or getattr(
        instance, "FACTOR_SLUG", ""
    )
    result = _with_calculation_trace(str(slug), result)
    instance.nivel_riesgo = result.nivel
    
    # 1. Reemplazo atómico de la trazabilidad para no conservar claves obsoletas.
    old = dict(getattr(instance, "calc_data", {}) or {})
    nuevos_detalles = asdict(result).get("detalle", {})
    previous_input = dict(old.get("input", {}) or {})
    new_input = nuevos_detalles.get("input")
    if isinstance(new_input, dict):
        previous_input.update(new_input)
    fresh_calc_data = {
        key: value
        for key, value in nuevos_detalles.items()
        if key != "calc_data"
    }
    if previous_input:
        fresh_calc_data["input"] = previous_input
    fresh_calc_data["estado_resultado"] = "calculado"
    fresh_calc_data["calculado_en"] = timezone.now().isoformat()
    instance.calc_data = fresh_calc_data

    # 2. Actualización inteligente de campos del modelo (DB)
    # Si la calculadora devuelve 'puntaje_final', lo guardamos en la columna SQL.
    update_fields = ["nivel_riesgo", "calc_data", "actualizado_en"]
    
    for key, value in nuevos_detalles.items():
        if key == "calc_data":
            continue
        # Verificamos si el modelo tiene ese campo y no es una relación compleja
        if hasattr(instance, key):
            # Solo actualizamos si es un valor simple (int/float/str), no diccionarios anidados
            # a menos que el campo del modelo espere JSON, pero aquí buscamos puntaje_a (int)
            setattr(instance, key, value)
            if key not in update_fields:
                update_fields.append(key)

    instance.save(update_fields=update_fields)
