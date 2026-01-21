# apps/accounts/forms.py
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
        help_text="Ingresá solo números, sin guiones ni puntos." # Agregamos esto
    )
    email = forms.EmailField(label="Email")
    job_title = forms.CharField(label="Puesto", max_length=200)
    company_name = forms.CharField(label="Empresa", max_length=200)

    def clean_cuil(self):
        return normalize_cuil(self.cleaned_data["cuil"])

    def clean_email(self):
        return (self.cleaned_data["email"] or "").strip().lower()

class LoginForm(forms.Form):
    cuil = forms.CharField(
        label="CUIL", 
        max_length=20,
        help_text="Ingresá solo números, sin guiones ni puntos." # Agregamos esto
    )
    email = forms.EmailField(label="Email")

    def clean_cuil(self):
        return normalize_cuil(self.cleaned_data["cuil"])

    def clean_email(self):
        return (self.cleaned_data["email"] or "").strip().lower()