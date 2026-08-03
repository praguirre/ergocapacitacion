# evaluaciones/models.py

from django.db import models
from django.conf import settings

# Importamos Evaluacion del dominio de planillas
from planillas.models import Evaluacion

# Choices compartidos
from .choices import (
    EstadoEval,
    NivelRiesgo,
    VAltura,
    HDist,
    Poblacion,
    AlturaAgarreCM,
    DistanciaLinealM,
    FrecuenciaMovimiento,
    FactorSlug,
)

# =========================
# Núcleo de Evaluaciones
# =========================

class RiskEvaluation(models.Model):
    """
    Entidad raíz de la Evaluación de Riesgos “post-Planilla 2”.
    Se crea una por cada Evaluacion (planillas.Evaluacion).
    """
    evaluacion = models.OneToOneField(
        Evaluacion,
        on_delete=models.CASCADE,
        related_name="risk_evaluation",
    )
    estado = models.CharField(
        max_length=20, choices=EstadoEval.choices, default=EstadoEval.PENDING
    )
    # Slugs canónicos de factores que hay que completar
    factores_requeridos = models.JSONField(default=list)  
    resultado_global = models.CharField(
        max_length=20, choices=NivelRiesgo.choices, blank=True, null=True
    )
    # Resumen por factor
    resumen_json = models.JSONField(default=dict, blank=True)

    # Trazabilidad
    creado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL
    )
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Evaluación de Riesgos"
        verbose_name_plural = "Evaluaciones de Riesgos"

    def __str__(self) -> str:
        return f"Evaluación de Riesgos #{self.pk} - Evaluación {self.evaluacion_id}"


class BaseFactorEvaluation(models.Model):
    """
    Clase base abstracta para todos los factores.
    """
    FACTOR_SLUG: str = ""

    risk_evaluation = models.ForeignKey(
        RiskEvaluation,
        on_delete=models.CASCADE,
        related_name="%(class)s_items"
    )
    factor_slug = models.SlugField()
    nivel_riesgo = models.CharField(
        max_length=20, choices=NivelRiesgo.choices, default=NivelRiesgo.NA
    )
    aplicable = models.BooleanField(default=True)
    observaciones = models.TextField(blank=True, default="")
    calc_data = models.JSONField(default=dict, blank=True)

    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
        indexes = [
            models.Index(fields=["factor_slug"]),
            models.Index(fields=["risk_evaluation", "factor_slug"]),
        ]

    def save(self, *args, **kwargs):
        if not self.factor_slug and getattr(self, "FACTOR_SLUG", ""):
            self.factor_slug = getattr(self, "FACTOR_SLUG")
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f"{self.factor_slug} (RiskEval {self.risk_evaluation_id})"


# ====================================
# FACTORES CON TABLAS NORMATIVAS
# ====================================

class LMC_Eval(BaseFactorEvaluation):
    FACTOR_SLUG = FactorSlug.LMC
    risk_evaluation = models.ForeignKey(
        RiskEvaluation, on_delete=models.CASCADE, related_name="lmc_evals"
    )

    peso_kg = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    duracion_h = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)
    frecuencia_h = models.PositiveIntegerField(null=True, blank=True)
    v_altura = models.CharField(max_length=32, choices=VAltura.choices, blank=True)
    h_dist = models.CharField(max_length=16, choices=HDist.choices, blank=True)
    # Agravantes
    giro_mayor_30 = models.BooleanField(default=False)
    una_mano = models.BooleanField(default=False)
    postura_agachada = models.BooleanField(default=False)
    carga_inestable = models.BooleanField(default=False)
    entorno_adverso = models.BooleanField(default=False)
    turnos_largos = models.BooleanField(default=False)


class EmpujeInicial_Eval(BaseFactorEvaluation):
    FACTOR_SLUG = FactorSlug.EMPUJE_INICIAL
    risk_evaluation = models.ForeignKey(
        RiskEvaluation, on_delete=models.CASCADE, related_name="empuje_inicial_evals"
    )

    poblacion = models.CharField(max_length=1, choices=Poblacion.choices, blank=True)
    altura_agarre_cm = models.IntegerField(choices=AlturaAgarreCM.choices, null=True, blank=True)
    distancia_m = models.IntegerField(choices=DistanciaLinealM.choices, null=True, blank=True)
    frecuencia_opcion = models.CharField(max_length=32, choices=FrecuenciaMovimiento.choices, blank=True)
    fuerza_n = models.DecimalField(max_digits=7, decimal_places=2, null=True, blank=True)


