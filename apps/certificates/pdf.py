# apps/certificates/pdf.py
"""
Generador de certificados PDF usando ReportLab.

Uso:
    pdf_bytes = build_certificate_pdf(user, module, issued_at, valid_until)
    # pdf_bytes es un bytes object listo para guardar o enviar
"""

import io
from datetime import datetime
from typing import TYPE_CHECKING

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm, mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.enums import TA_CENTER

if TYPE_CHECKING:
    from apps.accounts.models import CustomUser
    from apps.training.models import TrainingModule


def build_certificate_pdf(
    user: "CustomUser",
    module: "TrainingModule",
    issued_at: datetime,
    valid_until: datetime,
) -> bytes:
    """
    Genera un PDF de certificado profesional.
    
    Args:
        user: Usuario que aprobó
        module: Módulo de capacitación
        issued_at: Fecha de emisión
        valid_until: Fecha de vencimiento
    
    Returns:
        bytes: Contenido del PDF
    """
    buffer = io.BytesIO()
    
    # Configuramos página horizontal (landscape) en A4
    page_width, page_height = landscape(A4)
    
    doc = SimpleDocTemplate(
        buffer,
        pagesize=landscape(A4),
        rightMargin=2*cm,
        leftMargin=2*cm,
        topMargin=1.5*cm,
        bottomMargin=1.5*cm,
    )
    
    # Definir estilos
    styles = _get_styles()
    
    # Construir el contenido
    story = []
    
    # === ENCABEZADO ===
    story.append(Spacer(1, 1*cm))
    story.append(Paragraph("CERTIFICADO DE CAPACITACIÓN", styles["title"]))
    story.append(Spacer(1, 0.5*cm))
    story.append(Paragraph("ERGONOMÍA Y PREVENCIÓN DE RIESGOS LABORALES", styles["subtitle"]))
    story.append(Spacer(1, 1.5*cm))
    
    # === CUERPO ===
    story.append(Paragraph("Se certifica que", styles["body_center"]))
    story.append(Spacer(1, 0.5*cm))
    
    # ✅ FIX: Usar full_name del modelo TraineeUser (no first_name/last_name)
    full_name = getattr(user, 'full_name', None) or user.email
    story.append(Paragraph(full_name.upper(), styles["name"]))
    story.append(Spacer(1, 0.3*cm))
    
    # CUIL
    story.append(Paragraph(f"CUIL: {user.cuil}", styles["body_center"]))
    story.append(Spacer(1, 0.8*cm))
    
    # Texto de aprobación
    story.append(Paragraph(
        f"ha completado satisfactoriamente la capacitación en",
        styles["body_center"]
    ))
    story.append(Spacer(1, 0.3*cm))
    
    # Nombre del módulo (destacado)
    story.append(Paragraph(f'"{module.title}"', styles["module_title"]))
    story.append(Spacer(1, 1*cm))
    
    # === DATOS DE VALIDEZ ===
    # Tabla con fechas
    fecha_emision = issued_at.strftime("%d/%m/%Y")
    fecha_vencimiento = valid_until.strftime("%d/%m/%Y")
    
    data = [
        ["Fecha de emisión:", fecha_emision],
        ["Válido hasta:", fecha_vencimiento],
    ]
    
    table = Table(data, colWidths=[5*cm, 4*cm])
    table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
        ('ALIGN', (1, 0), (1, -1), 'LEFT'),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor("#333333")),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(table)
    story.append(Spacer(1, 1.5*cm))
    
    # === FIRMA ===
    # Datos del responsable de capacitación
    story.append(Paragraph("Pablo Ricardo Aguirre", styles["signature_name"]))
    story.append(Paragraph("Licenciado en Kinesiología - MN 10.027", styles["signature_title"]))
    story.append(Paragraph("Especialista en Ergonomía", styles["signature_title"]))
    story.append(Paragraph("_" * 40, styles["body_center"]))
    story.append(Spacer(1, 0.2*cm))
    story.append(Paragraph("Responsable de Capacitación", styles["signature"]))
    story.append(Spacer(1, 1*cm))
    
    # === LEYENDA DE VALIDEZ ===
    story.append(Paragraph(
        "Este certificado tiene una validez de 1 (un) año desde la fecha de emisión.",
        styles["footer"]
    ))
    story.append(Paragraph(
        "Emitido por el Sistema de Capacitación en Ergonomía.",
        styles["footer"]
    ))
    
    # Generar PDF
    doc.build(story)
    
    # Retornar bytes
    pdf_bytes = buffer.getvalue()
    buffer.close()
    
    return pdf_bytes


