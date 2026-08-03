# planillas/forms.py
from django import forms
from django.db import models
from django.forms import inlineformset_factory
from .models import *

# --- MIXIN DE LÓGICA REUTILIZABLE ---
# Centraliza la lógica para convertir BooleanFields en radios Sí/No.
class YesNoMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Este bucle se ejecuta al crear el formulario
        for field_name, field in self.fields.items():
            # Si el campo del modelo es un BooleanField...
            if isinstance(self.instance._meta.get_field(field_name), models.BooleanField):
                # ...lo reemplazamos en el formulario por un TypedChoiceField.
                self.fields[field_name] = forms.TypedChoiceField(
                    choices=[(True, 'Sí'), (False, 'No')],
                    widget=forms.RadioSelect, # Usamos el RadioSelect estándar de Django
                    coerce=lambda v: v == 'True',
                    required=False,
                    label=field.label,
                    initial=False
                )

# --- Formularios ---
class EvaluacionForm(forms.ModelForm):
    class Meta:
        model = Evaluacion
        fields = ['razon_social', 'cuit', 'ciiu', 'direccion_establecimiento', 'provincia']

class Planilla1Form(forms.ModelForm):
    class Meta:
        model = Planilla1
        exclude = ['evaluacion']

class FactorRiesgoForm(forms.ModelForm):
    presente = forms.BooleanField(required=False, widget=forms.CheckboxInput())
    class Meta:
        model = FactorRiesgo
        fields = ['tipo_factor', 'presente', 'tiempo_exposicion', 'riesgo_tarea1', 'riesgo_tarea2', 'riesgo_tarea3']
        widgets = {'tipo_factor': forms.HiddenInput()}

FactorRiesgoFormSet = inlineformset_factory(Planilla1, FactorRiesgo, form=FactorRiesgoForm, extra=0, can_delete=False)

# --- FORMULARIOS PARA PLANILLAS 2 (A-I) ---

class BasePlanilla2Form(YesNoMixin, forms.ModelForm):
    pass

class Planilla2AForm(BasePlanilla2Form):
    class Meta:
        model = Planilla2A
        exclude = ['evaluacion']

class Planilla2BForm(BasePlanilla2Form):
    class Meta:
        model = Planilla2B
        exclude = ['evaluacion']

class Planilla2CForm(BasePlanilla2Form):
    class Meta:
        model = Planilla2C
        exclude = ['evaluacion']

class Planilla2DForm(BasePlanilla2Form):
    class Meta:
        model = Planilla2D
        exclude = ['evaluacion']

class Planilla2EForm(BasePlanilla2Form):
    class Meta:
        model = Planilla2E
        exclude = ['evaluacion']

class Planilla2FForm(BasePlanilla2Form):
    class Meta:
        model = Planilla2F
        exclude = ['evaluacion']

class Planilla2GForm(BasePlanilla2Form):
    class Meta:
        model = Planilla2G
        exclude = ['evaluacion']

class Planilla2HForm(BasePlanilla2Form):
    class Meta:
        model = Planilla2H
        exclude = ['evaluacion']

class Planilla2IForm(BasePlanilla2Form):
    class Meta:
        model = Planilla2I
        exclude = ['evaluacion']

# --- INICIO: NUEVOS FORMULARIOS Y FORMSETS PARA PLANILLA 3 Y 4 ---

class Planilla3Form(YesNoMixin, forms.ModelForm):
    class Meta:
        model = Planilla3
        exclude = ['evaluacion']
        widgets = {
            'fecha_informado_riesgo': forms.DateInput(attrs={'type': 'date'}),
            'fecha_capacitado_sintomas': forms.DateInput(attrs={'type': 'date'}),
            'fecha_capacitado_medidas': forms.DateInput(attrs={'type': 'date'}),
            'observaciones_generales': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        # Llama al __init__ de YesNoMixin y luego al de ModelForm
        super().__init__(*args, **kwargs)
        # Lógica para autocompletar datos de la evaluación
        if self.instance and self.instance.evaluacion_id:
            evaluacion = self.instance.evaluacion
            try:
                # La planilla 1 contiene los datos del puesto
                planilla1 = evaluacion.planilla1
                self.fields['tarea_analizada'].initial = f"{planilla1.puesto_trabajo} - {planilla1.area_sector}"
            except Planilla1.DoesNotExist:
                pass


class MedidaEspecificaForm(forms.ModelForm):
    class Meta:
        model = MedidaEspecifica
        fields = ['descripcion', 'observaciones']
        widgets = {
            'descripcion': forms.Textarea(attrs={'rows': 2}),
            'observaciones': forms.Textarea(attrs={'rows': 2}),
        }

# Formset para las Medidas Específicas de la Planilla 3
MedidaEspecificaFormSet = inlineformset_factory(
    Planilla3, 
    MedidaEspecifica, 
    form=MedidaEspecificaForm, 
    extra=3, # Empezar con 3 filas vacías para nuevas medidas
    can_delete=True,
    can_delete_extra=True
)


class SeguimientoMedidaForm(forms.ModelForm):
    class Meta:
        model = SeguimientoMedida
        fields = ['nombre_puesto', 'fecha_evaluacion', 'nivel_riesgo', 'fecha_impl_admin', 'fecha_impl_ing', 'fecha_cierre']
        widgets = {
            'fecha_evaluacion': forms.DateInput(attrs={'type': 'date'}),
            'fecha_impl_admin': forms.DateInput(attrs={'type': 'date'}),
            'fecha_impl_ing': forms.DateInput(attrs={'type': 'date'}),
            'fecha_cierre': forms.DateInput(attrs={'type': 'date'}),
        }

# Formset para las filas de la Matriz de Seguimiento (Planilla 4)
SeguimientoMedidaFormSet = inlineformset_factory(
    MedidaEspecifica,
    SeguimientoMedida,
    form=SeguimientoMedidaForm,
    extra=0, # No agregar filas vacías, se crean a partir de las medidas existentes
    can_delete=False # No permitir eliminar el seguimiento desde esta pantalla
)

# --- FIN: NUEVOS FORMULARIOS ---
