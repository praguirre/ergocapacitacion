"""Generación autocontenida del resumen cuantitativo en PDF."""

from __future__ import annotations

from io import BytesIO
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.enums import TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


def _text(value) -> str:
    return escape(str(value or "—"))


def _factor_state(factor: dict) -> str:
    state = factor.get("operational_state")
    if state == "sin_iniciar":
        return "Sin iniciar"
    if state == "desactualizado":
        return "Requiere recálculo"
    if state == "borrador":
        return "Borrador"
    if state == "no_aplicable":
        return "No aplicable"
    if state == "revisado":
        return "Revisado"
    if state == "calculado":
        return "Calculado"
    return "Pendiente"


def _factor_level(factor: dict) -> str:
    if factor.get("result_state") != "calculado":
        return "—"
    instance = factor.get("instance")
    if instance is None:
        return "—"
    display = getattr(instance, "get_nivel_riesgo_display", None)
    value = display() if callable(display) else str(factor.get("nivel") or "—")
    calc_data = getattr(instance, "calc_data", {}) or {}
    review = calc_data.get("revision_profesional") or {}
    if review.get("modificada"):
        base = str(review.get("clasificacion_tabla") or "—").title()
        return f"{value} (ajuste profesional; tabla: {base})"
    if calc_data.get("requiere_revision_profesional"):
        return f"{value} (tabla; agravantes revisados)"
    return value


def _draw_page_number(canvas, document) -> None:
    canvas.saveState()
    canvas.setFillColor(colors.HexColor("#64748b"))
    canvas.setFont("Helvetica", 8)
    canvas.drawRightString(
        A4[0] - 15 * mm,
        10 * mm,
        f"Página {document.page}",
    )
    canvas.restoreState()


def build_wizard_summary_pdf(*, risk_eval, factors: list[dict], generated_at) -> bytes:
    """Devuelve un PDF A4 válido sin depender de librerías gráficas del sistema."""
    output = BytesIO()
    document = SimpleDocTemplate(
        output,
        pagesize=A4,
        rightMargin=15 * mm,
        leftMargin=15 * mm,
        topMargin=16 * mm,
        bottomMargin=18 * mm,
        title=f"Resumen de evaluación {risk_eval.pk}",
        author="ErgoApp SRT 886",
    )
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "ErgoTitle",
        parent=styles["Title"],
        textColor=colors.HexColor("#0f3d63"),
        fontSize=18,
        leading=22,
        spaceAfter=5 * mm,
    )
    section_style = ParagraphStyle(
        "ErgoSection",
        parent=styles["Heading2"],
        textColor=colors.HexColor("#0f3d63"),
        fontSize=11,
        leading=14,
        spaceBefore=5 * mm,
        spaceAfter=2 * mm,
    )
    small_style = ParagraphStyle(
        "ErgoSmall",
        parent=styles["BodyText"],
        textColor=colors.HexColor("#475569"),
        fontSize=8,
        leading=11,
    )
    right_style = ParagraphStyle(
        "ErgoRight",
        parent=styles["BodyText"],
        alignment=TA_RIGHT,
    )

    evaluation = risk_eval.evaluacion
    summary = risk_eval.resumen_json or {}
    global_result = (
        risk_eval.resultado_global
        or summary.get("resultado_preliminar")
        or "Sin resultado vigente"
    )
    global_result_kind = (
        "final"
        if risk_eval.resultado_global
        else ("preliminar" if summary.get("resultado_preliminar") else "no disponible")
    )
    story = [
        Paragraph("Resumen de evaluación ergonómica", title_style),
        Table(
            [
                [Paragraph("<b>Evaluación</b>", styles["BodyText"]), f"#{risk_eval.pk}"],
                [Paragraph("<b>Razón social</b>", styles["BodyText"]), Paragraph(_text(evaluation.razon_social), styles["BodyText"])],
                [
                    Paragraph("<b>Establecimiento</b>", styles["BodyText"]),
                    Paragraph(
                        f"{_text(evaluation.direccion_establecimiento)}, {_text(evaluation.provincia)}",
                        styles["BodyText"],
                    ),
                ],
                [
                    Paragraph("<b>Generado</b>", styles["BodyText"]),
                    generated_at.strftime("%d/%m/%Y %H:%M"),
                ],
                [
                    Paragraph("<b>Estado global</b>", styles["BodyText"]),
                    _text(risk_eval.get_estado_display()),
                ],
                [
                    Paragraph("<b>Resultado global</b>", styles["BodyText"]),
                    Paragraph(
                        f"{_text(global_result)} ({global_result_kind})",
                        styles["BodyText"],
                    ),
                ],
            ],
            colWidths=[38 * mm, 137 * mm],
            style=TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#eff6ff")),
                    ("BOX", (0, 0), (-1, -1), 0.8, colors.HexColor("#93c5fd")),
                    ("INNERGRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#bfdbfe")),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("LEFTPADDING", (0, 0), (-1, -1), 6),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                    ("TOPPADDING", (0, 0), (-1, -1), 5),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                ]
            ),
        ),
        Paragraph("Estado de los factores cuantitativos", section_style),
    ]

    rows = [["Factor", "Estado", "Nivel", "Requerido"]]
    for factor in factors:
        rows.append(
            [
                Paragraph(_text(factor.get("label")), styles["BodyText"]),
                Paragraph(_text(_factor_state(factor)), styles["BodyText"]),
                Paragraph(_text(_factor_level(factor)), styles["BodyText"]),
                Paragraph("Sí" if factor.get("required") else "No", right_style),
            ]
        )
    story.append(
        Table(
            rows,
            colWidths=[74 * mm, 42 * mm, 34 * mm, 25 * mm],
            repeatRows=1,
            style=TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#e2e8f0")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.HexColor("#0f172a")),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#cbd5e1")),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("LEFTPADDING", (0, 0), (-1, -1), 5),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 5),
                    ("TOPPADDING", (0, 0), (-1, -1), 5),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                ]
            ),
        )
    )
    story.extend(
        [
            Spacer(1, 7 * mm),
            Paragraph(
                "Documento de apoyo generado por ErgoApp SRT 886. La interpretación "
                "y firma del protocolo deben quedar a cargo de profesionales "
                "competentes. Un resultado en borrador o desactualizado no constituye "
                "una conclusión vigente.",
                small_style,
            ),
        ]
    )

    document.build(
        story,
        onFirstPage=_draw_page_number,
        onLaterPages=_draw_page_number,
    )
    return output.getvalue()
