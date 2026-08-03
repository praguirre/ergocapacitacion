"""Render de los documentos propios de ErgoApp: detalle técnico e informe."""

from __future__ import annotations

import json
from io import BytesIO
from typing import Any, Dict, Iterable, List
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

AZUL = colors.HexColor("#0f3d63")
AZUL_CLARO = colors.HexColor("#eff6ff")
BORDE = colors.HexColor("#93c5fd")
GRIS = colors.HexColor("#cbd5e1")
GRIS_TEXTO = colors.HexColor("#475569")

AVISO_LEGAL = (
    "Documento de apoyo generado por ErgoApp SRT 886. No constituye una "
    "homologación ni un dictamen automático. La interpretación, la validación "
    "de las mediciones y la firma del protocolo quedan a cargo de los "
    "profesionales competentes. Un resultado en estado borrador o "
    "desactualizado no constituye una conclusión vigente."
)


def _t(valor: Any) -> str:
    if valor is None or valor == "":
        return "—"
    if isinstance(valor, bool):
        valor = "Sí" if valor else "No"
    return escape(str(valor))


def _estilos() -> Dict[str, ParagraphStyle]:
    base = getSampleStyleSheet()
    return {
        "base": base,
        "titulo": ParagraphStyle(
            "ErgoTitulo", parent=base["Title"], textColor=AZUL,
            fontSize=17, leading=21, spaceAfter=4 * mm,
        ),
        "seccion": ParagraphStyle(
            "ErgoSeccion", parent=base["Heading2"], textColor=AZUL,
            fontSize=11, leading=14, spaceBefore=5 * mm, spaceAfter=2 * mm,
        ),
        "subseccion": ParagraphStyle(
            "ErgoSubseccion", parent=base["Heading3"], textColor=AZUL,
            fontSize=9.5, leading=12, spaceBefore=3 * mm, spaceAfter=1.5 * mm,
        ),
        "cuerpo": base["BodyText"],
        "mono": ParagraphStyle(
            "ErgoMono", parent=base["BodyText"], fontName="Courier",
            fontSize=6.5, leading=8, textColor=GRIS_TEXTO,
        ),
        "pequeno": ParagraphStyle(
            "ErgoPequeno", parent=base["BodyText"], textColor=GRIS_TEXTO,
            fontSize=7.5, leading=10,
        ),
    }


def _numero_pagina(canvas_obj, documento) -> None:
    canvas_obj.saveState()
    canvas_obj.setFillColor(colors.HexColor("#64748b"))
    canvas_obj.setFont("Helvetica", 8)
    canvas_obj.drawRightString(A4[0] - 15 * mm, 10 * mm, f"Página {documento.page}")
    canvas_obj.restoreState()


def _tabla_clave_valor(filas: Iterable[tuple[str, Any]], estilos) -> Table:
    datos = [
        [Paragraph(f"<b>{escape(str(k))}</b>", estilos["cuerpo"]),
         Paragraph(_t(v), estilos["cuerpo"])]
        for k, v in filas
    ]
    if not datos:
        datos = [[Paragraph("<b>Sin datos</b>", estilos["cuerpo"]),
                  Paragraph("—", estilos["cuerpo"])]]
    return Table(
        datos,
        colWidths=[58 * mm, 117 * mm],
        style=TableStyle([
            ("BACKGROUND", (0, 0), (0, -1), AZUL_CLARO),
            ("BOX", (0, 0), (-1, -1), 0.8, BORDE),
            ("INNERGRID", (0, 0), (-1, -1), 0.25, BORDE),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("LEFTPADDING", (0, 0), (-1, -1), 5),
            ("RIGHTPADDING", (0, 0), (-1, -1), 5),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ]),
    )


def _tabla_matriz(encabezados: List[str], filas: List[List[str]],
                  anchos: List[float], estilos) -> Table:
    datos = [[Paragraph(f"<b>{escape(h)}</b>", estilos["cuerpo"]) for h in encabezados]]
    for fila in filas:
        datos.append([Paragraph(_t(c), estilos["pequeno"]) for c in fila])
    return Table(
        datos, colWidths=anchos, repeatRows=1,
        style=TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#e2e8f0")),
            ("GRID", (0, 0), (-1, -1), 0.4, GRIS),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("LEFTPADDING", (0, 0), (-1, -1), 4),
            ("RIGHTPADDING", (0, 0), (-1, -1), 4),
            ("TOPPADDING", (0, 0), (-1, -1), 3),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ]),
    )


