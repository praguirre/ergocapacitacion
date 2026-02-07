# apps/dashboard/views.py
# ============================================================================
# COMMIT 11: Vistas placeholder para dashboard (se completan en Fase 3)
# ============================================================================

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from apps.accounts.decorators import professional_required


@login_required
@professional_required
def home(request):
    """
    Dashboard principal del profesional.
    Muestra selector de Evaluaciones / Capacitaciones.
    """
    # Placeholder - se completa en Commit 15
    return render(request, "dashboard/home.html", {
        "user": request.user,
    })


@login_required
@professional_required
def profile(request):
    """Perfil del profesional."""
    # Placeholder - se completa en Commit 26
    return render(request, "dashboard/profile.html", {
        "user": request.user,
    })
