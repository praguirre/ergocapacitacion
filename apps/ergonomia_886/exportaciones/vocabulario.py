"""Traducciones entre los vocabularios de `planillas` y `evaluaciones`.

Existe un único lugar donde se resuelve esta divergencia. Cualquier otro
módulo que la reimplemente introduce una inconsistencia en un documento
que se presenta ante terceros.
"""

from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import Any

NIVEL_A_NUMERO = {
    "bajo": 1,
    "medio": 2,
    "alto": 3,
    "no_aplicable": None,
}

NUMERO_A_ETIQUETA = {
    1: "Nivel 1: Tolerable",
    2: "Nivel 2: Moderado",
    3: "Nivel 3: No Tolerable",
}

ESTADO_OPERATIVO_LEGIBLE = {
    "sin_iniciar": "Sin iniciar",
    "borrador": "Borrador",
    "desactualizado": "Requiere recálculo",
    "no_aplicable": "No aplicable",
    "calculado": "Calculado",
    "revisado": "Revisado",
}


def nivel_a_numero(nivel: str | None) -> int | None:
    """Convierte `bajo|medio|alto|no_aplicable` al 1/2/3 del formulario."""
    if not nivel:
        return None
    return NIVEL_A_NUMERO.get(str(nivel))


def nivel_numerico_texto(nivel: str | None) -> str:
    numero = nivel_a_numero(nivel)
    return "" if numero is None else str(numero)


def marca_si_no(valor: bool | None, *, respondido: bool) -> str | None:
    """Devuelve 'si', 'no' o None según la regla del hueco G-2."""
    if not respondido:
        return None
    return "si" if bool(valor) else "no"


def fecha_es(valor: date | datetime | None) -> str:
    """Formato de fecha argentino. Cadena vacía si no hay dato."""
    if valor is None:
        return ""
    if isinstance(valor, datetime):
        valor = valor.date()
    return valor.strftime("%d/%m/%Y")


def numero_es(valor: Any, decimales: int = 2) -> str:
    """Formato numérico con coma decimal. Cadena vacía si no hay dato."""
    if valor is None or valor == "":
        return ""
    if isinstance(valor, bool):
        return "Sí" if valor else "No"
    try:
        numero = Decimal(str(valor))
    except Exception:
        return str(valor)
    texto = f"{numero:.{decimales}f}".rstrip("0").rstrip(".")
    return (texto or "0").replace(".", ",")


def si_no(valor: bool | None) -> str:
    if valor is None:
        return "—"
    return "SI" if valor else "NO"


__all__ = (
    "ESTADO_OPERATIVO_LEGIBLE",
    "NIVEL_A_NUMERO",
    "NUMERO_A_ETIQUETA",
    "fecha_es",
    "marca_si_no",
    "nivel_a_numero",
    "nivel_numerico_texto",
    "numero_es",
    "si_no",
)
