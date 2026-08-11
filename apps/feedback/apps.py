"""Configuración Django de la aplicación de feedback."""

from django.apps import AppConfig


class FeedbackConfig(AppConfig):
    """Configura el dominio independiente de comentarios de la beta."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.feedback"
    verbose_name = "Feedback de la beta"
