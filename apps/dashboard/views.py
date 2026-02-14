# apps/dashboard/views.py
# ============================================================================
# COMMIT 15-16: Dashboard y Menu de Capacitaciones
# ============================================================================

from django.contrib.auth.decorators import login_required
from django.shortcuts import render

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
