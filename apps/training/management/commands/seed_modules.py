# apps/training/management/commands/seed_modules.py
# ============================================================================
# COMMIT 27: Seed de módulos de capacitación adicionales
# ============================================================================

from django.core.management.base import BaseCommand

from apps.training.models import TrainingModule


MODULES = [
    {
        'slug': 'riesgo-electrico',
        'title': 'Riesgo Eléctrico',
        'description': 'Prevención de accidentes por contacto eléctrico directo e indirecto. Normas de seguridad y procedimientos de bloqueo/etiquetado.',
        'youtube_id': '',
        'icon': 'bi-lightning-charge',
        'color': '#ffc107',
        'order': 2,
        'is_active': False,
    },
    {
        'slug': 'trabajo-en-altura',
        'title': 'Trabajo en Altura',
        'description': 'Medidas de prevención para tareas en altura. Uso de arnés, líneas de vida y sistemas de protección contra caídas.',
        'youtube_id': '',
        'icon': 'bi-building-up',
        'color': '#17a2b8',
        'order': 3,
        'is_active': False,
    },
    {
        'slug': 'prevencion-incendios',
        'title': 'Prevención de Incendios',
        'description': 'Prevención, detección y combate de incendios. Uso de extintores, evacuación y plan de emergencia.',
        'youtube_id': '',
        'icon': 'bi-fire',
        'color': '#dc3545',
        'order': 4,
        'is_active': False,
    },
    {
        'slug': 'elementos-proteccion-personal',
        'title': 'Elementos de Protección Personal',
        'description': 'Selección, uso correcto y mantenimiento de EPP según el tipo de riesgo laboral.',
        'youtube_id': '',
        'icon': 'bi-shield-check',
        'color': '#6f42c1',
        'order': 5,
        'is_active': False,
    },
]


class Command(BaseCommand):
    help = 'Crea módulos de capacitación adicionales (placeholders)'

    def handle(self, *args, **options):
        created = 0
        for data in MODULES:
            obj, was_created = TrainingModule.objects.get_or_create(
                slug=data['slug'],
                defaults=data,
            )
            if was_created:
                created += 1
                self.stdout.write(self.style.SUCCESS(f'  ✅ Creado: {obj.title}'))
            else:
                self.stdout.write(self.style.WARNING(f'  ⚠️ Ya existe: {obj.title}'))

        self.stdout.write(self.style.SUCCESS(f'\nTotal creados: {created}'))
