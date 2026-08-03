"""Ensamblado de los datos de una evaluación en dicts JSON-serializables.

Regla dura: este módulo SÓLO LEE. No escribe en la base, no dibuja y no
llama al LLM. Su salida es la única entrada de los builders y del informe.
"""

from __future__ import annotations

from typing import Any, Dict, List

from django.utils.module_loading import import_string

from apps.ergonomia_886.evaluaciones.catalog import FACTOR_DEFINITIONS, get_factor_definition
from apps.ergonomia_886.evaluaciones.models import RiskEvaluation
from apps.ergonomia_886.planillas.models import (
    Evaluacion, FactorRiesgo, MedidaEspecifica, Planilla1, Planilla3,
    SeguimientoMedida,
)

from . import vocabulario as voc

# ⚠️ CF-4: no agregar la relación Planilla1.trabajadores a ningún payload que
# vaya hacia el modelo de lenguaje. Los documentos del profesional imprimen
# `nombres_trabajadores`, que es texto que él mismo escribió; la relación
# expone CUIL, DNI y email de personas identificables.

PLANILLA2_MODELOS = {
    "planilla2a": "apps.ergonomia_886.planillas.models.Planilla2A",
    "planilla2b": "apps.ergonomia_886.planillas.models.Planilla2B",
    "planilla2c": "apps.ergonomia_886.planillas.models.Planilla2C",
    "planilla2d": "apps.ergonomia_886.planillas.models.Planilla2D",
    "planilla2e": "apps.ergonomia_886.planillas.models.Planilla2E",
    "planilla2f": "apps.ergonomia_886.planillas.models.Planilla2F",
    "planilla2g": "apps.ergonomia_886.planillas.models.Planilla2G",
    "planilla2h": "apps.ergonomia_886.planillas.models.Planilla2H",
    "planilla2i": "apps.ergonomia_886.planillas.models.Planilla2I",
}


def build_cabecera(evaluacion: Evaluacion) -> Dict[str, Any]:
    """Datos que se repiten en el encabezado de varias planillas."""
    planilla1 = Planilla1.objects.filter(evaluacion=evaluacion).first()
    empresa = evaluacion.empresa
    contacto_nombre = getattr(empresa, "contacto_nombre", "") or ""
    contacto_cargo = getattr(empresa, "contacto_cargo", "") or ""
    firma_empleador = (
        f"{contacto_nombre}\n{contacto_cargo}"
        if contacto_nombre and contacto_cargo
        else ""
    )

    profesional = evaluacion.usuario
    nombre_profesional = getattr(profesional, "display_name", "") or ""
    profesion = getattr(profesional, "profession", "") or ""
    matricula = getattr(profesional, "license_number", "") or ""
    firma_higiene = (
        f"{nombre_profesional}\n{profesion} - Matrícula {matricula}"
        if nombre_profesional and profesion and matricula
        else ""
    )
    return {
        "evaluacion_id": evaluacion.pk,
        "razon_social": evaluacion.razon_social or "",
        "cuit": evaluacion.cuit or "",
        "ciiu": evaluacion.ciiu or "",
        "direccion": evaluacion.direccion_establecimiento or "",
        "provincia": evaluacion.provincia or "",
        "fecha_creacion": voc.fecha_es(evaluacion.fecha_creacion),
        "area_sector": getattr(planilla1, "area_sector", "") or "",
        "puesto_trabajo": getattr(planilla1, "puesto_trabajo", "") or "",
        "nombres_trabajadores": getattr(planilla1, "nombres_trabajadores", "") or "",
        "aclaraciones_firma": {
            "empleador": firma_empleador,
            "higiene_seguridad": firma_higiene,
            # CF-5: el sistema no registra al responsable de Medicina Laboral.
            "medicina_trabajo": "",
        },
    }


ORDEN_FACTORES = ["A", "B", "C", "D", "E", "F", "G", "H", "I"]


