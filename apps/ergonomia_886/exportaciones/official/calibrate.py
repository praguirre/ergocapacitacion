"""Utilidad de calibración de coordenadas sobre el PDF oficial.

Uso (sólo en desarrollo):

    python -m exportaciones.official.calibrate geometria 1
    python -m exportaciones.official.calibrate etiquetas 1
    python -m exportaciones.official.calibrate regla 1 --salida /tmp/regla.pdf
"""

from __future__ import annotations

import argparse
import io
import re
import sys

from pypdf import PdfReader, PdfWriter
from reportlab.lib import colors
from reportlab.pdfgen import canvas

from .catalog import OFFICIAL_PAGESIZE, official_pdf_bytes

RE_RECT = re.compile(r"([-\d.]+)\s+([-\d.]+)\s+([-\d.]+)\s+([-\d.]+)\s+re")


def _reader() -> PdfReader:
    return PdfReader(io.BytesIO(official_pdf_bytes()))


def cmd_geometria(page_number: int) -> None:
    page = _reader().pages[page_number - 1]
    raw = page.get_contents().get_data().decode("latin-1", "replace")
    rects = [tuple(float(g) for g in m.groups()) for m in RE_RECT.finditer(raw)]

    verticales = sorted({round(x, 2) for x, y, w, h in rects if w <= 2.2 and h > 5})
    horizontales = sorted(
        {round(y, 1) for x, y, w, h in rects if h <= 2.2 and w > 5}, reverse=True
    )
    print(f"PÁGINA {page_number}")
    print("  columnas (x):", verticales)
    print("  filas    (y):", horizontales)
    if len(horizontales) > 2:
        pasos = [round(horizontales[i] - horizontales[i + 1], 2)
                 for i in range(len(horizontales) - 1)]
        print("  pasos entre filas:", pasos)


def cmd_etiquetas(page_number: int) -> None:
    encontrados: list[tuple[float, float, float, str]] = []

    def visitor(text, cm, tm, font_dict, font_size):
        limpio = (text or "").strip()
        if limpio:
            encontrados.append((round(tm[4], 1), round(tm[5], 1),
                                round(font_size, 1), limpio[:70]))

    _reader().pages[page_number - 1].extract_text(visitor_text=visitor)
    print(f"PÁGINA {page_number} — textos ordenados de arriba hacia abajo")
    for x, y, size, texto in sorted(encontrados, key=lambda p: (-p[1], p[0])):
        print(f"  x={x:7.1f} y={y:7.1f} pt={size:4.1f}  {texto!r}")


def cmd_regla(page_number: int, salida: str) -> None:
    """Superpone una cuadrícula de 10 pt con rótulos cada 50 pt."""
    ancho, alto = OFFICIAL_PAGESIZE
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=OFFICIAL_PAGESIZE)
    c.setLineWidth(0.2)

    for x in range(0, int(ancho) + 1, 10):
        c.setStrokeColor(colors.Color(1, 0, 0, alpha=0.5 if x % 50 == 0 else 0.15))
        c.line(x, 0, x, alto)
    for y in range(0, int(alto) + 1, 10):
        c.setStrokeColor(colors.Color(0, 0, 1, alpha=0.5 if y % 50 == 0 else 0.15))
        c.line(0, y, ancho, y)

    c.setFont("Helvetica", 5)
    c.setFillColor(colors.red)
    for x in range(0, int(ancho) + 1, 50):
        c.drawString(x + 1, 3, str(x))
    c.setFillColor(colors.blue)
    for y in range(0, int(alto) + 1, 50):
        c.drawString(2, y + 1, str(y))

    c.showPage()
    c.save()
    buffer.seek(0)

    reader = _reader()
    page = reader.pages[page_number - 1]
    page.merge_page(PdfReader(buffer).pages[0])
    writer = PdfWriter()
    writer.add_page(page)
    with open(salida, "wb") as fh:
        writer.write(fh)
    print(f"Regla generada en {salida}")


def cmd_anclas(page_number: int) -> None:
    """Devuelve la línea base de cada número de ítem de la columna Nº.

    Implementa el refinamiento R-1: las marcas SI/NO se anclan a la altura
    del número impreso de la fila, no a la banda del separador vertical.
    Es inmune a las fusiones de encabezado con primer ítem y funciona igual
    en las nueve páginas de Planilla 2, cuyas columnas SI/NO no comparten x.
    """
    page = _reader().pages[page_number - 1]
    raw = page.get_contents().get_data().decode("latin-1", "replace")
    rects = [tuple(float(g) for g in m.groups()) for m in RE_RECT.finditer(raw)]

    crudas = sorted({round(x, 2) for x, y, w, h in rects if w <= 2.2 and h > 5})
    verticales: list[float] = []
    grupo: list[float] = []
    for valor in crudas:
        if grupo and valor - grupo[-1] > 1.5:
            verticales.append(round(sum(grupo) / len(grupo), 2))
            grupo = []
        grupo.append(valor)
    if grupo:
        verticales.append(round(sum(grupo) / len(grupo), 2))

    interiores = [x for x in verticales if 300 < x < 570]
    if len(interiores) < 3:
        print(f"PÁGINA {page_number}: no se detectaron columnas SI/NO.")
        return
    x_si, x_no, x_fin = interiores[0], interiores[1], interiores[2]
    x_num0, x_num1 = verticales[0], verticales[1]

    textos: list[tuple[float, float, str]] = []

    def visitor(text, cm, tm, font_dict, font_size):
        limpio = (text or "").strip()
        if limpio:
            textos.append((round(tm[4], 2), round(tm[5], 2), limpio))

    page.extract_text(visitor_text=visitor)

    lineas = sorted(
        (y for x, y, t in textos
         if t.isdigit() and x_num0 - 2 <= x <= x_num1 + 6 and 100 < y < 720),
        reverse=True,
    )

    print(f"PÁGINA {page_number}")
    print(f"  columna SI  : x0={x_si}  x1={x_no}  centro={round((x_si + x_no) / 2, 2)}")
    print(f"  columna NO  : x0={x_no}  x1={x_fin}  centro={round((x_no + x_fin) / 2, 2)}")
    print(f"  columna Nº  : x0={x_num0}  x1={x_num1}")
    print(f"  ítems detectados: {len(lineas)}")
    for indice, y in enumerate(lineas, start=1):
        print(f"     ítem {indice:>2}  y = {y}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Calibración del PDF oficial SRT 886.")
    sub = parser.add_subparsers(dest="comando", required=True)

    p_geo = sub.add_parser("geometria")
    p_geo.add_argument("pagina", type=int)

    p_lab = sub.add_parser("etiquetas")
    p_lab.add_argument("pagina", type=int)

    p_reg = sub.add_parser("regla")
    p_reg.add_argument("pagina", type=int)
    p_reg.add_argument("--salida", default="regla.pdf")

    p_anc = sub.add_parser("anclas")
    p_anc.add_argument("pagina", type=int)

    args = parser.parse_args(argv)
    if args.comando == "geometria":
        cmd_geometria(args.pagina)
    elif args.comando == "etiquetas":
        cmd_etiquetas(args.pagina)
    elif args.comando == "anclas":
        cmd_anclas(args.pagina)
    else:
        cmd_regla(args.pagina, args.salida)
    return 0


if __name__ == "__main__":
    sys.exit(main())
