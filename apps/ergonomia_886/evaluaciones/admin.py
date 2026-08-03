# evaluaciones/admin.py
from django.contrib import admin

# Importamos modelos de Evaluaciones
from .models import (
    RiskEvaluation,
    LMC_Eval,
    EmpujeInicial_Eval,
    EmpujeSostenida_Eval,
    TraccionInicial_Eval,
    TraccionSostenida_Eval,
    Transporte_Eval,
    Bipedestacion_Eval,
    RepetitivosMS_Eval,
    PosturasForzadas_Eval,
    VibracionMB_Eval,
    VibracionCE_Eval,
    ConfortTermico_Eval,
    EstresContacto_Eval,
)

# Importamos modelos de Planillas
from apps.ergonomia_886.planillas.models import (
    Evaluacion,
    Planilla1,
    FactorRiesgo,
    Planilla2A,
    Planilla2B,
    Planilla2C,
    Planilla2D,
    Planilla2E,
    Planilla2F,
    Planilla2G,
    Planilla2H,
    Planilla2I,
    Planilla3,
    MedidaEspecifica,
    SeguimientoMedida,
)

# =============================================================================
# CONFIGURACIÓN DE ADMIN PARA MODELOS DE PLANILLAS
# =============================================================================

@admin.register(Evaluacion)
class EvaluacionAdmin(admin.ModelAdmin):
    list_display = ["id", "razon_social", "cuit", "ciiu", "provincia", "fecha_creacion", "usuario"]
    list_filter = ["provincia", "fecha_creacion", "fecha_modificacion"]
    search_fields = ["razon_social", "cuit", "direccion_establecimiento", "ciiu"]
    readonly_fields = ["fecha_creacion", "fecha_modificacion"]
    date_hierarchy = "fecha_creacion"

    fieldsets = (
        ("Usuario", {"fields": ("usuario",)}),
        ("Información de la Empresa", {"fields": ("razon_social", "cuit", "ciiu")}),
        ("Ubicación", {"fields": ("direccion_establecimiento", "provincia")}),
        ("Fechas", {"fields": ("fecha_creacion", "fecha_modificacion"), "classes": ("collapse",)}),
    )


@admin.register(Planilla1)
class Planilla1Admin(admin.ModelAdmin):
    list_display = [
        "evaluacion",
        "puesto_trabajo",
        "area_sector",
        "nro_trabajadores",
        "procedimiento_escrito",
        "capacitacion",
    ]
    list_filter = ["procedimiento_escrito", "capacitacion", "manifestacion_temprana"]
    search_fields = ["evaluacion__razon_social", "puesto_trabajo", "area_sector", "nombres_trabajadores"]
    raw_id_fields = ["evaluacion"]

    fieldsets = (
        ("Evaluación", {"fields": ("evaluacion",)}),
        ("Datos del Puesto", {"fields": ("area_sector", "puesto_trabajo", "nro_trabajadores")}),
        ("Procedimientos", {"fields": ("procedimiento_escrito", "capacitacion")}),
        ("Trabajadores", {"fields": ("nombres_trabajadores",)}),
        ("Manifestaciones", {"fields": ("manifestacion_temprana", "ubicacion_sintoma")}),
        ("Tareas Habituales", {"fields": ("tarea_1", "tarea_2", "tarea_3"), "classes": ("collapse",)}),
    )


@admin.register(FactorRiesgo)
class FactorRiesgoAdmin(admin.ModelAdmin):
    """
    OJO: En planillas.models.FactorRiesgo NO existe 'nivel_riesgo' único ni 'requiere_evaluacion' ni 'observaciones'.
    Existen: presente, tiempo_exposicion, riesgo_tarea1/2/3.
    """
    list_display = [
        "planilla1",
        "tipo_factor",
        "presente",
        "tiempo_exposicion",
        "riesgo_tarea1",
        "riesgo_tarea2",
        "riesgo_tarea3",
    ]
    list_filter = ["tipo_factor", "presente", "riesgo_tarea1", "riesgo_tarea2", "riesgo_tarea3"]
    search_fields = ["planilla1__evaluacion__razon_social", "tiempo_exposicion"]
    raw_id_fields = ["planilla1"]


