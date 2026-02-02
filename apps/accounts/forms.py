# apps/accounts/forms.py
# ============================================================================
# COMMIT 8: Agregados campos employer_email y safety_responsible_email
# ============================================================================
from django import forms
from django.core.validators import RegexValidator
import re

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
        help_text="Ingresá solo números, sin guiones ni puntos."
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
        help_text="Email del empleador para recibir copia del certificado (opcional)"
    )
    safety_responsible_email = forms.EmailField(
        label="Email del responsable de Seg. e Higiene",
        required=False,
        help_text="Email del responsable de Seguridad e Higiene, Salud o Ergonomía (opcional)"
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
        help_text="Ingresá solo números, sin guiones ni puntos."
    )
    email = forms.EmailField(label="Email")

    def clean_cuil(self):
        return normalize_cuil(self.cleaned_data["cuil"])

    def clean_email(self):
        return (self.cleaned_data["email"] or "").strip().lower()
