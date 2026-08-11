"""Pruebas exhaustivas del contrato de validación de adjuntos."""

import io
import zipfile
from unittest.mock import MagicMock, patch

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import SimpleTestCase
from django.utils.datastructures import MultiValueDict
from PIL import Image
from pypdf import PdfWriter

from apps.feedback.forms import FeedbackForm
from apps.feedback.validators import (
    MAX_ATTACHMENT_BYTES,
    MAX_IMAGE_PIXELS,
    MAX_OFFICE_MEMBERS,
    MAX_OFFICE_UNCOMPRESSED_BYTES,
)


def valid_form_data(**overrides):
    data = {
        "category": "bug",
        "subject": "Falla al guardar",
        "affected_screen": "/dashboard/",
        "description": "El botón no conserva el cambio.",
        "reproduction_steps": "Abrir y guardar.",
        "expected_result": "El cambio queda guardado.",
        "privacy_confirmed": "on",
    }
    data.update(overrides)
    return data


def form_with_files(files, **data):
    return FeedbackForm(
        data=valid_form_data(**data),
        files=MultiValueDict({"attachments": files}),
    )


def image_upload(name, image_format):
    buffer = io.BytesIO()
    Image.new("RGB", (2, 2), "white").save(buffer, format=image_format)
    return SimpleUploadedFile(name, buffer.getvalue(), content_type=f"image/{image_format.lower()}")


def pdf_upload(name="informe.pdf"):
    buffer = io.BytesIO()
    writer = PdfWriter()
    writer.add_blank_page(width=10, height=10)
    writer.write(buffer)
    return SimpleUploadedFile(name, buffer.getvalue(), content_type="application/pdf")


def office_upload(name, root):
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as archive:
        archive.writestr("[Content_Types].xml", "<Types />")
        archive.writestr(f"{root}/document.xml", "<document />")
    return SimpleUploadedFile(name, buffer.getvalue(), content_type="application/octet-stream")


class FeedbackFormAllowedFormatsTests(SimpleTestCase):
    """Acepta únicamente contenido genuino de la lista blanca."""

    def test_allowed_binary_and_text_formats(self):
        uploads = (
            image_upload("captura.png", "PNG"),
            image_upload("captura.jpg", "JPEG"),
            image_upload("captura.webp", "WEBP"),
            pdf_upload(),
            office_upload("documento.docx", "word"),
            office_upload("planilla.xlsx", "xl"),
            SimpleUploadedFile("detalle.txt", "válido".encode()),
            SimpleUploadedFile("datos.csv", b"columna,valor\nuno,dos\n"),
        )
        for upload in uploads:
            with self.subTest(upload=upload.name):
                form = form_with_files([upload])
                self.assertTrue(form.is_valid(), form.errors.as_text())

    def test_subject_rejects_crlf(self):
        form = FeedbackForm(data=valid_form_data(subject="Asunto\r\nBcc: attacker@test"))
        self.assertFalse(form.is_valid())
        self.assertIn("subject", form.errors)


class FeedbackFormRejectedFormatsTests(SimpleTestCase):
    """Rechaza engaños, comprimidos genéricos y estructuras inseguras."""

    def assert_file_rejected(self, upload):
        form = form_with_files([upload])
        self.assertFalse(form.is_valid())
        self.assertIn("attachments", form.errors)

    def test_executable_renamed_as_pdf_is_rejected(self):
        self.assert_file_rejected(SimpleUploadedFile("captura.pdf", b"MZ\x90 executable"))

    def test_svg_and_generic_zip_are_rejected(self):
        self.assert_file_rejected(SimpleUploadedFile("captura.svg", b"<svg></svg>"))
        self.assert_file_rejected(SimpleUploadedFile("archivos.zip", b"PK\x03\x04"))

    def test_dangerous_double_extension_is_rejected(self):
        self.assert_file_rejected(pdf_upload("captura.exe.pdf"))

    def test_office_requires_correct_structure(self):
        self.assert_file_rejected(office_upload("falso.docx", "xl"))
        self.assert_file_rejected(office_upload("falso.xlsx", "word"))

    def test_office_rejects_internal_path_traversal(self):
        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, "w") as archive:
            archive.writestr("[Content_Types].xml", "<Types />")
            archive.writestr("word/document.xml", "<document />")
            archive.writestr("../escape.txt", "no")
        self.assert_file_rejected(SimpleUploadedFile("ruta.docx", buffer.getvalue()))

    def test_more_than_five_files_is_rejected(self):
        uploads = [SimpleUploadedFile(f"{number}.txt", b"ok") for number in range(6)]
        form = form_with_files(uploads)
        self.assertFalse(form.is_valid())
        self.assertIn("attachments", form.errors)

    def test_individual_and_total_size_limits(self):
        self.assert_file_rejected(
            SimpleUploadedFile("grande.txt", b"a" * (MAX_ATTACHMENT_BYTES + 1))
        )
        each = (4 * 1024 * 1024) + 1
        form = form_with_files(
            [SimpleUploadedFile(f"{number}.txt", b"a" * each) for number in range(3)]
        )
        self.assertFalse(form.is_valid())
        self.assertIn("attachments", form.errors)

    def test_disproportionate_image_is_rejected(self):
        fake = MagicMock(format="PNG", width=MAX_IMAGE_PIXELS + 1, height=1)
        fake.__enter__.return_value = fake
        with patch("apps.feedback.validators.Image.open", return_value=fake):
            self.assert_file_rejected(SimpleUploadedFile("huge.png", b"fake"))

    def test_office_zip_bomb_and_member_limit_are_rejected(self):
        member = MagicMock(
            filename="word/document.xml",
            file_size=MAX_OFFICE_UNCOMPRESSED_BYTES + 1,
            flag_bits=0,
        )
        content_types = MagicMock(filename="[Content_Types].xml", file_size=1, flag_bits=0)
        archive = MagicMock()
        archive.__enter__.return_value = archive
        archive.infolist.return_value = [content_types, member]
        with patch("apps.feedback.validators.zipfile.is_zipfile", return_value=True), patch(
            "apps.feedback.validators.zipfile.ZipFile", return_value=archive
        ):
            self.assert_file_rejected(SimpleUploadedFile("bomba.docx", b"zip"))

        members = [
            MagicMock(filename=f"word/{index}.xml", file_size=1, flag_bits=0)
            for index in range(MAX_OFFICE_MEMBERS + 1)
        ]
        archive.infolist.return_value = members
        with patch("apps.feedback.validators.zipfile.is_zipfile", return_value=True), patch(
            "apps.feedback.validators.zipfile.ZipFile", return_value=archive
        ):
            self.assert_file_rejected(SimpleUploadedFile("miembros.docx", b"zip"))
