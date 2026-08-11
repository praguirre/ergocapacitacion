from django.shortcuts import get_object_or_404, redirect

from .attribution import remember_public_link
from .models import TrainingModule


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

    remember_public_link(request, module, ref_id)

    if request.user.is_authenticated and getattr(request.user, "is_trainee", False):
        return redirect("training:training_home")

    return redirect("accounts:trainee_landing")
