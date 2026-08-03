# exportaciones/packaging.py
"""Armado del paquete documental completo de una evaluación."""

from __future__ import annotations

import io
import zipfile

from django.utils import timezone
from django.utils.text import slugify

from apps.ergonomia_886.evaluaciones.catalog import FACTOR_DEFINITIONS
from apps.ergonomia_886.evaluaciones.models import RiskEvaluation

from . import serializers
from .official.builders import build_protocolo_pages
from .official.catalog import PLANILLA_DEFINITIONS
from .official.overlay import stamp_official_pdf
from .reports.pdf import AVISO_LEGAL, build_factor_detail_pdf

LEEME = """\
PAQUETE DOCUMENTAL — ErgoApp SRT 886
====================================

Evaluación: #{evaluacion_id}
Razón social: {razon_social}
Generado: {generado}

Contenido
---------
01-protocolo-oficial/   Planillas 1 a 4 en el formato oficial de la
                        Resolución SRT N° 886/15, completadas con los datos
                        cargados en ErgoApp. Tamaño de página: Carta.
02-detalle-tecnico/     Detalle cuantitativo de cada factor evaluado, con
                        todos los datos de entrada y la trazabilidad completa
                        del cálculo (límites aplicados, tablas utilizadas,
                        versión y checksum de cada fuente normativa).

Criterios aplicados
-------------------
- Una respuesta se marca como "NO" únicamente si la planilla correspondiente
  fue guardada. Si nunca se completó, la página se emite en blanco.
- En la Planilla 1, la presencia de un factor en una tarea se deriva de que se
  haya asignado un nivel de riesgo a esa tarea.
- Los niveles de riesgo de los factores cuantitativos se expresan también en la
  escala oficial 1 (Tolerable) / 2 (Moderado) / 3 (No Tolerable).

Aviso
-----
{aviso}
"""


def build_evaluation_package(evaluacion) -> bytes:
    """Devuelve un ZIP en memoria con el paquete documental completo."""
    buffer = io.BytesIO()
    ahora = timezone.localtime()
    payload = serializers.build_evaluacion_payload(evaluacion)
    empresa = slugify(evaluacion.razon_social)[:40] or "evaluacion"

    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr(
            "LEEME.txt",
            LEEME.format(
                evaluacion_id=evaluacion.pk,
                razon_social=evaluacion.razon_social,
                generado=ahora.strftime("%d/%m/%Y %H:%M"),
                aviso=AVISO_LEGAL,
            ),
        )

        # 1) Protocolo oficial completo, en un único PDF de 12+ páginas.
        zf.writestr(
            f"01-protocolo-oficial/{empresa}-protocolo-completo.pdf",
            stamp_official_pdf(build_protocolo_pages(payload)),
        )

        # 2) Detalle técnico de los factores iniciados.
        risk_eval = RiskEvaluation.objects.filter(evaluacion=evaluacion).first()
        if risk_eval is not None:
            cabecera = serializers.build_cabecera(evaluacion)
            for definition in FACTOR_DEFINITIONS:
                factor_payload = serializers.build_factor_payload(
                    risk_eval, definition.slug
                )
                if not factor_payload.get("existe"):
                    continue
                zf.writestr(
                    f"02-detalle-tecnico/{definition.slug}.pdf",
                    build_factor_detail_pdf(
                        cabecera=cabecera,
                        factores=[factor_payload],
                        generado_en=ahora,
                        titulo=f"Detalle técnico — {definition.label}",
                    ),
                )

    return buffer.getvalue()


__all__ = ("build_evaluation_package",)
