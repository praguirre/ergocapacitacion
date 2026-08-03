# planillas/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from django.views.generic import UpdateView
from django.db import transaction
from django.urls import reverse_lazy, reverse
from django.contrib import messages
from django.forms import modelformset_factory
from django.core.paginator import Paginator
from django.db.models import Prefetch, Q
from django.http import Http404
from django.views.decorators.http import require_POST
from apps.accounts.decorators import backoffice_required
from .models import (
    Evaluacion,
    Planilla1,
    FactorRiesgo,
    Planilla2A, Planilla2B, Planilla2C, Planilla2D, Planilla2E,
    Planilla2F, Planilla2G, Planilla2H, Planilla2I,
    Planilla3, MedidaEspecifica,
    SeguimientoMedida,
)
from .forms import (
    EvaluacionForm,
    Planilla1Form, FactorRiesgoFormSet,
    Planilla2AForm, Planilla2BForm, Planilla2CForm, Planilla2DForm, Planilla2EForm,
    Planilla2FForm, Planilla2GForm, Planilla2HForm, Planilla2IForm,
    Planilla3Form, MedidaEspecificaFormSet,
    SeguimientoMedidaForm,
)
from .querysets import (
    evaluaciones_visibles_para,
    obtener_evaluacion_o_404,
    puede_editar_evaluaciones,
)
from .agenda import sincronizar_medida_con_agenda

# NUEVOS imports para integrar el resumen de factores desde la app evaluaciones
from apps.ergonomia_886.evaluaciones.views import _build_wizard_items, _get_riskeval_or_404_for_user, _wizard_url


# Etiquetas legibles para los slugs de evaluaciones (evitamos acoplar a evaluaciones.views)
FACTOR_LABELS = {
    "lmc": "Levantamiento Manual de Cargas (LMC)",
    "empuje_inicial": "Empuje — Fuerza Inicial",
    "empuje_sostenida": "Empuje — Fuerza Sostenida",
    "traccion_inicial": "Tracción — Fuerza Inicial",
    "traccion_sostenida": "Tracción — Fuerza Sostenida",
    "transporte": "Transporte manual",
    "bipedestacion": "Bipedestación",
    "repetitivos_ms": "Movimientos repetitivos (MS)",
    "posturas_forzadas": "Posturas forzadas",
    "vibracion_mano_brazo": "Vibración mano-brazo",
    "vibracion_cuerpo_entero": "Vibración de cuerpo entero",
    "confort_termico": "Confort térmico",
    "estres_contacto": "Estrés de contacto",
}


@login_required
@backoffice_required
def evaluacion_list_view(request):
    """Pantalla de aterrizaje del módulo con propiedad mixta D-9."""
    evaluaciones_qs = (
        evaluaciones_visibles_para(request.user)
        .select_related("usuario", "empresa")
        .prefetch_related(Prefetch("planilla1", queryset=Planilla1.objects.all()))
    )

    search_query = request.GET.get("search", "").strip()
    if search_query:
        evaluaciones_qs = evaluaciones_qs.filter(
            Q(razon_social__icontains=search_query)
            | Q(cuit__icontains=search_query)
            | Q(provincia__icontains=search_query)
            | Q(direccion_establecimiento__icontains=search_query)
            | Q(planilla1__area_sector__icontains=search_query)
            | Q(planilla1__puesto_trabajo__icontains=search_query)
        ).distinct()

    provincia_filter = request.GET.get("provincia", "").strip()
    if provincia_filter:
        evaluaciones_qs = evaluaciones_qs.filter(
            provincia__iexact=provincia_filter
        )

    fecha_desde = request.GET.get("fecha_desde", "").strip()
    if fecha_desde:
        evaluaciones_qs = evaluaciones_qs.filter(
            fecha_creacion__date__gte=fecha_desde
        )

    fecha_hasta = request.GET.get("fecha_hasta", "").strip()
    if fecha_hasta:
        evaluaciones_qs = evaluaciones_qs.filter(
            fecha_creacion__date__lte=fecha_hasta
        )

    orden = request.GET.get("orden", "-fecha_modificacion")
    ordenes_validos = [
        "-fecha_modificacion", "fecha_modificacion",
        "-fecha_creacion", "fecha_creacion",
        "razon_social", "-razon_social",
    ]
    if orden not in ordenes_validos:
        orden = "-fecha_modificacion"
    evaluaciones_qs = evaluaciones_qs.order_by(orden)

    paginator = Paginator(evaluaciones_qs, 20)
    evaluaciones_page = paginator.get_page(request.GET.get("page"))

    provincias_disponibles = (
        evaluaciones_visibles_para(request.user)
        .values_list("provincia", flat=True)
        .distinct()
        .order_by("provincia")
    )

    return render(request, "planillas/evaluacion_list.html", {
        "evaluaciones": evaluaciones_page,
        "provincias_disponibles": provincias_disponibles,
        "total_resultados": evaluaciones_qs.count(),
        "current_search": search_query,
        "current_provincia": provincia_filter,
        "current_fecha_desde": fecha_desde,
        "current_fecha_hasta": fecha_hasta,
        "current_orden": orden,
        "puede_crear": puede_editar_evaluaciones(request.user),
    })