class Planilla2BaseAdmin(admin.ModelAdmin):
    """
    Base común Planilla2X.
    IMPORTANTE: NO ponemos p2_presenta_manifestacion_temprana acá porque Planilla2H no lo tiene.
    """
    list_display = ["id", "evaluacion", "tarea_nro"]
    search_fields = ["evaluacion__razon_social", "tarea_nro"]
    raw_id_fields = ["evaluacion"]


@admin.register(Planilla2A)
class Planilla2AAdmin(Planilla2BaseAdmin):
    list_display = Planilla2BaseAdmin.list_display + [
        "p1_levanta_2_a_25kg",
        "p1_levanta_mas_25kg",
        "p2_presenta_manifestacion_temprana",
    ]
    list_filter = [
        "p2_presenta_manifestacion_temprana",
        "p1_levanta_2_a_25kg",
        "p1_levanta_mas_25kg",
    ]


@admin.register(Planilla2B)
class Planilla2BAdmin(Planilla2BaseAdmin):
    list_display = Planilla2BaseAdmin.list_display + [
        "p1_tareas_ciclicas_diarias",
        "p1_desplaza_mas_de_60m",
        "p1_esfuerzo_supera_34kgf",
        "p2_presenta_manifestacion_temprana",
    ]
    list_filter = [
        "p2_presenta_manifestacion_temprana",
        "p1_tareas_ciclicas_diarias",
        "p1_desplaza_mas_de_60m",
        "p1_esfuerzo_supera_34kgf",
    ]


@admin.register(Planilla2C)
class Planilla2CAdmin(Planilla2BaseAdmin):
    list_display = Planilla2BaseAdmin.list_display + [
        "p1_transporta_2_a_25kg",
        "p1_transporta_mas_de_20m",
        "p1_transporta_mas_de_25kg",
        "p2_presenta_manifestacion_temprana",
    ]
    list_filter = [
        "p2_presenta_manifestacion_temprana",
        "p1_transporta_2_a_25kg",
        "p1_transporta_mas_de_20m",
        "p1_transporta_mas_de_25kg",
    ]


@admin.register(Planilla2D)
class Planilla2DAdmin(Planilla2BaseAdmin):
    list_display = Planilla2BaseAdmin.list_display + [
        "p1_de_pie_sin_sentarse_mas_2h",
        "p2_de_pie_mas_3h_escasa_deambulacion",
        "p2_presenta_manifestacion_temprana",
    ]
    list_filter = [
        "p2_presenta_manifestacion_temprana",
        "p1_de_pie_sin_sentarse_mas_2h",
        "p2_de_pie_mas_3h_escasa_deambulacion",
    ]


@admin.register(Planilla2E)
class Planilla2EAdmin(Planilla2BaseAdmin):
    list_display = Planilla2BaseAdmin.list_display + [
        "p1_extremidades_superiores_mas_4h",
        "p2_activas_mas_40_porciento",
        "p2_esfuerzo_borg_mayor_3",
        "p2_presenta_manifestacion_temprana",
    ]
    list_filter = [
        "p2_presenta_manifestacion_temprana",
        "p1_extremidades_superiores_mas_4h",
        "p2_activas_mas_40_porciento",
        "p2_esfuerzo_borg_mayor_3",
    ]


@admin.register(Planilla2F)
class Planilla2FAdmin(Planilla2BaseAdmin):
    # Campo viejo inexistente: p2_cuello_tronco_flexion_extension
    # Campos reales: p2_cuello, p2_cintura, etc.
    list_display = Planilla2BaseAdmin.list_display + [
        "p1_adopta_posturas_forzadas",
        "p2_cuello",
        "p2_cintura",
        "p2_presenta_manifestacion_temprana",
    ]
    list_filter = [
        "p2_presenta_manifestacion_temprana",
        "p1_adopta_posturas_forzadas",
        "p2_cuello",
        "p2_cintura",
        "p2_brazos",
        "p2_munecas",
        "p2_miembros_inferiores",
    ]


