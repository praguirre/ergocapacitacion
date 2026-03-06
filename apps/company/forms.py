# apps/company/forms.py
# ============================================================================
# COMMIT 37: Formularios de nómina
# ============================================================================

from django import forms
import re
from .models import AgendaEvent


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


class EditWorkerForm(forms.Form):
    """Editar datos laborales de un trabajador en la nómina."""

    employee_code = forms.CharField(
        label='Legajo', max_length=50, required=False,
        widget=forms.TextInput(attrs={'class': 'form-control bg-black text-light border-secondary'}),
    )
    department = forms.CharField(
        label='Sector', max_length=200, required=False,
        widget=forms.TextInput(attrs={'class': 'form-control bg-black text-light border-secondary'}),
    )
    position = forms.CharField(
        label='Puesto', max_length=200, required=False,
        widget=forms.TextInput(attrs={'class': 'form-control bg-black text-light border-secondary'}),
    )
    start_date = forms.DateField(
        label='Fecha de inicio', required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control bg-black text-light border-secondary', 'type': 'date',
        }),
    )
    end_date = forms.DateField(
        label='Fecha de baja', required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control bg-black text-light border-secondary', 'type': 'date',
        }),
    )
    is_active = forms.BooleanField(
        label='Activo', required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
    )
    notes = forms.CharField(
        label='Notas', required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control bg-black text-light border-secondary', 'rows': 3,
        }),
    )

    def __init__(self, *args, assignment=None, **kwargs):
        super().__init__(*args, **kwargs)
        if assignment and not args:
            self.initial.update({
                'employee_code': assignment.employee_code,
                'department': assignment.department,
                'position': assignment.position,
                'start_date': assignment.start_date,
                'end_date': assignment.end_date,
                'is_active': assignment.is_active,
                'notes': assignment.notes,
            })


class AgendaEventForm(forms.Form):
    """Formulario para crear/editar eventos de agenda."""

    title = forms.CharField(
        label='Título', max_length=300,
        widget=forms.TextInput(attrs={'class': 'form-control bg-black text-light border-secondary'}),
    )
    description = forms.CharField(
        label='Descripción', required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control bg-black text-light border-secondary', 'rows': 3,
        }),
    )
    event_type = forms.ChoiceField(
        label='Tipo de evento',
        choices=AgendaEvent.EventType.choices,
        widget=forms.Select(attrs={'class': 'form-select bg-black text-light border-secondary'}),
    )
    priority = forms.ChoiceField(
        label='Prioridad',
        choices=AgendaEvent.Priority.choices,
        initial='medium',
        widget=forms.Select(attrs={'class': 'form-select bg-black text-light border-secondary'}),
    )
    due_at = forms.DateTimeField(
        label='Fecha/hora límite',
        widget=forms.DateTimeInput(attrs={
            'class': 'form-control bg-black text-light border-secondary',
            'type': 'datetime-local',
        }),
    )
    start_at = forms.DateTimeField(
        label='Fecha/hora de inicio (opcional)', required=False,
        widget=forms.DateTimeInput(attrs={
            'class': 'form-control bg-black text-light border-secondary',
            'type': 'datetime-local',
        }),
    )
    worker_id = forms.IntegerField(
        label='Trabajador relacionado (ID)', required=False,
        widget=forms.HiddenInput(),
    )

    def __init__(self, *args, event=None, **kwargs):
        super().__init__(*args, **kwargs)
        if event and not args:
            self.initial.update({
                'title': event.title,
                'description': event.description,
                'event_type': event.event_type,
                'priority': event.priority,
                'due_at': event.due_at.strftime('%Y-%m-%dT%H:%M') if event.due_at else '',
                'start_at': event.start_at.strftime('%Y-%m-%dT%H:%M') if event.start_at else '',
                'worker_id': event.worker_id,
            })