@login_required
@backoffice_required
@require_POST
def eliminar_evaluacion_view(request, evaluacion_id):
    """Elimina una evaluación exclusivamente cuando la solicita su autor."""
    if not puede_editar_evaluaciones(request.user):
        raise Http404

    evaluacion = get_object_or_404(
        Evaluacion, pk=evaluacion_id, usuario=request.user,
    )
    razon_social = evaluacion.razon_social
    evaluacion.delete()
    messages.success(
        request,
        f"Evaluación de «{razon_social}» eliminada correctamente.",
    )
    return redirect("ergonomia_886:evaluacion_list")


# ─────────────────────────────────────────────────────────────────────
# EVALUACIÓN – alta inicial
# ─────────────────────────────────────────────────────────────────────
@login_required
@backoffice_required
def crear_evaluacion_view(request):
    if request.method == 'POST':
        form = EvaluacionForm(request.POST, user=request.user)
        if form.is_valid():
            evaluacion = form.save()
            return redirect('planillas:detalle_evaluacion', evaluacion_id=evaluacion.id)
    else:
        form = EvaluacionForm(user=request.user)
    return render(request, 'planillas/crear_evaluacion.html', {'form': form})

# ─────────────────────────────────────────────────────────────────────
# HUB – detalle de la evaluación (estado de todas las planillas)
# ─────────────────────────────────────────────────────────────────────

@login_required
@backoffice_required
def detalle_evaluacion_view(request, evaluacion_id):
    evaluacion = obtener_evaluacion_o_404(evaluacion_id, request.user)

    # Garantizar que exista Planilla3 para esta evaluación
    planilla3, _ = Planilla3.objects.get_or_create(evaluacion=evaluacion)

    # Lógica para Planilla 1
    p1 = Planilla1.objects.filter(evaluacion=evaluacion).first()
    has_planilla1 = bool(p1 and p1.puesto_trabajo)

    # --- INICIO DE LA LÓGICA MEJORADA PARA PLANILLA 4 ---
    total_medidas = planilla3.medidas.count()
    medidas_con_cierre = SeguimientoMedida.objects.filter(
        medida_especifica__planilla3=planilla3,
        fecha_cierre__isnull=False
    ).count()
    has_planilla4_completa = (total_medidas > 0) and (total_medidas == medidas_con_cierre)
    # --- FIN DE LA LÓGICA MEJORADA ---

    # --- Resumen tipo wizard (factores) ---
    # RiskEvaluation está enlazada 1:1 con Evaluacion; reutilizamos los helpers de 'evaluaciones'
    try:
        risk_eval = _get_riskeval_or_404_for_user(evaluacion_id, request.user)
        factores = _build_wizard_items(risk_eval)
    except Exception:
        # En caso de que no exista aún la evaluación en la app 'evaluaciones'
        factores = []

    context = {
        'evaluacion': evaluacion,
        'has_planilla1': has_planilla1,
        'has_planilla2a': Planilla2A.objects.filter(evaluacion=evaluacion).exists(),
        'has_planilla2b': Planilla2B.objects.filter(evaluacion=evaluacion).exists(),
        'has_planilla2c': Planilla2C.objects.filter(evaluacion=evaluacion).exists(),
        'has_planilla2d': Planilla2D.objects.filter(evaluacion=evaluacion).exists(),
        'has_planilla2e': Planilla2E.objects.filter(evaluacion=evaluacion).exists(),
        'has_planilla2f': Planilla2F.objects.filter(evaluacion=evaluacion).exists(),
        'has_planilla2g': Planilla2G.objects.filter(evaluacion=evaluacion).exists(),
        'has_planilla2h': Planilla2H.objects.filter(evaluacion=evaluacion).exists(),
        'has_planilla2i': Planilla2I.objects.filter(evaluacion=evaluacion).exists(),
        'has_planilla3': hasattr(evaluacion, 'planilla3') and evaluacion.planilla3.medidas.exists(),
        'has_planilla4': has_planilla4_completa,
        # Nuevos datos para el resumen de factores
        'factores': factores,
        'wizard_resumen_url': _wizard_url(evaluacion.pk),
    }

    return render(request, 'planillas/detalle_evaluacion.html', context)


