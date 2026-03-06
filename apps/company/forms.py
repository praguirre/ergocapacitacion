# apps/company/forms.py
# ============================================================================
# COMMIT 37: Formularios de nómina
# ============================================================================

from django import forms
import re


def normalize_cuil(value: str) -> str:
    """Normaliza CUIL/CUIT: extrae solo dígitos y valida longitud 11."""
    digits = re.sub(r"\D", "", (value or "").strip())
    if len(digits) != 11:
        raise forms.ValidationError("CUIL inválido (debe tener 11 dígitos).")
    return digits


class AddWorkerForm(forms.Form):
    """Formulario para agregar un trabajador a la nómina."""

    # Datos del trabajador
    cuil = forms.CharField(
        label='CUIL del trabajador',
        max_length=20,
        widget=forms.TextInput(attrs={
            'class': 'form-control bg-black text-light border-secondary',
            'placeholder': '20-12345678-9',
        }),
        help_text='Si el trabajador ya existe en el sistema, se vinculará automáticamente.',
    )
    email = forms.EmailField(
        label='Email',
        widget=forms.EmailInput(attrs={
            'class': 'form-control bg-black text-light border-secondary',
            'placeholder': 'trabajador@email.com',
        }),
    )
    full_name = forms.CharField(
        label='Nombre completo',
        max_length=300,
        widget=forms.TextInput(attrs={
            'class': 'form-control bg-black text-light border-secondary',
            'placeholder': 'Juan Pérez',
        }),
    )
    job_title = forms.CharField(
        label='Puesto / Cargo (general)',
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control bg-black text-light border-secondary',
        }),
    )

    # Datos de la relación laboral
    employee_code = forms.CharField(
        label='Legajo',
        max_length=50,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control bg-black text-light border-secondary',
        }),
    )
    department = forms.CharField(
        label='Sector',
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control bg-black text-light border-secondary',
        }),
    )
    position = forms.CharField(
        label='Puesto en la empresa',
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control bg-black text-light border-secondary',
        }),
    )
    start_date = forms.DateField(
        label='Fecha de inicio',
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control bg-black text-light border-secondary',
            'type': 'date',
        }),
    )
    notes = forms.CharField(
        label='Notas',
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control bg-black text-light border-secondary',
            'rows': 3,
        }),
    )

    def clean_cuil(self):
        return normalize_cuil(self.cleaned_data['cuil'])
