from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.core.management import call_command
from django.urls import reverse

from apps.training.models import TrainingModule


class SeedModulesCommandTests(TestCase):
    def test_seed_modules_is_idempotent(self):
        call_command('seed_modules')
        call_command('seed_modules')

        self.assertEqual(TrainingModule.objects.count(), 6)
        self.assertEqual(TrainingModule.objects.filter(slug='ergonomia').count(), 1)


class TrainingPageVideoTests(TestCase):
    """El trabajador permanece en ErgoSolutions para mirar el video."""

    def setUp(self):
        self.client = Client()
        self.trainee = get_user_model().objects.create_trainee(
            cuil="20-10000000-1",
            email="video-trainee@test.local",
            full_name="Trabajador Video",
        )
        self.module = TrainingModule.objects.create(
            slug="video-seguro",
            title="Video seguro",
            youtube_id="abc_123",
            is_active=True,
        )

    def test_online_renderiza_embed_privado_y_conserva_fallback(self):
        self.client.force_login(self.trainee)
        session = self.client.session
        session["target_module_slug"] = self.module.slug
        session.save()

        response = self.client.get(reverse("training:training_home"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            "https://www.youtube-nocookie.com/embed/abc_123",
        )
        self.assertContains(
            response,
            "https://www.youtube.com/watch?v=abc_123",
        )
        self.assertContains(response, 'loading="lazy"')
