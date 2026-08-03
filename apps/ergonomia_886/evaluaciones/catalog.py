"""Registro canónico de los factores cuantitativos de ErgoApp.

Este módulo es deliberadamente independiente de Django y de los módulos que
declaran modelos, formularios o vistas. Las referencias se expresan como rutas
de importación para evitar ciclos y permitir que cada consumidor las resuelva
cuando corresponda.
"""

from __future__ import annotations

from dataclasses import dataclass
from types import MappingProxyType
from typing import Mapping, Tuple


@dataclass(frozen=True)
class FactorDefinition:
    enum_name: str
    slug: str
    choice_label: str
    label: str
    icon: str
    route: str
    route_name: str
    view_class: str
    view_kind: str
    form_path: str
    model_path: str
    template_name: str
    help_slug: str
    calculator_slug: str
    data_files: Tuple[str, ...]

    @property
    def route_name_by_eval(self) -> str:
        return f"{self.route_name}_by_eval"


FACTOR_DEFINITIONS = (
    FactorDefinition(
        enum_name="LMC",
        slug="lmc",
        choice_label="Levantamiento Manual de Cargas",
        label="Levantamiento manual de cargas (LMC)",
        icon="bi bi-box-seam",
        route="lmc/",
        route_name="lmc_form",
        view_class="LMCView",
        view_kind="standard",
        form_path="apps.ergonomia_886.evaluaciones.forms.LMCForm",
        model_path="apps.ergonomia_886.evaluaciones.models.LMC_Eval",
        template_name="evaluaciones/lmc_form.html",
        help_slug="lmc",
        calculator_slug="lmc",
        data_files=("lmc_tablas.json",),
    ),
    FactorDefinition(
        enum_name="EMPUJE_INICIAL",
        slug="empuje_inicial",
        choice_label="Fuerza Inicial de Empuje",
        label="Empuje — Fuerza Inicial",
        icon="bi bi-arrow-right-circle",
        route="empuje/inicial/",
        route_name="empuje_inicial_form",
        view_class="EmpujeInicialView",
        view_kind="standard",
        form_path="apps.ergonomia_886.evaluaciones.forms.EmpujeInicialForm",
        model_path="apps.ergonomia_886.evaluaciones.models.EmpujeInicial_Eval",
        template_name="evaluaciones/empuje_inicial_form.html",
        help_slug="empuje_inicial",
        calculator_slug="empuje_inicial",
        data_files=("empuje_inicial.json",),
    ),
    FactorDefinition(
        enum_name="EMPUJE_SOSTENIDA",
        slug="empuje_sostenida",
        choice_label="Fuerza Sostenida de Empuje",
        label="Empuje — Fuerza Sostenida",
        icon="bi bi-arrow-right",
        route="empuje/sostenida/",
        route_name="empuje_sostenida_form",
        view_class="EmpujeSostenidaView",
        view_kind="standard",
        form_path="apps.ergonomia_886.evaluaciones.forms.EmpujeSostenidaForm",
        model_path="apps.ergonomia_886.evaluaciones.models.EmpujeSostenida_Eval",
        template_name="evaluaciones/empuje_sostenida_form.html",
        help_slug="empuje_sostenida",
        calculator_slug="empuje_sostenida",
        data_files=("empuje_sostenida.json",),
    ),
    FactorDefinition(
        enum_name="TRACCION_INICIAL",
        slug="traccion_inicial",
        choice_label="Fuerza Inicial de Tracción",
        label="Tracción — Fuerza Inicial",
        icon="bi bi-arrow-left-circle",
        route="traccion/inicial/",
        route_name="traccion_inicial_form",
        view_class="TraccionInicialView",
        view_kind="standard",
        form_path="apps.ergonomia_886.evaluaciones.forms.TraccionInicialForm",
        model_path="apps.ergonomia_886.evaluaciones.models.TraccionInicial_Eval",
        template_name="evaluaciones/traccion_inicial_form.html",
        help_slug="traccion_inicial",
        calculator_slug="traccion_inicial",
        data_files=("traccion_inicial.json",),
    ),
    FactorDefinition(
        enum_name="TRACCION_SOSTENIDA",
        slug="traccion_sostenida",
        choice_label="Fuerza Sostenida de Tracción",
        label="Tracción — Fuerza Sostenida",
        icon="bi bi-arrow-left",
        route="traccion/sostenida/",
        route_name="traccion_sostenida_form",
        view_class="TraccionSostenidaView",
        view_kind="standard",
        form_path="apps.ergonomia_886.evaluaciones.forms.TraccionSostenidaForm",
        model_path="apps.ergonomia_886.evaluaciones.models.TraccionSostenida_Eval",
        template_name="evaluaciones/traccion_sostenida_form.html",
        help_slug="traccion_sostenida",
        calculator_slug="traccion_sostenida",
        data_files=("traccion_sostenida.json",),
    ),
    FactorDefinition(
        enum_name="TRANSPORTE",
        slug="transporte",
        choice_label="Transporte Manual de Cargas",
        label="Transporte manual",
        icon="bi bi-truck",
        route="transporte/",
        route_name="transporte_form",
        view_class="TransporteView",
        view_kind="standard",
        form_path="apps.ergonomia_886.evaluaciones.forms.TransporteForm",
        model_path="apps.ergonomia_886.evaluaciones.models.Transporte_Eval",
        template_name="evaluaciones/transporte_form.html",
        help_slug="transporte",
        calculator_slug="transporte",
        data_files=("transporte_limites.json",),
    ),
    FactorDefinition(
        enum_name="BIPEDESTACION",
        slug="bipedestacion",
        choice_label="Bipedestación",
        label="Bipedestación",
        icon="bi bi-person-walking",
        route="bipedestacion/",
        route_name="bipedestacion_form",
        view_class="BipedestacionView",
        view_kind="standard",
        form_path="apps.ergonomia_886.evaluaciones.forms.BipedestacionForm",
        model_path="apps.ergonomia_886.evaluaciones.models.Bipedestacion_Eval",
        template_name="evaluaciones/bipedestacion_form.html",
        help_slug="bipedestacion",
        calculator_slug="bipedestacion",
        data_files=("bipedestacion_limites.json",),
    ),
    FactorDefinition(
        enum_name="REPETITIVOS_MS",
        slug="repetitivos_ms",
        choice_label="Repetitivos Miembros Superiores",
        label="Movimientos repetitivos (MS)",
        icon="bi bi-repeat",
        route="repetitivos-ms/",
        route_name="repetitivos_ms_form",
        view_class="RepetitivosMSView",
        view_kind="standard",
        form_path="apps.ergonomia_886.evaluaciones.forms.RepetitivosMSForm",
        model_path="apps.ergonomia_886.evaluaciones.models.RepetitivosMS_Eval",
        template_name="evaluaciones/repetitivos_ms_form.html",
        help_slug="repetitivos_ms",
        calculator_slug="repetitivos_ms",
        data_files=("repetitivos_ms_limites.json",),
    ),
    FactorDefinition(
        enum_name="POSTURAS_FORZADAS",
        slug="posturas_forzadas",
        choice_label="Posturas Forzadas",
        label="Posturas forzadas",
        icon="bi bi-person-arms-up",
        route="posturas-forzadas/",
        route_name="posturas_forzadas_form",
        view_class="PosturasForzadasView",
        view_kind="standard",
        form_path="apps.ergonomia_886.evaluaciones.forms.PosturasForzadasForm",
        model_path="apps.ergonomia_886.evaluaciones.models.PosturasForzadas_Eval",
        template_name="evaluaciones/posturas_forzadas_form.html",
        help_slug="posturas_forzadas",
        calculator_slug="posturas_forzadas",
        data_files=("posturas_forzadas_puntajes.json",),
    ),
    FactorDefinition(
        enum_name="VIBRACION_MB",
        slug="vibracion_mano_brazo",
        choice_label="Vibración Mano-Brazo",
        label="Vibración mano-brazo",
        icon="bi bi-tsunami",
        route="vibracion/mano-brazo/",
        route_name="vibracion_mano_brazo_form",
        view_class="VibracionMBView",
        view_kind="standard",
        form_path="apps.ergonomia_886.evaluaciones.forms.VibracionMBForm",
        model_path="apps.ergonomia_886.evaluaciones.models.VibracionMB_Eval",
        template_name="evaluaciones/vibracion_mano_brazo_form.html",
        help_slug="vibracion_mano_brazo",
        calculator_slug="vibracion_mano_brazo",
        data_files=("vibracion_mano_brazo_limites.json",),
    ),
    FactorDefinition(
        enum_name="VIBRACION_CE",
        slug="vibracion_cuerpo_entero",
        choice_label="Vibración Cuerpo Entero",
        label="Vibración de cuerpo entero",
        icon="bi bi-tsunami",
        route="vibracion/cuerpo-entero/",
        route_name="vibracion_cuerpo_entero_form",
        view_class="VibracionCEView",
        view_kind="vce",
        form_path="apps.ergonomia_886.evaluaciones.forms.VibracionCEForm",
        model_path="apps.ergonomia_886.evaluaciones.models.VibracionCE_Eval",
        template_name="evaluaciones/vibracion_cuerpo_entero_form.html",
        help_slug="vibracion_cuerpo_entero",
        calculator_slug="vibracion_cuerpo_entero",
        data_files=("vibracion_cuerpo_entero_limites.json",),
    ),
    FactorDefinition(
        enum_name="CONFORT_TERMICO",
        slug="confort_termico",
        choice_label="Confort Térmico",
        label="Confort térmico",
        icon="bi bi-thermometer-half",
        route="confort-termico/",
        route_name="confort_termico_form",
        view_class="ConfortTermicoView",
        view_kind="standard",
        form_path="apps.ergonomia_886.evaluaciones.forms.ConfortTermicoForm",
        model_path="apps.ergonomia_886.evaluaciones.models.ConfortTermico_Eval",
        template_name="evaluaciones/confort_termico_form.html",
        help_slug="confort_termico",
        calculator_slug="confort_termico",
        data_files=("confort_termico_umbrales.json",),
    ),
    FactorDefinition(
        enum_name="ESTRES_CONTACTO",
        slug="estres_contacto",
        choice_label="Estrés de Contacto",
        label="Estrés de contacto",
        icon="bi bi-hand-index-thumb",
        route="estres-contacto/",
        route_name="estres_contacto_form",
        view_class="EstresContactoView",
        view_kind="standard",
        form_path="apps.ergonomia_886.evaluaciones.forms.EstresContactoForm",
        model_path="apps.ergonomia_886.evaluaciones.models.EstresContacto_Eval",
        template_name="evaluaciones/estres_contacto_form.html",
        help_slug="estres_contacto",
        calculator_slug="estres_contacto",
        data_files=("estres_contacto_criterios.json",),
    ),
)


def _build_catalog() -> Mapping[str, FactorDefinition]:
    catalog = {definition.slug: definition for definition in FACTOR_DEFINITIONS}
    if len(catalog) != len(FACTOR_DEFINITIONS):
        raise RuntimeError("El catálogo de factores contiene slugs duplicados.")
    return MappingProxyType(catalog)


FACTOR_CATALOG = _build_catalog()


def get_factor_definition(slug: str) -> FactorDefinition:
    return FACTOR_CATALOG[str(slug)]


__all__ = (
    "FACTOR_CATALOG",
    "FACTOR_DEFINITIONS",
    "FactorDefinition",
    "get_factor_definition",
)
