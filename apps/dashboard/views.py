# apps/dashboard/views.py
# ============================================================================
# COMMIT 15-23: Dashboard, Capacitaciones y Links Online
# ============================================================================

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from apps.accounts.decorators import professional_required
from apps.presencial.models import PresencialSession
from apps.training.models import CapacitacionLink, TrainingModule


@login_required
@professional_required
def home(request):
    """
    Dashboard principal del profesional.
    Muestra selector de Evaluaciones / Capacitaciones y stats basicas.
    """
    presencial_count = PresencialSession.objects.filter(
        professional=request.user
    ).count()

    stats = {
        "capacitaciones_total": presencial_count,
        "links_generados": 0,
        "trabajadores_capacitados": 0,
    }

    return render(request, "dashboard/home.html", {
        "stats": stats,
    })


@login_required
@professional_required
def capacitaciones_menu(request):
    """
    Menu de capacitaciones disponibles.
    Muestra grid de cards con iconos y estados.
    """
    modules = TrainingModule.objects.all()

    return render(request, "dashboard/capacitaciones_menu.html", {
        "modules": modules,
    })


@login_required
@professional_required
def modalidad_selector(request, module_slug):
    """
    Selector de modalidad: Presencial u Online.
    """
    module = get_object_or_404(TrainingModule, slug=module_slug, is_active=True)

    return render(request, "dashboard/modalidad_selector.html", {
        "module": module,
    })


@login_required
@professional_required
def online_links(request, module_slug):
    """
    Gestión de links para una capacitación online.
    Lista links existentes y permite crear nuevos.
    """
    module = get_object_or_404(TrainingModule, slug=module_slug, is_active=True)

    links = CapacitacionLink.objects.filter(
        module=module,
        created_by=request.user,
    ).order_by("-created_at")

    return render(request, "dashboard/online_links.html", {
        "module": module,
        "links": links,
    })


@login_required
@professional_required
@require_POST
def generate_link(request, module_slug):
    """Genera un nuevo link de capacitación."""
    module = get_object_or_404(TrainingModule, slug=module_slug, is_active=True)

    label = request.POST.get("label", "").strip()

    CapacitacionLink.objects.create(
        module=module,
        created_by=request.user,
        label=label,
    )

    messages.success(request, "Link generado exitosamente.")
    return redirect("dashboard:online_links", module_slug=module_slug)


@login_required
@professional_required
def profile(request):
    """Perfil del profesional (placeholder - se completa en Commit 26)."""
    return render(request, "dashboard/profile.html")
