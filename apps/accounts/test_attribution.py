from datetime import datetime
from unittest.mock import patch

from django.conf import settings
from django.test import Client, TestCase


class AttributionMiddlewareTests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_get_with_all_utm_values_stores_attribution(self):
        response = self.client.get(
            "/",
            {
                "utm_source": "x",
                "utm_medium": "reply",
                "utm_campaign": "ergoreach",
                "utm_content": "d_test1234",
            },
        )

        self.assertEqual(response.status_code, 200)
        attribution = self.client.session["attribution"]
        self.assertEqual(attribution["source"], "x")
        self.assertEqual(attribution["medium"], "reply")
        self.assertEqual(attribution["campaign"], "ergoreach")
        self.assertEqual(attribution["content"], "d_test1234")
        self.assertEqual(attribution["landing_path"], "/")
        self.assertIsNotNone(datetime.fromisoformat(attribution["first_seen_at"]).tzinfo)

    def test_get_without_utm_does_not_create_attribution(self):
        response = self.client.get("/")

        self.assertEqual(response.status_code, 200)
        self.assertNotIn("attribution", self.client.session)

    def test_second_get_preserves_first_touch(self):
        self.client.get("/", {"utm_source": "first", "utm_content": "d_first"})
        first_touch = self.client.session["attribution"]

        self.client.get("/", {"utm_source": "second", "utm_content": "d_second"})

        self.assertEqual(self.client.session["attribution"], first_touch)

    def test_post_with_utm_is_ignored(self):
        self.client.post("/?utm_source=x&utm_campaign=ergoreach")

        self.assertNotIn("attribution", self.client.session)

    def test_long_content_is_truncated_to_64_characters(self):
        self.client.get("/", {"utm_content": "a" * 500})

        content = self.client.session["attribution"]["content"]
        self.assertLessEqual(len(content), 64)
        self.assertEqual(content, "a" * 64)

    def test_markup_in_source_is_discarded(self):
        self.client.get("/", {"utm_source": "<script>alert.test</script>"})

        source = self.client.session["attribution"]["source"]
        self.assertEqual(source, "")
        self.assertNotIn("script", source)

    def test_referer_stores_only_hostname(self):
        self.client.get(
            "/",
            {"utm_source": "x"},
            HTTP_REFERER="https://x.com/algo/largo?dato=privado",
        )

        attribution = self.client.session["attribution"]
        self.assertEqual(attribution["referrer_host"], "x.com")
        self.assertNotIn("algo", attribution["referrer_host"])

    def test_internal_attribution_error_never_breaks_request(self):
        with patch(
            "config.middleware._sanitize_utm",
            side_effect=RuntimeError("fallo interno controlado"),
        ):
            response = self.client.get("/", {"utm_source": "x"})

        self.assertEqual(response.status_code, 200)
        self.assertNotIn("attribution", self.client.session)

    def test_attribution_survives_navigation_to_registration(self):
        self.client.get(
            "/",
            {"utm_source": "x", "utm_content": "d_test1234"},
        )
        first_touch = self.client.session["attribution"]

        response = self.client.get("/auth/registro/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.client.session["attribution"], first_touch)

    def test_middleware_is_immediately_after_session_middleware(self):
        session_index = settings.MIDDLEWARE.index(
            "django.contrib.sessions.middleware.SessionMiddleware"
        )

        self.assertEqual(
            settings.MIDDLEWARE[session_index + 1],
            "config.middleware.AttributionMiddleware",
        )
