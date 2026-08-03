# evaluaciones/forms.py

from __future__ import annotations

import json
import math
from typing import Any, Dict, List

from django import forms
from django.core.exceptions import ValidationError

from django.forms import inlineformset_factory


from . import calculators as calc

from .choices import (
    VAltura, HDist,
    Poblacion, AlturaAgarreCM, DistanciaLinealM,
    FrecuenciaMovimiento,
    NAM_CHOICES, FPN_BORG_CHOICES,
)
from .models import (
    RiskEvaluation, BaseFactorEvaluation,
    LMC_Eval, EmpujeInicial_Eval, EmpujeSostenida_Eval,
    TraccionInicial_Eval, TraccionSostenida_Eval,
    Transporte_Eval,
    Bipedestacion_Eval, RepetitivosMS_Eval, PosturasForzadas_Eval,
    VibracionMB_Eval, VibracionCE_Eval, VCESegment,
    ConfortTermico_Eval, EstresContacto_Eval,
)

# ============================================================================
#                               HELPERS
# ============================================================================

def _is_nonempty_dict(d: Any) -> bool:
    return isinstance(d, dict) and bool(d)

def _merge_calc_input(instance: BaseFactorEvaluation, payload: Dict[str, Any]) -> None:
    """
    Mezcla dicts en instance.calc_data["input"] sin pisar otras claves de trazabilidad.
    """
    if not payload:
        return
    cd = dict(getattr(instance, "calc_data", {}) or {})
    base = dict(cd.get("input", {}) or {})
    base.update(payload)
    cd["input"] = base
    instance.calc_data = cd

def _json_loads_safe(text: str) -> Any:
    try:
        return json.loads(text)
    except Exception as e:
        raise ValidationError(f"JSON inválido: {e}")

def _add_bootstrap(widget: forms.Widget, css: str = "form-control") -> forms.Widget:
    # Aplica clases Bootstrap salvo a checkboxes/radios/hidden.
    if isinstance(widget, (forms.CheckboxInput, forms.RadioSelect, forms.CheckboxSelectMultiple, forms.HiddenInput)):
        return widget
    widget.attrs["class"] = (widget.attrs.get("class", "") + f" {css}").strip()
    return widget

class JSONTextarea(forms.JSONField):
    """
    Field JSON con Textarea simple (sin dependencias), ideal para inputs complejos.
    Úsalo como Field de la form, NO como widget en Meta.widgets.
    """
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("required", False)
        kwargs.setdefault("widget", forms.Textarea(attrs={"rows": 6, "class": "form-control font-monospace"}))
        super().__init__(*args, **kwargs)

# ============================================================================
#                           BASE FORM (común)
# ============================================================================

class BaseFactorForm(forms.ModelForm):
    """
    - Mantiene un campo interno `input_json` por compatibilidad con integraciones
      controladas, pero no lo expone en los formularios públicos.
    - Provee `save_and_calculate()` para guardar y ejecutar el motor.
    """
    input_json = JSONTextarea(
        label="Payload JSON opcional",
        help_text=(
            "Opcional. Estructura libre para completar parámetros avanzados que "
            "la calculadora toma desde calc_data['input']. Útil p/ banderas o "
            "subcampos que no estén modelados como fields."
        ),
        required=False,
    )

    class Meta:
        model = BaseFactorEvaluation
        fields: List[str] = []  # las hijas definen sus campos

    def __init__(self, *args, **kwargs):
        allow_advanced_input = kwargs.pop("allow_advanced_input", False)
        super().__init__(*args, **kwargs)
        if not allow_advanced_input:
            self.fields.pop("input_json", None)

    def clean_input_json(self):
        data = self.cleaned_data.get("input_json")
        # JSONField ya parsea a dict/list; si viene str lo parseamos.
        if isinstance(data, str) and data.strip():
            return _json_loads_safe(data)
        return data or {}

    def _post_clean_merge_input(self, instance: BaseFactorEvaluation):
        payload = self.cleaned_data.get("input_json") or {}
        if _is_nonempty_dict(payload):
            _merge_calc_input(instance, payload)

    def _calculation_requested(self) -> bool:
        return self.is_bound and self.data.get("action") == "save_and_calc"

    def _require_for_calculation(
        self,
        cleaned: Dict[str, Any],
        fields: List[str],
    ) -> None:
        """
        Permite guardar borradores incompletos, pero no calcularlos.
        Las calculadoras repiten estas defensas para cubrir datos históricos,
        llamadas directas y cualquier flujo que no pase por el ModelForm.
        """
        if not self._calculation_requested() or not cleaned.get("aplicable", True):
            return
        for field in fields:
            value = cleaned.get(field)
            if value is None or (isinstance(value, str) and not value.strip()):
                self.add_error(field, "Completá este campo antes de calcular.")

    def _invalidate_calculation(self, instance: BaseFactorEvaluation) -> None:
        previous = dict(getattr(instance, "calc_data", {}) or {})
        previous_input = dict(previous.get("input", {}) or {})
        was_calculated = (
            previous.get("estado_resultado") in {"calculado", "desactualizado"}
            or getattr(instance, "nivel_riesgo", "no_aplicable") != "no_aplicable"
        )
        instance.nivel_riesgo = "no_aplicable"
        instance.calc_data = {
            "input": previous_input,
            "estado_resultado": "desactualizado" if was_calculated else "borrador",
        }

    def save(self, commit=True):
        instance = super().save(commit=False)
        self._invalidate_calculation(instance)
        self._post_clean_merge_input(instance)
        if commit:
            instance.save()
        return instance

    def save_and_calculate(self, commit=True) -> BaseFactorEvaluation:
        """
        Guarda y ejecuta la calculadora registrada para FACTOR_SLUG.
        """
        instance = self.save(commit=commit)
        # Ejecuta el motor y persiste la trazabilidad con apply_result
        res = calc.run_for_instance(instance)
        calc.apply_result(instance, res)
        return instance

# ============================================================================
#                               LMC
# ============================================================================

class LMCForm(BaseFactorForm):
    class Meta:
        model = LMC_Eval
        fields = [
            "risk_evaluation",
            "peso_kg", "duracion_h", "frecuencia_h",
            "v_altura", "h_dist",
            "giro_mayor_30", "una_mano", "postura_agachada",
            "carga_inestable", "entorno_adverso", "turnos_largos",
            "aplicable", "observaciones",
        ]
        widgets = {
            "risk_evaluation": forms.HiddenInput(),
            "peso_kg": _add_bootstrap(forms.NumberInput(attrs={"step": "0.01", "min": "0"})),
            "duracion_h": _add_bootstrap(forms.NumberInput(attrs={"step": "0.25", "min": "0"})),
            "frecuencia_h": _add_bootstrap(forms.NumberInput(attrs={"step": "1", "min": "0"})),
            "v_altura": _add_bootstrap(forms.Select(choices=VAltura.choices)),
            "h_dist": _add_bootstrap(forms.Select(choices=HDist.choices)),
            "observaciones": _add_bootstrap(forms.Textarea(attrs={"rows": 3})),
        }

    def clean(self):
        cleaned = super().clean()
        self._require_for_calculation(
            cleaned,
            ["peso_kg", "duracion_h", "frecuencia_h", "v_altura", "h_dist"],
        )
        return cleaned

# ============================================================================
#                           EMPUJE / TRACCIÓN
# ============================================================================