def _bloque_encabezado(cabecera: Dict[str, Any], titulo: str,
                       generado_en, estilos) -> List[Any]:
    return [
        Paragraph(escape(titulo), estilos["titulo"]),
        _tabla_clave_valor(
            [
                ("Evaluación", f"#{cabecera['evaluacion_id']}"),
                ("Razón social", cabecera["razon_social"]),
                ("C.U.I.T.", cabecera["cuit"]),
                ("Establecimiento",
                 f"{cabecera['direccion']}, {cabecera['provincia']}"),
                ("Área y sector", cabecera["area_sector"]),
                ("Puesto de trabajo", cabecera["puesto_trabajo"]),
                ("Generado", generado_en.strftime("%d/%m/%Y %H:%M")),
            ],
            estilos,
        ),
    ]


def _bloque_factor(payload: Dict[str, Any], estilos) -> List[Any]:
    """Detalle completo de un factor: inputs + calc_data íntegro."""
    bloque: List[Any] = [
        Paragraph(escape(payload["factor_label"]), estilos["seccion"])
    ]

    if not payload.get("existe"):
        bloque.append(Paragraph(
            "Este factor no fue iniciado. No hay datos que exportar.",
            estilos["cuerpo"],
        ))
        return bloque

    bloque.append(_tabla_clave_valor(
        [
            ("Estado operativo", payload["estado_operativo"]),
            ("Estado del resultado", payload["estado_resultado"]),
            ("Aplicable", payload["aplicable"]),
            ("Nivel de riesgo", payload["nivel_riesgo_display"]),
            ("Nivel equivalente SRT", payload["nivel_numerico_srt"]),
            ("Calculado en", payload["calculado_en"]),
            ("Revisado en", payload["revisado_en"]),
            ("Revisado por", payload["revisado_por"]),
        ],
        estilos,
    ))

    bloque.append(Paragraph("Datos de entrada declarados", estilos["subseccion"]))
    bloque.append(_tabla_clave_valor(sorted(payload["inputs"].items()), estilos))

    revision = payload.get("revision_profesional") or {}
    if payload.get("requiere_revision_profesional") or revision:
        bloque.append(Paragraph("Juicio profesional aplicado", estilos["subseccion"]))
        bloque.append(_tabla_clave_valor(
            [
                ("Clasificación por tabla", revision.get("clasificacion_tabla")),
                ("Clasificación final", revision.get("clasificacion_final")),
                ("¿Fue modificada?", revision.get("modificada")),
                ("Agravantes considerados",
                 ", ".join(payload.get("agravantes_presentes", [])) or None),
                ("Justificación", revision.get("justificacion")),
            ],
            estilos,
        ))

    if payload.get("segmentos"):
        bloque.append(Paragraph("Tramos de exposición medidos", estilos["subseccion"]))
        bloque.append(_tabla_matriz(
            ["Vehículo / máquina", "Asiento", "Terreno", "h", "aw,x", "aw,y", "aw,z"],
            [
                [s["vehiculo_maquina"], s["tipo_asiento"], s["superficie_terreno"],
                 s["tiempo_horas"], s["aw_x"], s["aw_y"], s["aw_z"]]
                for s in payload["segmentos"]
            ],
            [45 * mm, 28 * mm, 28 * mm, 14 * mm, 20 * mm, 20 * mm, 20 * mm],
            estilos,
        ))
        evidencia = payload.get("evidencia_declarada") or {}
        if evidencia.get("foto_montaje") or evidencia.get("certificado_calibracion"):
            bloque.append(Paragraph(
                "Evidencia declarada (no adjunta a este documento): "
                f"{escape(evidencia.get('foto_montaje') or '—')} · "
                f"{escape(evidencia.get('certificado_calibracion') or '—')}.",
                estilos["pequeno"],
            ))

    fuentes = payload.get("fuentes") or []
    if fuentes:
        bloque.append(Paragraph("Fuentes normativas utilizadas", estilos["subseccion"]))
        bloque.append(_tabla_matriz(
            ["Artefacto", "Versión de datos", "Vigencia", "SHA-256 (12)"],
            [
                [
                    f.get("archivo", ""),
                    f.get("data_version", ""),
                    f.get("artifact_effective_date", ""),
                    (f.get("sha256", "") or "")[:12],
                ]
                for f in fuentes
            ],
            [55 * mm, 30 * mm, 40 * mm, 50 * mm],
            estilos,
        ))

    if payload.get("observaciones_profesional"):
        bloque.append(Paragraph("Observaciones del profesional", estilos["subseccion"]))
        bloque.append(Paragraph(
            escape(payload["observaciones_profesional"]).replace("\n", "<br/>"),
            estilos["cuerpo"],
        ))

    bloque.append(Paragraph("Trazabilidad completa del cálculo", estilos["subseccion"]))
    volcado = json.dumps(payload["calc_data"], indent=1, ensure_ascii=False,
                         sort_keys=True, default=str)
    for trozo in volcado.splitlines():
        bloque.append(Paragraph(escape(trozo).replace(" ", "&nbsp;"), estilos["mono"]))

    return bloque


