from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.company.models import CompanyWorker, AgendaEvent
from apps.certificates.models import Certificate


class Command(BaseCommand):
    help = "Genera eventos de agenda por vencimiento próximo de certificados"

    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            type=int,
            default=30,
            help='Días hacia adelante para buscar vencimientos',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Simula sin crear eventos',
        )

    def handle(self, *args, **options):
        days = options['days']
        dry_run = options['dry_run']

        now = timezone.now()
        threshold = now + timedelta(days=days)

        self.stdout.write(
            f"Buscando certificados que vencen entre {now.date()} y {threshold.date()}..."
        )

        expiring_certs = Certificate.objects.filter(
            valid_until__range=(now, threshold)
        ).select_related('user', 'module')

        created = 0
        skipped = 0

        for cert in expiring_certs:
            assignments = CompanyWorker.objects.filter(
                worker=cert.user, is_active=True
            ).select_related('company')

            for assignment in assignments:
                exists = AgendaEvent.objects.filter(
                    company=assignment.company,
                    event_type=AgendaEvent.EventType.CERTIFICATE_EXPIRY,
                    worker=cert.user,
                    related_object_type='certificate',
                    related_object_id=str(cert.id),
                ).exists()

                if exists:
                    skipped += 1
                    continue

                if dry_run:
                    self.stdout.write(
                        f"[DRY-RUN] Crearía evento: {cert.user.display_name} / "
                        f"{cert.module.title} → {assignment.company.display_name}"
                    )
                    created += 1
                    continue

                AgendaEvent.objects.create(
                    company=assignment.company,
                    worker=cert.user,
                    title=f"Vencimiento certificado: {cert.module.title}",
                    description=(
                        f"El certificado de '{cert.module.title}' de "
                        f"{cert.user.display_name} vence el día "
                        f"{cert.valid_until.strftime('%d/%m/%Y')}."
                    ),
                    event_type=AgendaEvent.EventType.CERTIFICATE_EXPIRY,
                    priority=AgendaEvent.Priority.HIGH,
                    due_at=cert.valid_until,
                    related_object_type='certificate',
                    related_object_id=str(cert.id),
                )
                created += 1

        prefix = "[DRY-RUN] " if dry_run else ""
        self.stdout.write(
            self.style.SUCCESS(
                f"{prefix}Completado: {created} eventos creados, {skipped} duplicados omitidos."
            )
        )