class EmpujeSostenida_Eval(BaseFactorEvaluation):
    FACTOR_SLUG = FactorSlug.EMPUJE_SOSTENIDA
    risk_evaluation = models.ForeignKey(
        RiskEvaluation, on_delete=models.CASCADE, related_name="empuje_sostenida_evals"
    )

    poblacion = models.CharField(max_length=1, choices=Poblacion.choices, blank=True)
    altura_agarre_cm = models.IntegerField(choices=AlturaAgarreCM.choices, null=True, blank=True)
    distancia_m = models.IntegerField(choices=DistanciaLinealM.choices, null=True, blank=True)
    frecuencia_opcion = models.CharField(max_length=32, choices=FrecuenciaMovimiento.choices, blank=True)
    fuerza_n = models.DecimalField(max_digits=7, decimal_places=2, null=True, blank=True)


class TraccionInicial_Eval(BaseFactorEvaluation):
    FACTOR_SLUG = FactorSlug.TRACCION_INICIAL
    risk_evaluation = models.ForeignKey(
        RiskEvaluation, on_delete=models.CASCADE, related_name="traccion_inicial_evals"
    )

    poblacion = models.CharField(max_length=1, choices=Poblacion.choices, blank=True)
    altura_agarre_cm = models.IntegerField(choices=AlturaAgarreCM.choices, null=True, blank=True)
    distancia_m = models.IntegerField(choices=DistanciaLinealM.choices, null=True, blank=True)
    frecuencia_opcion = models.CharField(max_length=32, choices=FrecuenciaMovimiento.choices, blank=True)
    fuerza_n = models.DecimalField(max_digits=7, decimal_places=2, null=True, blank=True)


class TraccionSostenida_Eval(BaseFactorEvaluation):
    FACTOR_SLUG = FactorSlug.TRACCION_SOSTENIDA
    risk_evaluation = models.ForeignKey(
        RiskEvaluation, on_delete=models.CASCADE, related_name="traccion_sostenida_evals"
    )

    poblacion = models.CharField(max_length=1, choices=Poblacion.choices, blank=True)
    altura_agarre_cm = models.IntegerField(choices=AlturaAgarreCM.choices, null=True, blank=True)
    distancia_m = models.IntegerField(choices=DistanciaLinealM.choices, null=True, blank=True)
    frecuencia_opcion = models.CharField(max_length=32, choices=FrecuenciaMovimiento.choices, blank=True)
    fuerza_n = models.DecimalField(max_digits=7, decimal_places=2, null=True, blank=True)


class Transporte_Eval(BaseFactorEvaluation):
    FACTOR_SLUG = FactorSlug.TRANSPORTE
    risk_evaluation = models.ForeignKey(
        RiskEvaluation, on_delete=models.CASCADE, related_name="transporte_evals"
    )

    # Datos de cálculo (Nota: Admin buscaba 'peso_kg', aqui es 'masa_kg')
    masa_kg = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    distancia_m = models.DecimalField(max_digits=6, decimal_places=1, null=True, blank=True)
    frecuencia_jornada = models.PositiveIntegerField(
        null=True, blank=True, help_text="Viajes por jornada"
    )
    frecuencia_max_minuto = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Máximo de traslados observado en cualquier minuto",
    )
    frecuencia_max_hora = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Máximo de traslados observado en cualquier hora",
    )

    # Condiciones
    en_plano_horizontal = models.BooleanField(null=True, blank=True)
    jornada_8h = models.BooleanField(null=True, blank=True)
    velocidad_05a1_ms = models.BooleanField(null=True, blank=True)
    superficie_plana = models.BooleanField(null=True, blank=True)


# ====================================
# FACTORES CON MODELOS PROGRESIVOS
# ====================================