def build_planilla1_payload(evaluacion: Evaluacion) -> Dict[str, Any]:
    planilla1 = Planilla1.objects.filter(evaluacion=evaluacion).first()
    cabecera = build_cabecera(evaluacion)

    if planilla1 is None:
        return {**cabecera, "existe": False, "factores": []}

    factores_por_tipo = {
        f.tipo_factor: f
        for f in FactorRiesgo.objects.filter(planilla1=planilla1)
    }

    factores: List[Dict[str, Any]] = []
    for tipo in ORDEN_FACTORES:
        factor = factores_por_tipo.get(tipo)
        if factor is None:
            factores.append({"tipo": tipo, "presente": False, "tiempo_exposicion": "",
                             "tarea1": False, "tarea2": False, "tarea3": False,
                             "nivel1": "", "nivel2": "", "nivel3": ""})
            continue
        factores.append({
            "tipo": tipo,
            "etiqueta": factor.get_tipo_factor_display(),
            "presente": bool(factor.presente),
            "tiempo_exposicion": factor.tiempo_exposicion or "",
            "tarea1": factor.riesgo_tarea1 is not None,
            "tarea2": factor.riesgo_tarea2 is not None,
            "tarea3": factor.riesgo_tarea3 is not None,
            "nivel1": "" if factor.riesgo_tarea1 is None else str(factor.riesgo_tarea1),
            "nivel2": "" if factor.riesgo_tarea2 is None else str(factor.riesgo_tarea2),
            "nivel3": "" if factor.riesgo_tarea3 is None else str(factor.riesgo_tarea3),
        })

    return {
        **cabecera,
        "existe": True,
        "nro_trabajadores": str(planilla1.nro_trabajadores or ""),
        "procedimiento_escrito": voc.si_no(planilla1.procedimiento_escrito),
        "capacitacion": voc.si_no(planilla1.capacitacion),
        "manifestacion_temprana": voc.si_no(planilla1.manifestacion_temprana),
        "ubicacion_sintoma": planilla1.ubicacion_sintoma or "",
        "tarea_1": planilla1.tarea_1 or "",
        "tarea_2": planilla1.tarea_2 or "",
        "tarea_3": planilla1.tarea_3 or "",
        "factores": factores,
    }


def build_planilla2_payloads(
    evaluacion: Evaluacion, planilla_slug: str
) -> List[Dict[str, Any]]:
    """Devuelve una lista: una entrada por instancia (hueco G-4)."""
    modelo = import_string(PLANILLA2_MODELOS[planilla_slug])
    cabecera = build_cabecera(evaluacion)
    instancias = list(modelo.objects.filter(evaluacion=evaluacion).order_by("pk"))

    if not instancias:
        return [{**cabecera, "existe": False, "tarea_nro": "", "respuestas": {}}]

    payloads: List[Dict[str, Any]] = []
    for instancia in instancias:
        respuestas = {
            campo.name: voc.marca_si_no(getattr(instancia, campo.name), respondido=True)
            for campo in modelo._meta.get_fields()
            if getattr(campo, "attname", "").startswith(("p1_", "p2_"))
        }
        payloads.append({
            **cabecera,
            "existe": True,
            "instancia_id": instancia.pk,
            "tarea_nro": instancia.tarea_nro or "",
            "respuestas": respuestas,
        })
    return payloads


def build_planilla3_payload(evaluacion: Evaluacion) -> Dict[str, Any]:
    planilla3 = Planilla3.objects.filter(evaluacion=evaluacion).first()
    cabecera = build_cabecera(evaluacion)
    if planilla3 is None:
        return {**cabecera, "existe": False, "generales": [], "especificas": []}
    generales = [
        {"campo": "general_informado_riesgo", "marca": voc.marca_si_no(planilla3.general_informado_riesgo, respondido=True), "fecha": voc.fecha_es(planilla3.fecha_informado_riesgo)},
        {"campo": "general_capacitado_sintomas", "marca": voc.marca_si_no(planilla3.general_capacitado_sintomas, respondido=True), "fecha": voc.fecha_es(planilla3.fecha_capacitado_sintomas)},
        {"campo": "general_capacitado_medidas", "marca": voc.marca_si_no(planilla3.general_capacitado_medidas, respondido=True), "fecha": voc.fecha_es(planilla3.fecha_capacitado_medidas)},
    ]
    especificas = [
        {"numero": indice, "descripcion": medida.descripcion or "",
         "observaciones": medida.observaciones or "", "medida_id": medida.pk}
        for indice, medida in enumerate(
            MedidaEspecifica.objects.filter(planilla3=planilla3).order_by("pk"), start=1
        )
    ]
    return {**cabecera, "existe": True,
            "tarea_analizada": planilla3.tarea_analizada or "",
            "observaciones_generales": planilla3.observaciones_generales or "",
            "generales": generales, "especificas": especificas}


