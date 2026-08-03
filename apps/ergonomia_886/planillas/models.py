# planillas/models.py

from django.conf import settings
from django.db import models
from django.utils import timezone # Importamos timezone para los valores por defecto de fechas

class Evaluacion(models.Model):
    """Raíz del dominio del Protocolo de Ergonomía SRT 886/15."""

    # Vinculación operativa.
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="evaluaciones_ergonomicas",
        verbose_name="Profesional responsable",
    )
    empresa = models.ForeignKey(
        "company.CompanyProfile",
        on_delete=models.PROTECT,
        related_name="evaluaciones_ergonomicas",
        null=True,
        blank=True,
        verbose_name="Empresa evaluada",
        help_text=(
            "Empresa registrada en la plataforma. Al seleccionarla se copian "
            "sus datos a los campos del documento, que quedan editables. "
            "Dejar vacío si la empresa no es usuaria de la plataforma."
        ),
    )

    # Respaldo histórico del documento emitido. Se puebla una sola vez al
    # crear y nunca se resincroniza: la exportación siempre lee estos campos.
    razon_social = models.CharField(max_length=300)
    cuit = models.CharField(max_length=20)
    ciiu = models.CharField(max_length=10, blank=True, null=True, verbose_name="CIIU")
    direccion_establecimiento = models.CharField(max_length=400)
    provincia = models.CharField(max_length=100)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_modificacion = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Evaluación ergonómica"
        verbose_name_plural = "Evaluaciones ergonómicas"
        indexes = [
            models.Index(
                fields=["usuario", "-fecha_modificacion"],
                name="idx_eval_usuario_fmod",
            ),
            models.Index(
                fields=["empresa", "-fecha_modificacion"],
                name="idx_eval_empresa_fmod",
            ),
            models.Index(fields=["cuit"], name="idx_eval_cuit"),
        ]

    def __str__(self):
        return f"Evaluación para {self.razon_social} - {self.fecha_creacion.strftime('%d/%m/%Y')}"

# Modelo para la Planilla 1
class Planilla1(models.Model):
    evaluacion = models.OneToOneField(Evaluacion, on_delete=models.CASCADE, primary_key=True)
    trabajadores = models.ManyToManyField(
        "company.CompanyWorker",
        blank=True,
        related_name="planillas_ergonomicas",
        verbose_name="Trabajadores relevados",
        help_text=(
            "Trabajadores de la nómina alcanzados por este relevamiento. "
            "La selección se copia al respaldo histórico sólo si éste está vacío."
        ),
    )
    area_sector = models.CharField(max_length=200, verbose_name="Área y Sector en estudio", blank=True, default='')
    puesto_trabajo = models.CharField(max_length=200, verbose_name="Puesto de trabajo", blank=True, default='')
    nro_trabajadores = models.PositiveIntegerField(verbose_name="Nº de trabajadores", default=0)
    procedimiento_escrito = models.BooleanField(default=False, verbose_name="Procedimiento de trabajo escrito")
    capacitacion = models.BooleanField(default=False, verbose_name="Capacitación")
    # CF-5: respaldo histórico y única fuente de los documentos oficiales. Una
    # modificación posterior de la nómina nunca cambia un protocolo emitido.
    nombres_trabajadores = models.TextField(blank=True, verbose_name="Nombre del trabajador/es")
    manifestacion_temprana = models.BooleanField(default=False, verbose_name="Manifestación temprana")
    ubicacion_sintoma = models.CharField(max_length=255, blank=True, verbose_name="Ubicación del síntoma")
    tarea_1 = models.TextField(blank=True, verbose_name="Tarea habitual 1")
    tarea_2 = models.TextField(blank=True, verbose_name="Tarea habitual 2")
    tarea_3 = models.TextField(blank=True, verbose_name="Tarea habitual 3")
    
    def __str__(self):
        return f"Planilla 1 para {self.evaluacion.razon_social}"

