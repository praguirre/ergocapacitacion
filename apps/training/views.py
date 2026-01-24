# apps/training/views.py

from django.views.decorators.csrf import ensure_csrf_cookie
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .models import TrainingModule

@ensure_csrf_cookie
@login_required(login_url="landing")
def training_home(request):
    """
    Obtiene el módulo de capacitación más reciente que esté activo
    y lo envía al template de la página de entrenamiento.
    """
    module = (
        TrainingModule.objects
        .filter(is_active=True)
        .order_by("-updated_at")
        .first()
    )
    
    # Enviamos el módulo en el contexto bajo el nombre 'module'
    return render(request, "training/training_page.html", {"module": module})