def build_factor_detail_pdf(*, cabecera: Dict[str, Any],
                            factores: List[Dict[str, Any]],
                            generado_en, titulo: str) -> bytes:
    """PDF A4 con el detalle técnico de uno o varios factores."""
    salida = BytesIO()
    estilos = _estilos()
    documento = SimpleDocTemplate(
        salida, pagesize=A4,
        rightMargin=15 * mm, leftMargin=15 * mm,
        topMargin=16 * mm, bottomMargin=18 * mm,
        title=titulo, author="ErgoApp SRT 886",
    )

    historia: List[Any] = _bloque_encabezado(cabecera, titulo, generado_en, estilos)
    for indice, payload in enumerate(factores):
        if indice:
            historia.append(PageBreak())
        historia.extend(_bloque_factor(payload, estilos))

    historia.extend([
        Spacer(1, 7 * mm),
        Paragraph(AVISO_LEGAL, estilos["pequeno"]),
    ])

    documento.build(historia, onFirstPage=_numero_pagina, onLaterPages=_numero_pagina)
    return salida.getvalue()


def build_professional_report_pdf(*, cabecera: Dict[str, Any],
                                  payload: Dict[str, Any],
                                  markdown_llm: str,
                                  metadatos: Dict[str, Any],
                                  generado_en) -> bytes:
    """PDF del informe profesional: datos + prosa redactada por el modelo."""
    salida = BytesIO()
    estilos = _estilos()
    titulo = f"Informe técnico — {payload['factor_label']}"
    documento = SimpleDocTemplate(
        salida, pagesize=A4,
        rightMargin=18 * mm, leftMargin=18 * mm,
        topMargin=16 * mm, bottomMargin=18 * mm,
        title=titulo, author="ErgoApp SRT 886",
    )

    historia: List[Any] = _bloque_encabezado(cabecera, titulo, generado_en, estilos)
    historia.append(Paragraph("Redacción profesional asistida", estilos["seccion"]))
    historia.append(Paragraph(
        "El texto que sigue fue redactado por un modelo de lenguaje a partir "
        "exclusivamente de los datos registrados en la aplicación. Los niveles "
        "de riesgo, los límites y las clasificaciones provienen del motor de "
        "cálculo determinístico de ErgoApp, no del modelo de lenguaje.",
        estilos["pequeno"],
    ))
    historia.append(Spacer(1, 3 * mm))
    historia.extend(_markdown_a_flowables(markdown_llm, estilos))

    historia.append(PageBreak())
    historia.append(Paragraph("Anexo — Datos de respaldo", estilos["seccion"]))
    historia.extend(_bloque_factor(payload, estilos))

    historia.extend([
        Spacer(1, 6 * mm),
        Paragraph("Trazabilidad de la generación", estilos["subseccion"]),
        _tabla_clave_valor(
            [
                ("Modelo", metadatos.get("modelo_llm")),
                ("Versión del prompt", metadatos.get("prompt_version")),
                ("Huella de los datos", (metadatos.get("inputs_hash") or "")[:16]),
                ("Duración", f"{metadatos.get('duracion_ms', 0)} ms"),
            ],
            estilos,
        ),
        Spacer(1, 5 * mm),
        Paragraph(AVISO_LEGAL, estilos["pequeno"]),
    ])

    documento.build(historia, onFirstPage=_numero_pagina, onLaterPages=_numero_pagina)
    return salida.getvalue()


def _markdown_a_flowables(texto: str, estilos) -> List[Any]:
    """Conversión mínima y segura de Markdown a flowables de ReportLab.

    Se admite deliberadamente un subconjunto muy chico (encabezados, viñetas,
    negrita, cursiva). Todo lo demás se escapa: el texto viene de un modelo y
    no debe poder inyectar marcado arbitrario en el PDF.
    """
    import re

    flowables: List[Any] = []
    for linea_cruda in (texto or "").splitlines():
        linea = linea_cruda.rstrip()
        if not linea.strip():
            flowables.append(Spacer(1, 2.5 * mm))
            continue

        nivel = len(linea) - len(linea.lstrip("#"))
        contenido = linea.lstrip("#").strip() if nivel else linea.strip()

        viñeta = contenido.startswith(("- ", "* ", "• "))
        if viñeta:
            contenido = "• " + contenido[2:].strip()

        seguro = escape(contenido)
        seguro = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", seguro)
        seguro = re.sub(r"(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)", r"<i>\1</i>", seguro)

        if nivel == 1:
            flowables.append(Paragraph(seguro, estilos["seccion"]))
        elif nivel >= 2:
            flowables.append(Paragraph(seguro, estilos["subseccion"]))
        else:
            flowables.append(Paragraph(seguro, estilos["cuerpo"]))
    return flowables


__all__ = (
    "AVISO_LEGAL",
    "build_factor_detail_pdf",
    "build_professional_report_pdf",
)
