"""Genera certificados online desde snapshots documentales explícitos.

Regla de identidad: este módulo no consulta usuarios ni contiene responsables
globales. El emisor debe pasar el nombre, la profesión y la matrícula que
fueron congelados en ``Certificate`` al aprobar el examen.
"""

from __future__ import annotations

import io
from datetime import datetime
from typing import TYPE_CHECKING
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

if TYPE_CHECKING:
    from apps.accounts.models import CustomUser
    from apps.training.models import TrainingModule


def build_certificate_pdf(
    user: "CustomUser",
    module: "TrainingModule",
    issued_at: datetime,
    valid_until: datetime,
    *,
    responsible_name: str,
    responsible_profession: str,
    responsible_license_number: str,
) -> bytes:
    """Construye un certificado sin inferir ni sustituir al responsable."""
    if not all((responsible_name, responsible_profession, responsible_license_number)):
        raise ValueError("El certificado requiere un responsable profesional completo")

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=landscape(A4),
        rightMargin=2 * cm,
        leftMargin=2 * cm,
        topMargin=1.5 * cm,
        bottomMargin=1.5 * cm,
    )
    styles = _get_styles()
    story = [
        Spacer(1, 1 * cm),
        Paragraph("CERTIFICADO DE CAPACITACIÓN", styles["title"]),
        Spacer(1, 0.5 * cm),
        Paragraph("ERGONOMÍA Y PREVENCIÓN DE RIESGOS LABORALES", styles["subtitle"]),
        Spacer(1, 1.5 * cm),
        Paragraph("Se certifica que", styles["body_center"]),
        Spacer(1, 0.5 * cm),
    ]

    full_name = getattr(user, "full_name", None) or user.email
    story.extend([
        Paragraph(escape(full_name.upper()), styles["name"]),
        Spacer(1, 0.3 * cm),
        Paragraph(f"CUIL: {escape(str(user.cuil or ''))}", styles["body_center"]),
        Spacer(1, 0.8 * cm),
        Paragraph(
            "ha completado satisfactoriamente la capacitación en",
            styles["body_center"],
        ),
        Spacer(1, 0.3 * cm),
        Paragraph(f'“{escape(module.title)}”', styles["module_title"]),
        Spacer(1, 1 * cm),
    ])

    table = Table(
        [
            ["Fecha de emisión:", issued_at.strftime("%d/%m/%Y")],
            ["Válido hasta:", valid_until.strftime("%d/%m/%Y")],
        ],
        colWidths=[5 * cm, 4 * cm],
    )
    table.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
        ("FONTSIZE", (0, 0), (-1, -1), 11),
        ("ALIGN", (0, 0), (0, -1), "RIGHT"),
        ("ALIGN", (1, 0), (1, -1), "LEFT"),
        ("TEXTCOLOR", (0, 0), (-1, -1), colors.HexColor("#333333")),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
    ]))
    story.extend([
        table,
        Spacer(1, 1.2 * cm),
        Paragraph(escape(responsible_name), styles["signature_name"]),
        Paragraph(escape(responsible_profession), styles["signature_title"]),
        Paragraph(
            f"Matrícula: {escape(responsible_license_number)}",
            styles["signature_title"],
        ),
        Paragraph("_" * 40, styles["body_center"]),
        Spacer(1, 0.2 * cm),
        Paragraph("Responsable de Capacitación", styles["signature"]),
        Spacer(1, 0.7 * cm),
        Paragraph(
            "Este certificado tiene una validez de 1 (un) año desde la fecha de emisión.",
            styles["footer"],
        ),
        Paragraph(
            "Emitido por el Sistema de Capacitación en Ergonomía.",
            styles["footer"],
        ),
    ])

    doc.build(story)
    pdf_bytes = buffer.getvalue()
    buffer.close()
    return pdf_bytes


def _get_styles() -> dict[str, ParagraphStyle]:
    """Estilos del certificado, centralizados para una única implementación."""
    return {
        "title": ParagraphStyle(
            "title", fontName="Helvetica-Bold", fontSize=24,
            textColor=colors.HexColor("#1a365d"), alignment=TA_CENTER,
            spaceAfter=12,
        ),
        "subtitle": ParagraphStyle(
            "subtitle", fontName="Helvetica", fontSize=14,
            textColor=colors.HexColor("#2d3748"), alignment=TA_CENTER,
            spaceAfter=6,
        ),
        "body_center": ParagraphStyle(
            "body_center", fontName="Helvetica", fontSize=12,
            textColor=colors.HexColor("#4a5568"), alignment=TA_CENTER,
            leading=16,
        ),
        "name": ParagraphStyle(
            "name", fontName="Helvetica-Bold", fontSize=20,
            textColor=colors.HexColor("#1a365d"), alignment=TA_CENTER,
            spaceAfter=6,
        ),
        "module_title": ParagraphStyle(
            "module_title", fontName="Helvetica-BoldOblique", fontSize=16,
            textColor=colors.HexColor("#2b6cb0"), alignment=TA_CENTER,
        ),
        "signature": ParagraphStyle(
            "signature", fontName="Helvetica", fontSize=10,
            textColor=colors.HexColor("#718096"), alignment=TA_CENTER,
        ),
        "signature_name": ParagraphStyle(
            "signature_name", fontName="Helvetica-Bold", fontSize=11,
            textColor=colors.HexColor("#2d3748"), alignment=TA_CENTER,
            spaceAfter=2,
        ),
        "signature_title": ParagraphStyle(
            "signature_title", fontName="Helvetica", fontSize=9,
            textColor=colors.HexColor("#4a5568"), alignment=TA_CENTER,
            spaceAfter=1,
        ),
        "footer": ParagraphStyle(
            "footer", fontName="Helvetica-Oblique", fontSize=9,
            textColor=colors.HexColor("#a0aec0"), alignment=TA_CENTER,
            leading=14,
        ),
    }
