"""Catálogo canónico de módulos de Evaluación de Seguridad e Higiene.

Un protocolo habilitado requiere código, URLs, formularios y cálculos propios;
por eso el catálogo vive en Python y no agrega estados inválidos en la base de
datos. Una card se considera disponible únicamente cuando declara ``url_name``.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class EvaluationModule:
    slug: str
    title: str
    description: str
    icon: str
    color: str
    url_name: str | None = None
    order: int = 0

    @property
    def is_active(self) -> bool:
        return self.url_name is not None


EVALUATION_MODULES: tuple[EvaluationModule, ...] = (
    EvaluationModule(
        slug="ergonomia-886",
        title="Ergonomía",
        description=(
            "Protocolo SRT 886/15: identificación de factores de riesgo, "
            "evaluación de los 13 factores y planillas oficiales."
        ),
        icon="bi bi-person-arms-up",
        color="#0d6efd",
        url_name="ergonomia_886:evaluacion_list",
        order=10,
    ),
    EvaluationModule(
        slug="iluminacion",
        title="Iluminación",
        description=(
            "Protocolo de medición de iluminación en el ambiente laboral "
            "conforme a la Resolución SRT 84/12."
        ),
        icon="bi bi-lightbulb",
        color="#ffc107",
        order=20,
    ),
    EvaluationModule(
        slug="ruido",
        title="Ruido",
        description=(
            "Protocolo de medición de ruido, dosimetría y nivel sonoro "
            "continuo equivalente conforme a la Resolución SRT 85/12."
        ),
        icon="bi bi-volume-up",
        color="#fd7e14",
        order=30,
    ),
    EvaluationModule(
        slug="carga-termica",
        title="Carga Térmica",
        description=(
            "Evaluación de estrés térmico por TGBH, condiciones ambientales "
            "y régimen de trabajo y descanso."
        ),
        icon="bi bi-thermometer-sun",
        color="#dc3545",
        order=40,
    ),
    EvaluationModule(
        slug="puesta-a-tierra",
        title="Puesta a Tierra y Continuidad",
        description=(
            "Medición de puesta a tierra y verificación de continuidad de "
            "masas conforme a la Resolución SRT 900/15."
        ),
        icon="bi bi-plug",
        color="#6f42c1",
        order=50,
    ),
    EvaluationModule(
        slug="contaminantes-quimicos",
        title="Contaminantes Químicos",
        description=(
            "Muestreo y evaluación de contaminantes químicos presentes en "
            "el aire del ambiente de trabajo."
        ),
        icon="bi bi-droplet-half",
        color="#20c997",
        order=60,
    ),
)


def get_evaluation_modules() -> list[EvaluationModule]:
    """Devuelve una copia ordenada del catálogo."""
    return sorted(EVALUATION_MODULES, key=lambda module: (module.order, module.title))