@admin.register(Planilla2G)
class Planilla2GAdmin(Planilla2BaseAdmin):
    # Campos viejos inexistentes (ej: p1_expuesto_vibraciones, etc.)
    # Campos reales: p1_mb_trabaja_con_herramientas, p2_mb_supera_limites, p2_ce_supera_limites, etc.
    list_display = Planilla2BaseAdmin.list_display + [
        "p1_mb_trabaja_con_herramientas",
        "p2_mb_supera_limites",
        "p2_ce_supera_limites",
        "p2_mb_presenta_manifestacion_temprana",
        "p2_ce_presenta_manifestacion_temprana",
    ]
    list_filter = [
        "p1_mb_trabaja_con_herramientas",
        "p2_mb_supera_limites",
        "p2_ce_supera_limites",
        "p2_mb_presenta_manifestacion_temprana",
        "p2_ce_presenta_manifestacion_temprana",
    ]


@admin.register(Planilla2H)
class Planilla2HAdmin(Planilla2BaseAdmin):
    # Planilla2H NO tiene p2_presenta_manifestacion_temprana.
    list_display = Planilla2BaseAdmin.list_display + [
        "p1_percibe_temp_no_confortables",
        "p2_curva_fanger_fuera_de_zona",
    ]
    list_filter = [
        "p1_percibe_temp_no_confortables",
        "p2_curva_fanger_fuera_de_zona",
    ]


@admin.register(Planilla2I)
class Planilla2IAdmin(Planilla2BaseAdmin):
    # Campo viejo inexistente: p1_contacto_cuerpo_superficie_dura
    # Campo real: p1_mantiene_apoyada_parte_cuerpo
    list_display = Planilla2BaseAdmin.list_display + [
        "p1_mantiene_apoyada_parte_cuerpo",
        "p2_apoya_sobre_superficie_aguda",
        "p2_utiliza_herramientas_presionan",
        "p2_presenta_manifestacion_temprana",
    ]
    list_filter = [
        "p2_presenta_manifestacion_temprana",
        "p1_mantiene_apoyada_parte_cuerpo",
        "p2_apoya_sobre_superficie_aguda",
        "p2_utiliza_herramientas_presionan",
        "p2_movimientos_percusion",
    ]


@admin.register(Planilla3)
class Planilla3Admin(admin.ModelAdmin):
    list_display = ["evaluacion", "tarea_analizada", "general_informado_riesgo", "general_capacitado_sintomas"]
    search_fields = ["evaluacion__razon_social", "tarea_analizada", "observaciones_generales"]
    raw_id_fields = ["evaluacion"]
    list_filter = [
        "general_informado_riesgo",
        "general_capacitado_sintomas",
        "general_capacitado_medidas",
        "fecha_informado_riesgo",
        "fecha_capacitado_sintomas",
        "fecha_capacitado_medidas",
    ]

    fieldsets = (
        ("Evaluación", {"fields": ("evaluacion", "tarea_analizada")}),
        (
            "Medidas Preventivas Generales",
            {
                "fields": (
                    "general_informado_riesgo",
                    "fecha_informado_riesgo",
                    "general_capacitado_sintomas",
                    "fecha_capacitado_sintomas",
                    "general_capacitado_medidas",
                    "fecha_capacitado_medidas",
                )
            },
        ),
        ("Observaciones", {"fields": ("observaciones_generales",), "classes": ("collapse",)}),
    )


@admin.register(MedidaEspecifica)
class MedidaEspecificaAdmin(admin.ModelAdmin):
    list_display = ["id", "planilla3", "descripcion_corta", "tiene_observaciones"]
    search_fields = ["planilla3__evaluacion__razon_social", "descripcion", "observaciones"]
    raw_id_fields = ["planilla3"]

    def descripcion_corta(self, obj):
        texto = obj.descripcion or ""
        return (texto[:50] + "...") if len(texto) > 50 else texto

    descripcion_corta.short_description = "Descripción"

    def tiene_observaciones(self, obj):
        return bool(obj.observaciones)

    tiene_observaciones.boolean = True
    tiene_observaciones.short_description = "Observaciones"


