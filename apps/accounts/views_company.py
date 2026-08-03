# apps/accounts/views_company.py
# ============================================================================
# COMMIT 32: Vistas de autenticación para empresas
# ============================================================================

from django.contrib import messages
from django.contrib.auth import authenticate, login, get_user_model
from django.shortcuts import render, redirect
from django.views.decorators.http import require_http_methods

from .forms import CompanyRegisterForm, ProfessionalLoginForm
from apps.company.models import CompanyProfile

User = get_user_model()


@require_http_methods(["GET", "POST"])
def company_register(request):
    """Registro de empresas. Crea CustomUser + CompanyProfile."""
    if request.user.is_authenticated:
        if request.user.is_backoffice_user:
            return redirect("dashboard:home")
        return redirect("training:training_home")

    if request.method == "POST":
        form = CompanyRegisterForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data

            # 1. Crear el CustomUser tipo company
            parts = cd["contacto_nombre"].strip().split(" ", 1)
            first = parts[0]
            last = parts[1] if len(parts) > 1 else ""

            user = User.objects.create_company(
                email=cd["email"],
                password=cd["password1"],
                first_name=first,
                last_name=last,
                full_name=cd["contacto_nombre"],
            )

            # 2. Crear el CompanyProfile asociado
            CompanyProfile.objects.create(
                user=user,
                razon_social=cd["razon_social"],
                nombre_comercial=cd.get("nombre_comercial", ""),
                cuit=cd["cuit"],
                rubro=cd.get("rubro", ""),
                cantidad_trabajadores=cd.get("cantidad_trabajadores") or 0,
                contacto_nombre=cd["contacto_nombre"],
                contacto_cargo=cd.get("contacto_cargo", ""),
                contacto_telefono=cd.get("contacto_telefono", ""),
                domicilio=cd.get("domicilio", ""),
                provincia=cd.get("provincia", ""),
            )

            # 3. Login automático
            login(request, user, backend='apps.accounts.backends.ProfessionalBackend')

            messages.success(
                request,
                f"¡Bienvenido! La cuenta de {cd['razon_social']} ha sido creada exitosamente.",
            )
            return redirect("dashboard:home")
    else:
        form = CompanyRegisterForm()

    return render(request, "accounts/company/register.html", {"form": form})


@require_http_methods(["GET", "POST"])
def company_login(request):
    """Login de empresas. Reutiliza ProfessionalLoginForm con verificación de tipo."""
    if request.user.is_authenticated:
        if request.user.is_backoffice_user:
            return redirect("dashboard:home")
        return redirect("training:training_home")

    if request.method == "POST":
        form = ProfessionalLoginForm(request.POST)
        if form.is_valid():
            identifier = form.cleaned_data["username"]
            password = form.cleaned_data["password"]

            user = authenticate(request, username=identifier, password=password)

            if user is not None:
                if not user.is_company:
                    messages.error(
                        request,
                        "Esta cuenta no es de empresa. "
                        "Si sos profesional, usá el login de profesionales.",
                    )
                    return render(request, "accounts/company/login.html", {"form": form})

                login(request, user)
                messages.success(request, f"Bienvenido, {user.display_name}")

                next_url = request.GET.get("next") or request.POST.get("next")
                return redirect(next_url or "dashboard:home")
            else:
                messages.error(request, "Email o contraseña incorrectos.")
    else:
        form = ProfessionalLoginForm()

    return render(request, "accounts/company/login.html", {"form": form})