def build_planilla4_payload(evaluacion: Evaluacion) -> Dict[str, Any]:
    planilla3 = Planilla3.objects.filter(evaluacion=evaluacion).first()
    cabecera = build_cabecera(evaluacion)
    if planilla3 is None:
        return {**cabecera, "existe": False, "filas": []}
    medidas = list(MedidaEspecifica.objects.filter(planilla3=planilla3).order_by("pk"))
    seguimientos = {
        s.medida_especifica_id: s
        for s in SeguimientoMedida.objects.filter(medida_especifica__in=medidas)
    }
    filas: List[Dict[str, Any]] = []
    for indice, medida in enumerate(medidas, start=1):
        seguimiento = seguimientos.get(medida.pk)
        filas.append({
            "numero": str(indice),
            "nombre_puesto": getattr(seguimiento, "nombre_puesto", "") or "",
            "fecha_evaluacion": voc.fecha_es(getattr(seguimiento, "fecha_evaluacion", None)),
            "nivel_riesgo": "" if seguimiento is None or seguimiento.nivel_riesgo is None else str(seguimiento.nivel_riesgo),
            "fecha_impl_admin": voc.fecha_es(getattr(seguimiento, "fecha_impl_admin", None)),
            "fecha_impl_ing": voc.fecha_es(getattr(seguimiento, "fecha_impl_ing", None)),
            "fecha_cierre": voc.fecha_es(getattr(seguimiento, "fecha_cierre", None)),
            "descripcion_medida": medida.descripcion or "",
        })
    return {**cabecera, "existe": True, "filas": filas}


CAMPOS_COMUNES_FACTOR = {
    "factor_slug", "nivel_riesgo", "aplicable", "observaciones",
    "calc_data", "creado_en", "actualizado_en", "id", "risk_evaluation",
}


def _valor_legible(instancia, campo) -> Any:
    """Valor de un campo con su etiqueta de choices cuando corresponde."""
    valor = getattr(instancia, campo.name, None)
    display = getattr(instancia, f"get_{campo.name}_display", None)
    if callable(display) and valor not in (None, ""):
        return display()
    if hasattr(valor, "isoformat"):
        return valor.isoformat()
    if valor.__class__.__name__ == "Decimal":
        return float(valor)
    if hasattr(valor, "name") or hasattr(valor, "url"):
        return getattr(valor, "name", "") or ""
    return valor


