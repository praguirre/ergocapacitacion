"""Purga controlada de binarios enviados conservando sus metadatos."""

import logging
from datetime import timedelta

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

from apps.feedback.models import FeedbackAttachment, FeedbackReport


logger = logging.getLogger("apps.feedback")


class Command(BaseCommand):
    help = "Purga adjuntos antiguos de reportes enviados; use --dry-run primero."

    def add_arguments(self, parser):
        parser.add_argument(
            "--older-than-days",
            type=int,
            default=settings.FEEDBACK_ATTACHMENT_RETENTION_DAYS,
        )
        parser.add_argument("--dry-run", action="store_true")

    def handle(self, *args, **options):
        days = options["older_than_days"]
        if days < 1:
            raise CommandError("--older-than-days debe ser mayor que cero.")
        cutoff = timezone.now() - timedelta(days=days)
        queryset = FeedbackAttachment.objects.filter(
            report__email_status=FeedbackReport.EmailStatus.SENT,
            created_at__lt=cutoff,
            purged_at__isnull=True,
        ).exclude(file="")
        count = queryset.count()
        if options["dry_run"]:
            self.stdout.write(f"dry_run=true candidates={count}")
            return

        purged = 0
        for attachment in queryset.iterator():
            attachment.file.delete(save=False)
            attachment.file = ""
            attachment.purged_at = timezone.now()
            attachment.save(update_fields=("file", "purged_at"))
            purged += 1
            logger.info(
                "feedback_attachment_purged attachment_id=%s report_id=%s",
                attachment.pk,
                attachment.report_id,
            )
        self.stdout.write(f"dry_run=false purged={purged}")
