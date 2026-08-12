"""Límites de uso locales para proteger el endpoint del Chat de Capacitaciones.

⚠️ CF-1 bis: es una copia deliberada de la mecánica del módulo 886, no un
   import. El prefijo de clave es propio: un usuario que esté consultando la
   ayuda de Evaluaciones no debe recibir "ya hay una consulta en curso" al
   abrir la ayuda de Capacitaciones.

   Efecto declarado: un usuario que use ambos asistentes en simultáneo puede
   alcanzar 2 × CHAT_AI_RATE_LIMIT consultas por ventana. Ver §8.12 del
   documento de auditoría para la variante de cuota unificada.
"""

import time
from dataclasses import dataclass

from django.conf import settings
from django.core.cache import cache


KEY_PREFIX = "help-capa"


class ChatLimitExceeded(Exception):
    """El usuario superó una cuota o ya posee un stream activo."""

    def __init__(self, message: str, retry_after: int):
        super().__init__(message)
        self.retry_after = retry_after


@dataclass(frozen=True)
class ChatLease:
    active_key: str


def acquire_chat_lease(user_id: int) -> ChatLease:
    window = settings.CHAT_AI_RATE_WINDOW_SECONDS
    limit = settings.CHAT_AI_RATE_LIMIT
    active_key = f"{KEY_PREFIX}:active:{user_id}"
    if not cache.add(
        active_key,
        1,
        timeout=settings.CHAT_AI_STREAM_TIMEOUT_SECONDS,
    ):
        raise ChatLimitExceeded(
            "Ya existe una consulta del asistente en curso para este usuario.",
            retry_after=2,
        )

    bucket = int(time.time() // window)
    rate_key = f"{KEY_PREFIX}:rate:{user_id}:{bucket}"

    if cache.add(rate_key, 1, timeout=window + 1):
        count = 1
    else:
        count = cache.incr(rate_key)

    retry_after = window - (int(time.time()) % window)
    if count > limit:
        cache.delete(active_key)
        raise ChatLimitExceeded(
            "Se alcanzó el límite temporal de consultas al asistente.",
            retry_after=max(1, retry_after),
        )

    return ChatLease(active_key=active_key)


def release_chat_lease(lease: ChatLease) -> None:
    cache.delete(lease.active_key)
