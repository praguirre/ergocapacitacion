"""Motor genérico de superposición sobre el PDF oficial de la SRT.

Diseño: este módulo NO conoce el dominio de negocio. Recibe operaciones de
dibujo ya resueltas y las estampa sobre las páginas indicadas del oficial.
La capa base del documento oficial nunca se modifica.
"""

from __future__ import annotations

import io
from dataclasses import dataclass, field
from typing import Iterable, Literal, Sequence

from pypdf import PdfReader, PdfWriter
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.pdfgen import canvas

from .catalog import OFFICIAL_PAGESIZE, official_pdf_bytes

Align = Literal["left", "center", "right"]

DEFAULT_FONT = "Helvetica"
DEFAULT_SIZE = 8.5
ELLIPSIS = "…"


@dataclass(frozen=True)
class DrawOp:
    """Una operación de dibujo de texto sobre la capa de superposición."""

    text: str
    x: float
    y: float
    font: str = DEFAULT_FONT
    size: float = DEFAULT_SIZE
    align: Align = "left"
    max_width: float | None = None
    wrap: bool = False
    leading: float = 9.0
    max_lines: int = 1
    opaque: bool = False


@dataclass
class PageOps:
    """Conjunto de operaciones a estampar sobre una página del oficial."""

    page_index: int
    ops: list[DrawOp] = field(default_factory=list)

    def add(self, op: DrawOp | None) -> None:
        if op is not None and op.text:
            self.ops.append(op)

    def extend(self, ops: Iterable[DrawOp | None]) -> None:
        for op in ops:
            self.add(op)


def _truncate(text: str, font: str, size: float, max_width: float) -> str:
    """Recorta con elipsis para no invadir celdas vecinas del formulario."""
    if stringWidth(text, font, size) <= max_width:
        return text
    recorte = text
    while recorte and stringWidth(recorte + ELLIPSIS, font, size) > max_width:
        recorte = recorte[:-1]
    return (recorte + ELLIPSIS) if recorte else ""


def _wrap(text: str, font: str, size: float, max_width: float,
          max_lines: int) -> list[str]:
    """Divide en líneas por palabras respetando el ancho de la celda."""
    palabras = text.split()
    lineas: list[str] = []
    actual = ""
    for palabra in palabras:
        tentativa = f"{actual} {palabra}".strip()
        if stringWidth(tentativa, font, size) <= max_width or not actual:
            actual = tentativa
        else:
            lineas.append(actual)
            actual = palabra
            if len(lineas) == max_lines:
                break
    if actual and len(lineas) < max_lines:
        lineas.append(actual)
    if len(lineas) == max_lines and len(" ".join(lineas)) < len(text):
        lineas[-1] = _truncate(lineas[-1] + " " + ELLIPSIS, font, size, max_width)
    return lineas


def _draw(c: canvas.Canvas, op: DrawOp) -> None:
    c.setFont(op.font, op.size)

    if op.opaque and op.max_width:
        if op.align == "center":
            x0 = op.x - op.max_width / 2.0
        elif op.align == "right":
            x0 = op.x - op.max_width
        else:
            x0 = op.x
        c.saveState()
        c.setFillColorRGB(1, 1, 1)
        c.rect(x0, op.y - 2.0, op.max_width, op.size + 4.0,
               stroke=0, fill=1)
        c.restoreState()
        c.setFont(op.font, op.size)

    if op.wrap and op.max_width:
        lineas = _wrap(op.text, op.font, op.size, op.max_width, op.max_lines)
        for i, linea in enumerate(lineas):
            y = op.y - i * op.leading
            _draw_line(c, linea, op, y)
        return

    texto = op.text
    if op.max_width:
        texto = _truncate(texto, op.font, op.size, op.max_width)
    _draw_line(c, texto, op, op.y)


def _draw_line(c: canvas.Canvas, texto: str, op: DrawOp, y: float) -> None:
    if op.align == "center":
        c.drawCentredString(op.x, y, texto)
    elif op.align == "right":
        c.drawRightString(op.x, y, texto)
    else:
        c.drawString(op.x, y, texto)


def render_overlay(ops: Sequence[DrawOp]) -> bytes:
    """Genera un PDF de una página con sólo la capa de datos."""
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=OFFICIAL_PAGESIZE)
    for op in ops:
        _draw(c, op)
    c.showPage()
    c.save()
    return buffer.getvalue()


def stamp_official_pdf(
    pages: Sequence[PageOps],
    *,
    title: str = "Protocolo de Ergonomía SRT 886/15",
    author: str = "ErgoApp SRT 886",
) -> bytes:
    """Devuelve un PDF con las páginas oficiales indicadas, ya rellenadas."""
    if not pages:
        raise ValueError("Se requiere al menos una página para estampar.")

    writer = PdfWriter()
    # PdfWriter identifica cada fuente por ``id(reader)`` al clonar objetos.
    # Mantenerlos vivos evita que Python reutilice un id entre páginas repetidas
    # y que la segunda copia pierda recursos gráficos durante la escritura.
    readers: list[PdfReader] = []
    for page_ops in pages:
        reader = PdfReader(io.BytesIO(official_pdf_bytes()))
        readers.append(reader)
        if not 0 <= page_ops.page_index < len(reader.pages):
            raise ValueError(
                f"Índice de página fuera de rango: {page_ops.page_index}"
            )
        page = reader.pages[page_ops.page_index]
        if page_ops.ops:
            overlay_reader = PdfReader(io.BytesIO(render_overlay(page_ops.ops)))
            readers.append(overlay_reader)
            overlay = overlay_reader.pages[0]
            page.merge_page(overlay)
        # Normalizar cada página antes de incorporarla al documento final.
        # pypdf puede colisionar recursos al añadir consecutivamente varias
        # copias estampadas de la misma página oficial; la serialización
        # intermedia les asigna un espacio de objetos independiente.
        pagina_buffer = io.BytesIO()
        pagina_writer = PdfWriter()
        pagina_writer.add_page(page)
        pagina_writer.write(pagina_buffer)
        pagina_reader = PdfReader(io.BytesIO(pagina_buffer.getvalue()))
        readers.append(pagina_reader)
        writer.add_page(pagina_reader.pages[0])

    writer.add_metadata({"/Title": title, "/Author": author})

    salida = io.BytesIO()
    writer.write(salida)
    return salida.getvalue()


__all__ = ("Align", "DrawOp", "PageOps", "render_overlay", "stamp_official_pdf")
