"""
Management command para verificar la configuración de email.

Uso:
    python manage.py send_test_email destinatario@example.com
    python manage.py send_test_email destinatario@example.com --with-attachment
"""
import socket

from django.conf import settings
from django.core.mail import EmailMessage, send_mail
from django.core.management.base import BaseCommand
from django.utils import timezone


class Command(BaseCommand):
    help = (
        "Envía un email de prueba para verificar la configuración SMTP. "
        "Opcionalmente adjunta un PDF de prueba."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "recipient",
            type=str,
            help="Email del destinatario de prueba.",
        )
        parser.add_argument(
            "--with-attachment",
            action="store_true",
            help="Incluir un PDF adjunto de prueba para simular envío de certificados.",
        )

    def handle(self, *args, **options):
        recipient = options["recipient"]
        with_attachment = options["with_attachment"]

        # 1. Mostrar config actual (password enmascarado)
        password_display = "***" if settings.EMAIL_HOST_PASSWORD else "(vacío)"
        self.stdout.write(
            f"\n--- Configuración actual ---\n"
            f"  EMAIL_BACKEND:       {settings.EMAIL_BACKEND}\n"
            f"  EMAIL_HOST:          {settings.EMAIL_HOST}\n"
            f"  EMAIL_PORT:          {settings.EMAIL_PORT}\n"
            f"  EMAIL_USE_TLS:       {settings.EMAIL_USE_TLS}\n"
            f"  EMAIL_USE_SSL:       {getattr(settings, 'EMAIL_USE_SSL', False)}\n"
            f"  EMAIL_HOST_USER:     {settings.EMAIL_HOST_USER or '(vacío)'}\n"
            f"  EMAIL_HOST_PASSWORD: {password_display}\n"
            f"  DEFAULT_FROM_EMAIL:  {settings.DEFAULT_FROM_EMAIL}\n"
            f"  ADMIN_EMAIL:         {getattr(settings, 'ADMIN_EMAIL', '(no definido)')}\n"
            f"----------------------------\n"
        )

        # 2. Avisar si usa console backend
        if "console" in settings.EMAIL_BACKEND.lower():
            self.stdout.write(self.style.WARNING(
                "ATENCIÓN: Estás usando el backend de consola. "
                "El email se imprimirá abajo, no se enviará realmente.\n"
            ))

        # 3. Enviar email de prueba
        now = timezone.now().strftime("%Y-%m-%d %H:%M:%S")
        host = socket.gethostname()
        subject = f"[ErgoSolutions] Email de prueba - {now}"

        if with_attachment:
            body = (
                f"Este es un email de prueba con adjunto enviado desde {host}.\n\n"
                f"Fecha: {now}\n"
                f"Si recibiste este email con un archivo PDF adjunto, "
                f"la configuración de email funciona correctamente.\n"
            )
            msg = EmailMessage(
                subject=subject,
                body=body,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[recipient],
            )
            # PDF mínimo válido para testear adjuntos
            test_pdf = (
                b"%PDF-1.4\n1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj\n"
                b"2 0 obj<</Type/Pages/Kids[]/Count 0>>endobj\n"
                b"xref\n0 3\ntrailer<</Size 3/Root 1 0 R>>\n"
                b"startxref\n9\n%%EOF"
            )
            msg.attach("test_ergosolutions.pdf", test_pdf, "application/pdf")
            msg.send(fail_silently=False)
            self.stdout.write(self.style.SUCCESS(
                f"\nEmail CON ADJUNTO enviado exitosamente a {recipient}\n"
            ))
        else:
            body = (
                f"Este es un email de prueba enviado desde {host}.\n\n"
                f"Fecha: {now}\n"
                f"Si recibiste este email, la configuración funciona correctamente.\n"
            )
            send_mail(
                subject=subject,
                message=body,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[recipient],
                fail_silently=False,
            )
            self.stdout.write(self.style.SUCCESS(
                f"\nEmail enviado exitosamente a {recipient}\n"
            ))
