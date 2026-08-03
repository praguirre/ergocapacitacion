"""Traducción de payloads a operaciones de dibujo sobre el PDF oficial.

Este módulo no consulta la base de datos: recibe los dicts que produce
`exportaciones.serializers` y devuelve `PageOps`.
"""

from __future__ import annotations

import math
from typing import Any, Dict, List, Sequence

from .catalog import get_planilla_definition, load_page_map
from .overlay import DrawOp, PageOps


def _campo_op(mapa: Dict[str, Any], clave: str, valor: str) -> DrawOp | None:
    if not valor:
        return None
    spec = mapa["campos"].get(clave)
    if spec is None:
        return None
    fuente, cuerpo = mapa.get("default_font", ["Helvetica", 8.5])
    return DrawOp(
        text=str(valor), x=float(spec["x"]), y=float(spec["y"]),
        font=spec.get("font", fuente), size=float(spec.get("size", cuerpo)),
        align=spec.get("align", "left"), max_width=spec.get("max_width"),
        wrap=bool(spec.get("wrap", False)), leading=float(spec.get("leading", 9.0)),
        max_lines=int(spec.get("max_lines", 1)),
    )


def _pie_hoja(mapa: Dict[str, Any], numero: int, total: int) -> List[DrawOp]:
    op = _campo_op(mapa, "hoja_nro", f"{numero} de {total}")
    return [op] if op else []


def _marca_checkbox(mapa: Dict[str, Any], marca: str | None,
                    y_baseline: float) -> DrawOp | None:
    """Dibuja la X en SI o NO a la altura del número impreso (R-1)."""
    if marca not in ("si", "no"):
        return None
    cfg = mapa["checkbox"]
    fuente, cuerpo = cfg.get("font", ["Helvetica-Bold", 10.0])
    return DrawOp(text=cfg.get("marca", "X"), x=float(cfg["columnas"][marca]),
                  y=float(y_baseline), font=fuente, size=float(cuerpo), align="center")


def build_planilla1_pages(payload: Dict[str, Any], *,
                          hoja: int = 1, total_hojas: int = 1) -> List[PageOps]:
    definition = get_planilla_definition("planilla1")
    mapa = load_page_map(definition.map_file)
    pagina = PageOps(page_index=definition.page_index)
    if not payload.get("existe"):
        return [pagina]
    for clave, valor in (
        ("razon_social", payload["razon_social"]), ("cuit", payload["cuit"]),
        ("ciiu", payload["ciiu"]), ("direccion", payload["direccion"]),
        ("provincia", payload["provincia"]), ("area_sector", payload["area_sector"]),
        ("nro_trabajadores", payload["nro_trabajadores"]),
        ("puesto_trabajo", payload["puesto_trabajo"]),
        ("procedimiento_si_no", payload["procedimiento_escrito"]),
        ("capacitacion_si_no", payload["capacitacion"]),
        ("nombres_trabajadores", payload["nombres_trabajadores"]),
        ("manifestacion_si_no", payload["manifestacion_temprana"]),
        ("ubicacion_sintoma", payload["ubicacion_sintoma"]),
        ("tarea_1", payload["tarea_1"]), ("tarea_2", payload["tarea_2"]),
        ("tarea_3", payload["tarea_3"]), ("fecha", payload["fecha_creacion"]),
    ):
        pagina.add(_campo_op(mapa, clave, valor))
    matriz = mapa["matriz_factores"]
    top, alto, offset = float(matriz["fila_top_y"]), float(matriz["fila_alto"]), float(matriz["offset_baseline"])
    columnas = matriz["columnas"]
    fuente, cuerpo = mapa.get("default_font", ["Helvetica", 8.5])
    indices = {tipo: i for i, tipo in enumerate(matriz["orden"])}
    for factor in payload["factores"]:
        indice = indices.get(factor["tipo"])
        if indice is None:
            continue
        y = top - alto * indice + offset
        def centrado(clave: str, texto: str, size: float = cuerpo) -> DrawOp | None:
            if not texto:
                return None
            col = columnas[clave]
            return DrawOp(text=texto, x=(float(col["x0"]) + float(col["x1"])) / 2.0,
                          y=y, font=fuente, size=size, align="center",
                          max_width=float(col["x1"]) - float(col["x0"]) - 4.0)
        pagina.add(centrado("tarea1", "X" if factor["tarea1"] else ""))
        pagina.add(centrado("tarea2", "X" if factor["tarea2"] else ""))
        pagina.add(centrado("tarea3", "X" if factor["tarea3"] else ""))
        pagina.add(centrado("tiempo", factor["tiempo_exposicion"], size=7.0))
        pagina.add(centrado("nivel1", factor["nivel1"]))
        pagina.add(centrado("nivel2", factor["nivel2"]))
        pagina.add(centrado("nivel3", factor["nivel3"]))
    pagina.extend(_pie_hoja(mapa, hoja, total_hojas))
    return [pagina]


