# evaluaciones/views.py
from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional, Type

from django.views import View
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404, HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.utils.functional import cached_property
from django.utils.module_loading import import_string
from django.views.generic import FormView, TemplateView
from django.db import transaction
from planillas.models import Evaluacion  # <- app planillas

from .catalog import FACTOR_CATALOG, FACTOR_DEFINITIONS
from .models import RiskEvaluation
from .pdf import build_wizard_summary_pdf
from .choices import FactorSlug, NivelRiesgo
from .forms import RiskEvaluationQuickForm, VCESegmentFormSet

logger = logging.getLogger(__name__)

# ------------------------------------------------------------------------------
# Utilidades
# ------------------------------------------------------------------------------

def _wizard_url(evaluacion_id: int) -> str:
    """URL al resumen tipo wizard para una RiskEvaluation existente."""
    return reverse("evaluaciones:wizard_resumen_by_eval", args=[evaluacion_id])


def _get_riskeval_or_404_for_user(evaluacion_id: int, user) -> RiskEvaluation:
    """
    Restringe por propiedad del usuario a través de la Evaluacion (planillas)
    y devuelve la RiskEvaluation correspondiente.
    """
    # RiskEvaluation.evaluacion -> planillas.Evaluacion (OneToOne)
    # Filtramos por el dueño de la Evaluacion (usuario autenticado)
    # Campos de RiskEvaluation usados: estado, factores_requeridos, resultado_global, resumen_json.
    # Ver definiciones en models.py (evaluaciones_app.md).
    return get_object_or_404(
        RiskEvaluation.objects.select_related("evaluacion"),
        pk=evaluacion_id,
        evaluacion__usuario=user,  # exige que la Evaluacion (planillas) sea del usuario logueado
    )


def _factor_operational_state(instance) -> str:
    if instance is None:
        return "sin_iniciar"

    calc_data = getattr(instance, "calc_data", {}) or {}
    result_state = calc_data.get("estado_resultado")
    if result_state == "desactualizado":
        return "desactualizado"
    if result_state == "borrador" or not result_state:
        return "borrador"
    if result_state != "calculado":
        return "borrador"
    if calc_data.get("revisado_en") and calc_data.get("revisado_por"):
        return "revisado"
    if (
        not getattr(instance, "aplicable", True)
        or getattr(instance, "nivel_riesgo", None) == NivelRiesgo.NA
    ):
        return "no_aplicable"
    return "calculado"


def _build_wizard_items(risk_eval: RiskEvaluation) -> List[Dict[str, Any]]:
    """
    Construye la lista que consume wizard_resumen.html:
    - label, icon, nivel, aplicable, edit_url, completed, slug
    Sólo marca como 'requeridos' los slugs declarados en risk_eval.factores_requeridos.
    """
    items: List[Dict[str, Any]] = []
    requeridos = set(risk_eval.factores_requeridos or [])

    for definition in FACTOR_DEFINITIONS:
        slug = definition.slug
        model_cls = import_string(definition.model_path)
        instance = model_cls.objects.filter(risk_evaluation=risk_eval).first()
        nivel = getattr(instance, "nivel_riesgo", None)
        aplicable = getattr(instance, "aplicable", None)
        result_state = (
            (getattr(instance, "calc_data", {}) or {}).get("estado_resultado")
            if instance is not None
            else None
        )
        operational_state = _factor_operational_state(instance)
        completed = operational_state in {
            "calculado",
            "no_aplicable",
            "revisado",
        }
        calc_data = getattr(instance, "calc_data", {}) or {}
        professional_review = calc_data.get("revision_profesional") or {}

        items.append(
            {
                "slug": slug,
                "label": definition.label,
                "icon": definition.icon,
                "required": slug in requeridos,
                "instance": instance,
                "nivel": nivel,
                "aplicable": aplicable,
                "result_state": result_state,
                "operational_state": operational_state,
                "reviewed_at": calc_data.get("revisado_en"),
                "reviewed_by": calc_data.get("revisado_por"),
                "requires_professional_review": bool(
                    calc_data.get("requiere_revision_profesional")
                ),
                "calculated_level": calc_data.get("clasificacion_base_nivel"),
                "professional_review": professional_review,
                "aggravants_present": calc_data.get("agravantes_presentes", []),
                "edit_url": reverse(
                    f"evaluaciones:{definition.route_name_by_eval}",
                    args=[risk_eval.pk],
                ),
                "completed": completed,
            }
        )
    return items


