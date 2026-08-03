"""Proyección unidireccional de medidas correctivas hacia la agenda.

La agenda refleja el protocolo y nunca escribe en él. CF-2: la prioridad sólo
mapea el entero ya persistido en ``SeguimientoMedida.nivel_riesgo``; no calcula
ni reclasifica ningún nivel de riesgo.
"""

from datetime import datetime, time

from django.utils import timezone

from apps.company.models import AgendaEvent


RELATED_OBJECT_TYPE = "ergonomia_886.SeguimientoMedida"

_PRIORIDAD_POR_NIVEL = {
    1: AgendaEvent.Priority.LOW,
    2: AgendaEvent.Priority.HIGH,
    3: AgendaEvent.Priority.URGENT,
}


def sincronizar_medida_con_agenda(seguimiento):
    """Crea o actualiza el evento correspondiente a una medida guardada."""
    evaluacion = seguimiento.medida_especifica.planilla3.evaluacion
    empresa = evaluacion.empresa
    if empresa is None:
        return None

    fecha = seguimiento.fecha_impl_ing or seguimiento.fecha_impl_admin
    if fecha is None:
        return None

    descripcion = seguimiento.medida_especifica.descripcion
    evento, _ = AgendaEvent.objects.update_or_create(
        company=empresa,
        related_object_type=RELATED_OBJECT_TYPE,
        related_object_id=str(seguimiento.pk),
        defaults={
            "title": f"Medida correctiva ergonómica - {descripcion[:80]}",
            "description": seguimiento.medida_especifica.observaciones or "",
            "event_type": AgendaEvent.EventType.EVALUATION_DUE,
            "due_at": timezone.make_aware(datetime.combine(fecha, time.min)),
            "status": (
                AgendaEvent.EventStatus.COMPLETED
                if seguimiento.fecha_cierre
                else AgendaEvent.EventStatus.PENDING
            ),
            "priority": _PRIORIDAD_POR_NIVEL.get(
                seguimiento.nivel_riesgo,
                AgendaEvent.Priority.MEDIUM,
            ),
            "assigned_professional": evaluacion.usuario,
        },
    )
    return evento


__all__ = ("RELATED_OBJECT_TYPE", "sincronizar_medida_con_agenda")
