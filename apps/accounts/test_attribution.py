from datetime import datetime
from types import SimpleNamespace
from unittest.mock import patch

from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.utils import timezone

from .attribution import ATTRIBUTION_FIELDS, aplicar_atribucion


User = get_user_model()


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


class AttributionPersistenceTests(TestCase):
    def setUp(self):
        self.client = Client()

    @staticmethod
    def attribution_data():
        return {
            "source": "x",
            "medium": "reply",
            "campaign": "ergoreach",
            "content": "d_prueba01",
            "landing_path": "/curso/ergonomia/",
            "referrer_host": "x.com",
            "first_seen_at": timezone.now().isoformat(),
        }

    @staticmethod
    def registration_data():
        return {
            "first_name": "Ana",
            "last_name": "Profesional",
            "dni": "30123456",
            "email": "ana.profesional@test.com",
            "profession": "Lic. en Higiene y Seguridad",
            "license_number": "MN 12345",
            "username": "anaprofesional",
            "password1": "clave-segura-123",
            "password2": "clave-segura-123",
        }

    def set_session_attribution(self, attribution=None):
        session = self.client.session
        session["attribution"] = attribution or self.attribution_data()
        session.save()

    def test_valid_registration_persists_all_attribution_fields(self):
        attribution = self.attribution_data()
        self.set_session_attribution(attribution)

        response = self.client.post("/auth/registro/", self.registration_data())

        self.assertEqual(response.status_code, 302)
        user = User.objects.get(username="anaprofesional")
        self.assertEqual(user.attribution_source, attribution["source"])
        self.assertEqual(user.attribution_medium, attribution["medium"])
        self.assertEqual(user.attribution_campaign, attribution["campaign"])
        self.assertEqual(user.attribution_content, attribution["content"])
        self.assertEqual(user.attribution_landing_path, attribution["landing_path"])
        self.assertEqual(user.attribution_referrer_host, attribution["referrer_host"])
        self.assertEqual(
            user.attribution_first_seen_at,
            datetime.fromisoformat(attribution["first_seen_at"]),
        )

    def test_valid_registration_without_attribution_keeps_empty_fields(self):
        response = self.client.post("/auth/registro/", self.registration_data())

        self.assertEqual(response.status_code, 302)
        user = User.objects.get(username="anaprofesional")
        for field_name in ATTRIBUTION_FIELDS[:-1]:
            self.assertEqual(getattr(user, field_name), "")
        self.assertIsNone(user.attribution_first_seen_at)

    def test_attribution_save_failure_does_not_prevent_registration_or_login(self):
        self.set_session_attribution()
        original_save = User.save

        def fail_only_attribution_save(instance, *args, **kwargs):
            if kwargs.get("update_fields") == ATTRIBUTION_FIELDS:
                raise RuntimeError("fallo de atribución controlado")
            return original_save(instance, *args, **kwargs)

        with patch.object(User, "save", new=fail_only_attribution_save):
            response = self.client.post(
                "/auth/registro/",
                self.registration_data(),
            )

        self.assertEqual(response.status_code, 302)
        user = User.objects.get(username="anaprofesional")
        self.assertEqual(self.client.session["_auth_user_id"], str(user.pk))
        self.assertIn("attribution", self.client.session)

    def test_successful_registration_removes_attribution_from_session(self):
        self.set_session_attribution()

        response = self.client.post("/auth/registro/", self.registration_data())

        self.assertEqual(response.status_code, 302)
        self.assertNotIn("attribution", self.client.session)

    def test_trainee_does_not_receive_attribution_fields(self):
        trainee = User.objects.create_trainee(
            cuil="20123456789",
            email="trainee-attribution@test.com",
            full_name="Trainee Sin Atribución",
        )
        request = SimpleNamespace(
            session={"attribution": self.attribution_data()}
        )

        aplicar_atribucion(trainee, request)

        trainee.refresh_from_db()
        for field_name in ATTRIBUTION_FIELDS[:-1]:
            self.assertEqual(getattr(trainee, field_name), "")
        self.assertIsNone(trainee.attribution_first_seen_at)
        self.assertNotIn("attribution", request.session)

    def test_complete_navigation_flow_persists_first_touch(self):
        self.client.get(
            "/",
            {
                "utm_source": "x",
                "utm_medium": "reply",
                "utm_campaign": "ergoreach",
                "utm_content": "d_prueba01",
            },
        )
        self.client.get("/auth/registro/")

        response = self.client.post("/auth/registro/", self.registration_data())

        self.assertEqual(response.status_code, 302)
        user = User.objects.get(username="anaprofesional")
        self.assertEqual(user.attribution_source, "x")
        self.assertEqual(user.attribution_campaign, "ergoreach")
        self.assertEqual(user.attribution_content, "d_prueba01")
        self.assertEqual(user.attribution_landing_path, "/")

    def test_invalid_first_seen_at_is_persisted_as_none(self):
        attribution = self.attribution_data()
        attribution["first_seen_at"] = "fecha-inválida"
        self.set_session_attribution(attribution)

        response = self.client.post("/auth/registro/", self.registration_data())

        self.assertEqual(response.status_code, 302)
        user = User.objects.get(username="anaprofesional")
        self.assertEqual(user.attribution_campaign, "ergoreach")
        self.assertIsNone(user.attribution_first_seen_at)