# ─────────────────────────────────────────────────────────────────────
# PLANILLA 1 (con formset de factores de riesgo)
# ─────────────────────────────────────────────────────────────────────
@login_required
@backoffice_required
@transaction.atomic
def planilla1_view(request, evaluacion_id):
    evaluacion = obtener_evaluacion_o_404(evaluacion_id, request.user)
    planilla1, created = Planilla1.objects.get_or_create(evaluacion=evaluacion)
    if created:
        for t, _ in FactorRiesgo.TIPO_FACTOR_CHOICES:
            FactorRiesgo.objects.create(planilla1=planilla1, tipo_factor=t)

    if request.method == 'POST':
        form = Planilla1Form(request.POST, instance=planilla1)
        formset = FactorRiesgoFormSet(request.POST, instance=planilla1)
        if form.is_valid() and formset.is_valid():
            form.save()
            formset.save()
            return redirect('planillas:detalle_evaluacion', evaluacion_id=evaluacion.id)
    else:
        form = Planilla1Form(instance=planilla1)
        formset = FactorRiesgoFormSet(instance=planilla1)

    return render(
        request,
        'planillas/planilla1_form.html',
        {
            'form': form,
            'formset': formset,
            'evaluacion': evaluacion,
            'titulo_planilla': 'Planilla 1: Identificación de Factores de Riesgo',
        },
    )


# ─────────────────────────────────────────────────────────────────────
# VISTA GENÉRICA PARA PLANILLAS 2 (VERSIÓN FINAL)
# ─────────────────────────────────────────────────────────────────────

def _generic_planilla2_view(
    request,
    evaluacion_id,
    model_cls,
    form_cls,
    titulo,
    help_slug,
    factor_slug=None,
    factor_slugs: list[str] | None = None,
):
    evaluacion = obtener_evaluacion_o_404(evaluacion_id, request.user)

    instance = model_cls.objects.filter(evaluacion=evaluacion).first() or model_cls(evaluacion=evaluacion)

    if request.method == 'POST':
        form = form_cls(request.POST, instance=instance)
        if form.is_valid():
            form.save()
            return redirect('planillas:detalle_evaluacion', evaluacion_id=evaluacion.id)
    else:
        form = form_cls(instance=instance)

    slugs = factor_slugs if factor_slugs else ([factor_slug] if factor_slug else [])
    evaluacion_factor_urls = []
    for s in slugs:
        if not s:
            continue
        evaluacion_factor_urls.append({
            "slug": s,
            "label": FACTOR_LABELS.get(s, s),
            "url": reverse("evaluaciones:start_factor", args=[evaluacion.pk, s]),
        })

    context = {
        'form': form,
        'evaluacion': evaluacion,
        'titulo_planilla': titulo,
        'help_slug': help_slug,
        'factor_slug': factor_slug,
        'evaluacion_factor_url': evaluacion_factor_urls[0]["url"] if evaluacion_factor_urls else None,
        'evaluacion_factor_urls': evaluacion_factor_urls,
    }

    return render(request, 'planillas/planilla2_structured_form.html', context)


# ─────────────────────────────────────────────────────────────────────
# VISTAS ESPECÍFICAS (2A–2I)
# ─────────────────────────────────────────────────────────────────────

@login_required
@backoffice_required
def planilla2a_view(request, evaluacion_id):
    return _generic_planilla2_view(
        request, evaluacion_id,
        Planilla2A, Planilla2AForm,
        'Planilla 2A: Levantamiento/Descenso',
        'planilla2a',
        factor_slug='lmc',
    )

@login_required
@backoffice_required
def planilla2b_view(request, evaluacion_id):
    return _generic_planilla2_view(
        request, evaluacion_id,
        Planilla2B, Planilla2BForm,
        'Planilla 2B: Empuje/Arrastre',
        'planilla2b',
        factor_slugs=[
            'empuje_inicial',
            'empuje_sostenida',
            'traccion_inicial',
            'traccion_sostenida',
        ],
    )

@login_required
@backoffice_required
def planilla2c_view(request, evaluacion_id):
    return _generic_planilla2_view(
        request, evaluacion_id,
        Planilla2C, Planilla2CForm,
        'Planilla 2C: Transporte Manual',
        'planilla2c',
        factor_slug='transporte',
    )

@login_required
@backoffice_required
def planilla2d_view(request, evaluacion_id):
    return _generic_planilla2_view(
        request, evaluacion_id,
        Planilla2D, Planilla2DForm,
        'Planilla 2D: Bipedestación',
        'planilla2d',
        factor_slug='bipedestacion',
    )

@login_required
@backoffice_required
def planilla2e_view(request, evaluacion_id):
    return _generic_planilla2_view(
        request, evaluacion_id,
        Planilla2E, Planilla2EForm,
        'Planilla 2E: Movimientos Repetitivos',
        'planilla2e',
        factor_slug='repetitivos_ms',
    )

