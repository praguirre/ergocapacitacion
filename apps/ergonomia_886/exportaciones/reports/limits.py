# exportaciones/reports/limits.py
"""Cuotas de generación de informes.

Réplica del patrón de `help_ai/limits.py` con contadores propios: un informe
cuesta mucho más que una consulta de chat y no debe compartir presupuesto.
"""

from __future__ import annotations

import time
from dataclasses import dataclass

from django.conf import settings
from django.core.cache import cache


class ReportLimitExceeded(Exception):
    def __init__(self, message: str, retry_after: int):
        super().__init__(message)
        self.retry_after = retry_after


@dataclass(frozen=True)
class ReportLease:
    active_key: str


def acquire_report_lease(user_id: int) -> ReportLease:
    ventana = getattr(settings, "REPORT_AI_RATE_WINDOW_SECONDS", 3600)
    limite = getattr(settings, "REPORT_AI_RATE_LIMIT", 20)
    timeout = getattr(settings, "REPORT_AI_TIMEOUT_SECONDS", 90)

    active_key = f"exportaciones:informe:activo:{user_id}"
    if not cache.add(active_key, 1, timeout=int(timeout) + 10):
        raise ReportLimitExceeded(
            "Ya hay un informe generándose para este usuario. "
            "Esperá a que termine.",
            retry_after=5,
        )

    bucket = int(time.time() // ventana)
    rate_key = f"exportaciones:informe:cuota:{user_id}:{bucket}"
    if cache.add(rate_key, 1, timeout=ventana + 1):
        cantidad = 1
    else:
        cantidad = cache.incr(rate_key)

    if cantidad > limite:
        cache.delete(active_key)
        raise ReportLimitExceeded(
            "Se alcanzó el límite de informes generados en esta hora.",
            retry_after=max(1, ventana - (int(time.time()) % ventana)),
        )

    return ReportLease(active_key=active_key)


def release_report_lease(lease: ReportLease) -> None:
    cache.delete(lease.active_key)


__all__ = (
    "ReportLease",
    "ReportLimitExceeded",
    "acquire_report_lease",
    "release_report_lease",
)
