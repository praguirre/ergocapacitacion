"""Formulario y campo múltiple del canal de feedback profesional."""

from django import forms
from django.core.exceptions import ValidationError

from .models import FeedbackReport
from .validators import (
    MAX_ATTACHMENTS,
    MAX_TOTAL_ATTACHMENT_BYTES,
    validate_feedback_attachment,
)


class MultipleFileInput(forms.ClearableFileInput):
    """Widget Django que declara explícitamente selección múltiple."""

    allow_multiple_selected = True


class MultipleFileField(forms.FileField):
    """Aplica el contrato de ``FileField`` a cada archivo recibido."""

    def clean(self, data, initial=None):
        files = data if isinstance(data, (list, tuple)) else [data] if data else []
        return [super(MultipleFileField, self).clean(item, initial) for item in files]


class FeedbackForm(forms.Form):
    """Valida texto, privacidad y adjuntos sin aceptar identidad por POST."""

    category = forms.ChoiceField(label="Categoría", choices=FeedbackReport.Category.choices)
    subject = forms.CharField(label="Asunto", max_length=160)
    affected_screen = forms.CharField(
        label="Pantalla o sección afectada",
        max_length=300,
        required=False,
    )
    description = forms.CharField(
        label="Descripción",
        max_length=5_000,
        widget=forms.Textarea,
    )
    reproduction_steps = forms.CharField(
        label="Pasos para reproducir",
        max_length=5_000,
        required=False,
        widget=forms.Textarea,
    )
    expected_result = forms.CharField(
        label="Resultado esperado",
        max_length=3_000,
        required=False,
        widget=forms.Textarea,
    )
    attachments = MultipleFileField(
        label="Adjuntos",
        required=False,
        widget=MultipleFileInput,
        validators=(validate_feedback_attachment,),
    )
    privacy_confirmed = forms.BooleanField(
        label="Confirmo que evité datos personales innecesarios",
        required=True,
    )

    def clean_subject(self):
        subject = self.cleaned_data["subject"].strip()
        if "\r" in subject or "\n" in subject:
            raise ValidationError("El asunto no puede contener saltos de línea.")
        return subject

    def clean_attachments(self):
        attachments = self.cleaned_data.get("attachments", [])
        if len(attachments) > MAX_ATTACHMENTS:
            raise ValidationError("Podés adjuntar como máximo 5 archivos.")
        total = sum(attachment.size for attachment in attachments)
        if total > MAX_TOTAL_ATTACHMENT_BYTES:
            raise ValidationError("Los adjuntos pueden pesar como máximo 12 MiB en total.")
        return attachments
