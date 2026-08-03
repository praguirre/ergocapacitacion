# planillas/forms.py
from django import forms
from django.db import models
from django.forms import inlineformset_factory
from apps.company.models import CompanyProfile, CompanyWorker
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
    """Alta y edición de la evaluación ergonómica.

    CF-5: al crear, los datos de una empresa registrada sólo se proponen. Los
    campos permanecen editables y lo escrito por el profesional siempre gana.
    Los snapshots nunca se resincronizan al editar el perfil de la empresa.
    """

    class Meta:
        model = Evaluacion
        fields = [
            "empresa", "razon_social", "cuit", "ciiu",
            "direccion_establecimiento", "provincia",
        ]
        widgets = {
            "empresa": forms.Select(attrs={
                "class": "form-select",
                "data-poblar-campos": "true",
            }),
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user

        if user is not None and user.is_company:
            try:
                perfil = user.company_profile
                self.fields["empresa"].queryset = CompanyProfile.objects.filter(
                    pk=perfil.pk
                )
                self.fields["empresa"].initial = perfil
                self.fields["empresa"].disabled = True
            except CompanyProfile.DoesNotExist:
                self.fields["empresa"].queryset = CompanyProfile.objects.none()
        else:
            self.fields["empresa"].queryset = CompanyProfile.objects.filter(
                account_status=CompanyProfile.AccountStatus.ACTIVE,
            ).order_by("razon_social")
            self.fields["empresa"].required = False
            self.fields["empresa"].empty_label = "— Otra (cargar manualmente) —"

        # Permite que un valor vacío sea propuesto desde CompanyProfile durante
        # clean(), antes de la validación del modelo. Sin empresa, clean()
        # conserva la obligatoriedad histórica de estos cuatro campos.
        for field_name in (
            "razon_social", "cuit", "direccion_establecimiento", "provincia",
        ):
            self.fields[field_name].required = False

    def clean(self):
        cleaned_data = super().clean()
        empresa = cleaned_data.get("empresa")
        if empresa is not None and self.instance.pk is None:
            propuestas = {
                "razon_social": empresa.razon_social,
                "cuit": empresa.cuit,
                "direccion_establecimiento": empresa.domicilio,
                "provincia": empresa.provincia,
            }
            for field_name, propuesta in propuestas.items():
                cleaned_data[field_name] = cleaned_data.get(field_name) or propuesta

        for field_name in (
            "razon_social", "cuit", "direccion_establecimiento", "provincia",
        ):
            if not cleaned_data.get(field_name):
                self.add_error(field_name, "Este campo es obligatorio.")
        return cleaned_data

    def save(self, commit=True):
        evaluacion = super().save(commit=False)
        empresa = self.cleaned_data.get("empresa")

        if empresa is not None and evaluacion.pk is None:
            evaluacion.razon_social = evaluacion.razon_social or empresa.razon_social
            evaluacion.cuit = evaluacion.cuit or empresa.cuit
            evaluacion.direccion_establecimiento = (
                evaluacion.direccion_establecimiento or empresa.domicilio
            )
            evaluacion.provincia = evaluacion.provincia or empresa.provincia

        if self.user is not None and evaluacion.pk is None:
            evaluacion.usuario = self.user

        if commit:
            evaluacion.save()
        return evaluacion

class Planilla1Form(forms.ModelForm):
    class Meta:
        model = Planilla1
        exclude = ['evaluacion']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        empresa = getattr(getattr(self.instance, "evaluacion", None), "empresa", None)
        if empresa is None:
            # Una evaluación manual no debe exponer una nómina ajena ni un
            # selector vacío: el respaldo de texto continúa operativo.
            self.fields.pop("trabajadores", None)
        else:
            self.fields["trabajadores"].queryset = (
                CompanyWorker.objects.filter(company=empresa, is_active=True)
                .select_related("worker")
                .order_by("worker__last_name", "worker__first_name", "worker__email")
            )
            self.fields["trabajadores"].widget.attrs["class"] = "form-select"

    def save(self, commit=True):
        planilla = super().save(commit=commit)
        if commit and "trabajadores" in self.cleaned_data:
            seleccionados = list(self.cleaned_data["trabajadores"])
            if seleccionados and not (planilla.nombres_trabajadores or "").strip():
                planilla.nombres_trabajadores = "\n".join(
                    relacion.worker.display_name for relacion in seleccionados
                )
                planilla.save(update_fields=["nombres_trabajadores"])
        return planilla

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