# Modelo para representar cada fila de la matriz de factores de riesgo de la Planilla 1
class FactorRiesgo(models.Model):
    planilla1 = models.ForeignKey(Planilla1, on_delete=models.CASCADE, related_name='factores_riesgo')
    TIPO_FACTOR_CHOICES = [
        ('A', 'Levantamiento y descenso'), ('B', 'Empuje / arrastre'), ('C', 'Transporte'),
        ('D', 'Bipedestación'), ('E', 'Movimientos repetitivos'), ('F', 'Postura forzada'),
        ('G', 'Vibraciones'), ('H', 'Confort térmico'), ('I', 'Estrés de contacto'),
    ]
    NIVEL_RIESGO_CHOICES = [ (1, 'Nivel 1: Tolerable'), (2, 'Nivel 2: Moderado'), (3, 'Nivel 3: No Tolerable'),]
    tipo_factor = models.CharField(max_length=1, choices=TIPO_FACTOR_CHOICES)
    presente = models.BooleanField(default=False, verbose_name="Factor Presente") 
    tiempo_exposicion = models.CharField(max_length=50, blank=True, verbose_name="Tiempo total de exposición")
    riesgo_tarea1 = models.IntegerField(choices=NIVEL_RIESGO_CHOICES, null=True, blank=True, verbose_name="Riesgo Tarea 1")
    riesgo_tarea2 = models.IntegerField(choices=NIVEL_RIESGO_CHOICES, null=True, blank=True, verbose_name="Riesgo Tarea 2")
    riesgo_tarea3 = models.IntegerField(choices=NIVEL_RIESGO_CHOICES, null=True, blank=True, verbose_name="Riesgo Tarea 3")
    class Meta:
        unique_together = ('planilla1', 'tipo_factor')
    def __str__(self):
        return f"Factor {self.get_tipo_factor_display()} para {self.planilla1.evaluacion.razon_social}"

# --- SECCIÓN CORREGIDA Y COMPLETADA ---

class Planilla2A(models.Model):
    evaluacion = models.ForeignKey(Evaluacion, on_delete=models.CASCADE, related_name='planillas2a')
    tarea_nro = models.CharField(max_length=50, verbose_name="Tarea N°", default="", blank=True)
    p1_levanta_2_a_25kg = models.BooleanField(default=False, verbose_name="Levantar y/o bajar manualmente cargas de peso superior a 2 Kg. y hasta 25 Kg.")
    p1_ciclico_diario = models.BooleanField(default=False, verbose_name="Realizar diariamente y en forma cíclica operaciones de levantamiento / descenso")
    p1_levanta_mas_25kg = models.BooleanField(default=False, verbose_name="Levantar y/o bajar manualmente cargas de peso superior a 25 Kg")
    p2_sobrepasa_hombro_30cm = models.BooleanField(default=False, verbose_name="El trabajador levanta, sostiene y deposita la carga sobrepasando con sus manos 30 cm. sobre la altura del hombro")
    p2_distancia_horizontal_80cm = models.BooleanField(default=False, verbose_name="El trabajador levanta, sostiene y deposita la carga sobrepasando con sus manos una distancia horizontal mayor de 80 cm.")
    p2_gira_inclina_cintura = models.BooleanField(default=False, verbose_name="Entre la toma y el depósito de la carga, el trabajador gira o inclina la cintura más de 30°")
    p2_cargas_irregulares = models.BooleanField(default=False, verbose_name="Las cargas poseen formas irregulares, son difíciles de asir, se deforman o hay movimiento en su interior")
    p2_levanta_un_solo_brazo = models.BooleanField(default=False, verbose_name="El trabajador levanta, sostiene y deposita la carga con un solo brazo")
    p2_presenta_manifestacion_temprana = models.BooleanField(default=False, verbose_name="El trabajador presenta alguna manifestación temprana de las enfermedades mencionadas")
    def __str__(self):
        return f"Planilla 2A para {self.evaluacion.razon_social} - Tarea {self.tarea_nro}"

class Planilla2B(models.Model):
    evaluacion = models.ForeignKey(Evaluacion, on_delete=models.CASCADE, related_name='planillas2b')
    tarea_nro = models.CharField(max_length=50, verbose_name="Tarea N°", default="", blank=True)
    p1_tareas_ciclicas_diarias = models.BooleanField(default=False, verbose_name="Se realizan diariamente tareas cíclicas, con una frecuencia ≥ 1 movimiento por jornada")
    p1_desplaza_mas_de_60m = models.BooleanField(default=False, verbose_name="El trabajador se desplaza empujando y/o arrastrando manualmente un objeto recorriendo una distancia mayor a los 60 metros")
    p1_esfuerzo_supera_34kgf = models.BooleanField(default=False, verbose_name="En el puesto de trabajo se empujan o arrastran cíclicamente objetos (...) cuyo esfuerzo medido con dinamómetro supera los 34 kgf")
    p2_empuje_inicial_mayor_12kgf_h_10kgf_m = models.BooleanField(default=False, verbose_name="Para empujar el objeto rodante se requiere un esfuerzo inicial medido con dinamómetro ≥ 12 Kgf para hombres o 10 Kgf para mujeres")
    p2_arrastre_inicial_mayor_10kgf = models.BooleanField(default=False, verbose_name="Para arrastrar el objeto rodante se requiere un esfuerzo inicial medido con dinamómetro ≥ 10 Kgf para hombres o mujeres")
    p2_empuje_con_dificultad = models.BooleanField(default=False, verbose_name="El objeto rodante es empujado y/o arrastrado con dificultad (superficie despareja, rampas, etc.)")
    p2_no_se_puede_ambas_manos = models.BooleanField(default=False, verbose_name="El objeto rodante no puede ser empujado y/o arrastrado con ambas manos, o altura incómoda")
    p2_esfuerzo_se_mantiene = models.BooleanField(default=False, verbose_name="El esfuerzo inicial requerido se mantiene significativamente una vez puesto en movimiento (atascamiento, tirones, etc.)")
    p2_empuja_con_una_mano = models.BooleanField(default=False, verbose_name="El trabajador empuja o arrastra el objeto rodante asiéndolo con una sola mano")
    p2_presenta_manifestacion_temprana = models.BooleanField(default=False, verbose_name="El trabajador presenta alguna manifestación temprana de las enfermedades")
    def __str__(self):
        return f"Planilla 2B para {self.evaluacion.razon_social} - Tarea {self.tarea_nro}"

