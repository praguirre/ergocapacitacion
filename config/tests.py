import re

from django.conf import settings
from django.http import HttpResponse
from django.test import RequestFactory, SimpleTestCase, override_settings

from .middleware import ContentSecurityPolicyMiddleware


class ContentSecurityPolicyMiddlewareTests(SimpleTestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def response(self):
        request = self.factory.get("/")
        response = ContentSecurityPolicyMiddleware(
            lambda prepared_request: HttpResponse(prepared_request.csp_nonce)
        )(request)
        return request, response

    @override_settings(CSP_REPORT_ONLY=True)
    def test_report_only_emits_observation_header_and_real_nonce(self):
        request, response = self.response()

        self.assertNotIn("Content-Security-Policy", response)
        policy = response["Content-Security-Policy-Report-Only"]
        self.assertIn(f"'nonce-{request.csp_nonce}'", policy)
        self.assertRegex(request.csp_nonce, r"^[A-Za-z0-9_-]{24}$")
        self.assertEqual(response.content.decode(), request.csp_nonce)

    @override_settings(CSP_REPORT_ONLY=False)
    def test_blocking_mode_uses_the_same_policy_and_security_headers(self):
        _, response = self.response()

        self.assertNotIn("Content-Security-Policy-Report-Only", response)
        policy = response["Content-Security-Policy"]
        self.assertRegex(policy, re.compile(r"script-src 'self' 'nonce-[^']+'"))
        self.assertIn("script-src-attr 'none'", policy)
        self.assertEqual(response["Referrer-Policy"], "same-origin")
        self.assertEqual(
            response["Permissions-Policy"],
            "camera=(), microphone=(), geolocation=(), payment=()",
        )

    def test_middleware_position_is_after_whitenoise_and_before_session(self):
        csp = settings.MIDDLEWARE.index(
            "config.middleware.ContentSecurityPolicyMiddleware"
        )
        whitenoise = settings.MIDDLEWARE.index(
            "whitenoise.middleware.WhiteNoiseMiddleware"
        )
        session = settings.MIDDLEWARE.index(
            "django.contrib.sessions.middleware.SessionMiddleware"
        )

        self.assertLess(whitenoise, csp)
        self.assertLess(csp, session)


class AsgiStackContractTests(SimpleTestCase):
    """El stack tiene que poder correr bajo ASGI sin adaptaciones."""

    def test_ningun_middleware_es_sync_only_en_produccion(self):
        """H-A1: un solo middleware sync-only degrada toda la cadena.

        Django (core/handlers/base.py) usa
        `getattr(mw, "async_capable", False)`. Un middleware que no lo
        declare se trata como sync-only y obliga a envolver con
        async_to_sync todo lo que tenga por debajo, incluida la vista SSE
        del Chat IA. Ése fue exactamente el caso de WhiteNoise.
        """
        from django.utils.module_loading import import_string

        # Se evalúa la cadena de PRODUCCIÓN: sin el WhiteNoise de desarrollo.
        cadena = [m for m in settings.MIDDLEWARE if "whitenoise" not in m]

        sync_only = [
            path for path in cadena
            if not getattr(import_string(path), "async_capable", False)
        ]
        self.assertEqual(
            sync_only, [],
            f"Middlewares sync-only en la cadena de producción: {sync_only}. "
            "Cada uno obliga a Django a adaptar con async_to_sync todo lo que "
            "tiene por debajo, y anula el beneficio de ASGI para el SSE.",
        )

    def test_el_middleware_de_csp_declara_ambas_capacidades(self):
        from config.middleware import ContentSecurityPolicyMiddleware as CSP

        self.assertTrue(CSP.sync_capable)
        self.assertTrue(CSP.async_capable)
        self.assertTrue(hasattr(CSP, "__acall__"))

    def test_atomic_requests_sigue_desactivado(self):
        """Con ATOMIC_REQUESTS=True habría que revisar cada vista async."""
        self.assertFalse(settings.DATABASES["default"].get("ATOMIC_REQUESTS", False))

    def test_no_hay_routers_de_base_de_datos(self):
        """El ruteo debe ser explícito con .using(), nunca implícito."""
        self.assertEqual(getattr(settings, "DATABASE_ROUTERS", []), [])