def _get_styles() -> dict:
    """Retorna diccionario con los estilos de párrafo."""
    return {
        "title": ParagraphStyle(
            "title",
            fontName="Helvetica-Bold",
            fontSize=24,
            textColor=colors.HexColor("#1a365d"),  # Azul oscuro
            alignment=TA_CENTER,
            spaceAfter=12,
        ),
        "subtitle": ParagraphStyle(
            "subtitle",
            fontName="Helvetica",
            fontSize=14,
            textColor=colors.HexColor("#2d3748"),
            alignment=TA_CENTER,
            spaceAfter=6,
        ),
        "body_center": ParagraphStyle(
            "body_center",
            fontName="Helvetica",
            fontSize=12,
            textColor=colors.HexColor("#4a5568"),
            alignment=TA_CENTER,
            leading=16,
        ),
        "name": ParagraphStyle(
            "name",
            fontName="Helvetica-Bold",
            fontSize=20,
            textColor=colors.HexColor("#1a365d"),
            alignment=TA_CENTER,
            spaceAfter=6,
        ),
        "module_title": ParagraphStyle(
            "module_title",
            fontName="Helvetica-BoldOblique",
            fontSize=16,
            textColor=colors.HexColor("#2b6cb0"),  # Azul medio
            alignment=TA_CENTER,
        ),
        "signature": ParagraphStyle(
            "signature",
            fontName="Helvetica",
            fontSize=10,
            textColor=colors.HexColor("#718096"),
            alignment=TA_CENTER,
        ),
        "signature_name": ParagraphStyle(
            "signature_name",
            fontName="Helvetica-Bold",
            fontSize=11,
            textColor=colors.HexColor("#2d3748"),
            alignment=TA_CENTER,
            spaceAfter=2,
        ),
        "signature_title": ParagraphStyle(
            "signature_title",
            fontName="Helvetica",
            fontSize=9,
            textColor=colors.HexColor("#4a5568"),
            alignment=TA_CENTER,
            spaceAfter=1,
        ),
        "footer": ParagraphStyle(
            "footer",
            fontName="Helvetica-Oblique",
            fontSize=9,
            textColor=colors.HexColor("#a0aec0"),
            alignment=TA_CENTER,
            leading=14,
        ),
    }