@login_required
@backoffice_required
def planilla2f_view(request, evaluacion_id):
    return _generic_planilla2_view(
        request, evaluacion_id,
        Planilla2F, Planilla2FForm,
        'Planilla 2F: Posturas Forzadas',
        'planilla2f',
        factor_slug='posturas_forzadas',
    )

@login_required
@backoffice_required
def planilla2g_view(request, evaluacion_id):
    return _generic_planilla2_view(
        request, evaluacion_id,
        Planilla2G, Planilla2GForm,
        'Planilla 2G: Vibraciones',
        'planilla2g',
        factor_slugs=[
            'vibracion_mano_brazo',
            'vibracion_cuerpo_entero',
        ],
    )

@login_required
@backoffice_required
def planilla2h_view(request, evaluacion_id):
    return _generic_planilla2_view(
        request, evaluacion_id,
        Planilla2H, Planilla2HForm,
        'Planilla 2H: Confort Térmico',
        'planilla2h',
        factor_slug='confort_termico',
    )

@login_required
@backoffice_required
def planilla2i_view(request, evaluacion_id):
    return _generic_planilla2_view(
        request, evaluacion_id,
        Planilla2I, Planilla2IForm,
        'Planilla 2I: Estrés de Contacto',
        'planilla2i',
        factor_slug='estres_contacto',
    )


# ─────────────────────────────────────────────────────────────────────
# PLANILLA 3 – Medidas Correctivas y Preventivas
# ─────────────────────────────────────────────────────────────────────
class Planilla3UpdateView(LoginRequiredMixin, UpdateView):
    model = Planilla3
    form_class = Planilla3Form
    template_name = "planillas/planilla3_form.html"

    def get_object(self, queryset=None):
        evaluacion = obtener_evaluacion_o_404(
            self.kwargs['evaluacion_id'], self.request.user
        )
        obj, _ = Planilla3.objects.get_or_create(evaluacion=evaluacion)
        return obj

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['evaluacion'] = self.object.evaluacion
        if self.request.POST:
            ctx['medidas_formset'] = MedidaEspecificaFormSet(
                self.request.POST, instance=self.object
            )
        else:
            ctx['medidas_formset'] = MedidaEspecificaFormSet(instance=self.object)
        return ctx

    @transaction.atomic
    def form_valid(self, form):
        ctx = self.get_context_data()
        formset = ctx['medidas_formset']
        if formset.is_valid():
            self.object = form.save()
            formset.instance = self.object
            formset.save()
            messages.success(self.request, "Planilla 3 guardada correctamente.")
            return redirect('planillas:detalle_evaluacion', evaluacion_id=self.object.evaluacion.id)

        messages.error(self.request, "Corrige los errores antes de continuar.")
        return self.form_invalid(form)


# ─────────────────────────────────────────────────────────────────────
# PLANILLA 4 – Matriz de Seguimiento
# ─────────────────────────────────────────────────────────────────────
class Planilla4UpdateView(LoginRequiredMixin, View):
    template_name = "planillas/planilla4_form.html"

    def _build_formset(self, planilla3, data=None):
        medidas = planilla3.medidas.all()
        for medida in medidas:
            SeguimientoMedida.objects.get_or_create(medida_especifica=medida)

        SeguimientoFormSet = modelformset_factory(
            SeguimientoMedida,
            form=SeguimientoMedidaForm,
            extra=0,
            can_delete=False,
        )
        qs = SeguimientoMedida.objects.filter(
            medida_especifica__in=medidas
        ).order_by("medida_especifica_id")
        return SeguimientoFormSet(data, queryset=qs, prefix='seg')

    def get(self, request, evaluacion_id):
        evaluacion = obtener_evaluacion_o_404(evaluacion_id, request.user)
        planilla3 = get_object_or_404(Planilla3, evaluacion=evaluacion)
        formset = self._build_formset(planilla3)
        return render(
            request,
            self.template_name,
            {"planilla3": planilla3, "formset": formset, "evaluacion": evaluacion},
        )

    @transaction.atomic
    def post(self, request, evaluacion_id):
        evaluacion = obtener_evaluacion_o_404(evaluacion_id, request.user)
        planilla3 = get_object_or_404(Planilla3, evaluacion=evaluacion)
        formset = self._build_formset(planilla3, data=request.POST)

        if formset.is_valid():
            formset.save()
            for form in formset.forms:
                if form.cleaned_data:
                    sincronizar_medida_con_agenda(form.instance)
            messages.success(request, "Matriz de seguimiento guardada.")
            return redirect('planillas:detalle_evaluacion', evaluacion_id=evaluacion.id)

        messages.error(request, "Revisa los campos señalados.")
        return render(
            request,
            self.template_name,
            {"planilla3": planilla3, "formset": formset, "evaluacion": evaluacion},
        )
