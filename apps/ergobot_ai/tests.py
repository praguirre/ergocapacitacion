"""Pruebas funcionales de separación entre Ergobot y la ayuda SRT 886."""

from unittest.mock import AsyncMock, patch

from django.contrib.auth import get_user_model
from django.test import AsyncRequestFactory, TestCase
from django.urls import reverse

from .views import ergobot_stream


class _DeltaData:
    type = "response.output_text.delta"
    delta = "Respuesta docente de Ergobot"


class _DeltaEvent:
    type = "raw_response_event"
    data = _DeltaData()


class _FakeRun:
    async def stream_events(self):
        yield _DeltaEvent()


class AssistantsSeparationFunctionalTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = get_user_model().objects.create_professional(
            email="cf1-assistants@example.com",
            username="cf1-assistants",
            password="test-password",
        )

    def test_widget_responde_con_tres_slugs_distintos(self):
        self.client.force_login(self.user)

        for slug in ("dashboard", "planilla1", "posturas_forzadas"):
            with self.subTest(slug=slug):
                response = self.client.get(
                    reverse("help_ai:help_guide", kwargs={"slug": slug})
                )
                self.assertEqual(response.status_code, 200)
                self.assertTrue(response.content.strip())
                self.assertTrue(response["X-Help-Content-Version"])

    async def test_ergobot_responde_en_su_stream_docente(self):
        request = AsyncRequestFactory().get(
            reverse("ergobot_ai:ergobot_stream", args=["ergonomia"]),
            {"q": "Explicá el objetivo de la capacitación", "thread": "[]"},
        )
        request.user = self.user
        request.auser = AsyncMock(return_value=self.user)

        with (
            patch(
                "apps.ergobot_ai.views.ergobot_agent",
                new_callable=AsyncMock,
                return_value=object(),
            ) as agent,
            patch(
                "apps.ergobot_ai.views.Runner.run_streamed",
                return_value=_FakeRun(),
            ) as runner,
        ):
            response = await ergobot_stream(request, "ergonomia")
            chunks = [chunk async for chunk in response.streaming_content]

        body = b"".join(chunks).decode()
        self.assertEqual(response.status_code, 200)
        self.assertIn("Respuesta docente de Ergobot", body)
        self.assertIn('"done": true', body)
        agent.assert_awaited_once_with("ergonomia")
        runner.assert_called_once()
