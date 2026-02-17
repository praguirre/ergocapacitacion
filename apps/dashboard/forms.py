# apps/dashboard/forms.py
# ============================================================================
# COMMIT 24: Formularios del dashboard
# ============================================================================

from django import forms


class ShareLinkForm(forms.Form):
    """Formulario para compartir link por email."""

    emails = forms.CharField(
        label="Emails destinatarios",
        widget=forms.Textarea(
            attrs={
                "rows": 3,
                "placeholder": "email1@ejemplo.com, email2@ejemplo.com",
                "class": "form-control bg-black text-light border-secondary",
            }
        ),
        help_text="Separar múltiples emails con coma.",
    )
    message = forms.CharField(
        label="Mensaje personalizado (opcional)",
        required=False,
        widget=forms.Textarea(
            attrs={
                "rows": 3,
                "placeholder": "Hola, te comparto la capacitación que debés completar...",
                "class": "form-control bg-black text-light border-secondary",
            }
        ),
    )

    def clean_emails(self):
        raw = self.cleaned_data.get("emails", "")
        emails = [e.strip().lower() for e in raw.replace(";", ",").split(",") if e.strip()]

        if not emails:
            raise forms.ValidationError("Ingresá al menos un email.")

        # Validación básica
        from django.core.validators import validate_email

        for email in emails:
            try:
                validate_email(email)
            except forms.ValidationError:
                raise forms.ValidationError(f"Email inválido: {email}")

        return emails
