# apps/dashboard/forms.py
# ============================================================================
# COMMIT 24: Formularios del dashboard
# ============================================================================

from django import forms
from django.contrib.auth import get_user_model

User = get_user_model()


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


# ============================================================================
# COMMIT 26: Formularios de perfil profesional
# ============================================================================


class ProfessionalProfileForm(forms.Form):
    """Formulario de edición de perfil del profesional."""

    first_name = forms.CharField(
        label="Nombre",
        max_length=100,
        widget=forms.TextInput(attrs={"class": "form-control bg-black text-light border-secondary"}),
    )
    last_name = forms.CharField(
        label="Apellido",
        max_length=100,
        widget=forms.TextInput(attrs={"class": "form-control bg-black text-light border-secondary"}),
    )
    email = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(attrs={"class": "form-control bg-black text-light border-secondary"}),
    )
    profession = forms.CharField(
        label="Profesión",
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control bg-black text-light border-secondary"}),
    )
    license_number = forms.CharField(
        label="Matrícula",
        max_length=50,
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control bg-black text-light border-secondary"}),
    )
    dni = forms.CharField(
        label="DNI",
        max_length=15,
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control bg-black text-light border-secondary"}),
    )

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user
        if user:
            self.fields["first_name"].initial = user.first_name
            self.fields["last_name"].initial = user.last_name
            self.fields["email"].initial = user.email
            self.fields["profession"].initial = user.profession
            self.fields["license_number"].initial = user.license_number
            self.fields["dni"].initial = user.dni

    def clean_email(self):
        email = self.cleaned_data.get("email", "").strip().lower()
        if self.user and User.objects.filter(email__iexact=email).exclude(pk=self.user.pk).exists():
            raise forms.ValidationError("Este email ya está en uso por otro usuario.")
        return email


class ChangePasswordForm(forms.Form):
    """Formulario de cambio de contraseña."""

    current_password = forms.CharField(
        label="Contraseña actual",
        widget=forms.PasswordInput(attrs={"class": "form-control bg-black text-light border-secondary"}),
    )
    new_password1 = forms.CharField(
        label="Nueva contraseña",
        min_length=8,
        widget=forms.PasswordInput(attrs={"class": "form-control bg-black text-light border-secondary"}),
    )
    new_password2 = forms.CharField(
        label="Confirmar nueva contraseña",
        widget=forms.PasswordInput(attrs={"class": "form-control bg-black text-light border-secondary"}),
    )

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user

    def clean_current_password(self):
        password = self.cleaned_data.get("current_password")
        if self.user and not self.user.check_password(password):
            raise forms.ValidationError("La contraseña actual es incorrecta.")
        return password

    def clean(self):
        cleaned_data = super().clean()
        p1 = cleaned_data.get("new_password1")
        p2 = cleaned_data.get("new_password2")
        if p1 and p2 and p1 != p2:
            self.add_error("new_password2", "Las contraseñas no coinciden.")
        return cleaned_data
