"""Reintenta entregas pendientes o fallidas sin imprimir datos sensibles."""

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from apps.feedback.models import FeedbackReport
from apps.feedback.services import send_feedback_email


class Command(BaseCommand):
    help = "Reintenta correos de feedback pendientes o fallidos."

    def add_arguments(self, parser):
        parser.add_argument("--limit", type=int, default=20)
        parser.add_argument("--report")

    def handle(self, *args, **options):
        limit = options["limit"]
        if limit < 1:
            raise CommandError("--limit debe ser mayor que cero.")
        queryset = FeedbackReport.objects.filter(
            email_status__in=(
                FeedbackReport.EmailStatus.PENDING,
                FeedbackReport.EmailStatus.FAILED,
            ),
            email_attempts__lt=settings.FEEDBACK_MAX_EMAIL_ATTEMPTS,
        ).order_by("created_at")
        if options["report"]:
            queryset = queryset.filter(pk=options["report"])

        processed = 0
        sent = 0
        for report in queryset[:limit]:
            delivered = send_feedback_email(report)
            processed += 1
            sent += int(delivered)
            self.stdout.write(f"report_id={report.pk} status={'sent' if delivered else 'failed'}")
        self.stdout.write(f"processed={processed} sent={sent} failed={processed - sent}")
