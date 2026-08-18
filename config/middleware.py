"""Cabeceras de seguridad comunes para las respuestas de ErgoSolutions.

Portado del módulo de Ergonomía SRT 886/15, con una extensión: la cabecera
puede emitirse en modo Report-Only mediante el setting ``CSP_REPORT_ONLY``.
"""

from __future__ import annotations

import re
import secrets
from urllib.parse import urlsplit

from asgiref.sync import iscoroutinefunction, markcoroutinefunction
from django.conf import settings
from django.utils import timezone
from django.utils.deprecation import MiddlewareMixin


class ContentSecurityPolicyMiddleware:
    """Genera un nonce por respuesta y bloquea recursos/script no autorizados."""

    sync_capable = True
    async_capable = True

    def __init__(self, get_response):
        self.get_response = get_response
        self.is_async = iscoroutinefunction(get_response)
        if self.is_async:
            markcoroutinefunction(self)

    @staticmethod
    def _prepare_request(request) -> None:
        request.csp_nonce = secrets.token_urlsafe(18)

    @staticmethod
    def _finalize_response(request, response):
        nonce = request.csp_nonce
        politica = "; ".join((
            "default-src 'self'",
            f"script-src 'self' 'nonce-{nonce}'",
            "script-src-attr 'none'",
            "style-src 'self' 'unsafe-inline'",
            "font-src 'self'",
            "img-src 'self' data:",
            "connect-src 'self'",
            "frame-src https://www.youtube-nocookie.com",
            "object-src 'none'",
            "base-uri 'self'",
            "frame-ancestors 'self'",
            "form-action 'self'",
        ))
        cabecera = (
            "Content-Security-Policy-Report-Only"
            if getattr(settings, "CSP_REPORT_ONLY", False)
            else "Content-Security-Policy"
        )
        response[cabecera] = politica
        response["Referrer-Policy"] = "same-origin"
        response["Permissions-Policy"] = (
            "camera=(), microphone=(), geolocation=(), payment=()"
        )
        return response

    def __call__(self, request):
        self._prepare_request(request)
        if self.is_async:
            return self.__acall__(request)
        response = self.get_response(request)
        return self._finalize_response(request, response)

    async def __acall__(self, request):
        response = await self.get_response(request)
        return self._finalize_response(request, response)


_UNSAFE_MARKUP_CHARS = frozenset("<>\"'")
_UNSAFE_UTM_CHARS = re.compile(r"[^A-Za-z0-9._-]")
_UNSAFE_PATH_CHARS = re.compile(r"[^A-Za-z0-9._/-]")
_UNSAFE_HOST_CHARS = re.compile(r"[^A-Za-z0-9._-]")


def _sanitize_value(value: str, *, max_length: int, unsafe_pattern) -> str:
    """Descarta markup y conserva únicamente el subconjunto ASCII permitido."""
    if not value or any(char in value for char in _UNSAFE_MARKUP_CHARS):
        return ""
    return unsafe_pattern.sub("", value)[:max_length]


def _sanitize_utm(value: str) -> str:
    return _sanitize_value(
        value,
        max_length=64,
        unsafe_pattern=_UNSAFE_UTM_CHARS,
    )


def _sanitize_landing_path(value: str) -> str:
    return _sanitize_value(
        value,
        max_length=255,
        unsafe_pattern=_UNSAFE_PATH_CHARS,
    )


def _extract_referrer_host(referer: str) -> str:
    if not referer:
        return ""
    host = urlsplit(referer).hostname or ""
    return _sanitize_value(
        host,
        max_length=128,
        unsafe_pattern=_UNSAFE_HOST_CHARS,
    )


class AttributionMiddleware(MiddlewareMixin):
    """Captura atribución UTM first-touch en la sesión sin romper requests."""

    def process_request(self, request):
        try:
            if request.method != "GET":
                return None
            if not any(key.startswith("utm_") for key in request.GET):
                return None
            if "attribution" in request.session:
                return None

            request.session["attribution"] = {
                "source": _sanitize_utm(request.GET.get("utm_source", "")),
                "medium": _sanitize_utm(request.GET.get("utm_medium", "")),
                "campaign": _sanitize_utm(request.GET.get("utm_campaign", "")),
                "content": _sanitize_utm(request.GET.get("utm_content", "")),
                "landing_path": _sanitize_landing_path(request.path),
                "referrer_host": _extract_referrer_host(
                    request.META.get("HTTP_REFERER", "")
                ),
                "first_seen_at": timezone.now().isoformat(),
            }
        except Exception:
            pass
        return None
