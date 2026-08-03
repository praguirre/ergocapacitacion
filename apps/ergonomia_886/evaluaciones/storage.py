"""Almacenamiento privado para evidencia documental del módulo 886.

Los archivos quedan fuera de ``MEDIA_ROOT``: nunca deben quedar expuestos por
la ruta pública ``/media/``. La descarga se realiza exclusivamente mediante
una vista autenticada que vuelve a comprobar la propiedad de la evaluación.
"""

from django.conf import settings
from django.core.files.storage import FileSystemStorage


class PrivateEvidenceStorage(FileSystemStorage):
    """Storage sin URL pública, estable y serializable en migraciones."""

    def __init__(self):
        super().__init__(
            location=settings.PRIVATE_ERGONOMIA_886_ROOT,
            base_url=None,
        )

    def url(self, name):
        """Impedir que widgets o serializers fabriquen una URL pública."""
        raise ValueError("La evidencia privada no tiene URL pública.")


private_evidence_storage = PrivateEvidenceStorage()


__all__ = ("PrivateEvidenceStorage", "private_evidence_storage")
