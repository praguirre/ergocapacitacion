# apps/presencial/pdf.py
# ============================================================================
# COMMIT 20: Generador de planilla PDF para capacitaciones presenciales
# ============================================================================

import io
from datetime import date, datetime

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm, mm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle


def build_planilla_presencial_pdf(module, professional, session_date=None, num_rows=25):
    """
    Genera una planilla PDF para capacitación presencial.

    Args:
        module: TrainingModule instance
        professional: CustomUser instance (profesional)
        session_date: fecha de la sesión (date o None para hoy)
        num_rows: cantidad de filas para participantes

    Returns:
        bytes del PDF generado
    """
    buffer = io.BytesIO()

    if session_date is None:
        session_date = date.today()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=1.5 * cm,
        leftMargin=1.5 * cm,
        topMargin=1.5 * cm,
        bottomMargin=1.5 * cm,
    )

    # Estilos
    styles = {
        "title": ParagraphStyle(
            "title",
            fontName="Helvetica-Bold",
            fontSize=16,
            textColor=colors.HexColor("#1a1a2e"),
            alignment=TA_CENTER,
            spaceAfter=6,
        ),
        "subtitle": ParagraphStyle(
            "subtitle",
            fontName="Helvetica",
            fontSize=11,
            textColor=colors.HexColor("#2d3748"),
            alignment=TA_CENTER,
            spaceAfter=4,
        ),
        "header_info": ParagraphStyle(
            "header_info",
            fontName="Helvetica",
            fontSize=10,
            textColor=colors.HexColor("#2d3748"),
            alignment=TA_LEFT,
            spaceAfter=2,
        ),
        "footer": ParagraphStyle(
            "footer",
            fontName="Helvetica-Oblique",
            fontSize=8,
            textColor=colors.HexColor("#718096"),
            alignment=TA_CENTER,
        ),
    }

    story = []

    # === ENCABEZADO ===
    story.append(Paragraph("PLANILLA DE CAPACITACIÓN PRESENCIAL", styles["title"]))
    story.append(Spacer(1, 2 * mm))
    story.append(Paragraph("REGISTRO DE ASISTENCIA", styles["subtitle"]))
    story.append(Spacer(1, 8 * mm))

    # === DATOS DE LA CAPACITACIÓN ===
    page_width = A4[0] - 3 * cm  # ancho disponible

    info_data = [
        ["Capacitación:", module.title],
        ["Responsable:", f"{professional.display_name}"],
        ["Profesión:", f"{professional.profession or 'No especificada'}"],
        ["Matrícula:", f"{professional.license_number or 'No especificada'}"],
        ["Fecha:", session_date.strftime("%d/%m/%Y")],
        ["Lugar:", "________________________________________"],
    ]

    info_table = Table(info_data, colWidths=[3.5 * cm, page_width - 3.5 * cm])
    info_table.setStyle(
        TableStyle(
            [
                ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
                ("FONTNAME", (1, 0), (1, -1), "Helvetica"),
                ("FONTSIZE", (0, 0), (-1, -1), 10),
                ("TEXTCOLOR", (0, 0), (-1, -1), colors.HexColor("#2d3748")),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
            ]
        )
    )
    story.append(info_table)
    story.append(Spacer(1, 10 * mm))

    # === TABLA DE PARTICIPANTES ===
    col_widths = [1 * cm, 6.5 * cm, 3 * cm, page_width - 10.5 * cm]

    # Header
    table_data = [["N°", "Nombre y Apellido", "DNI", "Firma"]]

    # Filas vacías para completar
    for i in range(1, num_rows + 1):
        table_data.append([str(i), "", "", ""])

    participants_table = Table(table_data, colWidths=col_widths, repeatRows=1)
    participants_table.setStyle(
        TableStyle(
            [
                # Header
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2d3748")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, 0), 9),
                ("ALIGN", (0, 0), (-1, 0), "CENTER"),
                # Cuerpo
                ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
                ("FONTSIZE", (0, 1), (-1, -1), 9),
                ("ALIGN", (0, 1), (0, -1), "CENTER"),
                # Bordes
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#a0aec0")),
                # Padding
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                # Altura de filas
                ("ROWHEIGHT", (0, 1), (-1, -1), 22),
                # Alternar color de fondo
                *[
                    ("BACKGROUND", (0, i), (-1, i), colors.HexColor("#f7fafc"))
                    for i in range(2, num_rows + 1, 2)
                ],
            ]
        )
    )
    story.append(participants_table)

    story.append(Spacer(1, 10 * mm))

    # === FOOTER ===
    story.append(
        Paragraph(
            "Documento generado por ErgoSolutions — www.ergosolutions.com.ar",
            styles["footer"],
        )
    )
    story.append(
        Paragraph(
            f"Generado el {datetime.now().strftime('%d/%m/%Y %H:%M')}",
            styles["footer"],
        )
    )

    doc.build(story)
    return buffer.getvalue()