@admin.register(SeguimientoMedida)
class SeguimientoMedidaAdmin(admin.ModelAdmin):
    """
    Modelo real planillas.SeguimientoMedida:
      - fecha_impl_admin
      - fecha_impl_ing
      - fecha_cierre
    NO existen: fecha_implementacion, fecha_verificacion.
    """
    list_display = ["id", "medida_especifica", "fecha_impl_admin", "fecha_impl_ing", "fecha_cierre", "completada"]
    search_fields = ["medida_especifica__descripcion", "medida_especifica__planilla3__evaluacion__razon_social"]
    raw_id_fields = ["medida_especifica"]
    list_filter = ["fecha_impl_admin", "fecha_impl_ing", "fecha_cierre"]
    date_hierarchy = "fecha_impl_admin"

    def completada(self, obj):
        return obj.fecha_cierre is not None

    completada.boolean = True
    completada.short_description = "Cerrada"

    fieldsets = (
        ("Medida", {"fields": ("medida_especifica",)}),
        ("Datos del Seguimiento", {"fields": ("nombre_puesto", "fecha_evaluacion", "nivel_riesgo")}),
        ("Fechas de Seguimiento", {"fields": ("fecha_impl_admin", "fecha_impl_ing", "fecha_cierre")}),
    )


# =============================================================================
# CONFIGURACIÓN DE ADMIN PARA EVALUACIONES DE RIESGO
# =============================================================================

@admin.register(RiskEvaluation)
class RiskEvaluationAdmin(admin.ModelAdmin):
    list_display = ["id", "evaluacion", "estado", "resultado_global", "creado_en"]
    list_filter = ["estado", "resultado_global", "creado_en"]
    search_fields = ["evaluacion__razon_social"]
    readonly_fields = ["creado_en", "actualizado_en"]
    raw_id_fields = ["evaluacion"]
    date_hierarchy = "creado_en"

    fieldsets = (
        ("Evaluación Base", {"fields": ("evaluacion",)}),
        ("Estado y Resultado", {"fields": ("estado", "resultado_global")}),
        ("Datos Adicionales", {"fields": ("resumen_json",), "classes": ("collapse",)}),
        ("Fechas", {"fields": ("creado_en", "actualizado_en"), "classes": ("collapse",)}),
    )


class FactorRiesgoBaseAdmin(admin.ModelAdmin):
    list_display = ["id", "risk_evaluation", "factor_slug", "nivel_riesgo", "aplicable", "creado_en"]
    list_filter = ["nivel_riesgo", "aplicable", "factor_slug", "creado_en"]
    search_fields = ["risk_evaluation__evaluacion__razon_social", "observaciones"]
    readonly_fields = ["creado_en", "actualizado_en", "calc_data"]
    raw_id_fields = ["risk_evaluation"]
    date_hierarchy = "creado_en"

    fieldsets = (
        ("Evaluación de Riesgo", {"fields": ("risk_evaluation", "factor_slug")}),
        ("Estado", {"fields": ("aplicable", "nivel_riesgo")}),
        ("Observaciones", {"fields": ("observaciones",)}),
        ("Datos de Cálculo", {"fields": ("calc_data",), "classes": ("collapse",)}),
        ("Fechas", {"fields": ("creado_en", "actualizado_en"), "classes": ("collapse",)}),
    )


@admin.register(LMC_Eval)
class LMC_EvalAdmin(FactorRiesgoBaseAdmin):
    list_display = ["id", "risk_evaluation", "peso_kg", "duracion_h", "frecuencia_h", "nivel_riesgo", "creado_en"]

    fieldsets = FactorRiesgoBaseAdmin.fieldsets + (
        (
            "Datos LMC",
            {
                "fields": (
                    "peso_kg",
                    "duracion_h",
                    "frecuencia_h",
                    "v_altura",
                    "h_dist",
                    "giro_mayor_30",
                    "una_mano",
                    "postura_agachada",
                    "carga_inestable",
                    "entorno_adverso",
                    "turnos_largos",
                )
            },
        ),
    )


@admin.register(EmpujeInicial_Eval)
class EmpujeInicial_EvalAdmin(FactorRiesgoBaseAdmin):
    list_display = ["id", "risk_evaluation", "fuerza_n", "poblacion", "altura_agarre_cm", "nivel_riesgo", "creado_en"]
    list_filter = FactorRiesgoBaseAdmin.list_filter + ["poblacion", "altura_agarre_cm", "distancia_m"]

    fieldsets = FactorRiesgoBaseAdmin.fieldsets + (
        (
            "Datos Empuje Inicial",
            {"fields": ("poblacion", "altura_agarre_cm", "distancia_m", "frecuencia_opcion", "fuerza_n")},
        ),
    )


