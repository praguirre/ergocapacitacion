"""Endpoints de exportación. Toda la autorización vive acá."""

from __future__ import annotations

import logging
import time

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.cache import cache
from django.http import Http404, HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.utils import timezone
from django.utils.text import slugify
from django.views import View
from django.views.generic import TemplateView

from apps.ergonomia_886.evaluaciones.catalog import FACTOR_CATALOG, FACTOR_DEFINITIONS
from apps.ergonomia_886.evaluaciones.models import RiskEvaluation
from apps.ergonomia_886.planillas.models import Evaluacion
from apps.ergonomia_886.planillas.querysets import obtener_evaluacion_o_404

from . import serializers
from .models import ExportAudit, TipoDocumento
from .official.builders import (
    build_planilla1_pages,
    build_planilla2_pages,
    build_planilla3_pages,
    build_planilla4_pages,
    build_protocolo_pages,
)
from .official.catalog import (
    PLANILLA_DEFINITIONS, OfficialTemplateError, get_planilla_definition,
)
from .official.overlay import stamp_official_pdf
from .reports.limits import (
    ReportLimitExceeded,
    acquire_report_lease,
    release_report_lease,
)
from .reports.llm import ReportGenerationError, get_or_create_report
from .reports.pdf import build_factor_detail_pdf, build_professional_report_pdf

logger = logging.getLogger(__name__)


class EvaluacionOwnerMixin(LoginRequiredMixin):
    """Restringe cualquier export al dueño sin revelar recursos ajenos."""

    @property
    def evaluacion(self) -> Evaluacion:
        if not hasattr(self, "_evaluacion"):
            self._evaluacion = obtener_evaluacion_o_404(
                self.kwargs["evaluacion_id"], self.request.user
            )
        return self._evaluacion


