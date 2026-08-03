# exportaciones/reports/llm.py
"""Generación del informe técnico profesional con el modelo configurado.

Este módulo redacta. No calcula, no clasifica y no decide niveles de riesgo:
esa autoridad es exclusiva de `evaluaciones/calculators.py`.
"""

from __future__ import annotations

import asyncio
import logging
import time
from dataclasses import dataclass
from typing import Any, Dict

from agents import Agent, RunConfig, Runner
from django.conf import settings

from ..models import EstadoInforme, GeneratedReport, TipoDocumento, payload_fingerprint
from .prompts import PROMPT_VERSION, SYSTEM_PROMPT, build_user_prompt

logger = logging.getLogger(__name__)

# Claves que NUNCA se envían al proveedor del modelo.
CLAVES_PROHIBIDAS = frozenset({
    "nombres_trabajadores", "cuit", "direccion", "ubicacion_sintoma",
    "salud_columna", "revisado_por", "evaluacion_id", "instancia_id",
    "medida_id", "foto_montaje", "certificado_calibracion",
    "evidencia_declarada",
})

# Tope de tamaño del payload. calc_data de VCE con muchos tramos puede crecer.
MAX_PAYLOAD_CHARS = 24_000


class ReportGenerationError(RuntimeError):
    """El informe no pudo generarse."""


@dataclass(frozen=True)
class ReportResult:
    markdown: str
    modelo: str
    prompt_version: str
    inputs_hash: str
    duracion_ms: int
    payload_enviado: Dict[str, Any]


def sanitize_payload(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Elimina recursivamente los datos personales y recorta lo excesivo."""
    def _limpiar(valor: Any) -> Any:
        if isinstance(valor, dict):
            return {
                k: _limpiar(v)
                for k, v in valor.items()
                if k not in CLAVES_PROHIBIDAS
            }
        if isinstance(valor, list):
            return [_limpiar(v) for v in valor]
        return valor

    limpio = _limpiar(payload)

    # El contexto se reconstruye explícitamente con lo mínimo indispensable.
    contexto = limpio.pop("contexto", {}) or {}
    limpio["contexto"] = {
        "razon_social": contexto.get("razon_social", ""),
        "area_sector": contexto.get("area_sector", ""),
        "puesto_trabajo": contexto.get("puesto_trabajo", ""),
        "provincia": contexto.get("provincia", ""),
    }
    return limpio


def _agente_informe() -> Agent:
    """Agente sin herramientas, dedicado exclusivamente al informe.

    Deliberadamente NO se cachea con lru_cache: el agente se instancia por
    request y no debe conservar estado entre evaluaciones distintas.
    """
    return Agent(
        name="Redactor de informes técnicos ErgoApp",
        instructions=SYSTEM_PROMPT,
        model=settings.CHAT_AI_MODEL,
        tools=[],
    )


async def _ejecutar(user_prompt: str, timeout_s: float) -> str:
    run = await asyncio.wait_for(
        Runner.run(
            _agente_informe(),
            input=[{"role": "user", "content": user_prompt}],
            max_turns=1,
            run_config=RunConfig(
                workflow_name="ErgoApp-Informe",
                trace_include_sensitive_data=False,
            ),
        ),
        timeout=timeout_s,
    )
    texto = (getattr(run, "final_output", "") or "").strip()
    if not texto:
        raise ReportGenerationError("El modelo devolvió una respuesta vacía.")
    return texto


def build_professional_report(payload: Dict[str, Any], *,
                              timeout_s: float | None = None) -> ReportResult:
    """Genera el informe de un factor. Bloqueante; pensado para vista síncrona."""
    limpio = sanitize_payload(payload)
    user_prompt = build_user_prompt(limpio)

    if len(user_prompt) > MAX_PAYLOAD_CHARS:
        raise ReportGenerationError(
            "Los datos del factor superan el tamaño máximo admitido para "
            "generar el informe. Reducí la cantidad de tramos cargados o "
            "generá el informe por partes."
        )

    limite = float(
        timeout_s
        if timeout_s is not None
        else getattr(settings, "REPORT_AI_TIMEOUT_SECONDS", 90)
    )

    inicio = time.monotonic()
    try:
        markdown = asyncio.run(_ejecutar(user_prompt, limite))
    except asyncio.TimeoutError as exc:
        raise ReportGenerationError(
            "La generación del informe superó el tiempo máximo permitido."
        ) from exc
    except ReportGenerationError:
        raise
    except Exception as exc:  # el SDK puede levantar excepciones propias
        logger.exception(
            "Fallo al generar el informe factor=%s", limpio.get("factor_slug")
        )
        raise ReportGenerationError(
            "No se pudo generar el informe en este momento. Intentá nuevamente."
        ) from exc

    return ReportResult(
        markdown=markdown,
        modelo=settings.CHAT_AI_MODEL,
        prompt_version=PROMPT_VERSION,
        inputs_hash=payload_fingerprint(limpio),
        duracion_ms=int((time.monotonic() - inicio) * 1000),
        payload_enviado=limpio,
    )


def get_or_create_report(*, evaluacion, payload: Dict[str, Any],
                         factor_slug: str, usuario) -> GeneratedReport:
    """Devuelve el informe cacheado si los datos no cambiaron, o genera uno.

    El caché por huella evita cobrar dos veces el mismo informe y garantiza
    que un documento ya descargado sea reproducible bit a bit.
    """
    limpio = sanitize_payload(payload)
    huella = payload_fingerprint(limpio)

    existente = GeneratedReport.objects.filter(
        evaluacion=evaluacion,
        tipo=TipoDocumento.INFORME_FACTOR,
        factor_slug=factor_slug,
        inputs_hash=huella,
        estado=EstadoInforme.LISTO,
    ).first()
    if existente is not None:
        logger.info(
            "Informe reutilizado desde caché evaluacion=%s factor=%s",
            evaluacion.pk, factor_slug,
        )
        return existente

    # Los informes previos del mismo factor con otra huella quedan obsoletos.
    GeneratedReport.objects.filter(
        evaluacion=evaluacion,
        tipo=TipoDocumento.INFORME_FACTOR,
        factor_slug=factor_slug,
    ).exclude(inputs_hash=huella).update(estado=EstadoInforme.OBSOLETO)

    resultado = build_professional_report(payload)

    return GeneratedReport.objects.create(
        evaluacion=evaluacion,
        tipo=TipoDocumento.INFORME_FACTOR,
        factor_slug=factor_slug,
        estado=EstadoInforme.LISTO,
        payload_json=resultado.payload_enviado,
        inputs_hash=resultado.inputs_hash,
        contenido_markdown=resultado.markdown,
        modelo_llm=resultado.modelo,
        prompt_version=resultado.prompt_version,
        duracion_ms=resultado.duracion_ms,
        generado_por=usuario,
    )


__all__ = (
    "CLAVES_PROHIBIDAS",
    "ReportGenerationError",
    "ReportResult",
    "build_professional_report",
    "get_or_create_report",
    "sanitize_payload",
)