@admin.register(EmpujeSostenida_Eval)
class EmpujeSostenida_EvalAdmin(FactorRiesgoBaseAdmin):
    list_display = ["id", "risk_evaluation", "fuerza_n", "poblacion", "altura_agarre_cm", "nivel_riesgo", "creado_en"]
    list_filter = FactorRiesgoBaseAdmin.list_filter + ["poblacion", "altura_agarre_cm", "distancia_m"]

    fieldsets = FactorRiesgoBaseAdmin.fieldsets + (
        (
            "Datos Empuje Sostenido",
            {"fields": ("poblacion", "altura_agarre_cm", "distancia_m", "frecuencia_opcion", "fuerza_n")},
        ),
    )


@admin.register(TraccionInicial_Eval)
class TraccionInicial_EvalAdmin(FactorRiesgoBaseAdmin):
    list_display = ["id", "risk_evaluation", "fuerza_n", "poblacion", "altura_agarre_cm", "nivel_riesgo", "creado_en"]
    list_filter = FactorRiesgoBaseAdmin.list_filter + ["poblacion", "altura_agarre_cm", "distancia_m"]

    fieldsets = FactorRiesgoBaseAdmin.fieldsets + (
        (
            "Datos Tracción Inicial",
            {"fields": ("poblacion", "altura_agarre_cm", "distancia_m", "frecuencia_opcion", "fuerza_n")},
        ),
    )


@admin.register(TraccionSostenida_Eval)
class TraccionSostenida_EvalAdmin(FactorRiesgoBaseAdmin):
    list_display = ["id", "risk_evaluation", "fuerza_n", "poblacion", "altura_agarre_cm", "nivel_riesgo", "creado_en"]
    list_filter = FactorRiesgoBaseAdmin.list_filter + ["poblacion", "altura_agarre_cm", "distancia_m"]

    fieldsets = FactorRiesgoBaseAdmin.fieldsets + (
        (
            "Datos Tracción Sostenida",
            {"fields": ("poblacion", "altura_agarre_cm", "distancia_m", "frecuencia_opcion", "fuerza_n")},
        ),
    )


@admin.register(Transporte_Eval)
class Transporte_EvalAdmin(FactorRiesgoBaseAdmin):
    """
    Modelo real evaluaciones.Transporte_Eval:
      - masa_kg
      - distancia_m
      - frecuencia_jornada
      - condiciones booleanas (en_plano_horizontal, jornada_8h, velocidad_05a1_ms, superficie_plana)
    NO existe: duracion_h
    """
    list_display = ["id", "risk_evaluation", "masa_kg", "distancia_m", "frecuencia_jornada", "nivel_riesgo", "creado_en"]
    list_filter = FactorRiesgoBaseAdmin.list_filter + ["en_plano_horizontal", "superficie_plana", "velocidad_05a1_ms", "jornada_8h"]

    fieldsets = FactorRiesgoBaseAdmin.fieldsets + (
        (
            "Datos Transporte",
            {
                "fields": (
                    "masa_kg",
                    "distancia_m",
                    "frecuencia_jornada",
                    "en_plano_horizontal",
                    "superficie_plana",
                    "velocidad_05a1_ms",
                    "jornada_8h",
                )
            },
        ),
    )


@admin.register(Bipedestacion_Eval)
class Bipedestacion_EvalAdmin(FactorRiesgoBaseAdmin):
    list_display = ["id", "risk_evaluation", "horas_de_pie_total", "nivel_riesgo", "creado_en"]

    fieldsets = FactorRiesgoBaseAdmin.fieldsets + (
        (
            "Datos Bipedestación",
            {"fields": ("horas_de_pie_total", "tiempo_continuo_min", "movilidad_tipo", "movilidad_m_por_h")},
        ),
        (
            "Factores Agravantes",
            {"fields": ("manipula_cargas_mayores_2kg", "ambiente_caluroso", "piso_duro", "calzado_inadecuado")},
        ),
    )


@admin.register(RepetitivosMS_Eval)
class RepetitivosMS_EvalAdmin(FactorRiesgoBaseAdmin):
    list_display = ["id", "risk_evaluation", "monotarea", "horas_dia", "nivel_riesgo", "creado_en"]
    list_filter = FactorRiesgoBaseAdmin.list_filter + ["monotarea", "posturas_obligadas", "estres_contacto", "bajas_temperaturas", "vibraciones_mb"]

    fieldsets = FactorRiesgoBaseAdmin.fieldsets + (
        (
            "Datos Movimientos Repetitivos",
            {
                "fields": (
                    "monotarea",
                    "horas_dia",
                    "nam_x_valor",
                    "borg_y_valor",
                    "posturas_obligadas",
                    "estres_contacto",
                    "bajas_temperaturas",
                    "vibraciones_mb",
                )
            },
        ),
    )


