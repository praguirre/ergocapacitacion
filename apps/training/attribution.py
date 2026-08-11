"""Conserva y valida la procedencia de una capacitación online.

La identidad responsable nace en ``CapacitacionLink.created_by``. Este módulo
es la única frontera entre el UUID guardado en sesión y los objetos de dominio:
nunca atribuye un intento a un link vencido, inactivo o de otro módulo.
"""

from __future__ import annotations

from django.db import models

from .models import CapacitacionLink, TrainingModule


CAPACITACION_REF_SESSION_KEY = "capacitacion_ref"
TARGET_MODULE_SESSION_KEY = "target_module_slug"


def clear_capacitacion_ref(request) -> None:
    """Elimina una referencia residual sin alterar el resto de la sesión."""
    request.session.pop(CAPACITACION_REF_SESSION_KEY, None)


def remember_public_link(request, module: TrainingModule, ref_id) -> CapacitacionLink | None:
    """Valida y recuerda un link público; incrementa su contador una sola vez."""
    clear_capacitacion_ref(request)
    if not ref_id:
        return None

    try:
        link = CapacitacionLink.objects.select_related("created_by").get(
            id=ref_id,
            module=module,
        )
    except (CapacitacionLink.DoesNotExist, ValueError, TypeError):
        return None

    if not link.is_usable:
        return None

    CapacitacionLink.objects.filter(id=link.id).update(
        access_count=models.F("access_count") + 1
    )
    request.session[CAPACITACION_REF_SESSION_KEY] = str(link.id)
    return link


def session_link_for_module(request, module: TrainingModule) -> CapacitacionLink | None:
    """Resuelve el link de sesión y descarta cualquier atribución insegura."""
    ref_id = request.session.get(CAPACITACION_REF_SESSION_KEY)
    if not ref_id:
        return None

    try:
        link = CapacitacionLink.objects.select_related("created_by").get(
            id=ref_id,
            module=module,
        )
    except (CapacitacionLink.DoesNotExist, ValueError, TypeError):
        clear_capacitacion_ref(request)
        return None

    if not link.is_usable:
        clear_capacitacion_ref(request)
        return None
    return link


def responsible_professional(link: CapacitacionLink):
    """Devuelve un profesional documentalmente completo o ``None``.

    Una cuenta empresa no se transforma implícitamente en profesional y los
    campos faltantes no se sustituyen con datos globales.
    """
    user = link.created_by
    if not getattr(user, "is_professional", False):
        return None
    if not all((user.display_name, user.profession, user.license_number)):
        return None
    return user
