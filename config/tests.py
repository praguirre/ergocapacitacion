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
