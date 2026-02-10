# apps/accounts/forms.py
# ============================================================================
# COMMIT 8: Agregados campos employer_email y safety_responsible_email
# COMMIT 13: Formularios para profesionales
# ============================================================================

import re

from django import forms
from django.contrib.auth import get_user_model
from django.core.validators import RegexValidator

User = get_user_model()


def normalize_cuil(value: str) -> str:
    digits = re.sub(r"\D", "", (value or "").strip())
    if len(digits) != 11:
        raise forms.ValidationError("CUIL inválido (debe tener 11 dígitos).")
    return digits


class RegisterForm(forms.Form):
    full_name = forms.CharField(label="Nombre y apellido", max_length=200)
    cuil = forms.CharField(
        label="CUIL",
        max_length=20,
        validators=[RegexValidator(r"^[0-9\-\. ]+$", "CUIL inválido.")],
        help_text="Ingresá solo números, sin guiones ni puntos.",
    )
    email = forms.EmailField(label="Email")
    job_title = forms.CharField(label="Puesto", max_length=200)
    company_name = forms.CharField(label="Empresa", max_length=200)

    # =========================================================================
    # ✅ COMMIT 8: Nuevos campos de email para notificaciones de certificados
    # =========================================================================
    employer_email = forms.EmailField(
        label="Email del empleador",
        required=False,
        help_text="Email del empleador para recibir copia del certificado (opcional)",
    )
    safety_responsible_email = forms.EmailField(
        label="Email del responsable de Seg. e Higiene",
        required=False,
        help_text="Email del responsable de Seguridad e Higiene, Salud o Ergonomía (opcional)",
    )
    # =========================================================================

    def clean_cuil(self):
        return normalize_cuil(self.cleaned_data["cuil"])

    def clean_email(self):
        return (self.cleaned_data["email"] or "").strip().lower()

    # =========================================================================
    # ✅ COMMIT 8: Normalización de los nuevos campos de email
    # =========================================================================
    def clean_employer_email(self):
        email = self.cleaned_data.get("employer_email") or ""
        return email.strip().lower()

    def clean_safety_responsible_email(self):
        email = self.cleaned_data.get("safety_responsible_email") or ""
        return email.strip().lower()
    # =========================================================================


class LoginForm(forms.Form):
    cuil = forms.CharField(
        label="CUIL",
        max_length=20,
        help_text="Ingresá solo números, sin guiones ni puntos.",
    )
    email = forms.EmailField(label="Email")

    def clean_cuil(self):
        return normalize_cuil(self.cleaned_data["cuil"])

    def clean_email(self):
        return (self.cleaned_data["email"] or "").strip().lower()


# ============================================================================
# COMMIT 13: Formularios para profesionales
# ============================================================================

class ProfessionalRegisterForm(forms.Form):
    """Formulario de registro para profesionales de SySO."""

    first_name = forms.CharField(
        label="Nombre",
        max_length=100,
        widget=forms.TextInput(attrs={"placeholder": "Juan"}),
    )
    last_name = forms.CharField(
        label="Apellido",
        max_length=100,
        widget=forms.TextInput(attrs={"placeholder": "Pérez"}),
    )
    dni = forms.CharField(
        label="DNI",
        max_length=15,
        validators=[RegexValidator(r"^\d{7,8}$", "DNI inválido (7-8 dígitos)")],
        widget=forms.TextInput(attrs={"placeholder": "12345678"}),
        help_text="Solo números, sin puntos",
    )
    email = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(attrs={"placeholder": "juan.perez@ejemplo.com"}),
    )
    profession = forms.CharField(
        label="Profesión",
        max_length=100,
        widget=forms.TextInput(attrs={"placeholder": "Lic. en Higiene y Seguridad"}),
        help_text="Ej: Lic. en Higiene y Seguridad, Médico Laboral, Ergónomo",
    )
    license_number = forms.CharField(
        label="Matrícula profesional",
        max_length=50,
        widget=forms.TextInput(attrs={"placeholder": "MN 12345"}),
        required=False,
        help_text="Opcional",
    )
    username = forms.CharField(
        label="Usuario",
        max_length=50,
        validators=[
            RegexValidator(
                r"^[\w.@+-]+$",
                "Usuario inválido. Solo letras, números y @/./+/-/_",
            )
        ],
        widget=forms.TextInput(attrs={"placeholder": "jperez"}),
        help_text="Para iniciar sesión",
    )
    password1 = forms.CharField(
        label="Contraseña",
        widget=forms.PasswordInput(attrs={"placeholder": "••••••••"}),
        min_length=8,
        help_text="Mínimo 8 caracteres",
    )
    password2 = forms.CharField(
        label="Confirmar contraseña",
        widget=forms.PasswordInput(attrs={"placeholder": "••••••••"}),
    )

    def clean_dni(self):
        dni = re.sub(r"\D", "", self.cleaned_data.get("dni", ""))
        if len(dni) < 7 or len(dni) > 8:
            raise forms.ValidationError("DNI inválido")
        return dni

    def clean_email(self):
        email = (self.cleaned_data.get("email") or "").strip().lower()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("Este email ya está registrado")
        return email

    def clean_username(self):
        username = (self.cleaned_data.get("username") or "").strip().lower()
        if User.objects.filter(username__iexact=username).exists():
            raise forms.ValidationError("Este usuario ya está en uso")
        return username

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")

        if password1 and password2 and password1 != password2:
            self.add_error("password2", "Las contraseñas no coinciden")

        return cleaned_data


class ProfessionalLoginForm(forms.Form):
    """Formulario de login para profesionales."""

    username = forms.CharField(
        label="Usuario o Email",
        widget=forms.TextInput(attrs={"placeholder": "usuario o email"}),
    )
    password = forms.CharField(
        label="Contraseña",
        widget=forms.PasswordInput(attrs={"placeholder": "••••••••"}),
    )