class Bipedestacion_Eval(BaseFactorEvaluation):
    FACTOR_SLUG = FactorSlug.BIPEDESTACION
    risk_evaluation = models.ForeignKey(
        RiskEvaluation, on_delete=models.CASCADE, related_name="bipedestacion_evals"
    )

    # Sección 2: Tiempo (Nota: Admin buscaba 'duracion_h', aqui es 'horas_de_pie_total')
    horas_de_pie_total = models.DecimalField(
        max_digits=4, decimal_places=2, null=True, blank=True, help_text="Horas/día"
    )
    tiempo_continuo_min = models.PositiveIntegerField(null=True, blank=True)

    # Sección 3: Movilidad
    movilidad_tipo = models.CharField(
        max_length=20,
        choices=[
            ("estatica", "Estática/Restringida"),
            ("deambulacion", "Con deambulación"),
        ],
        blank=True,
    )
    movilidad_m_por_h = models.PositiveIntegerField(null=True, blank=True)

    # Sección 4: Factores agravantes
    manipula_cargas_mayores_2kg = models.BooleanField(default=False)
    ambiente_caluroso = models.BooleanField(default=False)
    piso_duro = models.BooleanField(default=False)
    superficie_irregular = models.BooleanField(default=False)
    piso_resbaladizo = models.BooleanField(default=False)
    calzado_inadecuado = models.BooleanField(default=False)
    tronco_inclinado = models.BooleanField(default=False)
    brazos_elevados = models.BooleanField(default=False)
    cuello_giro_inclin = models.BooleanField(default=False)

    # Sección 5: Síntomas
    sintomas_json = models.JSONField(default=list, blank=True)
    SINTOMAS_FRECUENCIA_CHOICES = [
        ("", "---------"),
        ("diaria", "Diaria"),
        ("semanal", "Semanal"),
        ("ocasional", "Ocasional"),
    ]
    sintomas_frecuencia = models.CharField(
        max_length=16,
        choices=SINTOMAS_FRECUENCIA_CHOICES,
        blank=True,
        help_text="Frecuencia de los síntomas asociados a estar de pie."
    )
    controles_existentes_json = models.JSONField(default=list, blank=True)


class RepetitivosMS_Eval(BaseFactorEvaluation):
    FACTOR_SLUG = FactorSlug.REPETITIVOS_MS
    risk_evaluation = models.ForeignKey(
        RiskEvaluation, on_delete=models.CASCADE, related_name="repetitivos_ms_evals"
    )

    monotarea = models.BooleanField(default=False)
    horas_dia = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)
    
    # Eje X (tasación del observador) y Eje Y (Borg pico)
    nam_x_valor = models.PositiveSmallIntegerField(null=True, blank=True)  # 0..10
    borg_y_valor = models.PositiveSmallIntegerField(null=True, blank=True)  # 0..10
    
    # Factores agravantes
    posturas_obligadas = models.BooleanField(default=False)
    estres_contacto = models.BooleanField(default=False)
    bajas_temperaturas = models.BooleanField(default=False)
    vibraciones_mb = models.BooleanField(default=False)


class PosturasForzadas_Eval(BaseFactorEvaluation):
    FACTOR_SLUG = FactorSlug.POSTURAS_FORZADAS
    risk_evaluation = models.ForeignKey(
        RiskEvaluation, on_delete=models.CASCADE, related_name="posturas_forzadas_evals"
    )

    puntaje_a = models.PositiveSmallIntegerField(null=True, blank=True)
    puntaje_b = models.PositiveSmallIntegerField(null=True, blank=True)
    puntaje_c = models.PositiveSmallIntegerField(null=True, blank=True)
    puntaje_final = models.PositiveSmallIntegerField(null=True, blank=True)

    detalles_json = models.JSONField(default=dict, blank=True)


class VibracionMB_Eval(BaseFactorEvaluation):
    """
    Modelo actualizado para Vibraciones Mano-Brazo (Res. 295/03)
    Soporta:
    1. Carga 'Legacy' (Un solo valor, compatible con datos viejos).
    2. Carga por Ejes (X, Y, Z) -> Calcula Eje Dominante (Recomendado).
    3. Exposición Múltiple -> Almacena tramos y calcula energía total.
    """
    FACTOR_SLUG = FactorSlug.VIBRACION_MB
    risk_evaluation = models.ForeignKey(
        RiskEvaluation, on_delete=models.CASCADE, related_name="vibracion_mb_evals"
    )

    # Tipo de exposición
    tipo_exposicion = models.CharField(
        max_length=10,
        choices=[("simple", "Exposición Simple"), ("multiple", "Exposición Múltiple")],
        default="simple",
        blank=True,
    )

    # --- EXPOSICIÓN SIMPLE ---
    # Legacy (un solo valor)
    a_k_m_s2 = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    # Nuevos (por ejes - Recomendado)
    ax_mps2 = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, help_text="Eje X (Dorso-Palma)")
    ay_mps2 = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, help_text="Eje Y (Lateral/Pulgar)")
    az_mps2 = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, help_text="Eje Z (Longitudinal)")
    
    duracion_h = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)

    # --- EXPOSICIÓN MÚLTIPLE ---
    # Guardará lista de objetos: {"ax":..., "ay":..., "az":..., "Ti":...}
    exposiciones_json = models.JSONField(default=list, blank=True)

    # --- RESULTADOS GUARDADOS (Para trazabilidad directa en BD) ---
    eje_dominante_final = models.CharField(max_length=20, blank=True, help_text="X, Y, Z o Legacy")
    valor_final_mps2 = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)

