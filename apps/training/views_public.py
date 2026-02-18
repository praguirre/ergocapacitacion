from django.db import models
from django.shortcuts import get_object_or_404, redirect

from .models import CapacitacionLink, TrainingModule


def public_landing(request, module_slug):
    """
    Landing de capacitación accedida vía link compartido.
    - Si tiene parámetro ref, trackea el acceso
    - Guarda sesión para redirección posterior
    - Redirige según tipo de usuario
    """
    module = get_object_or_404(TrainingModule, slug=module_slug, is_active=True)
    ref_id = request.GET.get("ref")

    # Siempre guardamos el módulo objetivo para un posible flujo post-login.
    request.session["target_module_slug"] = module.slug

    if ref_id:
        try:
            link = CapacitacionLink.objects.get(id=ref_id, module=module)
            if link.is_usable:
                CapacitacionLink.objects.filter(id=link.id).update(
                    access_count=models.F("access_count") + 1
                )
                request.session["capacitacion_ref"] = str(link.id)
        except (CapacitacionLink.DoesNotExist, ValueError, TypeError):
            pass

    if request.user.is_authenticated and getattr(request.user, "is_trainee", False):
        return redirect("training_home")

    return redirect("trainee_landing")
