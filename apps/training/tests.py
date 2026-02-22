from django.test import TestCase
from django.core.management import call_command

from apps.training.models import TrainingModule


class SeedModulesCommandTests(TestCase):
    def test_seed_modules_is_idempotent(self):
        call_command('seed_modules')
        call_command('seed_modules')

        self.assertEqual(TrainingModule.objects.count(), 6)
        self.assertEqual(TrainingModule.objects.filter(slug='ergonomia').count(), 1)
