"""Validación defensiva de tamaño, firma y estructura de adjuntos."""

from __future__ import annotations

import io
import warnings
import zipfile
from pathlib import Path, PurePosixPath

from django.core.exceptions import ValidationError
from PIL import Image
from pypdf import PdfReader


MAX_ATTACHMENTS = 5
MAX_ATTACHMENT_BYTES = 5 * 1024 * 1024
MAX_TOTAL_ATTACHMENT_BYTES = 12 * 1024 * 1024
MAX_IMAGE_PIXELS = 25_000_000
MAX_OFFICE_MEMBERS = 2_000
MAX_OFFICE_UNCOMPRESSED_BYTES = 50 * 1024 * 1024

ALLOWED_EXTENSIONS = frozenset(
    {".png", ".jpg", ".jpeg", ".webp", ".pdf", ".docx", ".xlsx", ".txt", ".csv"}
)
DANGEROUS_EXTENSIONS = frozenset(
    {
        ".exe", ".com", ".bat", ".cmd", ".sh", ".ps1", ".js", ".svg",
        ".html", ".htm", ".zip", ".rar", ".7z", ".docm", ".xlsm",
    }
)


def sanitized_original_name(raw_name: str) -> str:
    """Conserva sólo un basename legible y rechaza controles o vacíos."""
    candidate = Path((raw_name or "").replace("\\", "/")).name.strip()
    if not candidate or any(ord(character) < 32 for character in candidate):
        raise ValidationError("El archivo tiene un nombre inválido.")
    if len(candidate) > 255:
        candidate = candidate[-255:]
    return candidate


def validate_feedback_attachment(upload) -> None:
    """Valida un archivo y deja metadatos seguros para la persistencia."""
    safe_name = sanitized_original_name(upload.name)
    suffixes = [suffix.lower() for suffix in Path(safe_name).suffixes]
    extension = suffixes[-1] if suffixes else ""
    if extension not in ALLOWED_EXTENSIONS:
        raise ValidationError("El formato del archivo no está permitido.")
    if any(suffix in DANGEROUS_EXTENSIONS for suffix in suffixes[:-1]):
        raise ValidationError("El nombre contiene una extensión peligrosa.")
    if upload.size > MAX_ATTACHMENT_BYTES:
        raise ValidationError("Cada archivo puede pesar como máximo 5 MiB.")

    data = _read_upload(upload)
    try:
        if extension in {".png", ".jpg", ".jpeg", ".webp"}:
            _validate_image(data, extension)
        elif extension == ".pdf":
            _validate_pdf(data)
        elif extension in {".docx", ".xlsx"}:
            _validate_office(data, extension)
        else:
            _validate_text(data)
    finally:
        upload.seek(0)

    upload._feedback_safe_name = safe_name
    upload._feedback_extension = extension


def _read_upload(upload) -> bytes:
    upload.seek(0)
    data = b"".join(upload.chunks())
    if len(data) > MAX_ATTACHMENT_BYTES:
        raise ValidationError("Cada archivo puede pesar como máximo 5 MiB.")
    return data


def _validate_image(data: bytes, extension: str) -> None:
    expected = {
        ".png": "PNG",
        ".jpg": "JPEG",
        ".jpeg": "JPEG",
        ".webp": "WEBP",
    }[extension]
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("error", Image.DecompressionBombWarning)
            with Image.open(io.BytesIO(data)) as image:
                if image.format != expected:
                    raise ValidationError("La firma de la imagen no coincide con su extensión.")
                if image.width * image.height > MAX_IMAGE_PIXELS:
                    raise ValidationError("La imagen supera el máximo de 25 millones de píxeles.")
                image.verify()
    except ValidationError:
        raise
    except (Image.DecompressionBombError, Image.DecompressionBombWarning, OSError, ValueError) as exc:
        raise ValidationError("La imagen está dañada o no es segura.") from exc


def _validate_pdf(data: bytes) -> None:
    if not data.startswith(b"%PDF-"):
        raise ValidationError("La firma del PDF no es válida.")
    try:
        reader = PdfReader(io.BytesIO(data), strict=False)
        if reader.is_encrypted:
            raise ValidationError("No se admiten archivos PDF cifrados.")
        len(reader.pages)
    except ValidationError:
        raise
    except Exception as exc:
        raise ValidationError("El PDF está dañado o no puede inspeccionarse.") from exc


def _validate_office(data: bytes, extension: str) -> None:
    if not zipfile.is_zipfile(io.BytesIO(data)):
        raise ValidationError("El documento Office no tiene una estructura válida.")
    required_prefix = "word/" if extension == ".docx" else "xl/"
    try:
        with zipfile.ZipFile(io.BytesIO(data)) as archive:
            members = archive.infolist()
            if len(members) > MAX_OFFICE_MEMBERS:
                raise ValidationError("El documento Office contiene demasiados elementos.")
            if sum(member.file_size for member in members) > MAX_OFFICE_UNCOMPRESSED_BYTES:
                raise ValidationError("El documento Office se expande por encima del límite seguro.")
            names = {member.filename for member in members}
            for member in members:
                normalized = member.filename.replace("\\", "/")
                path = PurePosixPath(normalized)
                if path.is_absolute() or ".." in path.parts:
                    raise ValidationError("El documento Office contiene rutas internas inseguras.")
                if member.flag_bits & 0x1:
                    raise ValidationError("No se admiten documentos Office cifrados.")
                if normalized.lower().endswith("vbaproject.bin"):
                    raise ValidationError("No se admiten documentos Office con macros.")
            if "[Content_Types].xml" not in names or not any(
                name.startswith(required_prefix) for name in names
            ):
                raise ValidationError("El documento Office no coincide con su extensión.")
            if archive.testzip() is not None:
                raise ValidationError("El documento Office contiene un miembro dañado.")
    except ValidationError:
        raise
    except (OSError, RuntimeError, zipfile.BadZipFile) as exc:
        raise ValidationError("El documento Office está dañado o no puede inspeccionarse.") from exc


def _validate_text(data: bytes) -> None:
    if b"\x00" in data:
        raise ValidationError("Los archivos de texto no pueden contener bytes NUL.")
    try:
        data.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ValidationError("Los archivos de texto deben estar codificados en UTF-8.") from exc
