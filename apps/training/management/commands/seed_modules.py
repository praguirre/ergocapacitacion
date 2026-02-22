# apps/training/management/commands/seed_modules.py
# ============================================================================
# COMMIT 27: Seed de módulos de capacitación adicionales
# ============================================================================

from django.core.management.base import BaseCommand

from apps.training.models import TrainingModule


MODULES = [
    {
        'slug': 'ergonomia',
        'title': 'Ergonomía',
        'description': 'Capacitación ergonómica para prevenir lesiones musculoesqueléticas y promover hábitos de trabajo saludables.',
        'youtube_id': 'IIgZp_NbsAE',
        'icon': 'bi-body-text',
        'color': '#28a745',
        'order': 1,
        'is_active': True,
    },
    {
        'slug': 'ruido',
        'title': 'Ruido',
        'description': 'Identificación y control del riesgo por exposición a ruido ocupacional. Medidas preventivas y protección auditiva.',
        'youtube_id': '',
        'icon': 'bi-volume-up',
        'color': '#f59e0b',
        'order': 2,
        'is_active': False,
    },
    {
        'slug': 'riesgo-electrico',
        'title': 'Riesgo Eléctrico',
        'description': 'Prevención de accidentes por contacto eléctrico directo e indirecto. Normas de seguridad y procedimientos de bloqueo/etiquetado.',
        'youtube_id': '',
        'icon': 'bi-lightning-charge',
        'color': '#ffc107',
        'order': 3,
        'is_active': False,
    },
    {
        'slug': 'trabajo-en-altura',
        'title': 'Trabajo en Altura',
        'description': 'Medidas de prevención para tareas en altura. Uso de arnés, líneas de vida y sistemas de protección contra caídas.',
        'youtube_id': '',
        'icon': 'bi-building-up',
        'color': '#17a2b8',
        'order': 4,
        'is_active': False,
    },
    {
        'slug': 'prevencion-incendios',
        'title': 'Prevención de Incendios',
        'description': 'Prevención, detección y combate de incendios. Uso de extintores, evacuación y plan de emergencia.',
        'youtube_id': '',
        'icon': 'bi-fire',
        'color': '#dc3545',
        'order': 5,
        'is_active': False,
    },
    {
        'slug': 'elementos-proteccion-personal',
        'title': 'Elementos de Protección Personal',
        'description': 'Selección, uso correcto y mantenimiento de EPP según el tipo de riesgo laboral.',
        'youtube_id': '',
        'icon': 'bi-shield-check',
        'color': '#6f42c1',
        'order': 6,
        'is_active': False,
    },
]


class Command(BaseCommand):
    help = 'Crea o actualiza módulos de capacitación canónicos'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force-active-defaults',
            action='store_true',
            help='Fuerza is_active default (ergonomía=True, resto=False) incluso en módulos existentes.',
        )

    def handle(self, *args, **options):
        force_active_defaults = options.get('force_active_defaults', False)

        created = 0
        updated = 0
        unchanged = 0

        for data in MODULES:
            slug = data['slug']
            existing = TrainingModule.objects.filter(slug=slug).first()

            defaults = data.copy()
            if existing and not force_active_defaults:
                # En DB existentes respetamos el estado activo actual por defecto.
                defaults.pop('is_active', None)

            has_changes = False
            if existing:
                has_changes = any(getattr(existing, field) != value for field, value in defaults.items())

            obj, was_created = TrainingModule.objects.update_or_create(
                slug=slug,
                defaults=defaults,
            )

            if was_created:
                created += 1
                self.stdout.write(self.style.SUCCESS(f'  ✅ Creado: {obj.title}'))
            elif has_changes:
                updated += 1
                self.stdout.write(self.style.SUCCESS(f'  🔄 Actualizado: {obj.title}'))
            else:
                unchanged += 1
                self.stdout.write(self.style.WARNING(f'  ⚠️ Sin cambios: {obj.title}'))

        active_modules = list(
            TrainingModule.objects.filter(is_active=True)
            .order_by('order', 'title')
            .values_list('slug', flat=True)
        )
        active_summary = ', '.join(active_modules) if active_modules else 'ninguno'

        self.stdout.write(self.style.SUCCESS('\nResumen seed_modules'))
        self.stdout.write(self.style.SUCCESS(f'  creados: {created}'))
        self.stdout.write(self.style.SUCCESS(f'  actualizados: {updated}'))
        self.stdout.write(self.style.SUCCESS(f'  sin cambios: {unchanged}'))
        self.stdout.write(self.style.SUCCESS(f'  activos: {active_summary}'))