class Planilla2C(models.Model):
    evaluacion = models.ForeignKey(Evaluacion, on_delete=models.CASCADE, related_name='planillas2c')
    tarea_nro = models.CharField(max_length=50, verbose_name="Tarea N°", default="", blank=True)
    p1_transporta_2_a_25kg = models.BooleanField(default=False, verbose_name="Transportar manualmente cargas de peso superior a 2 Kg y hasta 25 Kg")
    p1_desplaza_mas_de_1m = models.BooleanField(default=False, verbose_name="El trabajador se desplaza sosteniendo manualmente la carga recorriendo una distancia mayor a 1 metro")
    p1_realiza_diariamente_ciclica = models.BooleanField(default=False, verbose_name="Realizarla diariamente en forma cíclica")
    p1_transporta_mas_de_20m = models.BooleanField(default=False, verbose_name="Se transporta manualmente cargas a una distancia superior a 20 metros")
    p1_transporta_mas_de_25kg = models.BooleanField(default=False, verbose_name="Se transporta manualmente cargas de peso superior a 25 Kg")
    p2_masa_acumulada_1_10_m_mayor_10000kg = models.BooleanField(default=False, verbose_name="Transporta la carga entre 1 y 10 metros con una masa acumulada > 10.000 Kg")
    p2_masa_acumulada_10_20_m_mayor_6000kg = models.BooleanField(default=False, verbose_name="Transporta la carga entre 10 y 20 metros con una masa acumulada > 6.000 Kg")
    p2_cargas_irregulares = models.BooleanField(default=False, verbose_name="Las cargas poseen formas irregulares, son difíciles de asir, se deforman o hay movimiento")
    p2_presenta_manifestacion_temprana = models.BooleanField(default=False, verbose_name="El trabajador presenta alguna manifestación temprana de las enfermedades")
    def __str__(self):
        return f"Planilla 2C para {self.evaluacion.razon_social} - Tarea {self.tarea_nro}"

class Planilla2D(models.Model):
    evaluacion = models.ForeignKey(Evaluacion, on_delete=models.CASCADE, related_name='planillas2d')
    tarea_nro = models.CharField(max_length=50, verbose_name="Tarea N°", default="", blank=True)
    p1_de_pie_sin_sentarse_mas_2h = models.BooleanField(default=False, verbose_name="El puesto de trabajo se desarrolla en posición de pie, sin posibilidad de sentarse, durante 2 horas seguidas o más")
    p2_de_pie_mas_3h_escasa_deambulacion = models.BooleanField(default=False, verbose_name="Permanece de pie durante 3 horas seguidas o más, sin posibilidades de sentarse con escasa deambulación")
    p2_de_pie_mas_2h_transportando_mas_2kg = models.BooleanField(default=False, verbose_name="Permanece de pie durante 2 horas seguidas o más, levantando y/o transportando cargas > 2 Kg")
    p2_bipedestacion_limites_termicos = models.BooleanField(default=False, verbose_name="Trabajos efectuados con bipedestación prolongada en ambientes donde la temperatura y humedad sobrepasan los límites")
    p2_presenta_manifestacion_temprana = models.BooleanField(default=False, verbose_name="El trabajador presenta alguna manifestación temprana de las enfermedades")
    def __str__(self):
        return f"Planilla 2D para {self.evaluacion.razon_social} - Tarea {self.tarea_nro}"

