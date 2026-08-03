"""Reglas de visibilidad del módulo de Ergonomía SRT 886/15.

Modelo de propiedad MIXTO (decisión de arquitectura D-9):

    professional  ve las evaluaciones que él creó.
    company       ve las de su propia empresa, sin importar qué profesional
                  las hizo.
    trainee       no ve ninguna: el módulo es del backoffice.

Un profesional NO ve las evaluaciones de otro profesional, aunque ambos
trabajen para la misma empresa. Es el comportamiento actual de ErgoApp y la
opción conservadora: ampliarlo después es aditivo, restringirlo después rompe
expectativas ya creadas.
"""

from apps.company.models import CompanyProfile

from .models import Evaluacion


def evaluaciones_visibles_para(user):
    """Devuelve el queryset de evaluaciones que ``user`` puede ver."""
    if not user.is_authenticated:
        return Evaluacion.objects.none()

    if user.is_professional:
        return Evaluacion.objects.filter(usuario=user)

    if user.is_company:
        try:
            return Evaluacion.objects.filter(empresa=user.company_profile)
        except CompanyProfile.DoesNotExist:
            return Evaluacion.objects.none()

    return Evaluacion.objects.none()


def puede_editar_evaluaciones(user):
    """Sólo un profesional activo emite o modifica un protocolo."""
    return bool(
        user.is_authenticated
        and user.is_professional
        and user.is_active
    )


def obtener_evaluacion_o_404(evaluacion_id, user):
    """Devuelve la evaluación visible o responde 404 para no enumerarla."""
    from django.shortcuts import get_object_or_404

    return get_object_or_404(evaluaciones_visibles_para(user), pk=evaluacion_id)
