# evaluaciones/choices.py
"""
Enums/choices compartidos para toda la app `evaluaciones/`.

Objetivos:
- Evitar "magic strings" en modelos y formularios.
- Centralizar etiquetas legibles para Admin/UIs.
- Mantener un set canónico de valores para que las calculadoras
  puedan mapear a tablas JSON (evaluaciones/data/*.json).

Tip: usá estos enums en tus ModelFields (choices=...) y en tus
ModelForms para que los <select> salgan listos.
"""

from django.db.models import TextChoices, IntegerChoices
from .catalog import FACTOR_DEFINITIONS


# --- Slugs canónicos por factor (útiles para routing y motor) ---
FactorSlug = TextChoices(
    "FactorSlug",
    {
        definition.enum_name: (definition.slug, definition.choice_label)
        for definition in FACTOR_DEFINITIONS
    },
)


# --- Estados de la evaluación y nivel de riesgo global ---
class EstadoEval(TextChoices):
    PENDING = "pending", "Pendiente"
    IN_PROGRESS = "in_progress", "En curso"
    DONE = "done", "Completada"


class NivelRiesgo(TextChoices):
    NA = "no_aplicable", "No aplicable"
    BAJO = "bajo", "Bajo"
    MEDIO = "medio", "Medio"
    ALTO = "alto", "Alto"


# --- LMC: Zonas de altura (V) y alejamiento horizontal (H) ---
class VAltura(TextChoices):
    SUELO_ESPINILLA = "suelo_espinilla", "Suelo a mitad espinilla"
    ESPINILLA_NUDILLOS = "espinilla_nudillos", "Mitad espinilla a nudillos"
    NUDILLOS_HOMBRO = "nudillos_hombro", "Nudillos a codo/hombro"
    SOBRE_HOMBRO = "sobre_hombro", "Por encima del hombro"


class HDist(TextChoices):
    PROXIMO = "proximo", "Próximo (<30 cm)"
    INTERMEDIO = "intermedio", "Intermedio (30–60 cm)"
    ALEJADO = "alejado", "Alejado (60–80 cm)"


# --- Empuje/Tracción: población, altura de agarre y distancias típicas ---
class Poblacion(TextChoices):
    MASCULINA = "m", "Exclusivamente Masculina"
    FEMENINA_MIXTA = "f", "Femenina o Mixta"


class AlturaAgarreCM(IntegerChoices):
    # El valor (int) se mantiene para compatibilidad, la etiqueta mejora la UX
    CM_64 = 64, "Baja (aprox. 64 cm - Nudillos/Muslos)"
    CM_95 = 95, "Media (aprox. 95 cm - Cintura/Codo)"
    CM_144 = 144, "Alta (aprox. 144 cm - Hombros/Pecho)"


class DistanciaLinealM(IntegerChoices):
    # El usuario ve un rango, el sistema guarda el límite superior (ej: 8)
    M_2 = 2, "Hasta 2 metros"
    M_8 = 8, "Más de 2 m hasta 8 m"
    M_15 = 15, "Más de 8 m hasta 15 m"
    M_30 = 30, "Más de 15 m hasta 30 m"
    M_45 = 45, "Más de 30 m hasta 45 m"
    M_60 = 60, "Más de 45 m hasta 60 m"


class FrecuenciaMovimiento(TextChoices):
    # Slugs legibles + etiqueta con Hz entre paréntesis (idénticas a los formularios)
    X10_POR_MIN = "10_min", "10 por minuto (0,1667 Hz)"
    X5_POR_MIN = "5_min", "5 por minuto (0,0833 Hz)"
    X4_POR_MIN = "4_min", "4 por minuto (0,0667 Hz)"
    X2_5_POR_MIN = "2_5_min", "2,5 por minuto (0,042 Hz)"
    X1_POR_MIN = "1_min", "1 por minuto (0,0167 Hz)"
    CADA_2_MIN = "1_cada_2_min", "1 cada 2 minutos (0,0083 Hz)"
    CADA_5_MIN = "1_cada_5_min", "1 cada 5 minutos (0,0033 Hz)"
    CADA_8_HS = "1_cada_8_h", "1 cada 8 horas (3,5×10⁻⁵ Hz)"


# Mapeo numérico auxiliar para calculadoras (cuando haga falta convertir a Hz)
FRECUENCIA_HZ = {
    FrecuenciaMovimiento.X10_POR_MIN: 0.1667,
    FrecuenciaMovimiento.X5_POR_MIN: 0.0833,
    FrecuenciaMovimiento.X4_POR_MIN: 0.0667,
    FrecuenciaMovimiento.X2_5_POR_MIN: 0.0420,
    FrecuenciaMovimiento.X1_POR_MIN: 0.0167,
    FrecuenciaMovimiento.CADA_2_MIN: 0.0083,
    # ✅ CORRECCIÓN: el enum es CADA_5_MIN
    FrecuenciaMovimiento.CADA_5_MIN: 0.0033,
    FrecuenciaMovimiento.CADA_8_HS: 0.000035,
}


# ----------------------------------------------------------------------
# OPCIONES ESPECÍFICAS PARA EL MÉTODO REPETITIVOS MS (NAM)
# ----------------------------------------------------------------------

# Opciones para el Nivel de Actividad Manual (NAM)
# Guardamos el valor canónico del manual (0,2,4,6,8,10)
NAM_CHOICES = (
    (0,  "0/1 - Sin manejo manual la mayor parte del tiempo: sin esfuerzos regulares"),
    (2,  "2/3 - Pausas constantes, destacadas, largas o movimientos muy lentos"),
    (4,  "4/5 - Movimientos/esfuerzos lentos: fijos; pausas breves frecuentes"),
    (6,  "6/7 - Movimientos/esfuerzo fijo, pausas infrecuentes"),
    (8,  "8/9 - Movimientos/esfuerzos rápidos, fijos, sin pausas regulares"),
    (10, "10 - Movimiento rápido, fijo, difícil para mantener o realizar esfuerzos continuos"),
)

# Opciones para Borg Pico / FPN
# En rangos se toma el valor mayor (criterio conservador)
FPN_BORG_CHOICES = (
    (0,  "0 - Ausencia de esfuerzo"),
    (1,  "1 - Esfuerzo muy débil"),
    (2,  "2 - Esfuerzo débil / ligero"),
    (3,  "3 - Esfuerzo moderado / regular"),
    (4,  "4 - Esfuerzo algo fuerte"),
    (6,  "5 o 6 - Esfuerzo fuerte (se toma 6)"),
    (9,  "7, 8 o 9 - Esfuerzo muy fuerte (se toma 9)"),
    (10, "10 - Esfuerzo extremadamente fuerte"),
)


__all__ = [
    # factores
    "FactorSlug",
    # estados y riesgo
    "EstadoEval",
    "NivelRiesgo",
    # LMC
    "VAltura",
    "HDist",
    # Empuje/Tracción comunes
    "Poblacion",
    "AlturaAgarreCM",
    "DistanciaLinealM",
    "FrecuenciaMovimiento",
    "FRECUENCIA_HZ",
    # Repetitivos MS (NAM)
    "NAM_CHOICES",
    "FPN_BORG_CHOICES",
]