def build_planilla2_pages(planilla_slug: str, payloads: Sequence[Dict[str, Any]],
                          *, hoja_inicial: int = 1,
                          total_hojas: int = 1) -> List[PageOps]:
    """Devuelve una página por instancia de la planilla (hueco G-4)."""
    definition = get_planilla_definition(planilla_slug)
    mapa = load_page_map(definition.map_file)
    paginas: List[PageOps] = []
    for desplazamiento, payload in enumerate(payloads):
        pagina = PageOps(page_index=definition.page_index)
        if not payload.get("existe"):
            paginas.append(pagina)
            continue
        for clave, valor in (
            ("area_sector", payload["area_sector"]),
            ("puesto_trabajo", payload["puesto_trabajo"]),
            ("tarea_nro", payload["tarea_nro"]),
            ("fecha", payload["fecha_creacion"]),
        ):
            pagina.add(_campo_op(mapa, clave, valor))
        respuestas = payload.get("respuestas", {})
        for item in mapa["items"]:
            pagina.add(_marca_checkbox(mapa, respuestas.get(item["campo"]), item["y"]))
        pagina.extend(_pie_hoja(mapa, hoja_inicial + desplazamiento, total_hojas))
        paginas.append(pagina)
    return paginas


def build_planilla3_pages(payload: Dict[str, Any], *,
                          hoja_inicial: int = 1,
                          total_hojas: int = 1) -> List[PageOps]:
    definition = get_planilla_definition("planilla3")
    mapa = load_page_map(definition.map_file)

    if not payload.get("existe"):
        return [PageOps(page_index=definition.page_index)]

    especificas = payload.get("especificas", [])
    cfg = mapa["medidas_especificas"]
    por_pagina = int(cfg["filas_por_pagina"])
    total_paginas = max(1, math.ceil(len(especificas) / por_pagina))

    paginas: List[PageOps] = []
    for indice_pagina in range(total_paginas):
        pagina = PageOps(page_index=definition.page_index)

        for clave, valor in (
            ("razon_social", payload["razon_social"]),
            ("nombres_trabajadores", payload["nombres_trabajadores"]),
            ("direccion", payload["direccion"]),
            ("area_sector", payload["area_sector"]),
            ("puesto_trabajo", payload["puesto_trabajo"]),
            ("tarea_analizada", payload["tarea_analizada"]),
        ):
            pagina.add(_campo_op(mapa, clave, valor))

        if indice_pagina == 0:
            obs_col = mapa["observaciones_col"]
            fuente, cuerpo = mapa.get("default_font", ["Helvetica", 7.5])
            for general in payload["generales"]:
                banda = next(
                    (g for g in mapa["medidas_generales"]
                     if g["campo"] == general["campo"]),
                    None,
                )
                if banda is None:
                    continue
                pagina.add(_marca_checkbox(mapa, general["marca"], banda["y"]))
                if general["fecha"]:
                    pagina.add(DrawOp(
                        text=f"Fecha: {general['fecha']}",
                        x=float(obs_col["x0"]) + 3.0,
                        y=float(banda["y"]),
                        font=fuente,
                        size=cuerpo,
                        max_width=float(obs_col["x1"]) - float(obs_col["x0"]) - 6.0,
                    ))
            pagina.add(_campo_op(
                mapa, "observaciones_generales", payload["observaciones_generales"]
            ))

        lote = especificas[indice_pagina * por_pagina:(indice_pagina + 1) * por_pagina]
        primera_y = float(cfg["primera_fila_y"])
        alto = float(cfg["alto_fila"])
        offset = float(cfg["offset_baseline"])
        fuente_med, cuerpo_med = cfg.get("font", ["Helvetica", 6.5])
        num_col = mapa["numero_col"]
        desc_col = mapa["descripcion_col"]
        obs_col = mapa["observaciones_col"]

        for fila, medida in enumerate(lote):
            y = primera_y - alto * fila + offset
            pagina.add(DrawOp(
                text=str(medida["numero"]),
                x=(float(num_col["x0"]) + float(num_col["x1"])) / 2.0,
                y=y, font=fuente_med, size=cuerpo_med, align="center",
            ))
            pagina.add(DrawOp(
                text=medida["descripcion"],
                x=float(desc_col["x0"]) + 3.0, y=y,
                font=fuente_med, size=cuerpo_med,
                max_width=float(desc_col["x1"]) - float(desc_col["x0"]) - 6.0,
            ))
            pagina.add(DrawOp(
                text=medida["observaciones"],
                x=float(obs_col["x0"]) + 3.0, y=y,
                font=fuente_med, size=cuerpo_med,
                max_width=float(obs_col["x1"]) - float(obs_col["x0"]) - 6.0,
            ))

        pagina.extend(_pie_hoja(mapa, hoja_inicial + indice_pagina, total_hojas))
        paginas.append(pagina)

    return paginas


