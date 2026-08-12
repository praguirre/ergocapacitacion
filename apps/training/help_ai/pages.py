"""Identidad humana de cada pantalla del área de Capacitaciones.

El slug es un identificador técnico: el modelo no puede deducir de él en qué
pantalla está parado el usuario. Este registro le da a cada slug un título y
una ruta reales, que el preámbulo del prompt afirma como hecho.

Regla dura: este módulo NO lee la base de datos ni el request. Sólo traduce un
slug del catálogo a texto estático. Toda entrada debe existir en
`ALLOWED_HELP_SLUGS` y viceversa; el test de cobertura lo verifica.

Los tramos variables se muestran como <modulo> y <id> a propósito: el prompt no
debe afirmar un identificador concreto que no conoce.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class PageInfo:
    """Título, ruta y propósito de una pantalla, en lenguaje de usuario."""

    titulo: str
    ruta: str
    proposito: str


# Rutas verificadas contra el resolvedor de URLs en el commit 4187b10.
PAGE_INFO: dict[str, PageInfo] = {
    "home": PageInfo(
        "Área de Capacitaciones",
        "/dashboard/capacitaciones/",
        "ayuda general del área de capacitaciones; esta entrada es el respaldo "
        "que se usa cuando una pantalla no declara su propia guía",
    ),
    "capacitaciones_menu": PageInfo(
        "Menú de capacitaciones",
        "/dashboard/capacitaciones/",
        "listado de las capacitaciones generales y personalizadas disponibles "
        "para la cuenta, con acceso a elegir la modalidad de dictado",
    ),
    "modalidad_selector": PageInfo(
        "Elegir la modalidad de la capacitación",
        "/dashboard/capacitaciones/<modulo>/",
        "elección entre dictar la capacitación en modo presencial o generar "
        "links para el modo online",
    ),
    "online_links": PageInfo(
        "Links de la capacitación online",
        "/dashboard/capacitaciones/<modulo>/links/",
        "generación, copia y seguimiento de los links que se comparten con los "
        "trabajadores para que realicen la capacitación por su cuenta",
    ),
    "share_link": PageInfo(
        "Compartir un link por correo",
        "/dashboard/capacitaciones/<modulo>/links/<id>/compartir/",
        "envío del link de la capacitación a una o varias direcciones de correo "
        "y consulta de los envíos anteriores",
    ),
    "presencial_capacitacion": PageInfo(
        "Dictado presencial de la capacitación",
        "/dashboard/presencial/<modulo>/",
        "pantalla de proyección: video de la capacitación, chat con Ergobot "
        "para consultas del grupo y acceso al quiz presencial",
    ),
    "presencial_quiz": PageInfo(
        "Quiz presencial",
        "/dashboard/presencial/<modulo>/quiz/",
        "evaluación grupal del dictado presencial, con resultado inmediato y "
        "generación de la planilla de asistencia",
    ),
    "presencial_historial": PageInfo(
        "Historial de capacitaciones presenciales",
        "/dashboard/presencial/historial/",
        "listado de las sesiones presenciales registradas por el profesional, "
        "con fecha, ubicación, participantes y resultado del quiz",
    ),
}


def page_info(slug: str) -> PageInfo:
    """Ficha de la pantalla. Falla cerrado: un slug sin ficha es un error."""
    try:
        return PAGE_INFO[slug]
    except KeyError as exc:
        raise KeyError(
            f"El slug {slug!r} no tiene ficha de pantalla en pages.PAGE_INFO. "
            "Toda página habilitada debe declarar título, ruta y propósito."
        ) from exc
