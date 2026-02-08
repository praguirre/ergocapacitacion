# apps/landing/views.py
# ============================================================================
# COMMIT 12: Landing page completa
# ============================================================================

from django.shortcuts import render, redirect
from django.views.decorators.http import require_GET


@require_GET
def home(request):
    """
    Landing page principal de ErgoSolutions.
    Redirige usuarios autenticados a su área correspondiente.
    """
    if request.user.is_authenticated:
        if request.user.is_professional:
            return redirect("dashboard:home")
        return redirect("training_home")

    return render(request, "landing/home.html")
