from django.http import HttpResponseForbidden


def check_module_access(module, user):
    """
    Permite acceso libre a módulos generales.
    Restringe módulos personalizados a sus profesionales asignados.
    """
    if not module.is_personalized:
        return None

    if module.assigned_professionals.filter(pk=user.pk).exists():
        return None

    return HttpResponseForbidden(
        "No tenés acceso a esta capacitación personalizada."
    )