def build_factor_payload(
    risk_eval: RiskEvaluation, factor_slug: str
) -> Dict[str, Any]:
    """Payload canónico de un factor: inputs declarados + calc_data íntegro."""
    definition = get_factor_definition(factor_slug)
    modelo = import_string(definition.model_path)
    instancia = modelo.objects.filter(risk_evaluation=risk_eval).first()

    if instancia is None:
        return {
            "schema_version": "1.0.0",
            "factor_slug": factor_slug,
            "factor_label": definition.label,
            "existe": False,
            "estado_operativo": "sin_iniciar",
            "inputs": {},
            "calc_data": {},
        }

    inputs = {
        campo.name: _valor_legible(instancia, campo)
        for campo in modelo._meta.concrete_fields
        if campo.name not in CAMPOS_COMUNES_FACTOR
    }

    calc_data = dict(instancia.calc_data or {})
    estado = calc_data.get("estado_resultado") or "borrador"
    revision = calc_data.get("revision_profesional") or {}

    payload: Dict[str, Any] = {
        "schema_version": "1.0.0",
        "factor_slug": factor_slug,
        "factor_label": definition.label,
        "existe": True,
        "aplicable": bool(instancia.aplicable),
        "nivel_riesgo": instancia.nivel_riesgo,
        "nivel_riesgo_display": instancia.get_nivel_riesgo_display(),
        "nivel_numerico_srt": voc.nivel_a_numero(instancia.nivel_riesgo),
        "observaciones_profesional": instancia.observaciones or "",
        "estado_resultado": estado,
        "estado_operativo": _estado_operativo(instancia, calc_data),
        "calculado_en": calc_data.get("calculado_en", ""),
        "revisado_en": calc_data.get("revisado_en", ""),
        "revisado_por": (calc_data.get("revisado_por") or {}).get("username", ""),
        "requiere_revision_profesional": bool(
            calc_data.get("requiere_revision_profesional")
        ),
        "revision_profesional": revision,
        "agravantes_presentes": calc_data.get("agravantes_presentes", []),
        "inputs": inputs,
        "calc_data": calc_data,
        "fuentes": (calc_data.get("calculation_trace") or {}).get("sources", []),
        "actualizado_en": instancia.actualizado_en.isoformat(),
    }

    if factor_slug == "vibracion_cuerpo_entero":
        payload["segmentos"] = [
            {
                "vehiculo_maquina": s.vehiculo_maquina,
                "tipo_asiento": s.get_tipo_asiento_display(),
                "superficie_terreno": s.get_superficie_terreno_display(),
                "velocidad_promedio": voc.numero_es(s.velocidad_promedio, 1),
                "estado_neumaticos": s.get_estado_neumaticos_display(),
                "tiempo_horas": voc.numero_es(s.tiempo_horas, 2),
                "aw_x": voc.numero_es(s.aw_x, 3),
                "aw_y": voc.numero_es(s.aw_y, 3),
                "aw_z": voc.numero_es(s.aw_z, 3),
                "cf_x": voc.numero_es(s.cf_x, 2),
                "cf_y": voc.numero_es(s.cf_y, 2),
                "cf_z": voc.numero_es(s.cf_z, 2),
                "pico_espectral_hz": s.pico_espectral_hz,
            }
            for s in instancia.segmentos.all().order_by("id")
        ]
        payload["evidencia_declarada"] = {
            "foto_montaje": getattr(instancia.foto_montaje, "name", "") or "",
            "certificado_calibracion": getattr(
                instancia.certificado_calibracion, "name", ""
            ) or "",
            "adjunta": False,
            "motivo": "MEDIA_ROOT no está configurado en el proyecto.",
        }

    return payload


def _estado_operativo(instancia, calc_data: Dict[str, Any]) -> str:
    """Réplica probada de `evaluaciones.views._factor_operational_state`."""
    estado = calc_data.get("estado_resultado")
    if estado == "desactualizado":
        return "desactualizado"
    if estado != "calculado":
        return "borrador"
    if calc_data.get("revisado_en") and calc_data.get("revisado_por"):
        return "revisado"
    if not getattr(instancia, "aplicable", True) or instancia.nivel_riesgo == "no_aplicable":
        return "no_aplicable"
    return "calculado"


def build_evaluacion_payload(evaluacion: Evaluacion) -> Dict[str, Any]:
    """Payload consolidado de toda la evaluación."""
    risk_eval = RiskEvaluation.objects.filter(evaluacion=evaluacion).first()
    requeridos = set((risk_eval.factores_requeridos or []) if risk_eval else [])

    factores = []
    if risk_eval is not None:
        for definition in FACTOR_DEFINITIONS:
            payload = build_factor_payload(risk_eval, definition.slug)
            payload["requerido"] = definition.slug in requeridos
            factores.append(payload)

    return {
        "schema_version": "1.0.0",
        "cabecera": build_cabecera(evaluacion),
        "planilla1": build_planilla1_payload(evaluacion),
        "planillas2": {
            slug: build_planilla2_payloads(evaluacion, slug)
            for slug in PLANILLA2_MODELOS
        },
        "planilla3": build_planilla3_payload(evaluacion),
        "planilla4": build_planilla4_payload(evaluacion),
        "risk_evaluation": (
            {
                "estado": risk_eval.estado,
                "estado_display": risk_eval.get_estado_display(),
                "resultado_global": risk_eval.resultado_global,
                "resumen_json": risk_eval.resumen_json or {},
                "factores_requeridos": sorted(requeridos),
            }
            if risk_eval is not None
            else None
        ),
        "factores": factores,
    }
