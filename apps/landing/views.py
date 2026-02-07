# apps/landing/views.py

# ============================================================================
# COMMIT 11: Vista placeholder para landing (se completa en Commit 12)
# ============================================================================


from django.shortcuts import redirect
from django.views.decorators.http import require_GET

@require_GET
def home(request):
    """
    Landing page principal de ErgoSolutions.
    Si el usuario ya está logueado, redirige al área correspondiente.
    """
    if request.user.is_authenticated:
        if request.user.is_professional:
            return redirect('dashboard:home')
        return redirect('training_home')

    # Por ahora, redirigimos al landing actual de capacitaciones (accounts)
    return redirect('landing')