class VibracionCE_Eval(BaseFactorEvaluation):
    """
    Modelo actualizado para Vibración Cuerpo Entero (Res. 295/03 / ISO 2631).
    - Mantiene compatibilidad con carga simple (Legacy).
    - Integra datos de contexto (Formulario 2 - Secciones B y C).
    - Permite carga detallada por tramos (Sección D) vía VCESegment.
    """
    FACTOR_SLUG = FactorSlug.VIBRACION_CE
    risk_evaluation = models.ForeignKey(
        RiskEvaluation, on_delete=models.CASCADE, related_name="vibracion_ce_evals"
    )

    # --------------------------------------------------------------------------
    # 1. CAMPOS LEGACY / MODO SIMPLE (Conservados para evitar roturas)
    # --------------------------------------------------------------------------
    metodo = models.CharField(
        max_length=15,
        choices=[("espectral", "Análisis Espectral"), ("ponderadas", "Aceleraciones Ponderadas")],
        blank=True,
    )
    # Método 1: espectral
    espectro_json = models.JSONField(default=dict, blank=True)
    # Método 2: aceleraciones totales (Valores únicos sin tramos)
    a_wx = models.DecimalField(max_digits=5, decimal_places=3, null=True, blank=True)
    a_wy = models.DecimalField(max_digits=5, decimal_places=3, null=True, blank=True)
    a_wz = models.DecimalField(max_digits=5, decimal_places=3, null=True, blank=True)
    
    duracion_h = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)
    factor_cresta_gt6 = models.BooleanField(default=False)

    # --------------------------------------------------------------------------
    # 2. NUEVOS CAMPOS: CONTEXTO Y MONTAJE (Formulario 2 - Secciones B y C)
    # --------------------------------------------------------------------------
    postura = models.CharField(
        "Postura",
        max_length=20,
        choices=[('sentado', 'Sentado'), ('de_pie', 'De Pie'), ('recostado', 'Recostado')],
        default='sentado'
    )
    salud_columna = models.TextField("Antecedentes Salud (Opcional)", blank=True, null=True)

    ubicacion_sensor = models.CharField(
        "Ubicación Sensor",
        max_length=50,
        choices=[('isquiones', 'Bajo Isquiones (Disco)'), ('respaldo', 'Respaldo'), ('pies', 'Pies')],
        default='isquiones'
    )
    
    # Evidencia (Requerido por auditoría)
    foto_montaje = models.ImageField(upload_to='evidencia_vce/', blank=True, null=True)
    certificado_calibracion = models.FileField(upload_to='certificados_vce/', blank=True, null=True)

    # --------------------------------------------------------------------------
    # 3. RESULTADOS GLOBALES (Calculados)
    # --------------------------------------------------------------------------
    valor_final_a8 = models.DecimalField("A(8) Global Max", max_digits=6, decimal_places=3, null=True, blank=True)
    eje_dominante = models.CharField(max_length=30, blank=True, help_text="X / Y / Z")
    
    # JSON para guardar detalles técnicos del cálculo (A8 por eje, warnings, debug tramos)
    calc_details = models.JSONField(default=dict, blank=True)

    def __str__(self):
        return f"VCE Eval {self.id}"