class Planilla2E(models.Model):
    evaluacion = models.ForeignKey(Evaluacion, on_delete=models.CASCADE, related_name='planillas2e')
    tarea_nro = models.CharField(max_length=50, verbose_name="Tarea N°", default="", blank=True)
    p1_extremidades_superiores_mas_4h = models.BooleanField(default=False, verbose_name="Realizar diariamente, una o más tareas donde se utilizan las extremedidas superiores, durante 4 o más horas en forma ciclica")
    p2_activas_mas_40_porciento = models.BooleanField(default=False, verbose_name="Las extremidades superiores están activas por más del 40% del tiempo total del ciclo de trabajo")
    p2_esfuerzo_borg_mayor_3 = models.BooleanField(default=False, verbose_name="Se realiza un esfuerzo superior a moderado a 3 según la Escala de Borg, durante más de 6 segundos y más de una vez por minuto")
    p2_esfuerzo_borg_mayor_7 = models.BooleanField(default=False, verbose_name="Se realiza un esfuerzo superior a 7 según la escala de Borg")
    p2_presenta_manifestacion_temprana = models.BooleanField(default=False, verbose_name="El trabajador presenta alguna manifestación temprana de las enfermedades")
    def __str__(self):
        return f"Planilla 2E para {self.evaluacion.razon_social} - Tarea {self.tarea_nro}"

class Planilla2F(models.Model):
    evaluacion = models.ForeignKey(Evaluacion, on_delete=models.CASCADE, related_name='planillas2f')
    tarea_nro = models.CharField(max_length=50, verbose_name="Tarea N°", default="", blank=True)
    p1_adopta_posturas_forzadas = models.BooleanField(default=False, verbose_name="Adoptar posturas forzadas en forma habitual durante la jornada de trabajo")
    p2_cuello = models.BooleanField(default=False, verbose_name="Cuello en extensión, flexión, lateralización y/o rotación")
    p2_brazos = models.BooleanField(default=False, verbose_name="Brazos por encima de los hombros o con movimientos de supinación, pronación o rotación")
    p2_munecas = models.BooleanField(default=False, verbose_name="Muñecas y manos en flexión, extensión, desviación cubital o radial")
    p2_cintura = models.BooleanField(default=False, verbose_name="Cintura en flexión, extensión, lateralización y/o rotación")
    p2_miembros_inferiores = models.BooleanField(default=False, verbose_name="Miembros inferiores: trabajo en posición de rodillas o en cuclillas")
    p2_presenta_manifestacion_temprana = models.BooleanField(default=False, verbose_name="El trabajador presenta alguna manifestación temprana de las enfermedades")
    def __str__(self):
        return f"Planilla 2F para {self.evaluacion.razon_social} - Tarea {self.tarea_nro}"

class Planilla2G(models.Model):
    evaluacion = models.ForeignKey(Evaluacion, on_delete=models.CASCADE, related_name='planillas2g')
    tarea_nro = models.CharField(max_length=50, verbose_name="Tarea N°", default="", blank=True)
    p1_mb_trabaja_con_herramientas = models.BooleanField(default=False, verbose_name="Mano-Brazo: Trabajar con herramientas que producen vibraciones")
    p1_mb_sujeta_piezas = models.BooleanField(default=False, verbose_name="Mano-Brazo: Sujetar piezas con las manos mientras estas son mecanizadas")
    p1_mb_sujeta_palancas = models.BooleanField(default=False, verbose_name="Mano-Brazo: Sujetar palancas, volantes, etc. que transmiten vibraciones")
    p2_mb_supera_limites = models.BooleanField(default=False, verbose_name="Mano-Brazo: El valor de las vibraciones supera los límites de la Tabla I MTEYSS N° 295/03")
    p2_mb_presenta_manifestacion_temprana = models.BooleanField(default=False, verbose_name="Mano-Brazo: El trabajador presenta alguna manifestación temprana")
    p1_ce_conduce_vehiculos = models.BooleanField(default=False, verbose_name="Cuerpo Entero: Conducir vehículos industriales, camiones, etc.")
    p1_ce_trabaja_prox_maquinas = models.BooleanField(default=False, verbose_name="Cuerpo Entero: Trabajar próximo a maquinarias generadoras de impacto")
    p2_ce_supera_limites = models.BooleanField(default=False, verbose_name="Cuerpo Entero: El valor de las vibraciones supera los límites de MTEYSS N° 295/03")
    p2_ce_presenta_manifestacion_temprana = models.BooleanField(default=False, verbose_name="Cuerpo Entero: El trabajador presenta alguna manifestación temprana")
    def __str__(self):
        return f"Planilla 2G para {self.evaluacion.razon_social} - Tarea {self.tarea_nro}"

