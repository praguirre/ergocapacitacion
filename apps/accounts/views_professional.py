# apps/accounts/views_professional.py
# ============================================================================
# COMMIT 13-14: Vistas de autenticación para profesionales
# ============================================================================

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.shortcuts import render, redirect
from django.views.decorators.http import require_http_methods, require_POST

from .forms import ProfessionalRegisterForm, ProfessionalLoginForm

User = get_user_model()


@require_http_methods(["GET", "POST"])
def register(request):
    """Registro de profesionales."""
    if request.user.is_authenticated:
        # Si ya está logueado y es profesional -> dashboard
        if request.user.is_professional:
            return redirect("dashboard:home")
        # Si es trainee logueado -> capacitación
        return redirect("training_home")

    if request.method == "POST":
        form = ProfessionalRegisterForm(request.POST)
        if form.is_valid():
            # Crear el usuario profesional usando el manager custom (Commit 9)
            user = User.objects.create_professional(
                email=form.cleaned_data["email"],
                password=form.cleaned_data["password1"],
                username=form.cleaned_data["username"],
                first_name=form.cleaned_data["first_name"],
                last_name=form.cleaned_data["last_name"],
                dni=form.cleaned_data["dni"],
                profession=form.cleaned_data["profession"],
                license_number=form.cleaned_data.get("license_number", ""),
            )

            # Login automático usando el backend de profesionales (Commit 10)
            login(request, user, backend="apps.accounts.backends.ProfessionalBackend")

            messages.success(request, f"¡Bienvenido {user.first_name}! Tu cuenta ha sido creada.")
            return redirect("dashboard:home")
    else:
        form = ProfessionalRegisterForm()

    return render(request, "accounts/professional/register.html", {"form": form})


@require_http_methods(["GET", "POST"])
def login_view(request):
    """Login de profesionales."""
    if request.user.is_authenticated:
        if request.user.is_professional:
            return redirect("dashboard:home")
        return redirect("training_home")

    # Preservar next tanto por GET (primer acceso) como por POST (submit)
    next_url = request.POST.get("next") or request.GET.get("next", "")

    if request.method == "POST":
        form = ProfessionalLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password"]

            # Autenticación dual (Commit 10) -> ProfessionalBackend soporta email o username
            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)
                name = getattr(user, "display_name", "") or user.first_name or user.email
                messages.success(request, f"¡Hola {name}!")

                if next_url and next_url.startswith("/"):
                    return redirect(next_url)
                return redirect("dashboard:home")

            messages.error(request, "Usuario o contraseña incorrectos.")
    else:
        form = ProfessionalLoginForm()

    return render(
        request,
        "accounts/professional/login.html",
        {
            "form": form,
            "next": next_url,
        },
    )


@require_POST
def logout_view(request):
    """Logout de profesionales."""
    logout(request)
    messages.info(request, "Has cerrado sesión.")
    return redirect("landing:home")