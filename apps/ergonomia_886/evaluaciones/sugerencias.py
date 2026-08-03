"""Capacitaciones sugeridas a partir de niveles YA persistidos.

CF-2: este módulo lee niveles existentes. No calcula, deriva, reinterpreta ni
escribe ninguna clasificación; ``calculators.py`` continúa siendo la única
autoridad del motor.
"""

from django.urls import reverse

from apps.training.models import TrainingModule


SUGERENCIAS_POR_FACTOR = {
    "lmc": "ergonomia",
    "transporte": "ergonomia",
    "empuje_inicial": "ergonomia",
    "posturas_forzadas": "ergonomia",
    "repetitivos_ms": "ergonomia",
}

NIVELES_QUE_DISPARAN_SUGERENCIA = {"medio", "alto"}


def sugerencias_para_factores(factores):
    """Agrupa factores medio/alto por módulo activo, sin tocar sus niveles."""
    candidatos = {}
    for factor in factores:
        slug_modulo = SUGERENCIAS_POR_FACTOR.get(factor.get("slug"))
        if (
            slug_modulo
            and factor.get("nivel") in NIVELES_QUE_DISPARAN_SUGERENCIA
        ):
            candidatos.setdefault(slug_modulo, []).append(factor["label"])

    modulos = {
        modulo.slug: modulo
        for modulo in TrainingModule.objects.filter(
            slug__in=candidatos,
            is_active=True,
        )
    }
    return [
        {
            "module": modulos[slug],
            "url": reverse(
                "training_public:training_public",
                args=[slug],
            ),
            "factores": etiquetas,
        }
        for slug, etiquetas in candidatos.items()
        if slug in modulos
    ]


__all__ = (
    "NIVELES_QUE_DISPARAN_SUGERENCIA",
    "SUGERENCIAS_POR_FACTOR",
    "sugerencias_para_factores",
)