class _CommonEmpujeTraccion(BaseFactorForm):
    FORCE_TABLE_FILES = {
        "empuje_inicial": "empuje_inicial.json",
        "empuje_sostenida": "empuje_sostenida.json",
        "traccion_inicial": "traccion_inicial.json",
        "traccion_sostenida": "traccion_sostenida.json",
    }
    SCOPE_FIELDS = (
        "alcance_una_persona",
        "alcance_de_pie",
        "alcance_ambas_manos",
        "alcance_objeto_frente",
    )

    alcance_una_persona = forms.BooleanField(
        required=False,
        label="La acción la realiza una sola persona",
    )
    alcance_de_pie = forms.BooleanField(
        required=False,
        label="La persona trabaja de pie",
    )
    alcance_ambas_manos = forms.BooleanField(
        required=False,
        label="La fuerza se aplica con ambas manos",
    )
    alcance_objeto_frente = forms.BooleanField(
        required=False,
        label="El objeto se encuentra frente a la persona",
    )

    class Meta:
        fields = [
            "risk_evaluation",
            "poblacion", "altura_agarre_cm", "distancia_m",
            "frecuencia_opcion", "fuerza_n",
            "aplicable", "observaciones",
        ]
        widgets = {
            "risk_evaluation": forms.HiddenInput(),
            "poblacion": _add_bootstrap(forms.Select(choices=Poblacion.choices)),
            "altura_agarre_cm": _add_bootstrap(forms.Select(choices=AlturaAgarreCM.choices)),
            "distancia_m": _add_bootstrap(forms.Select(choices=DistanciaLinealM.choices)),
            "frecuencia_opcion": _add_bootstrap(forms.Select(choices=FrecuenciaMovimiento.choices)),
            "fuerza_n": _add_bootstrap(forms.NumberInput(attrs={"step": "0.1", "min": "0"})),
            "observaciones": _add_bootstrap(forms.Textarea(attrs={"rows": 3})),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        slug = str(self.Meta.model.FACTOR_SLUG)
        config = calc.load_json(self.FORCE_TABLE_FILES[slug])
        valid_by_distance = {
            distance: list(frequencies)
            for distance, frequencies in config.get("limites_N", {}).items()
        }
        self.fields["frecuencia_opcion"].widget.attrs[
            "data-valid-by-distance"
        ] = json.dumps(valid_by_distance, separators=(",", ":"))

        if self.instance and self.instance.pk:
            scope = (
                (self.instance.calc_data or {})
                .get("input", {})
                .get("alcance_metodo", {})
            )
            for field in self.SCOPE_FIELDS:
                self.fields[field].initial = scope.get(field, False)

    def clean(self):
        cleaned = super().clean()
        self._require_for_calculation(
            cleaned,
            [
                "poblacion",
                "altura_agarre_cm",
                "distancia_m",
                "frecuencia_opcion",
                "fuerza_n",
            ],
        )

        distance = cleaned.get("distancia_m")
        frequency = cleaned.get("frecuencia_opcion")
        if distance is not None and frequency:
            slug = str(self.Meta.model.FACTOR_SLUG)
            config = calc.load_json(self.FORCE_TABLE_FILES[slug])
            valid = list(
                config.get("limites_N", {})
                .get(str(distance), {})
                .keys()
            )
            if frequency not in valid:
                labels = dict(FrecuenciaMovimiento.choices)
                valid_labels = ", ".join(labels.get(item, item) for item in valid)
                self.add_error(
                    "frecuencia_opcion",
                    "La frecuencia no existe para la distancia seleccionada. "
                    f"Opciones válidas: {valid_labels}.",
                )

        if self._calculation_requested() and cleaned.get("aplicable", True):
            for field in self.SCOPE_FIELDS:
                if cleaned.get(field) is not True:
                    self.add_error(
                        field,
                        "Debe confirmar esta condición para aplicar la tabla.",
                    )
        return cleaned

    def save(self, commit=True):
        instance = super().save(commit=False)
        scope = {
            field: bool(self.cleaned_data.get(field))
            for field in self.SCOPE_FIELDS
        }
        _merge_calc_input(instance, {"alcance_metodo": scope})
        if commit:
            instance.save()
        return instance

class EmpujeInicialForm(_CommonEmpujeTraccion):
    class Meta(_CommonEmpujeTraccion.Meta):
        model = EmpujeInicial_Eval

class EmpujeSostenidaForm(_CommonEmpujeTraccion):
    class Meta(_CommonEmpujeTraccion.Meta):
        model = EmpujeSostenida_Eval

class TraccionInicialForm(_CommonEmpujeTraccion):
    class Meta(_CommonEmpujeTraccion.Meta):
        model = TraccionInicial_Eval

class TraccionSostenidaForm(_CommonEmpujeTraccion):
    class Meta(_CommonEmpujeTraccion.Meta):
        model = TraccionSostenida_Eval

# ============================================================================
#                              TRANSPORTE
# ============================================================================


class TransporteForm(BaseFactorForm):
    class Meta:
        model = Transporte_Eval
        fields = [
            "risk_evaluation",
            # --- Sección 2: condiciones de aplicabilidad ---
            "en_plano_horizontal", "jornada_8h", "velocidad_05a1_ms", "superficie_plana",
            # --- Sección 3: datos de cálculo ---
            "masa_kg", "distancia_m", "frecuencia_max_minuto",
            "frecuencia_max_hora", "frecuencia_jornada",
            "aplicable", "observaciones",
        ]
        widgets = {
            "risk_evaluation": forms.HiddenInput(),

            # Sección 2 (checkboxes)
            "en_plano_horizontal": _add_bootstrap(forms.CheckboxInput()),
            "jornada_8h": _add_bootstrap(forms.CheckboxInput()),
            "velocidad_05a1_ms": _add_bootstrap(forms.CheckboxInput()),
            "superficie_plana": _add_bootstrap(forms.CheckboxInput()),

            # Sección 3 (datos)
            "masa_kg": _add_bootstrap(forms.NumberInput(attrs={"step": "0.01", "min": "0"})),
            # Cambiamos a step=0.1 para permitir 12,5 m
            "distancia_m": _add_bootstrap(forms.NumberInput(attrs={"step": "0.1", "min": "1"})),
            "frecuencia_max_minuto": _add_bootstrap(forms.NumberInput(attrs={"step": "1", "min": "1"})),
            "frecuencia_max_hora": _add_bootstrap(forms.NumberInput(attrs={"step": "1", "min": "1"})),
            "frecuencia_jornada": _add_bootstrap(forms.NumberInput(attrs={"step": "1", "min": "1"})),

            "observaciones": _add_bootstrap(forms.Textarea(attrs={"rows": 3})),
        }

    # Validación server-side (sin impedir “No”; sólo exigimos que se responda Sí/No)
    def clean(self):
        cleaned = super().clean()
        m = cleaned.get("masa_kg")
        d = cleaned.get("distancia_m")
        f_min = cleaned.get("frecuencia_max_minuto")
        f_h = cleaned.get("frecuencia_max_hora")
        f = cleaned.get("frecuencia_jornada")

        # obligamos a responder los 4 checkboxes (pueden ser True o False)
        must_answer = {
            "en_plano_horizontal": "Indicá si la tarea es en plano horizontal.",
            "jornada_8h": "Indicá si la jornada considerada es de 8 horas.",
            "velocidad_05a1_ms": "Indicá si la velocidad es 0,5–1,0 m/s.",
            "superficie_plana": "Indicá si la superficie es plana.",
        }
        errors = {}
        for field, msg in must_answer.items():
            if cleaned.get(field) is None:
                errors[field] = msg

        # Reglas mínimas de datos (el cálculo igual revalida y puede devolver No aplicable)
        if m is not None and float(m) < 2.0:
            errors["masa_kg"] = "Según Res. 3345/15, el peso mínimo evaluable es 2,00 kg."
        if d is not None and float(d) < 1.0:
            errors["distancia_m"] = "La distancia por viaje debe ser ≥ 1,0 m."
        if f is not None and int(f) <= 0:
            errors["frecuencia_jornada"] = "La frecuencia debe ser un entero positivo."
        if f_min is not None and int(f_min) <= 0:
            errors["frecuencia_max_minuto"] = "Ingresá al menos un traslado en el minuto de mayor exposición."
        if f_h is not None and int(f_h) <= 0:
            errors["frecuencia_max_hora"] = "Ingresá al menos un traslado en la hora de mayor exposición."
        if f_min is not None and f_h is not None and int(f_h) < int(f_min):
            errors["frecuencia_max_hora"] = "El máximo horario no puede ser menor que el máximo observado en un minuto."
        if f_h is not None and f is not None and int(f) < int(f_h):
            errors["frecuencia_jornada"] = "El total de la jornada no puede ser menor que el máximo observado en una hora."

        if self._calculation_requested() and cleaned.get("aplicable", True):
            for field in (
                "masa_kg",
                "distancia_m",
                "frecuencia_max_minuto",
                "frecuencia_max_hora",
                "frecuencia_jornada",
            ):
                if cleaned.get(field) is None:
                    errors[field] = "Completá este campo antes de calcular."
            for field in must_answer:
                if cleaned.get(field) is None:
                    errors[field] = must_answer[field]

        if errors:
            raise forms.ValidationError(errors)
        return cleaned

# ============================================================================
#                           BIPEDESTACIÓN
# ============================================================================


BIPE_CONTROLES_CHOICES = [
    ("alfombra", "Alfombra antifatiga"),
    ("banqueta", "Banqueta/alternar sedente"),
    ("footrest", "Apoyo pie (footrest)"),
    ("rotacion", "Rotación/micropausas"),
]

class BipedestacionForm(BaseFactorForm):
    """
    - `controles_existentes` se persisten en controles_existentes_json (list[str]).
    - Se mantienen `input_json` y `sintomas_json` por compatibilidad,
      pero ahora los agravantes principales también están modelados.
    """

    controles_existentes = forms.MultipleChoiceField(
        required=False,
        choices=BIPE_CONTROLES_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        label="Controles existentes",
        help_text="Se usan para atenuar agravantes (reglas en JSON).",
    )

    # ✅ Field (no widget)
    sintomas_json = JSONTextarea(
        label="Síntomas (JSON)",
        help_text='Ej.: ["dolor_lumbar","calambres"]',
        required=False,
    )

    class Meta:
        model = Bipedestacion_Eval
        fields = [
            "risk_evaluation",

            # Duración y movilidad
            "horas_de_pie_total",
            "tiempo_continuo_min",
            "movilidad_tipo",
            "movilidad_m_por_h",

            # Agravantes
            "manipula_cargas_mayores_2kg",
            "ambiente_caluroso",
            "piso_duro",
            "superficie_irregular",
            "piso_resbaladizo",
            "calzado_inadecuado",
            "tronco_inclinado",
            "brazos_elevados",
            "cuello_giro_inclin",

            # Síntomas
            "sintomas_json",
            "sintomas_frecuencia",

            # Base
            "aplicable",
            "observaciones",
        ]

        widgets = {
            "risk_evaluation": forms.HiddenInput(),

            "horas_de_pie_total": _add_bootstrap(
                forms.NumberInput(attrs={"step": "0.25", "min": "0"})
            ),
            "tiempo_continuo_min": _add_bootstrap(
                forms.NumberInput(attrs={"step": "1", "min": "0"})
            ),
            "movilidad_tipo": _add_bootstrap(
                forms.Select(
                    choices=[
                        ("", "---------"),
                        ("estatica", "Estática/Restringida"),
                        ("deambulacion", "Con deambulación"),
                    ]
                )
            ),
            "movilidad_m_por_h": _add_bootstrap(
                forms.NumberInput(attrs={"step": "1", "min": "0"})
            ),

            "sintomas_frecuencia": _add_bootstrap(
                forms.Select(choices=Bipedestacion_Eval.SINTOMAS_FRECUENCIA_CHOICES)
            ),

            # ⚠️ NO definir "sintomas_json" aquí
            "observaciones": _add_bootstrap(forms.Textarea(attrs={"rows": 3})),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.fields["controles_existentes"].initial = list(
                self.instance.controles_existentes_json or []
            )

    def clean(self):
        cleaned = super().clean()
        self._require_for_calculation(
            cleaned,
            ["horas_de_pie_total", "tiempo_continuo_min", "movilidad_tipo"],
        )
        if (
            self._calculation_requested()
            and cleaned.get("aplicable", True)
            and cleaned.get("movilidad_tipo") == "deambulacion"
            and cleaned.get("movilidad_m_por_h") is None
        ):
            self.add_error(
                "movilidad_m_por_h",
                "Indicá la distancia recorrida por hora antes de calcular.",
            )
        return cleaned

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.controles_existentes_json = list(
            self.cleaned_data.get("controles_existentes") or []
        )
        if commit:
            instance.save()
        return instance



# ======================================================================
# REPETITIVOS MIEMBROS SUPERIORES (NAM)
# ======================================================================

class RepetitivosMSForm(BaseFactorForm):
    # NAM: ahora también se elige por categorías del manual
    nam_x_valor = forms.TypedChoiceField(
        required=False,
        coerce=int,
        choices=NAM_CHOICES,
        label="Nam x valor (Eje X)",
        widget=_add_bootstrap(forms.Select()),
        help_text="Seleccione la categoría de nivel de actividad manual según el método NAM.",
    )

    # Borg/FPN: mantenemos tu lógica conservadora en UI
    borg_y_valor = forms.TypedChoiceField(
        required=False,
        coerce=int,
        choices=FPN_BORG_CHOICES,
        label="Borg pico (FPN)",
        widget=_add_bootstrap(forms.Select()),
        help_text="Seleccione la categoría de esfuerzo percibido. En rangos se toma el mayor valor.",
    )

    class Meta:
        model = RepetitivosMS_Eval
        fields = [
            "risk_evaluation",
            "monotarea", "horas_dia", "nam_x_valor", "borg_y_valor",
            "posturas_obligadas", "estres_contacto",
            "bajas_temperaturas", "vibraciones_mb",
            "aplicable", "observaciones",
        ]
        widgets = {
            "risk_evaluation": forms.HiddenInput(),
            "horas_dia": _add_bootstrap(
                forms.NumberInput(attrs={"step": "0.25", "min": "0"})
            ),
            # OJO: quitamos nam_x_valor y borg_y_valor de widgets
            # para no pisar los fields custom.
            "observaciones": _add_bootstrap(forms.Textarea(attrs={"rows": 3})),
        }

    def clean(self):
        cleaned = super().clean()
        horas = cleaned.get("horas_dia")
        method_applies = (
            cleaned.get("aplicable", True)
            and cleaned.get("monotarea")
            and horas is not None
            and horas >= 4
        )
        if method_applies:
            if cleaned.get("nam_x_valor") in (None, ""):
                self.add_error(
                    "nam_x_valor",
                    "Seleccione el nivel de actividad manual para calcular.",
                )
            if cleaned.get("borg_y_valor") in (None, ""):
                self.add_error(
                    "borg_y_valor",
                    "Seleccione el esfuerzo percibido FPN/Borg para calcular.",
                )
        return cleaned

# ============================================================================
#                              POSTURAS FORZADAS (REBA)
# ============================================================================

REBA_HELP = (
    "Estructura esperada en input_json → calc_data['input'] (ejemplo):\n"
    "{\n"
    "  \"cuello_base\": 1, \"cuello_torsion_inclin\": true,\n"
    "  \"piernas_base\": 1, \"piernas_flex_30_60\": false, \"piernas_sedente\": false,\n"
    "  \"tronco_base\": 2, \"tronco_torsion_inclin\": true,\n"
    "  \"carga_categoria\": 1, \"fuerza_rapida\": false,\n"
    "  \"brazo_base\": 2, \"brazo_abduccion_rotacion\": true, \"brazo_hombro_elevado\": false, \"brazo_apoyo\": false,\n"
    "  \"antebrazo_base\": 1, \"muneca_base\": 2, \"muneca_torsion_desviacion\": false,\n"
    "  \"agarre\": 1,\n"
    "  \"actividad_estatica\": false, \"actividad_repetitiva\": true, \"actividad_inestable\": false\n"
    "}"
)


# --- PEGAR ESTO EN evaluaciones/forms.py (Reemplazando la clase PosturasForzadasForm existente) ---

# CHOICES ESPECÍFICOS PARA REBA (Basados en el Manual)
REBA_CUELLO_CHOICES = [
    (1, "0° - 20° flexión (1)"),
    (2, "> 20° flexión o cualquier extensión (2)"),
]
REBA_PIERNAS_CHOICES = [
    (1, "Soporte bilateral, andando o sentado (1)"),
    (2, "Soporte unilateral, soporte ligero o postura inestable (2)"),
]
REBA_TRONCO_CHOICES = [
    (1, "Erguido / Neutro (1)"),
    (2, "0° - 20° flexión o extensión (2)"),
    (3, "20° - 60° flexión o > 20° extensión (3)"),
    (4, "> 60° flexión (4)"),
]
REBA_CARGA_CHOICES = [
    (0, "Carga < 5 Kg (+0)"),
    (1, "Carga 5 - 10 Kg (+1)"),
    (2, "Carga > 10 Kg (+2)"),
]
REBA_BRAZO_CHOICES = [
    (1, "Extensión 0°-20° o Flexión 0°-20° (1)"),
    (2, "Extensión >20° o Flexión 21°-45° (2)"),
    (3, "Flexión 45°-90° (3)"),
    (4, "Flexión >90° (4)"),
]
REBA_ANTEBRAZO_CHOICES = [
    (1, "Flexión 60° - 100° (1)"),
    (2, "Flexión < 60° o > 100° (2)"),
]
REBA_MUNECA_CHOICES = [
    (1, "Flexión/Extensión 0° - 15° (1)"),
    (2, "Flexión/Extensión > 15° (2)"),
]
REBA_AGARRE_CHOICES = [
    (0, "Bueno: Agarre fuerza, asa óptima (+0)"),
    (1, "Regular: Aceptable pero no ideal (+1)"),
    (2, "Malo: Posible pero incómodo (+2)"),
    (3, "Inaceptable: Sin agarre manual (+3)"),
]

class PosturasForzadasForm(BaseFactorForm):
    """
    Formulario UI para REBA.
    Mapea selecciones visuales al JSON 'input' que espera la calculadora.
    """
    # --- GRUPO A ---
    cuello_base = forms.TypedChoiceField(
        label="Cuello (Flexión/Extensión)", choices=REBA_CUELLO_CHOICES, coerce=int, widget=_add_bootstrap(forms.Select())
    )
    cuello_torsion_inclin = forms.BooleanField(
        label="¿Torsión o inclinación lateral? (+1)", required=False, widget=_add_bootstrap(forms.CheckboxInput())
    )

    piernas_base = forms.TypedChoiceField(
        label="Piernas (Soporte)", choices=REBA_PIERNAS_CHOICES, coerce=int, widget=_add_bootstrap(forms.Select())
    )
    piernas_flex_30_60 = forms.BooleanField(
        label="Flexión rodillas 30°-60° (+1)", required=False, widget=_add_bootstrap(forms.CheckboxInput())
    )
    piernas_flex_mas_60 = forms.BooleanField(
        label="Flexión rodillas > 60° (+2)", required=False, widget=_add_bootstrap(forms.CheckboxInput())
    )
    piernas_sedente = forms.BooleanField(
        label="Persona sentada (anula penalización >60°)", required=False, widget=_add_bootstrap(forms.CheckboxInput())
    )

    tronco_base = forms.TypedChoiceField(
        label="Tronco (Flexión/Extensión)", choices=REBA_TRONCO_CHOICES, coerce=int, widget=_add_bootstrap(forms.Select())
    )
    tronco_torsion_inclin = forms.BooleanField(
        label="¿Torsión o inclinación lateral? (+1)", required=False, widget=_add_bootstrap(forms.CheckboxInput())
    )

    # --- CARGA ---
    carga_categoria = forms.TypedChoiceField(
        label="Carga / Fuerza", choices=REBA_CARGA_CHOICES, coerce=int, widget=_add_bootstrap(forms.Select())
    )
    fuerza_rapida = forms.BooleanField(
        label="Fuerza rápida, brusca o golpe (+1)", required=False, widget=_add_bootstrap(forms.CheckboxInput())
    )

    # --- GRUPO B ---
    brazo_base = forms.TypedChoiceField(
        label="Brazo (Hombro)", choices=REBA_BRAZO_CHOICES, coerce=int, widget=_add_bootstrap(forms.Select())
    )
    brazo_hombro_elevado = forms.BooleanField(
        label="Hombro elevado (+1)", required=False, widget=_add_bootstrap(forms.CheckboxInput())
    )
    brazo_abduccion_rotacion = forms.BooleanField(
        label="Brazo abducido o rotado (+1)", required=False, widget=_add_bootstrap(forms.CheckboxInput())
    )
    brazo_apoyo = forms.BooleanField(
        label="Brazo apoyado / a favor gravedad (-1)", required=False, widget=_add_bootstrap(forms.CheckboxInput())
    )

    antebrazo_base = forms.TypedChoiceField(
        label="Antebrazo (Codo)", choices=REBA_ANTEBRAZO_CHOICES, coerce=int, widget=_add_bootstrap(forms.Select())
    )

    muneca_base = forms.TypedChoiceField(
        label="Muñeca", choices=REBA_MUNECA_CHOICES, coerce=int, widget=_add_bootstrap(forms.Select())
    )
    muneca_torsion_desviacion = forms.BooleanField(
        label="¿Torsión o desviación lateral? (+1)", required=False, widget=_add_bootstrap(forms.CheckboxInput())
    )

    agarre = forms.TypedChoiceField(
        label="Tipo de Agarre", choices=REBA_AGARRE_CHOICES, coerce=int, widget=_add_bootstrap(forms.Select())
    )

    # --- ACTIVIDAD ---
    actividad_estatica = forms.BooleanField(
        label="Estática > 1 min (+1)", required=False, widget=_add_bootstrap(forms.CheckboxInput())
    )
    actividad_repetitiva = forms.BooleanField(
        label="Repetitiva > 4 veces/min (+1)", required=False, widget=_add_bootstrap(forms.CheckboxInput())
    )
    actividad_inestable = forms.BooleanField(
        label="Cambios rápidos o inestable (+1)", required=False, widget=_add_bootstrap(forms.CheckboxInput())
    )

    class Meta:
        model = PosturasForzadas_Eval
        # Campos del modelo que Django manejará automáticamente.
        # 'detalles_json' se llenará automáticamente con los resultados del cálculo.
        fields = [
            "risk_evaluation",
            "aplicable", "observaciones",
        ]
        widgets = {
            "risk_evaluation": forms.HiddenInput(),
            "observaciones": _add_bootstrap(forms.Textarea(attrs={"rows": 3})),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Si estamos editando, leer del JSON guardado (calc_data['input']) y poblar los campos del form
        if self.instance and self.instance.pk:
            cd = self.instance.calc_data or {}
            inp = cd.get("input", {})
            # Lista de campos declarados arriba que deben leerse del JSON
            fields_to_load = [
                "cuello_base", "cuello_torsion_inclin",
                "piernas_base", "piernas_flex_30_60", "piernas_flex_mas_60", "piernas_sedente",
                "tronco_base", "tronco_torsion_inclin",
                "carga_categoria", "fuerza_rapida",
                "brazo_base", "brazo_hombro_elevado", "brazo_abduccion_rotacion", "brazo_apoyo",
                "antebrazo_base", "muneca_base", "muneca_torsion_desviacion",
                "agarre",
                "actividad_estatica", "actividad_repetitiva", "actividad_inestable"
            ]
            for f in fields_to_load:
                if f in inp:
                    self.fields[f].initial = inp[f]

    def clean(self):
        cleaned = super().clean()
        if cleaned.get("piernas_flex_30_60") and cleaned.get("piernas_flex_mas_60"):
            raise ValidationError(
                "Las flexiones de rodilla de 30°–60° y mayor a 60° "
                "son alternativas y no pueden seleccionarse juntas."
            )
        if cleaned.get("piernas_sedente") and (
            cleaned.get("piernas_flex_30_60")
            or cleaned.get("piernas_flex_mas_60")
        ):
            raise ValidationError(
                "En postura sedente no corresponde aplicar correcciones de "
                "flexión de rodillas de pie."
            )
        return cleaned

    def save(self, commit=True):
        instance = super().save(commit=False)
        
        # 1. Construir el diccionario Payload para la calculadora
        # Las claves DEBEN coincidir con lo que espera calculators.py -> _get_inputs 
        payload = {
            "cuello_base": self.cleaned_data.get("cuello_base"),
            "cuello_torsion_inclin": self.cleaned_data.get("cuello_torsion_inclin"),
            
            "piernas_base": self.cleaned_data.get("piernas_base"),
            "piernas_flex_30_60": self.cleaned_data.get("piernas_flex_30_60"),
            "piernas_flex_mas_60": self.cleaned_data.get("piernas_flex_mas_60"),
            "piernas_sedente": self.cleaned_data.get("piernas_sedente"),
            
            "tronco_base": self.cleaned_data.get("tronco_base"),
            "tronco_torsion_inclin": self.cleaned_data.get("tronco_torsion_inclin"),
            
            "carga_categoria": self.cleaned_data.get("carga_categoria"),
            "fuerza_rapida": self.cleaned_data.get("fuerza_rapida"),
            
            "brazo_base": self.cleaned_data.get("brazo_base"),
            "brazo_abduccion_rotacion": self.cleaned_data.get("brazo_abduccion_rotacion"),
            "brazo_hombro_elevado": self.cleaned_data.get("brazo_hombro_elevado"),
            "brazo_apoyo": self.cleaned_data.get("brazo_apoyo"),
            
            "antebrazo_base": self.cleaned_data.get("antebrazo_base"),
            
            "muneca_base": self.cleaned_data.get("muneca_base"),
            "muneca_torsion_desviacion": self.cleaned_data.get("muneca_torsion_desviacion"),
            
            "agarre": self.cleaned_data.get("agarre"),
            
            "actividad_estatica": self.cleaned_data.get("actividad_estatica"),
            "actividad_repetitiva": self.cleaned_data.get("actividad_repetitiva"),
            "actividad_inestable": self.cleaned_data.get("actividad_inestable"),
        }

        # 2. Guardar este payload en instance.calc_data['input']
        # Usamos el helper _merge_calc_input que ya está importado en forms.py
        _merge_calc_input(instance, payload)

        if commit:
            instance.save()
            # Forzamos update de calc_data
            instance.save(update_fields=["calc_data"])
            
        return instance



# ============================================================================
#                          VIBRACIÓN MANO-BRAZO (VMB)
# ============================================================================

class VibracionMBForm(BaseFactorForm):
    tipo_exposicion = forms.ChoiceField(
        choices=[("simple", "Exposición Simple"), ("multiple", "Exposición Múltiple")],
        required=False,
        initial="simple",
        widget=_add_bootstrap(forms.Select()),
    )

    # JSON Textarea para el JS (fuente de verdad en la UI)
    items_json = JSONTextarea(
        label="Ítems de Exposición (Detalle)",
        required=False,
        help_text="Cargue los tramos usando los campos de arriba.",
    )

    class Meta:
        model = VibracionMB_Eval
        fields = [
            "risk_evaluation", "tipo_exposicion",
            "a_k_m_s2", "duracion_h",
            "ax_mps2", "ay_mps2", "az_mps2",
            "exposiciones_json",
            "aplicable", "observaciones",
        ]
        widgets = {
            "risk_evaluation": forms.HiddenInput(),
            "a_k_m_s2": _add_bootstrap(forms.NumberInput(attrs={"step": "0.01", "min": "0"})),
            "duracion_h": _add_bootstrap(forms.NumberInput(attrs={"step": "0.01", "min": "0"})),
            "ax_mps2": _add_bootstrap(forms.NumberInput(attrs={"step": "0.01", "min": "0"})),
            "ay_mps2": _add_bootstrap(forms.NumberInput(attrs={"step": "0.01", "min": "0"})),
            "az_mps2": _add_bootstrap(forms.NumberInput(attrs={"step": "0.01", "min": "0"})),
            # Solo lectura: se completa desde items_json al guardar
            "exposiciones_json": _add_bootstrap(forms.Textarea(attrs={"rows": 6, "readonly": True, "class": "form-control font-monospace"})),
            "observaciones": _add_bootstrap(forms.Textarea(attrs={"rows": 3})),
        }

    # -------------------------
    # Helpers locales
    # -------------------------
    @staticmethod
    def _to_float_or_none(x):
        try:
            if x is None or x == "":
                return None
            v = float(x)
            if not math.isfinite(v):
                return None
            return v
        except Exception:
            return None

    # -------------------------
    # Inicialización (edición)
    # -------------------------
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Si editamos una instancia existente, precargamos items_json desde exposiciones_json
        if getattr(self.instance, "pk", None):
            tipo = (getattr(self.instance, "tipo_exposicion", "") or "simple").lower()
            self.fields["tipo_exposicion"].initial = tipo

            if tipo == "multiple":
                expo = getattr(self.instance, "exposiciones_json", None) or []
                # ✅ clave: así el builder JS arranca con lo ya guardado
                self.fields["items_json"].initial = expo

    # -------------------------
    # Validación de estructura
    # -------------------------
    def clean_items_json(self):
        data = self.cleaned_data.get("items_json")

        # JSONTextarea (JSONField) ya suele devolver list/dict, pero por seguridad:
        if isinstance(data, str) and data.strip():
            data = _json_loads_safe(data)
        if data in (None, "", []):
            return []

        if not isinstance(data, list):
            raise ValidationError("El JSON debe ser una lista de ítems.")

        normalized = []
        seen_axes = False
        seen_scalar = False

        for idx, it in enumerate(data, start=1):
            if not isinstance(it, dict):
                raise ValidationError(f"Ítem #{idx}: debe ser un objeto JSON.")

            ti = self._to_float_or_none(it.get("Ti_h"))
            if ti is None or ti <= 0:
                raise ValidationError(f"Ítem #{idx}: Ti_h debe ser > 0 (horas).")

            # ¿viene por ejes?
            ax = self._to_float_or_none(it.get("ax_mps2"))
            ay = self._to_float_or_none(it.get("ay_mps2"))
            az = self._to_float_or_none(it.get("az_mps2"))
            has_axes = (ax is not None or ay is not None or az is not None)

            # ¿viene por a_wi escalar?
            aw = self._to_float_or_none(it.get("awi_mps2"))
            if aw is None:
                aw = self._to_float_or_none(it.get("ak_mps2"))

            if has_axes:
                # si usa ejes, deben venir los 3
                if ax is None or ay is None or az is None:
                    raise ValidationError(f"Ítem #{idx}: si usa ejes, debe incluir ax_mps2, ay_mps2 y az_mps2.")
                if ax < 0 or ay < 0 or az < 0:
                    raise ValidationError(f"Ítem #{idx}: los ejes no pueden ser negativos.")
                seen_axes = True
                normalized.append(
                    {"ax_mps2": round(ax, 3), "ay_mps2": round(ay, 3), "az_mps2": round(az, 3), "Ti_h": round(ti, 3)}
                )
            else:
                # escalar
                if aw is None:
                    raise ValidationError(f"Ítem #{idx}: debe incluir a_wi (awi_mps2) o ejes (ax/ay/az).")
                if aw < 0:
                    raise ValidationError(f"Ítem #{idx}: a_wi no puede ser negativo.")
                seen_scalar = True
                normalized.append({"awi_mps2": round(aw, 3), "Ti_h": round(ti, 3)})

        # ✅ NO permitir mezcla: tu calculadora original subestima si se mezclan
        if seen_axes and seen_scalar:
            raise ValidationError("No mezcle tramos por ejes con tramos por a_wi (use un único modo).")

        return normalized

    def clean(self):
        cleaned = super().clean()
        if not cleaned.get("aplicable", True):
            return cleaned

        tipo = (cleaned.get("tipo_exposicion") or "simple").lower()

        if tipo == "simple":
            dur = cleaned.get("duracion_h")
            if dur is None or float(dur) <= 0:
                self.add_error("duracion_h", "La duración debe ser mayor a 0.")

            ax = cleaned.get("ax_mps2")
            ay = cleaned.get("ay_mps2")
            az = cleaned.get("az_mps2")
            ak = cleaned.get("a_k_m_s2")

            usando_ejes = any(v is not None for v in [ax, ay, az])
            if usando_ejes:
                if None in [ax, ay, az]:
                    self.add_error(None, "Si usa el método de Ejes, debe completar X, Y y Z.")
                elif any(float(v) < 0 for v in [ax, ay, az]):
                    self.add_error(None, "Las aceleraciones por eje no pueden ser negativas.")
            else:
                if ak is None:
                    self.add_error("a_k_m_s2", "Debe ingresar una aceleración (por Ejes o valor único).")
                elif float(ak) < 0:
                    self.add_error("a_k_m_s2", "La aceleración no puede ser negativa.")

        elif tipo == "multiple":
            items = cleaned.get("items_json") or []
            if not items:
                self.add_error("items_json", "Debe agregar al menos un tramo de exposición.")

        return cleaned

    def save(self, commit=True):
        instance = super().save(commit=False)

        tipo = (self.cleaned_data.get("tipo_exposicion") or "simple").lower()
        instance.tipo_exposicion = tipo

        if tipo == "multiple":
            items = self.cleaned_data.get("items_json") or []
            instance.exposiciones_json = items

            # (opcional pero recomendable) limpiar campos de simple para evitar “basura” histórica
            instance.a_k_m_s2 = None
            instance.ax_mps2 = None
            instance.ay_mps2 = None
            instance.az_mps2 = None
            instance.duracion_h = None

        else:
            # simple => vaciar exposiciones múltiples
            instance.exposiciones_json = []

        # Trazabilidad (calc_data["input"])
        _merge_calc_input(instance, {
            "tipo_exposicion": instance.tipo_exposicion,
            "items": list(instance.exposiciones_json) if instance.tipo_exposicion == "multiple" else [],
        })

        if commit:
            instance.save()
            instance.save(update_fields=["calc_data", "tipo_exposicion", "exposiciones_json", "a_k_m_s2", "ax_mps2", "ay_mps2", "az_mps2", "duracion_h"])

        return instance



# ============================================================================
#                        VIBRACIÓN CUERPO ENTERO (VCE)
# ============================================================================

class VibracionCEForm(BaseFactorForm):
    """
    Formulario VCE compatible con arquitectura actual + nuevos campos Formulario 2:
    - Legacy (método 1/2 simples).
    - Contexto y montaje (Secciones B y C).
    - Los tramos se manejan vía VCESegmentFormSet.
    """

    class Meta:
        model = VibracionCE_Eval
        fields = [
            "risk_evaluation",

            # --- LEGACY (Compatibilidad) ---
            "metodo",
            "espectro_json",
            "a_wx", "a_wy", "a_wz",
            "duracion_h", "factor_cresta_gt6",

            # --- NUEVOS (Formulario 2 - B y C) ---
            "postura",
            "salud_columna",
            "ubicacion_sensor",
            "foto_montaje",
            "certificado_calibracion",

            # --- COMUNES ---
            "aplicable", "observaciones",
        ]
        widgets = {
            "risk_evaluation": forms.HiddenInput(),

            # Legacy
            "metodo": _add_bootstrap(
                forms.Select(choices=[("espectral", "Análisis Espectral"), ("ponderadas", "Aceleraciones Ponderadas")]),
                css="form-select"
            ),
            "espectro_json": _add_bootstrap(
                forms.Textarea(attrs={"rows": 6, "class": "form-control font-monospace"})
            ),
            "a_wx": _add_bootstrap(forms.NumberInput(attrs={"step": "0.001", "min": "0"})),
            "a_wy": _add_bootstrap(forms.NumberInput(attrs={"step": "0.001", "min": "0"})),
            "a_wz": _add_bootstrap(forms.NumberInput(attrs={"step": "0.001", "min": "0"})),
            "duracion_h": _add_bootstrap(forms.NumberInput(attrs={"step": "0.25", "min": "0"})),
            "factor_cresta_gt6": _add_bootstrap(forms.CheckboxInput()),

            # Nuevos (B y C)
            "postura": _add_bootstrap(forms.Select(), css="form-select"),
            "ubicacion_sensor": _add_bootstrap(forms.Select(), css="form-select"),
            "salud_columna": _add_bootstrap(forms.Textarea(attrs={"rows": 2})),
            "foto_montaje": _add_bootstrap(forms.ClearableFileInput()),
            "certificado_calibracion": _add_bootstrap(forms.ClearableFileInput()),

            "observaciones": _add_bootstrap(forms.Textarea(attrs={"rows": 3})),
        }

    SPECTRUM_KEYS = (
        "pico_x_hz",
        "pico_x_mps2",
        "pico_y_hz",
        "pico_y_mps2",
        "pico_z_hz",
        "pico_z_mps2",
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        field = self.fields["espectro_json"]
        field.label = "Picos espectrales por eje (JSON)"
        field.help_text = (
            "Para el método espectral, informe exactamente las seis claves del "
            "ejemplo. Frecuencias en Hz y aceleraciones en m/s²."
        )
        field.widget.attrs["placeholder"] = (
            '{\n'
            '  "pico_x_hz": 2, "pico_x_mps2": 0.25,\n'
            '  "pico_y_hz": 2, "pico_y_mps2": 0.20,\n'
            '  "pico_z_hz": 5, "pico_z_mps2": 0.35\n'
            '}'
        )

    def clean_espectro_json(self):
        spectrum = self.cleaned_data.get("espectro_json") or {}
        if not spectrum:
            return {}
        if not isinstance(spectrum, dict):
            raise ValidationError("El espectro debe ser un objeto JSON.")

        expected = set(self.SPECTRUM_KEYS)
        received = set(spectrum)
        missing = sorted(expected - received)
        unexpected = sorted(received - expected)
        if missing or unexpected:
            parts = []
            if missing:
                parts.append(f"faltan: {', '.join(missing)}")
            if unexpected:
                parts.append(f"no admitidas: {', '.join(unexpected)}")
            raise ValidationError(
                "El espectro debe contener exactamente las seis claves requeridas "
                f"({'; '.join(parts)})."
            )

        normalized = {}
        for key in self.SPECTRUM_KEYS:
            try:
                value = float(spectrum[key])
            except (TypeError, ValueError):
                raise ValidationError(f"{key} debe ser un número.") from None
            if not math.isfinite(value) or value < 0:
                raise ValidationError(
                    f"{key} debe ser un número finito y no negativo."
                )
            normalized[key] = value
        return normalized

    def clean(self):
        cleaned = super().clean()
        for field in ("a_wx", "a_wy", "a_wz"):
            value = cleaned.get(field)
            if value is not None and (not math.isfinite(float(value)) or value < 0):
                self.add_error(field, "La aceleración debe ser finita y no negativa.")
        duration = cleaned.get("duracion_h")
        if duration is not None and (
            not math.isfinite(float(duration)) or duration <= 0
        ):
            self.add_error("duracion_h", "La duración debe ser finita y mayor a 0.")
        return cleaned

    def save(self, commit=True):
        """
        Mantiene comportamiento legacy: inyecta tipo_datos en calc_data
        para que la calculadora sepa qué método usar.
        """
        instance = super().save(commit=False)

        metodo = (self.cleaned_data.get("metodo") or "").lower()
        tipo_datos = "metodo2" if metodo == "ponderadas" else "metodo1"
        spectrum = dict(self.cleaned_data.get("espectro_json") or {})
        calc_data = dict(instance.calc_data or {})
        current_input = dict(calc_data.get("input", {}) or {})
        for key in self.SPECTRUM_KEYS:
            current_input.pop(key, None)
        current_input.update({"tipo_datos": tipo_datos, **spectrum})
        calc_data["input"] = current_input
        instance.calc_data = calc_data

        if commit:
            instance.save()

        return instance


class VCESegmentForm(forms.ModelForm):
    """
    Formulario para cada tramo VCE (Sección D).
    Nota: Aquí no usamos BaseFactorForm porque es un hijo simple.
    """
    class Meta:
        model = VCESegment
        fields = [
            "vehiculo_maquina", "tipo_asiento", "superficie_terreno",
            "velocidad_promedio", "estado_neumaticos",
            "tiempo_horas",
            "aw_x", "aw_y", "aw_z",
            "cf_x", "cf_y", "cf_z",
            "pico_espectral_hz",
        ]
        widgets = {
            # Usamos attrs directos para inputs pequeños de tabla
            "vehiculo_maquina": forms.TextInput(attrs={"class": "form-control form-control-sm"}),
            "tipo_asiento": forms.Select(attrs={"class": "form-select form-select-sm"}),
            "superficie_terreno": forms.Select(attrs={"class": "form-select form-select-sm"}),
            "velocidad_promedio": forms.NumberInput(attrs={"class": "form-control form-control-sm", "step": "0.1"}),
            "estado_neumaticos": forms.Select(attrs={"class": "form-select form-select-sm"}),

            "tiempo_horas": forms.NumberInput(attrs={"class": "form-control form-control-sm", "step": "0.1", "min": "0"}),

            # RMS Wd/Wk
            "aw_x": forms.NumberInput(attrs={"class": "form-control form-control-sm", "step": "0.01", "min": "0"}),
            "aw_y": forms.NumberInput(attrs={"class": "form-control form-control-sm", "step": "0.01", "min": "0"}),
            "aw_z": forms.NumberInput(attrs={"class": "form-control form-control-sm", "step": "0.01", "min": "0"}),

            # Opcionales
            "cf_x": forms.NumberInput(attrs={"class": "form-control form-control-sm", "step": "0.1", "placeholder": "Opcional"}),
            "cf_y": forms.NumberInput(attrs={"class": "form-control form-control-sm", "step": "0.1", "placeholder": "Opcional"}),
            "cf_z": forms.NumberInput(attrs={"class": "form-control form-control-sm", "step": "0.1", "placeholder": "Opcional"}),

            "pico_espectral_hz": forms.NumberInput(attrs={"class": "form-control form-control-sm", "step": "1", "placeholder": "Hz"}),
        }

    def clean(self):
        cleaned = super().clean()
        positive = ("tiempo_horas",)
        non_negative = (
            "velocidad_promedio",
            "aw_x",
            "aw_y",
            "aw_z",
            "cf_x",
            "cf_y",
            "cf_z",
            "pico_espectral_hz",
        )
        for field in positive:
            value = cleaned.get(field)
            if value is not None and (
                not math.isfinite(float(value)) or float(value) <= 0
            ):
                self.add_error(field, "El valor debe ser finito y mayor a 0.")
        for field in non_negative:
            value = cleaned.get(field)
            if value is not None and (
                not math.isfinite(float(value)) or float(value) < 0
            ):
                self.add_error(field, "El valor debe ser finito y no negativo.")
        return cleaned


VCESegmentFormSet = inlineformset_factory(
    VibracionCE_Eval,
    VCESegment,
    form=VCESegmentForm,
    extra=1,
    can_delete=True,
)


# ============================================================================
#                           CONFORT TÉRMICO
# ============================================================================

class ConfortTermicoForm(BaseFactorForm):
    class Meta:
        model = ConfortTermico_Eval
        fields = [
            "risk_evaluation",
            "temperatura_operativa_c", "humedad_relativa_pct",
            "aplicable", "observaciones",
        ]
        widgets = {
            "risk_evaluation": forms.HiddenInput(),
            "temperatura_operativa_c": _add_bootstrap(forms.NumberInput(attrs={"step": "0.1", "placeholder": "Ej: 24.0"})),
            "humedad_relativa_pct": _add_bootstrap(forms.NumberInput(attrs={"step": "0.1", "placeholder": "Ej: 50.0"})),
            "observaciones": _add_bootstrap(forms.Textarea(attrs={"rows": 3})),
        }

    # -------------------------------------------------------------------------
    # VALIDACIONES DE RANGO (Fanger)
    # -------------------------------------------------------------------------

    def clean_temperatura_operativa_c(self):
        to = self.cleaned_data.get("temperatura_operativa_c")
        # El gráfico de Fanger en el manual va de 15°C a 40°C
        if to is not None and (to < 15 or to > 40):
            raise ValidationError(
                "La Temperatura Operativa debe estar entre 15°C y 40°C para la evaluación mediante las Curvas de Fanger."
            )
        return to

    def clean_humedad_relativa_pct(self):
        hr = self.cleaned_data.get("humedad_relativa_pct")
        # El gráfico de Fanger va de 0% a 90%
        if hr is not None and (hr < 0 or hr > 90):
            raise ValidationError(
                "La Humedad Relativa debe estar entre 0% y 90% para la evaluación mediante las Curvas de Fanger."
            )
        return hr

    def clean(self):
        cleaned = super().clean()
        self._require_for_calculation(
            cleaned,
            ["temperatura_operativa_c", "humedad_relativa_pct"],
        )
        return cleaned


# ============================================================================
#                          ESTRÉS DE CONTACTO
# ============================================================================

EC_SINTOMAS_CHOICES = [
    ("hormigueo", "Hormigueo"),
    ("adormecimiento", "Adormecimiento"),
    ("dolor", "Dolor"),
    ("marcas", "Marcas/piel"),
]
EC_CONTROLES_CHOICES = [
    ("bordes_redondeados", "Bordes redondeados"),
    ("herramientas_ergonomicas", "Herramientas ergonómicas"),
    ("apoyos_muneca", "Apoyos de muñeca"),
    ("rotacion_micropausas", "Rotación / micropausas"),
    ("guantes_acolchados", "Guantes acolchados"),
]

class EstresContactoForm(BaseFactorForm):
    """
    - El modelo guarda bandas de frecuencia; la calculadora usa % del ciclo.
      Mapeamos: bajo→20, moderado→45, alto→80.
    - Campos opcionales de apoyo al cálculo (no modelados): fuerza_n, area_cm2, borg.
    """
    sintomas = forms.MultipleChoiceField(
        required=False, choices=EC_SINTOMAS_CHOICES,
        widget=forms.CheckboxSelectMultiple, label="Síntomas"
    )
    controles = forms.MultipleChoiceField(
        required=False, choices=EC_CONTROLES_CHOICES,
        widget=forms.CheckboxSelectMultiple, label="Controles existentes"
    )
    # Apoyos opcionales para cálculo
    fuerza_n = forms.FloatField(required=False, min_value=0, label="Fuerza (N)")
    area_cm2 = forms.FloatField(required=False, min_value=0, label="Área de contacto (cm²)")
    borg = forms.IntegerField(required=False, min_value=0, max_value=10, label="Borg (0–10)")

    class Meta:
        model = EstresContacto_Eval
        fields = [
            "risk_evaluation",
            "segmento_afectado", "objeto_superficie", "tipo_borde",
            "duracion_continua_min", "frecuencia_exposicion",
            "mano_como_martillo", "mango_inadecuado", "postura_forzada_asociada",
            "aplicable", "observaciones",
        ]
        widgets = {
            "risk_evaluation": forms.HiddenInput(),
            "segmento_afectado": _add_bootstrap(forms.Select()),
            "objeto_superficie": _add_bootstrap(forms.TextInput()),
            "tipo_borde": _add_bootstrap(forms.Select()),
            "duracion_continua_min": _add_bootstrap(forms.NumberInput(attrs={"step": "1", "min": "0"})),
            "frecuencia_exposicion": _add_bootstrap(forms.Select(choices=[
                ("bajo", "Bajo (<30%)"), ("moderado", "Moderado (30–60%)"), ("alto", "Alto (>60%)")
            ])),
            "observaciones": _add_bootstrap(forms.Textarea(attrs={"rows": 3})),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.fields["sintomas"].initial = list(self.instance.sintomas_json or [])
            self.fields["controles"].initial = list(
                self.instance.controles_existentes_json or []
            )

    def clean(self):
        cleaned = super().clean()
        area = cleaned.get("area_cm2")
        fuerza = cleaned.get("fuerza_n")
        borg = cleaned.get("borg")
        if (area is None) != (fuerza is None):
            message = "Para calcular presión, complete fuerza y área juntas."
            if area is None:
                self.add_error("area_cm2", message)
            else:
                self.add_error("fuerza_n", message)
        if area is not None and area <= 0:
            self.add_error("area_cm2", "El área debe ser mayor que cero.")
        if borg is not None and not (0 <= int(borg) <= 10):
            raise ValidationError("Borg debe estar entre 0 y 10.")
        duration = cleaned.get("duracion_continua_min")
        if duration is not None and duration <= 0:
            self.add_error(
                "duracion_continua_min",
                "La duración continua debe ser mayor que cero.",
            )
        self._require_for_calculation(
            cleaned,
            [
                "segmento_afectado",
                "objeto_superficie",
                "tipo_borde",
                "duracion_continua_min",
                "frecuencia_exposicion",
            ],
        )
        return cleaned

    def save(self, commit=True):
        instance = super().save(commit=False)

        # Persistimos selecciones amigables en los JSONFields del modelo
        sintomas = self.cleaned_data.get("sintomas") or []
        controles = self.cleaned_data.get("controles") or []
        instance.sintomas_json = list(sintomas)
        instance.controles_existentes_json = list(controles)

        # Mapear banda → % estimado para la calculadora
        freq_band = (self.cleaned_data.get("frecuencia_exposicion") or "").lower()
        freq_pct_map = {"bajo": 20, "moderado": 45, "alto": 80}
        freq_pct = freq_pct_map.get(freq_band, 45)

        # Mapear nombres de flags a los que espera la calculadora
        payload = {
            "borde_tipo": self.cleaned_data.get("tipo_borde"),
            "duracion_continua_min": self.cleaned_data.get("duracion_continua_min"),
            "frecuencia_pct": freq_pct,
            "mano_martillo": bool(self.cleaned_data.get("mano_como_martillo")),
            "mango_inadecuado": bool(self.cleaned_data.get("mango_inadecuado")),
            "postura_forzada": bool(self.cleaned_data.get("postura_forzada_asociada")),
            "sintomas": list(sintomas),
            "controles": list(controles),
        }

        # Opcionales de apoyo (si vinieron)
        if self.cleaned_data.get("fuerza_n") is not None:
            payload["fuerza_n"] = float(self.cleaned_data["fuerza_n"])
        if self.cleaned_data.get("area_cm2") is not None:
            payload["area_cm2"] = float(self.cleaned_data["area_cm2"])
        if self.cleaned_data.get("borg") is not None:
            payload["borg"] = int(self.cleaned_data["borg"])

        _merge_calc_input(instance, payload)

        if commit:
            instance.save()

        # Mezclamos además cualquier input_json genérico
        self._post_clean_merge_input(instance)
        if commit:
            instance.save(update_fields=["calc_data"])
        return instance

# ============================================================================
#                           RISK EVALUATION (root)
# ============================================================================

class RiskEvaluationQuickForm(forms.ModelForm):
    """
    Form simple útil para actualizar estado y resumen global desde el dashboard.
    """
    class Meta:
        model = RiskEvaluation
        fields = ["estado", "resultado_global", "resumen_json"]
        widgets = {
            "estado": _add_bootstrap(forms.Select()),
            "resultado_global": _add_bootstrap(forms.Select()),
            # ✅ Textarea normal (NO JSONTextarea Field aquí)
            "resumen_json": _add_bootstrap(forms.Textarea(attrs={"rows": 6, "class": "form-control font-monospace"})),
        }

# ============================================================================
#                            EXPORT PUBLIC API
# ============================================================================

__all__ = [
    # raíz
    "RiskEvaluationQuickForm",
    # factores
    "LMCForm",
    "EmpujeInicialForm", "EmpujeSostenidaForm",
    "TraccionInicialForm", "TraccionSostenidaForm",
    "TransporteForm",
    "BipedestacionForm",
    "RepetitivosMSForm",
    "PosturasForzadasForm",
    "VibracionMBForm",
    "VibracionCEForm",
    "ConfortTermicoForm",
    "EstresContactoForm",
]
