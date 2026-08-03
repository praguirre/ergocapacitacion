"""Resolución autorizada de enlaces desde eventos de agenda al protocolo."""

from django import template
from django.urls import reverse

from apps.ergonomia_886.planillas.agenda import RELATED_OBJECT_TYPE
from apps.ergonomia_886.planillas.models import SeguimientoMedida
from apps.ergonomia_886.planillas.querysets import evaluaciones_visibles_para


register = template.Library()


@register.simple_tag
def medida_protocolo_url(event, user):
    """Devuelve Planilla 4 sólo si el usuario puede ver esa evaluación."""
    if event.related_object_type != RELATED_OBJECT_TYPE:
        return ""
    try:
        seguimiento = (
            SeguimientoMedida.objects.filter(
                pk=event.related_object_id,
                medida_especifica__planilla3__evaluacion__in=(
                    evaluaciones_visibles_para(user)
                ),
            )
            .select_related("medida_especifica__planilla3")
            .first()
        )
    except (TypeError, ValueError):
        return ""
    if seguimiento is None:
        return ""
    evaluacion_id = seguimiento.medida_especifica.planilla3.evaluacion_id
    return reverse("planillas:planilla4", args=[evaluacion_id])


__all__ = ("medida_protocolo_url",)
