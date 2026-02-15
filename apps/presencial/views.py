# apps/presencial/views.py
# ============================================================================
# COMMIT 18: Vistas de capacitación presencial
# ============================================================================

from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render
from django.views.decorators.csrf import ensure_csrf_cookie

from apps.accounts.decorators import professional_required
from apps.training.models import TrainingModule


@login_required
@professional_required
@ensure_csrf_cookie
def capacitacion_presencial(request, module_slug):
    """
    Página de capacitación para uso presencial.
    Incluye video + chat Ergobot, sin registro de trabajadores.
    Diseñada para proyección en sala.
    """
    module = get_object_or_404(TrainingModule, slug=module_slug, is_active=True)

    return render(request, 'presencial/capacitacion.html', {
        'module': module,
    })
