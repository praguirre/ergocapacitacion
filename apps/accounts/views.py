# apps/accounts/views.py
# ============================================================================
# COMMIT 12: Actualizado redirect("landing") → redirect("trainee_landing")
# para compatibilidad con nueva estructura de URLs.
# ============================================================================
# AJUSTE POST-RENAME: templates/accounts/landing.html → trainee_landing.html
# ============================================================================

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.decorators.http import require_GET, require_POST

from .forms import RegisterForm, LoginForm

User = get_user_model()

PENDING_KEY = "pending_register_data"


def _post_login_redirect():
    """
    Determina a dónde enviar al usuario tras un registro o login exitoso.
    Actualizado en Commit 3 para redirigir a la capacitación.
    """
    return reverse("training_home")


@require_GET
def health(_request):
    """Mantenemos el endpoint de salud pero ahora con restricción GET."""
    return HttpResponse("OK")


@require_GET
def landing(request):
    ctx = {
        "register_form": RegisterForm(),
        "login_form": LoginForm(),
    }
    return render(request, "accounts/trainee_landing.html", ctx)


@require_POST
def register_post(request):
    form = RegisterForm(request.POST)
    if not form.is_valid():
        return render(
            request,
            "accounts/trainee_landing.html",
            {
                "register_form": form,
                "login_form": LoginForm(),
            },
        )

    data = form.cleaned_data

    # Validación de duplicados
    if User.objects.filter(cuil=data["cuil"]).exists() or User.objects.filter(email__iexact=data["email"]).exists():
        messages.warning(request, "Ese CUIL o email ya está registrado. Ingresá desde Login.")
        return redirect("trainee_landing")

    request.session[PENDING_KEY] = data
    request.session.modified = True
    return redirect("confirm")


@require_GET
def confirm_get(request):
    data = request.session.get(PENDING_KEY)
    if not data:
        messages.info(request, "No hay datos para confirmar. Completá el registro.")
        return redirect("trainee_landing")
    return render(request, "accounts/confirm.html", {"data": data})


@require_POST
def confirm_post(request):
    data = request.session.get(PENDING_KEY)
    if not data:
        messages.info(request, "No hay datos para confirmar. Completá el registro.")
        return redirect("trainee_landing")

    # =========================================================================
    # ✅ COMMIT 8: Crear usuario incluyendo los nuevos campos de email
    # =========================================================================
    user = User.objects.create_user(
        cuil=data["cuil"],
        email=data["email"],
        full_name=data["full_name"],
        job_title=data["job_title"],
        company_name=data["company_name"],
        # Nuevos campos - usamos .get() con default "" para retrocompatibilidad
        employer_email=data.get("employer_email", ""),
        safety_responsible_email=data.get("safety_responsible_email", ""),
    )
    # =========================================================================

    # Login (sin password, usando nuestro Backend custom)
    login(request, user, backend="apps.accounts.backends.CuilEmailBackend")

    # Limpieza de sesión
    request.session.pop(PENDING_KEY, None)

    messages.success(request, "Registro confirmado. ¡Bienvenido!")
    return redirect(_post_login_redirect())


@require_POST
def login_post(request):
    form = LoginForm(request.POST)
    if not form.is_valid():
        return render(
            request,
            "accounts/trainee_landing.html",
            {
                "register_form": RegisterForm(),
                "login_form": form,
            },
        )

    cuil = form.cleaned_data["cuil"]
    email = form.cleaned_data["email"]
    user = authenticate(request, cuil=cuil, email=email)

    if user is None:
        messages.error(request, "CUIL o email incorrectos, o usuario no registrado.")
        return redirect("trainee_landing")

    login(request, user)
    messages.success(request, "Ingreso exitoso.")
    return redirect(_post_login_redirect())


@require_POST
def logout_post(request):
    logout(request)
    messages.info(request, "Sesión cerrada.")
    return redirect("trainee_landing")