class VCESegment(models.Model):
    """
    Modelo HIJO: Corresponde a la Sección D del Formulario (Tramos).
    Cada tramo representa un período de exposición bajo condiciones constantes.
    """
    evaluation = models.ForeignKey(
        VibracionCE_Eval, 
        related_name='segmentos', 
        on_delete=models.CASCADE
    )
    
    # --- D1. FUENTE Y TERRENO ---
    vehiculo_maquina = models.CharField("Vehículo / Máquina", max_length=100, help_text="Ej: Autoelevador Toyota")
    tipo_asiento = models.CharField(
        max_length=50,
        choices=[
            ('fijo', 'Fijo / Sin suspensión'),
            ('mecanica', 'Suspensión Mecánica'),
            ('neumatica', 'Suspensión Neumática'),
            ('desgastado', 'Deteriorado / Desgastado')
        ],
        default='mecanica'
    )
    superficie_terreno = models.CharField(
        max_length=50,
        choices=[
            ('liso', 'Liso (Hormigón/Asfalto bueno)'),
            ('irregular', 'Irregular (Tierra/Gravilla)'),
            ('baches', 'Muy Irregular (Baches/Pozos)'),
            ('offroad', 'Off-road / Campo traviesa')
        ],
        default='liso'
    )
    velocidad_promedio = models.DecimalField("Velocidad (km/h)", max_digits=5, decimal_places=1, blank=True, null=True)
    estado_neumaticos = models.CharField(
        max_length=20,
        choices=[('correcto', 'Correcto'), ('desinflado', 'Desinflado'), ('macizo', 'Macizo')],
        default='correcto'
    )

    # --- D2. TIEMPOS ---
    tiempo_horas = models.DecimalField("Tiempo Exp. (Horas)", max_digits=4, decimal_places=2)

    # --- D3. VALORES MEDIDOS (RMS Ponderado y Picos) ---
    # Importante: El usuario ingresa el valor del equipo (ponderado Wd/Wk). 
    # El sistema aplicará el factor 1.4 a X e Y internamente.
    aw_x = models.DecimalField("Eje X - RMS (m/s²)", max_digits=6, decimal_places=3)
    aw_y = models.DecimalField("Eje Y - RMS (m/s²)", max_digits=6, decimal_places=3)
    aw_z = models.DecimalField("Eje Z - RMS (m/s²)", max_digits=6, decimal_places=3)

    # Datos para Método B (Doble verificación)
    cf_x = models.DecimalField("FC X", max_digits=5, decimal_places=2, blank=True, null=True)
    cf_y = models.DecimalField("FC Y", max_digits=5, decimal_places=2, blank=True, null=True)
    cf_z = models.DecimalField("FC Z", max_digits=5, decimal_places=2, blank=True, null=True)
    
    pico_espectral_hz = models.PositiveIntegerField(
        "Pico Espectral (Hz)", 
        blank=True, null=True, 
        help_text="Frecuencia dominante para análisis de resonancia"
    )

    class Meta:
        verbose_name = "Tramo VCE"
        verbose_name_plural = "Tramos VCE"
        ordering = ["id"]

    def __str__(self):
        return f"Tramo {self.vehiculo_maquina} ({self.tiempo_horas}h)"


class ConfortTermico_Eval(BaseFactorEvaluation):
    FACTOR_SLUG = FactorSlug.CONFORT_TERMICO
    risk_evaluation = models.ForeignKey(
        RiskEvaluation, on_delete=models.CASCADE, related_name="confort_termico_evals"
    )

    temperatura_operativa_c = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    humedad_relativa_pct = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)


class EstresContacto_Eval(BaseFactorEvaluation):
    FACTOR_SLUG = FactorSlug.ESTRES_CONTACTO
    risk_evaluation = models.ForeignKey(
        RiskEvaluation, on_delete=models.CASCADE, related_name="estres_contacto_evals"
    )

    segmento_afectado = models.CharField(
        max_length=32,
        choices=[
            ("muneca", "Muñeca"),
            ("antebrazo", "Antebrazo"),
            ("mano_dedos", "Palma/Dedos"),
            ("codo", "Codo"),
            ("muslo_pierna", "Muslo/Pierna"),
            ("otro", "Otro"),
        ],
        blank=True,
    )
    objeto_superficie = models.CharField(max_length=64, blank=True)
    tipo_borde = models.CharField(
        max_length=16,
        choices=[
            ("afilado", "Afilado/Canto Vivo"),
            ("duro", "Duro/Recto"),
            ("acolchado", "Acolchado/Redondeado"),
        ],
        blank=True,
    )
    duracion_continua_min = models.PositiveIntegerField(null=True, blank=True)
    frecuencia_exposicion = models.CharField(
        max_length=16,
        choices=[
            ("bajo", "Bajo (<30% del ciclo)"),
            ("moderado", "Moderado (30–60%)"),
            ("alto", "Alto (>60%)"),
        ],
        blank=True,
    )
    # Factores agravantes
    mano_como_martillo = models.BooleanField(default=False)
    mango_inadecuado = models.BooleanField(default=False)
    postura_forzada_asociada = models.BooleanField(default=False)
    # Síntomas y controles
    sintomas_json = models.JSONField(default=list, blank=True)
    controles_existentes_json = models.JSONField(default=list, blank=True)
