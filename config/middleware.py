"""Cabeceras de seguridad comunes para las respuestas de ErgoSolutions.

Portado del módulo de Ergonomía SRT 886/15, con una extensión: la cabecera
puede emitirse en modo Report-Only mediante el setting ``CSP_REPORT_ONLY``.
"""

from __future__ import annotations

import secrets

from asgiref.sync import iscoroutinefunction, markcoroutinefunction
from django.conf import settings


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