class Planilla2H(models.Model):
    evaluacion = models.ForeignKey(Evaluacion, on_delete=models.CASCADE, related_name='planillas2h')
    tarea_nro = models.CharField(max_length=50, verbose_name="Tarea N°", default="", blank=True)
    p1_percibe_temp_no_confortables = models.BooleanField(default=False, verbose_name="En el puesto de trabajo se perciben temperaturas no confortables")
    p2_curva_fanger_fuera_de_zona = models.BooleanField(default=False, verbose_name="El resultado del uso de la Curva de Confort de Fanger se encuentra por fuera de la zona de confort")
    def __str__(self):
        return f"Planilla 2H para {self.evaluacion.razon_social} - Tarea {self.tarea_nro}"

class Planilla2I(models.Model):
    evaluacion = models.ForeignKey(Evaluacion, on_delete=models.CASCADE, related_name='planillas2i')
    tarea_nro = models.CharField(max_length=50, verbose_name="Tarea N°", default="", blank=True)
    p1_mantiene_apoyada_parte_cuerpo = models.BooleanField(default=False, verbose_name="Mantiene apoyada alguna parte del cuerpo ejerciendo presión contra una herramienta, etc.")
    p2_apoya_sobre_superficie_aguda = models.BooleanField(default=False, verbose_name="El trabajador mantiene apoyada la muñeca, antebrazo, etc. sobre una superficie aguda o con canto")
    p2_utiliza_herramientas_presionan = models.BooleanField(default=False, verbose_name="El trabajador utiliza herramientas que presionan sobre sus dedos y/o palma de la mano hábil")
    p2_movimientos_percusion = models.BooleanField(default=False, verbose_name="El trabajador realiza movimientos de percusión sobre partes o herramientas")
    p2_presenta_manifestacion_temprana = models.BooleanField(default=False, verbose_name="El trabajador presenta alguna manifestación temprana de las enfermedades")
    def __str__(self):
        return f"Planilla 2I para {self.evaluacion.razon_social} - Tarea {self.tarea_nro}"


class Planilla3(models.Model):
    evaluacion = models.OneToOneField(Evaluacion, on_delete=models.CASCADE, primary_key=True)
    
    # Nuevos campos para autocompletar en la plantilla
    tarea_analizada = models.CharField(max_length=255, blank=True)
    
    # Medidas Preventivas Generales (usaremos YesNoChoiceField en el formulario)
    general_informado_riesgo = models.BooleanField(default=False)
    fecha_informado_riesgo = models.DateField(null=True, blank=True)
    general_capacitado_sintomas = models.BooleanField(default=False)
    fecha_capacitado_sintomas = models.DateField(null=True, blank=True)
    general_capacitado_medidas = models.BooleanField(default=False)
    fecha_capacitado_medidas = models.DateField(null=True, blank=True)
    observaciones_generales = models.TextField(blank=True, verbose_name="Observaciones Generales")

    def __str__(self):
        return f"Planilla 3 para {self.evaluacion.razon_social}"

class MedidaEspecifica(models.Model):
    planilla3 = models.ForeignKey(Planilla3, on_delete=models.CASCADE, related_name='medidas')
    # El número lo generaremos en la plantilla, no es necesario guardarlo aquí.
    descripcion = models.TextField(verbose_name="Descripción de la Medida")
    observaciones = models.TextField(blank=True, verbose_name="Observaciones")
    
    def __str__(self):
        return self.descripcion[:50]

# El modelo de Seguimiento ahora se relaciona con una Medida Específica
class SeguimientoMedida(models.Model):
    # La relación clave: cada seguimiento pertenece a UNA medida.
    medida_especifica = models.OneToOneField(MedidaEspecifica, on_delete=models.CASCADE, related_name='seguimiento')
    
    # Estos campos se pueden autocompletar o dejar que el usuario los llene.
    # Los definimos en el modelo para guardar los datos.
    nombre_puesto = models.CharField(max_length=200, blank=True)
    fecha_evaluacion = models.DateField(null=True, blank=True)
    nivel_riesgo = models.IntegerField(choices=FactorRiesgo.NIVEL_RIESGO_CHOICES, null=True, blank=True)
    
    # Campos que el usuario llenará en la Planilla 4
    fecha_impl_admin = models.DateField(null=True, blank=True, verbose_name="Fecha Implementación Medida Administrativa")
    fecha_impl_ing = models.DateField(null=True, blank=True, verbose_name="Fecha Implementación Medida de Ingeniería")
    fecha_cierre = models.DateField(null=True, blank=True, verbose_name="Fecha de Cierre")

    def __str__(self):
        return f"Seguimiento para medida: {self.medida_especifica.descripcion[:30]}"
