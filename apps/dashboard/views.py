# apps/dashboard/views.py
# ============================================================================
# COMMIT 15-17: Dashboard, Menu y Selector de Modalidad
# ============================================================================

from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render

from apps.accounts.decorators import professional_required
from apps.training.models import TrainingModule


@login_required
@professional_required
def home(request):
    """
    Dashboard principal del profesional.
    Muestra selector de Evaluaciones / Capacitaciones y stats basicas.
    """
    stats = {
        "capacitaciones_total": 0,
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
def profile(request):
    """Perfil del profesional (placeholder - se completa en Commit 26)."""
    return render(request, "dashboard/profile.html")


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