def _aggregate_wizard(items: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Aplica una regla global explícita sólo sobre factores requeridos."""
    required = [item for item in items if item["required"]]
    blocking_states = {"sin_iniciar", "borrador", "desactualizado"}
    blockers = [
        item for item in required if item["operational_state"] in blocking_states
    ]
    pending_review = [
        item
        for item in required
        if item["operational_state"] in {"calculado", "no_aplicable"}
    ]
    reviewed = [
        item for item in required if item["operational_state"] == "revisado"
    ]

    severity = {
        NivelRiesgo.BAJO: 1,
        NivelRiesgo.MEDIO: 2,
        NivelRiesgo.ALTO: 3,
    }
    valid_levels = [
        item["nivel"]
        for item in required
        if item["operational_state"]
        in {"calculado", "no_aplicable", "revisado"}
        and item["nivel"] in severity
    ]
    preliminary = (
        max(valid_levels, key=severity.get)
        if valid_levels
        else (NivelRiesgo.NA if required and not blockers else None)
    )
    all_reviewed = bool(required) and not blockers and not pending_review

    return {
        "schema_version": "1.0.0",
        "regla_global": (
            "El resultado final es el mayor nivel entre los factores requeridos "
            "vigentes. Borradores, resultados desactualizados o sin iniciar "
            "bloquean el cierre; todo resultado debe quedar revisado."
        ),
        "required_count": len(required),
        "completed_count": len(required) - len(blockers),
        "reviewed_count": len(reviewed),
        "blocking_slugs": [item["slug"] for item in blockers],
        "blocking_labels": [item["label"] for item in blockers],
        "pending_review_slugs": [item["slug"] for item in pending_review],
        "pending_review_labels": [item["label"] for item in pending_review],
        "resultado_preliminar": preliminary,
        "resultado_final": preliminary if all_reviewed else None,
        "ready_for_review": bool(required) and not blockers,
        "all_reviewed": all_reviewed,
    }


def _sync_wizard_summary(
    risk_eval: RiskEvaluation,
    items: Optional[List[Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    items = items if items is not None else _build_wizard_items(risk_eval)
    summary = _aggregate_wizard(items)

    if not summary["required_count"]:
        state = "pending"
    elif summary["all_reviewed"]:
        state = "done"
    else:
        state = "in_progress"

    current_summary = dict(risk_eval.resumen_json or {})
    current_summary.pop("actualizado_en", None)
    if (
        current_summary != summary
        or risk_eval.estado != state
        or risk_eval.resultado_global != summary["resultado_final"]
    ):
        risk_eval.estado = state
        risk_eval.resultado_global = summary["resultado_final"]
        risk_eval.resumen_json = {
            **summary,
            "actualizado_en": timezone.now().isoformat(),
        }
        risk_eval.save(
            update_fields=[
                "estado",
                "resultado_global",
                "resumen_json",
                "actualizado_en",
            ]
        )
    return summary


# ------------------------------------------------------------------------------
# Resumen / Wizard
# ------------------------------------------------------------------------------

class WizardResumenView(LoginRequiredMixin, TemplateView):
    """
    Muestra el resumen con tarjetas por factor, links de edición y estado global.
    El template espera 'evaluacion' (RiskEvaluation) y 'factores' (lista).
    """
    template_name = "evaluaciones/wizard_resumen.html"

    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        if "evaluacion_id" not in kwargs:
            # Sin ID no podemos asociar a una Evaluacion (planillas). Redirigimos
            # a donde tenga sentido en tu navegación (dashboard o similar).
            # Si prefieres, aquí podrías crear/seleccionar una Evaluacion.
            raise Http404("Falta evaluacion_id en la URL")
        return super().get(request, *args, **kwargs)

    def post(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        if "evaluacion_id" not in kwargs:
            raise Http404("Falta evaluacion_id en la URL")
        action = request.POST.get("action")
        if action == "review_factor":
            slug = request.POST.get("factor_slug", "")
            definition = FACTOR_CATALOG.get(slug)
            if definition is None:
                return HttpResponse("Factor desconocido.", status=400)
            if slug not in set(self.risk_eval.factores_requeridos or []):
                return HttpResponse(
                    "El factor no está marcado como requerido.",
                    status=409,
                )
            model_cls = import_string(definition.model_path)
            instance = get_object_or_404(
                model_cls,
                risk_evaluation=self.risk_eval,
            )
            calc_data = dict(instance.calc_data or {})
            if calc_data.get("estado_resultado") != "calculado":
                return HttpResponse(
                    "Sólo puede revisarse un resultado calculado y vigente.",
                    status=409,
                )
            requires_professional_review = bool(
                calc_data.get("requiere_revision_profesional")
            )
            manual_level = request.POST.get("manual_level", "").strip()
            justification = request.POST.get("review_justification", "").strip()
            update_fields = ["calc_data", "actualizado_en"]

            if requires_professional_review:
                allowed_levels = {
                    NivelRiesgo.BAJO,
                    NivelRiesgo.MEDIO,
                    NivelRiesgo.ALTO,
                }
                if manual_level not in allowed_levels:
                    return HttpResponse(
                        "Seleccioná una clasificación profesional final válida.",
                        status=400,
                    )
                calculated_level = (
                    calc_data.get("clasificacion_base_nivel")
                    or instance.nivel_riesgo
                )
                if manual_level != calculated_level and not justification:
                    return HttpResponse(
                        "Justificá el cambio respecto de la clasificación de tabla.",
                        status=400,
                    )
                if len(justification) > 2000:
                    return HttpResponse(
                        "La justificación no puede superar 2000 caracteres.",
                        status=400,
                    )
                calc_data["revision_profesional"] = {
                    "clasificacion_tabla": calculated_level,
                    "clasificacion_final": manual_level,
                    "modificada": manual_level != calculated_level,
                    "justificacion": justification,
                    "agravantes_considerados": calc_data.get(
                        "agravantes_presentes", []
                    ),
                }
                instance.nivel_riesgo = manual_level
                update_fields.append("nivel_riesgo")
            elif manual_level:
                return HttpResponse(
                    "Este factor no admite una clasificación manual en esta revisión.",
                    status=400,
                )
            calc_data["revisado_en"] = timezone.now().isoformat()
            calc_data["revisado_por"] = {
                "id": request.user.pk,
                "username": request.user.get_username(),
            }
            instance.calc_data = calc_data
            instance.save(update_fields=update_fields)
            items = _build_wizard_items(self.risk_eval)
            _sync_wizard_summary(self.risk_eval, items)
            messages.success(request, f"Se revisó el factor {definition.label}.")
            return redirect(_wizard_url(self.risk_eval.pk))

        if action != "generate_pdf":
            return HttpResponse("Acción no reconocida.", status=400)

        factors = _build_wizard_items(self.risk_eval)
        _sync_wizard_summary(self.risk_eval, factors)
        pdf = build_wizard_summary_pdf(
            risk_eval=self.risk_eval,
            factors=factors,
            generated_at=timezone.localtime(),
        )
        response = HttpResponse(pdf, content_type="application/pdf")
        response["Content-Disposition"] = (
            f'attachment; filename="evaluacion-{self.risk_eval.pk}-resumen.pdf"'
        )
        response["X-Content-Type-Options"] = "nosniff"
        return response

    @cached_property
    def risk_eval(self) -> RiskEvaluation:
        return _get_riskeval_or_404_for_user(self.kwargs["evaluacion_id"], self.request.user)

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        ctx = super().get_context_data(**kwargs)
        ctx["evaluacion"] = self.risk_eval
        ctx["factores"] = _build_wizard_items(self.risk_eval)
        ctx["resumen_global"] = _sync_wizard_summary(
            self.risk_eval,
            ctx["factores"],
        )
        # Enlaces útiles
        ctx["wizard_resumen_url"] = _wizard_url(self.risk_eval.pk)
        return ctx


# ------------------------------------------------------------------------------
# Factor base (FormView)
# ------------------------------------------------------------------------------

class FactorFormView(LoginRequiredMixin, FormView):
    """
    Base para todos los factores.
    - Usa el ModelForm concreto (form_class) y su Meta.model para obtener/crear la instancia.
    - Integra los dos botones del template base:
        * name="action" value="save"            -> sólo guarda
        * name="action" value="save_and_calc"   -> guarda y calcula
      (ver factor_form_base.html)
    - Redirige a 'next' si vino, o al wizard resumen por defecto.
    """
    factor_slug: str = ""            # ej. FactorSlug.LMC
    form_class: Type = None          # asignado en subclase
    template_name: str = ""          # asignado en subclase
    url_name: str = ""               # ej. "lmc_form_by_eval"

    def dispatch(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        if "evaluacion_id" not in kwargs:
            raise Http404("Falta evaluacion_id en la URL")
        # Carga y control de propiedad
        self._risk_eval = _get_riskeval_or_404_for_user(kwargs["evaluacion_id"], request.user)
        logger.info(
            "FactorFormView dispatch factor=%s evaluacion_id=%s user=%s",
            self.factor_slug,
            self._risk_eval.pk,
            request.user,
        )
        return super().dispatch(request, *args, **kwargs)

    @property
    def risk_eval(self) -> RiskEvaluation:
        return self._risk_eval

    @cached_property
    def model_cls(self):
        return self.form_class._meta.model

    @cached_property
    def instance(self):
        obj, created = self.model_cls.objects.get_or_create(
            risk_evaluation=self.risk_eval,
            defaults={"factor_slug": self.factor_slug} if self.factor_slug else {},
        )
        logger.debug(
            "FactorFormView instance factor=%s risk_eval=%s created=%s instance_pk=%s",
            self.factor_slug,
            self.risk_eval.pk,
            created,
            obj.pk,
        )
        return obj

    # ----- Form hooks ---------------------------------------------------------

    def get_form_kwargs(self) -> Dict[str, Any]:
        """
        Inyecta siempre la instancia y, si hace falta, el FK risk_evaluation
        tanto en GET (initial) como en POST (data), para forms que lo declaran.
        """
        kwargs = super().get_form_kwargs()
        kwargs["instance"] = self.instance

        # Si es POST/PUT y el form tiene el campo risk_evaluation pero no vino en la data,
        # lo agregamos nosotros para evitar el "This field is required".
        if self.request.method in ("POST", "PUT"):
            data = kwargs.get("data")
            base_fields = getattr(self.form_class, "base_fields", {})
            if data is not None and "risk_evaluation" in base_fields and "risk_evaluation" not in data:
                data = data.copy()
                data["risk_evaluation"] = str(self.risk_eval.pk)
                kwargs["data"] = data
                logger.debug(
                    "Inyectado risk_evaluation=%s en POST para factor=%s",
                    self.risk_eval.pk,
                    self.factor_slug,
                )

        # Para GET, seteamos initial si el form tiene el campo
        if self.request.method == "GET":
            base_fields = getattr(self.form_class, "base_fields", {})
            initial = kwargs.get("initial", {}) or {}
            if "risk_evaluation" in base_fields:
                initial.setdefault("risk_evaluation", self.risk_eval.pk)
            kwargs["initial"] = initial

        return kwargs

    def form_valid(self, form):
        action = self.request.POST.get("action")  # "save" o "save_and_calc"
        logger.info(
            "FactorFormView form_valid factor=%s action=%s user=%s risk_eval=%s",
            self.factor_slug,
            action,
            self.request.user,
            self.risk_eval.pk,
        )

        # Set FK explícitamente por robustez
        obj = form.save(commit=False)
        obj.risk_evaluation = self.risk_eval
        obj.factor_slug = obj.factor_slug or self.factor_slug
        obj.save()

        # Mezcla inputs/calc_data que hace tu BaseFactorForm al salvar:
        # Si el botón fue "guardar y calcular", usar el helper del form.
        if action == "save_and_calc" and hasattr(form, "save_and_calculate"):
            logger.info(
                "Ejecutando save_and_calculate para factor=%s instancia=%s",
                self.factor_slug,
                obj.pk,
            )
            form.instance = obj  # asegurar instancia
            obj = form.save_and_calculate()  # integra calculators

            messages.success(self.request, "Guardado y calculado correctamente.")
        else:
            logger.info(
                "Guardado simple (sin cálculo) para factor=%s instancia=%s",
                self.factor_slug,
                obj.pk,
            )
            # Guardado 'simple'
            form.save()  # esto llamará a la lógica de post_clean que normaliza calc_data
            messages.success(self.request, "Guardado correctamente.")

        # Decidir redirección
        next_url = self.request.POST.get("next") or self.request.GET.get("next")
        if next_url:
            logger.debug("Redirigiendo a next_url=%s", next_url)
            return redirect(next_url)
        logger.debug(
            "Redirigiendo al wizard_resumen para risk_eval=%s", self.risk_eval.pk
        )
        return redirect(_wizard_url(self.risk_eval.pk))

    def form_invalid(self, form):
        """Registra la falla de validación sin valores enviados por el usuario."""
        error_codes = {
            field: sorted(
                {
                    error.code or "invalid"
                    for error in error_list
                }
            )
            for field, error_list in form.errors.as_data().items()
        }
        logger.warning(
            "FactorFormView form_invalid factor=%s user=%s risk_eval=%s "
            "error_codes=%s",
            self.factor_slug,
            self.request.user,
            getattr(self, "_risk_eval", None),
            error_codes,
        )
        messages.error(
            self.request,
            "Hay errores en el formulario. Revisá los campos marcados en rojo.",
        )
        return super().form_invalid(form)

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        ctx = super().get_context_data(**kwargs)
        # 'object' lo usan varios templates para mostrar el último resultado
        ctx["object"] = self.instance
        # wizard snippet homogéneo
        ctx["wizard_resumen_url"] = _wizard_url(self.risk_eval.pk)
        ctx["factores"] = _build_wizard_items(self.risk_eval)
        # Las URLs de exportaciones esperan planillas.Evaluacion.pk, no la PK
        # de RiskEvaluation que viaja en las rutas de esta app (riesgo H-7).
        ctx["export_evaluacion_id"] = self.risk_eval.evaluacion_id
        ctx["export_factor_slug"] = self.factor_slug

        calc_data = getattr(self.instance, "calc_data", {}) or {}
        ctx["export_estado_resultado"] = calc_data.get("estado_resultado") or "borrador"
        return ctx


# ==============================================================================
# VIBRACIÓN CUERPO ENTERO (VCE)
# ==============================================================================

class _VibracionCESpecializedView(FactorFormView):
    """
    Vista especializada para VCE.
    - Maneja el Formulario Padre (VibracionCE_Eval)
    - Maneja los Tramos Hijos (VCESegment) vía Inline Formset.
    - Realiza guardado atómico y ejecución de cálculo post-guardado.
    """
    def get_context_data(self, **kwargs):
        """Inyecta el formset de segmentos en el contexto."""
        context = super().get_context_data(**kwargs)

        # Si ya viene en kwargs (ej: por error de validación), no lo pisamos
        if "segmentos" in kwargs:
            context["segmentos"] = kwargs["segmentos"]
        else:
            # Instanciamos el formset ligado a self.instance (que provee FactorFormView)
            if self.request.method == "POST":
                context["segmentos"] = VCESegmentFormSet(
                    self.request.POST,
                    self.request.FILES,
                    instance=self.instance
                )
            else:
                context["segmentos"] = VCESegmentFormSet(instance=self.instance)
        
        return context

    def form_valid(self, form):
        """
        Sobreescribimos para manejar el guardado conjunto de Padre + Hijos.
        """
        action = (self.request.POST.get("action") or "save").lower()

        # Reconstruimos el formset con los datos del POST
        segmentos = VCESegmentFormSet(
            self.request.POST,
            self.request.FILES,
            instance=self.instance
        )

        # Validación del Formset
        if not segmentos.is_valid():
            logger.warning(
                "[VCE] Error en segmentos | risk_eval=%s | errors=%s",
                self.risk_eval.pk, segmentos.errors
            )
            messages.error(self.request, "Hay errores en los tramos cargados. Por favor revísalos.")
            # Retornamos a la misma página con los errores visibles
            return self.render_to_response(self.get_context_data(form=form, segmentos=segmentos))

        # Guardado Atómico (Todo o Nada)
        try:
            with transaction.atomic():
                # 1. Guardar PADRE
                # FactorFormView ya vinculó self.instance, pero guardamos el form
                obj = form.save(commit=False)
                obj.risk_evaluation = self.risk_eval
                obj.factor_slug = self.factor_slug
                obj.save()
                
                # Sincronizamos form.instance para que save_and_calculate funcione bien
                form.instance = obj

                # 2. Guardar HIJOS (Segmentos)
                segmentos.instance = obj
                segmentos.save()

                # 3. Cálculo (Si el usuario pidió 'Guardar y Calcular')
                # Nota: El cálculo debe correr DESPUÉS de guardar los segmentos
                if action == "save_and_calc":
                    # Usamos el método estándar de BaseFactorForm
                    form.save_and_calculate()
                    messages.success(self.request, "Evaluación guardada y calculada correctamente.")
                else:
                    # Si es solo guardar, ya lo hicimos arriba, solo actualizamos metadatos si hace falta
                    form.save() # Para mergear input_json si hubiera
                    messages.success(self.request, "Cambios guardados correctamente.")

        except Exception as e:
            logger.error(f"[VCE] Error crítico al guardar: {e}", exc_info=True)
            messages.error(self.request, "Ocurrió un error inesperado al guardar.")
            return self.render_to_response(self.get_context_data(form=form, segmentos=segmentos))

        # Redirección estándar (Wizard o Detalle)
        # FactorFormView suele tener un success_url o lógica de wizard.
        # Aquí intentamos usar la lógica nativa si existe, o fallback al detalle.
        next_url = self.request.POST.get("next") or self.request.GET.get("next")
        if next_url:
            return redirect(next_url)

        return redirect(_wizard_url(self.risk_eval.pk))


def _install_catalog_view_classes() -> None:
    """Materializa las clases públicas declaradas por el catálogo."""
    for definition in FACTOR_DEFINITIONS:
        base_class = (
            _VibracionCESpecializedView
            if definition.view_kind == "vce"
            else FactorFormView
        )
        view_class = type(
            definition.view_class,
            (base_class,),
            {
                "__module__": __name__,
                "factor_slug": definition.slug,
                "form_class": import_string(definition.form_path),
                "template_name": definition.template_name,
                "url_name": definition.route_name_by_eval,
            },
        )
        globals()[definition.view_class] = view_class


_install_catalog_view_classes()

# Alias histórico conservado para imports externos previos.
VibracionCuerpoEnteroView = globals()["VibracionCEView"]
VibracionManoBrazoView = globals()["VibracionMBView"]


class StartFactorRedirectView(LoginRequiredMixin, View):
    """
    Bridge UX: desde Planilla 2 (por factor) aterriza en el form correcto
    asegurando que exista la RiskEvaluation para la Evaluacion (planillas).
    """

    def get(self, request, plan_eval_id: int, factor: str):
        # 1) Verificar que la Evaluacion (planillas) sea del usuario
        eval_obj = get_object_or_404(Evaluacion, pk=plan_eval_id, usuario=request.user)

        # 2) Obtener/crear la RiskEvaluation OneToOne (núcleo post-Planilla 2)
        riskeval, _created = RiskEvaluation.objects.get_or_create(
            evaluacion=eval_obj,
            defaults={"creado_por": request.user},
        )

        # 3) Resolver a qué URL por-evaluación redirigir según el slug
        try:
            # normalizamos factor al enum
            factor_choice = FactorSlug(factor)
        except Exception:
            # slug inválido -> fallback al resumen/“wizard”
            return redirect(reverse("evaluaciones:wizard_resumen_by_eval", args=[riskeval.pk]))

        definition = FACTOR_CATALOG.get(str(factor_choice))
        if definition is None:
            # Si no hay config, vamos al resumen
            return redirect(reverse("evaluaciones:wizard_resumen_by_eval", args=[riskeval.pk]))

        required = list(riskeval.factores_requeridos or [])
        if str(factor_choice) not in required:
            required.append(str(factor_choice))
            riskeval.factores_requeridos = required
            riskeval.estado = "in_progress"
            riskeval.save(
                update_fields=[
                    "factores_requeridos",
                    "estado",
                    "actualizado_en",
                ]
            )

        return redirect(
            reverse(
                f"evaluaciones:{definition.route_name_by_eval}",
                args=[riskeval.pk],
            )
        )
