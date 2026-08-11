"""Almacenamiento privado de adjuntos del canal de feedback."""

from django.conf import settings
from django.core.files.storage import FileSystemStorage


class PrivateFeedbackStorage(FileSystemStorage):
    """Storage fuera de ``MEDIA_ROOT`` que falla ante pedidos de URL."""

    def __init__(self):
        super().__init__(location=settings.PRIVATE_FEEDBACK_ROOT, base_url=None)

    def url(self, name):
        """Impedir que admin, widgets o serializers fabriquen una URL."""
        raise ValueError("El adjunto de feedback no tiene URL pública.")


private_feedback_storage = PrivateFeedbackStorage()


__all__ = ("PrivateFeedbackStorage", "private_feedback_storage")