@admin.register(PosturasForzadas_Eval)
class PosturasForzadas_EvalAdmin(FactorRiesgoBaseAdmin):
    list_display = ["id", "risk_evaluation", "puntaje_a", "puntaje_b", "puntaje_c", "puntaje_final", "nivel_riesgo", "creado_en"]

    fieldsets = FactorRiesgoBaseAdmin.fieldsets + (
        ("Puntajes", {"fields": ("puntaje_a", "puntaje_b", "puntaje_c", "puntaje_final", "detalles_json")}),
    )


@admin.register(VibracionMB_Eval)
class VibracionMB_EvalAdmin(FactorRiesgoBaseAdmin):
    list_display = ["id", "risk_evaluation", "tipo_exposicion", "valor_final_mps2", "eje_dominante_final", "nivel_riesgo", "creado_en"]
    list_filter = FactorRiesgoBaseAdmin.list_filter + ["tipo_exposicion", "eje_dominante_final"]

    fieldsets = FactorRiesgoBaseAdmin.fieldsets + (
        (
            "Datos Vibración Mano-Brazo",
            {
                "fields": (
                    "tipo_exposicion",
                    "a_k_m_s2",
                    "ax_mps2",
                    "ay_mps2",
                    "az_mps2",
                    "duracion_h",
                    "exposiciones_json",
                    "eje_dominante_final",
                    "valor_final_mps2",
                )
            },
        ),
    )


@admin.register(VibracionCE_Eval)
class VibracionCE_EvalAdmin(FactorRiesgoBaseAdmin):
    list_display = ["id", "risk_evaluation", "metodo", "duracion_h", "nivel_riesgo", "creado_en"]

    fieldsets = FactorRiesgoBaseAdmin.fieldsets + (
        (
            "Datos Vibración Cuerpo Entero",
            {"fields": ("metodo", "duracion_h", "a_wx", "a_wy", "a_wz", "espectro_json", "factor_cresta_gt6")},
        ),
    )


@admin.register(ConfortTermico_Eval)
class ConfortTermico_EvalAdmin(FactorRiesgoBaseAdmin):
    list_display = ["id", "risk_evaluation", "temperatura_operativa_c", "humedad_relativa_pct", "nivel_riesgo", "creado_en"]

    fieldsets = FactorRiesgoBaseAdmin.fieldsets + (
        ("Datos Confort Térmico", {"fields": ("temperatura_operativa_c", "humedad_relativa_pct")}),
    )


@admin.register(EstresContacto_Eval)
class EstresContacto_EvalAdmin(FactorRiesgoBaseAdmin):
    list_display = ["id", "risk_evaluation", "segmento_afectado", "tipo_borde", "duracion_continua_min", "nivel_riesgo", "creado_en"]
    list_filter = FactorRiesgoBaseAdmin.list_filter + ["segmento_afectado", "tipo_borde", "frecuencia_exposicion", "mano_como_martillo", "mango_inadecuado", "postura_forzada_asociada"]
    search_fields = FactorRiesgoBaseAdmin.search_fields + ["objeto_superficie"]

    fieldsets = FactorRiesgoBaseAdmin.fieldsets + (
        (
            "Datos Estrés de Contacto",
            {
                "fields": (
                    "segmento_afectado",
                    "objeto_superficie",
                    "tipo_borde",
                    "duracion_continua_min",
                    "frecuencia_exposicion",
                    "mano_como_martillo",
                    "mango_inadecuado",
                    "postura_forzada_asociada",
                    "sintomas_json",
                    "controles_existentes_json",
                )
            },
        ),
    )


# =============================================================================
# PERSONALIZACIÓN DEL SITIO ADMIN
# =============================================================================

admin.site.site_header = "ErgoApp SRT 886 - Administración"
admin.site.site_title = "ErgoApp Admin"
admin.site.index_title = "Panel de Administración de Evaluaciones Ergonómicas"