"""
import io
from datetime import datetime
from typing import TYPE_CHECKING

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm, mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.enums import TA_CENTER

if TYPE_CHECKING:
    from apps.accounts.models import CustomUser
    from apps.training.models import TrainingModule


def build_certificate_pdf(
    user: "CustomUser",
    module: "TrainingModule",
    issued_at: datetime,
    valid_until: datetime,
) -> bytes:
   
    buffer = io.BytesIO()
    
    # Configuramos página horizontal (landscape) en A4
    page_width, page_height = landscape(A4)
    
    doc = SimpleDocTemplate(
        buffer,
        pagesize=landscape(A4),
        rightMargin=2*cm,
        leftMargin=2*cm,
        topMargin=1.5*cm,
        bottomMargin=1.5*cm,
    )
    
    # Definir estilos
    styles = _get_styles()
    
    # Construir el contenido
    story = []
    
    # === ENCABEZADO ===
    story.append(Spacer(1, 1*cm))
    story.append(Paragraph("CERTIFICADO DE CAPACITACIÓN", styles["title"]))
    story.append(Spacer(1, 0.5*cm))
    story.append(Paragraph("ERGONOMÍA Y PREVENCIÓN DE RIESGOS LABORALES", styles["subtitle"]))
    story.append(Spacer(1, 1.5*cm))
    
    # === CUERPO ===
    story.append(Paragraph("Se certifica que", styles["body_center"]))
    story.append(Spacer(1, 0.5*cm))
    
    # ✅ FIX: Usar full_name del modelo TraineeUser (no first_name/last_name)
    full_name = getattr(user, 'full_name', None) or user.email
    story.append(Paragraph(full_name.upper(), styles["name"]))
    story.append(Spacer(1, 0.3*cm))
    
    # CUIL
    story.append(Paragraph(f"CUIL: {user.cuil}", styles["body_center"]))
    story.append(Spacer(1, 0.8*cm))
    
    # Texto de aprobación
    story.append(Paragraph(
        f"ha completado satisfactoriamente la capacitación en",
        styles["body_center"]
    ))
    story.append(Spacer(1, 0.3*cm))
    
    # Nombre del módulo (destacado)
    story.append(Paragraph(f'"{module.title}"', styles["module_title"]))
    story.append(Spacer(1, 1*cm))
    
    # === DATOS DE VALIDEZ ===
    # Tabla con fechas
    fecha_emision = issued_at.strftime("%d/%m/%Y")
    fecha_vencimiento = valid_until.strftime("%d/%m/%Y")
    
    data = [
        ["Fecha de emisión:", fecha_emision],
        ["Válido hasta:", fecha_vencimiento],
    ]
    
    table = Table(data, colWidths=[5*cm, 4*cm])
    table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
        ('ALIGN', (1, 0), (1, -1), 'LEFT'),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor("#333333")),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(table)
    story.append(Spacer(1, 1.5*cm))
    
    # === FIRMA ===
    story.append(Paragraph("_" * 40, styles["body_center"]))
    story.append(Spacer(1, 0.2*cm))
    story.append(Paragraph("Responsable de Capacitación", styles["signature"]))
    story.append(Spacer(1, 1*cm))
    
    # === LEYENDA DE VALIDEZ ===
    story.append(Paragraph(
        "Este certificado tiene una validez de 1 (un) año desde la fecha de emisión.",
        styles["footer"]
    ))
    story.append(Paragraph(
        "Emitido por el Sistema de Capacitación en Ergonomía.",
        styles["footer"]
    ))
    
    # Generar PDF
    doc.build(story)
    
    # Retornar bytes
    pdf_bytes = buffer.getvalue()
    buffer.close()
    
    return pdf_bytes


def _get_styles() -> dict:
    
    return {
        "title": ParagraphStyle(
            "title",
            fontName="Helvetica-Bold",
            fontSize=24,
            textColor=colors.HexColor("#1a365d"),  # Azul oscuro
            alignment=TA_CENTER,
            spaceAfter=12,
        ),
        "subtitle": ParagraphStyle(
            "subtitle",
            fontName="Helvetica",
            fontSize=14,
            textColor=colors.HexColor("#2d3748"),
            alignment=TA_CENTER,
            spaceAfter=6,
        ),
        "body_center": ParagraphStyle(
            "body_center",
            fontName="Helvetica",
            fontSize=12,
            textColor=colors.HexColor("#4a5568"),
            alignment=TA_CENTER,
            leading=16,
        ),
        "name": ParagraphStyle(
            "name",
            fontName="Helvetica-Bold",
            fontSize=20,
            textColor=colors.HexColor("#1a365d"),
            alignment=TA_CENTER,
            spaceAfter=6,
        ),
        "module_title": ParagraphStyle(
            "module_title",
            fontName="Helvetica-BoldOblique",
            fontSize=16,
            textColor=colors.HexColor("#2b6cb0"),  # Azul medio
            alignment=TA_CENTER,
        ),
        "signature": ParagraphStyle(
            "signature",
            fontName="Helvetica",
            fontSize=10,
            textColor=colors.HexColor("#718096"),
            alignment=TA_CENTER,
        ),
        "footer": ParagraphStyle(
            "footer",
            fontName="Helvetica-Oblique",
            fontSize=9,
            textColor=colors.HexColor("#a0aec0"),
            alignment=TA_CENTER,
            leading=14,
        ),
    }
"""