def build_planilla4_pages(payload: Dict[str, Any], *,
                          hoja_inicial: int = 1,
                          total_hojas: int = 1) -> List[PageOps]:
    definition = get_planilla_definition("planilla4")
    mapa = load_page_map(definition.map_file)

    if not payload.get("existe"):
        return [PageOps(page_index=definition.page_index)]

    tabla = mapa["tabla"]
    por_pagina = int(tabla["filas_por_pagina"])
    filas = payload.get("filas", [])
    total_paginas = max(1, math.ceil(len(filas) / por_pagina))
    fuente, cuerpo = mapa.get("default_font", ["Helvetica", 8.0])

    paginas: List[PageOps] = []
    for indice_pagina in range(total_paginas):
        pagina = PageOps(page_index=definition.page_index)

        for clave, valor in (
            ("razon_social", payload["razon_social"]),
            ("cuit", payload["cuit"]),
            ("direccion", payload["direccion"]),
            ("area_sector", payload["area_sector"]),
        ):
            pagina.add(_campo_op(mapa, clave, valor))

        lote = filas[indice_pagina * por_pagina:(indice_pagina + 1) * por_pagina]
        primera_y = float(tabla["primera_fila_y"])
        alto = float(tabla["alto_fila"])
        offset = float(tabla["offset_baseline"])

        for indice_fila, fila in enumerate(lote):
            y = primera_y - alto * indice_fila + offset
            for columna in tabla["columnas"]:
                valor = str(fila.get(columna["clave"], "") or "")
                if not valor:
                    continue
                x0, x1 = float(columna["x0"]), float(columna["x1"])
                alineacion = columna.get("align", "center")
                padding = float(columna.get("padding", 0.0))
                x = {
                    "center": (x0 + x1) / 2.0,
                    "left": x0 + padding,
                    "right": x1 - padding,
                }[alineacion]
                pagina.add(DrawOp(
                    text=valor, x=x, y=y, font=fuente, size=cuerpo,
                    align=alineacion, max_width=x1 - x0 - 6.0,
                    opaque=columna["clave"] == "numero",
                ))

        pagina.extend(_pie_hoja(mapa, hoja_inicial + indice_pagina, total_hojas))
        paginas.append(pagina)

    return paginas


ORDEN_PROTOCOLO = (
    "planilla1", "planilla2a", "planilla2b", "planilla2c", "planilla2d",
    "planilla2e", "planilla2f", "planilla2g", "planilla2h", "planilla2i",
    "planilla3", "planilla4",
)


def build_protocolo_pages(evaluacion_payload: Dict[str, Any]) -> List[PageOps]:
    """Ensambla el protocolo completo y numera con una segunda pasada."""
    def _armar(total: int) -> List[PageOps]:
        paginas: List[PageOps] = []
        for slug in ORDEN_PROTOCOLO:
            hoja = len(paginas) + 1
            if slug == "planilla1":
                paginas.extend(build_planilla1_pages(
                    evaluacion_payload["planilla1"], hoja=hoja, total_hojas=total))
            elif slug == "planilla3":
                paginas.extend(build_planilla3_pages(
                    evaluacion_payload["planilla3"],
                    hoja_inicial=hoja, total_hojas=total))
            elif slug == "planilla4":
                paginas.extend(build_planilla4_pages(
                    evaluacion_payload["planilla4"],
                    hoja_inicial=hoja, total_hojas=total))
            else:
                paginas.extend(build_planilla2_pages(
                    slug, evaluacion_payload["planillas2"][slug],
                    hoja_inicial=hoja, total_hojas=total))
        return paginas

    return _armar(len(_armar(0)))