class ExportRateLimitMixin:
    """Freno simple contra la descarga masiva automatizada."""

    def check_export_rate(self, request: HttpRequest) -> None:
        ventana = getattr(settings, "EXPORT_RATE_WINDOW_SECONDS", 300)
        limite = getattr(settings, "EXPORT_RATE_LIMIT", 60)
        bucket = int(time.time() // ventana)
        clave = f"exportaciones:descargas:{request.user.pk}:{bucket}"
        if cache.add(clave, 1, timeout=ventana + 1):
            cantidad = 1
        else:
            cantidad = cache.incr(clave)
        if cantidad > limite:
            raise Http404("Demasiadas descargas en poco tiempo.")


def _respuesta_pdf(contenido: bytes, nombre: str) -> HttpResponse:
    respuesta = HttpResponse(contenido, content_type="application/pdf")
    respuesta["Content-Disposition"] = f'attachment; filename="{nombre}"'
    respuesta["X-Content-Type-Options"] = "nosniff"
    respuesta["Cache-Control"] = "private, no-store"
    return respuesta


def _nombre_archivo(evaluacion: Evaluacion, sufijo: str, extension: str) -> str:
    """Nombre estable, sin datos sensibles más allá de la razón social."""
    empresa = slugify(evaluacion.razon_social)[:40] or "evaluacion"
    fecha = timezone.localdate().strftime("%Y%m%d")
    return f"ergoapp-{empresa}-{evaluacion.pk}-{sufijo}-{fecha}.{extension}"


def _auditar(evaluacion, usuario, tipo, detalle, contenido: bytes) -> None:
    ExportAudit.objects.create(
        evaluacion=evaluacion,
        usuario=usuario,
        tipo=tipo,
        detalle=detalle[:120],
        bytes_entregados=len(contenido),
    )


class PanelExportacionView(EvaluacionOwnerMixin, TemplateView):
    template_name = "exportaciones/panel_exportacion.html"

    def get_context_data(self, **kwargs):
        contexto = super().get_context_data(**kwargs)
        evaluacion = self.evaluacion
        risk_eval = RiskEvaluation.objects.filter(evaluacion=evaluacion).first()
        requeridos = set((risk_eval.factores_requeridos or []) if risk_eval else [])

        contexto["evaluacion"] = evaluacion
        contexto["planillas"] = [
            {"slug": definition.slug, "label": definition.label}
            for definition in PLANILLA_DEFINITIONS
        ]
        contexto["factores"] = [
            {
                "slug": definition.slug,
                "label": definition.label,
                "icon": definition.icon,
                "requerido": definition.slug in requeridos,
            }
            for definition in FACTOR_DEFINITIONS
        ]
        contexto["tiene_risk_eval"] = risk_eval is not None
        return contexto


class PlanillaOficialPDFView(EvaluacionOwnerMixin, ExportRateLimitMixin, View):

    def get(self, request: HttpRequest, evaluacion_id: int, planilla_slug: str):
        self.check_export_rate(request)
        evaluacion = self.evaluacion

        try:
            get_planilla_definition(planilla_slug)
        except OfficialTemplateError:
            raise Http404("Planilla desconocida.")

        if planilla_slug == "planilla1":
            payload = serializers.build_planilla1_payload(evaluacion)
            paginas = build_planilla1_pages(payload)
        elif planilla_slug == "planilla3":
            payload = serializers.build_planilla3_payload(evaluacion)
            paginas = build_planilla3_pages(payload)
        elif planilla_slug == "planilla4":
            payload = serializers.build_planilla4_payload(evaluacion)
            paginas = build_planilla4_pages(payload)
        else:
            payloads = serializers.build_planilla2_payloads(evaluacion, planilla_slug)
            paginas = build_planilla2_pages(planilla_slug, payloads)

        try:
            contenido = stamp_official_pdf(paginas)
        except OfficialTemplateError:
            logger.exception("Plantilla oficial no disponible.")
            return JsonResponse(
                {"error": "La plantilla oficial no está disponible."}, status=503
            )

        _auditar(evaluacion, request.user, TipoDocumento.PLANILLA_OFICIAL,
                 planilla_slug, contenido)
        return _respuesta_pdf(
            contenido, _nombre_archivo(evaluacion, planilla_slug, "pdf")
        )


class ProtocoloCompletoPDFView(EvaluacionOwnerMixin, ExportRateLimitMixin, View):

    def get(self, request: HttpRequest, evaluacion_id: int):
        self.check_export_rate(request)
        evaluacion = self.evaluacion
        payload = serializers.build_evaluacion_payload(evaluacion)
        contenido = stamp_official_pdf(build_protocolo_pages(payload))
        _auditar(evaluacion, request.user, TipoDocumento.PROTOCOLO_COMPLETO,
                 "protocolo", contenido)
        return _respuesta_pdf(
            contenido, _nombre_archivo(evaluacion, "protocolo-completo", "pdf")
        )


class FactorDetallePDFView(EvaluacionOwnerMixin, ExportRateLimitMixin, View):

    def get(self, request: HttpRequest, evaluacion_id: int, factor_slug: str):
        self.check_export_rate(request)
        if factor_slug not in FACTOR_CATALOG:
            raise Http404("Factor desconocido.")

        evaluacion = self.evaluacion
        risk_eval = RiskEvaluation.objects.filter(evaluacion=evaluacion).first()
        if risk_eval is None:
            raise Http404("La evaluación no tiene factores cuantitativos.")

        payload = serializers.build_factor_payload(risk_eval, factor_slug)
        contenido = build_factor_detail_pdf(
            cabecera=serializers.build_cabecera(evaluacion),
            factores=[payload],
            generado_en=timezone.localtime(),
            titulo=f"Detalle técnico — {payload['factor_label']}",
        )
        _auditar(evaluacion, request.user, TipoDocumento.DETALLE_FACTOR,
                 factor_slug, contenido)
        return _respuesta_pdf(
            contenido, _nombre_archivo(evaluacion, f"detalle-{factor_slug}", "pdf")
        )


class FactoresDetalleTodosPDFView(EvaluacionOwnerMixin, ExportRateLimitMixin, View):

    def get(self, request: HttpRequest, evaluacion_id: int):
        self.check_export_rate(request)
        evaluacion = self.evaluacion
        risk_eval = RiskEvaluation.objects.filter(evaluacion=evaluacion).first()
        if risk_eval is None:
            raise Http404("La evaluación no tiene factores cuantitativos.")

        payloads = [
            serializers.build_factor_payload(risk_eval, d.slug)
            for d in FACTOR_DEFINITIONS
        ]
        contenido = build_factor_detail_pdf(
            cabecera=serializers.build_cabecera(evaluacion),
            factores=[p for p in payloads if p.get("existe")] or payloads,
            generado_en=timezone.localtime(),
            titulo="Detalle técnico de los factores evaluados",
        )
        _auditar(evaluacion, request.user, TipoDocumento.DETALLE_FACTOR,
                 "todos", contenido)
        return _respuesta_pdf(
            contenido, _nombre_archivo(evaluacion, "detalle-factores", "pdf")
        )


class InformeFactorView(EvaluacionOwnerMixin, View):
    """POST genera (o reutiliza) el informe y devuelve el PDF.

    Es POST y no GET porque puede tener efectos: crea un `GeneratedReport` y
    consume cuota del proveedor del modelo. Django exige CSRF en POST.
    """

    def post(self, request: HttpRequest, evaluacion_id: int, factor_slug: str):
        if factor_slug not in FACTOR_CATALOG:
            raise Http404("Factor desconocido.")

        evaluacion = self.evaluacion
        risk_eval = RiskEvaluation.objects.filter(evaluacion=evaluacion).first()
        if risk_eval is None:
            raise Http404("La evaluación no tiene factores cuantitativos.")

        payload = serializers.build_factor_payload(risk_eval, factor_slug)

        if not payload.get("existe"):
            messages.error(
                request,
                "No hay datos cargados para este factor. Completalo antes de "
                "generar el informe.",
            )
            return redirect("exportaciones:panel", evaluacion_id=evaluacion.pk)

        if payload["estado_operativo"] in {"borrador", "desactualizado"}:
            messages.warning(
                request,
                "El resultado de este factor está en borrador o desactualizado. "
                "Recalculá el factor antes de generar o presentar el informe.",
            )
            return redirect("exportaciones:panel", evaluacion_id=evaluacion.pk)

        payload["contexto"] = {
            "razon_social": evaluacion.razon_social,
            "area_sector": payload.get("area_sector", ""),
            "puesto_trabajo": payload.get("puesto_trabajo", ""),
            "provincia": evaluacion.provincia,
        }

        try:
            lease = acquire_report_lease(request.user.pk)
        except ReportLimitExceeded as exc:
            respuesta = JsonResponse({"error": str(exc)}, status=429)
            respuesta["Retry-After"] = str(exc.retry_after)
            return respuesta

        try:
            informe = get_or_create_report(
                evaluacion=evaluacion,
                payload=payload,
                factor_slug=factor_slug,
                usuario=request.user,
            )
        except ReportGenerationError as exc:
            messages.error(request, str(exc))
            return redirect("exportaciones:panel", evaluacion_id=evaluacion.pk)
        finally:
            release_report_lease(lease)

        contenido = build_professional_report_pdf(
            cabecera=serializers.build_cabecera(evaluacion),
            payload=payload,
            markdown_llm=informe.contenido_markdown,
            metadatos={
                "modelo_llm": informe.modelo_llm,
                "prompt_version": informe.prompt_version,
                "inputs_hash": informe.inputs_hash,
                "duracion_ms": informe.duracion_ms,
            },
            generado_en=timezone.localtime(informe.creado_en),
        )
        _auditar(evaluacion, request.user, TipoDocumento.INFORME_FACTOR,
                 factor_slug, contenido)
        return _respuesta_pdf(
            contenido, _nombre_archivo(evaluacion, f"informe-{factor_slug}", "pdf")
        )


class PaqueteZipView(EvaluacionOwnerMixin, ExportRateLimitMixin, View):

    def get(self, request: HttpRequest, evaluacion_id: int):
        from .packaging import build_evaluation_package

        self.check_export_rate(request)
        evaluacion = self.evaluacion
        contenido = build_evaluation_package(evaluacion)
        _auditar(evaluacion, request.user, TipoDocumento.PAQUETE_ZIP,
                 "paquete", contenido)

        respuesta = HttpResponse(contenido, content_type="application/zip")
        respuesta["Content-Disposition"] = (
            f'attachment; filename="{_nombre_archivo(evaluacion, "paquete", "zip")}"'
        )
        respuesta["X-Content-Type-Options"] = "nosniff"
        respuesta["Cache-Control"] = "private, no-store"
        return respuesta
