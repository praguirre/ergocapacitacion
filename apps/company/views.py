# apps/company/views.py
# ============================================================================
# COMMIT 36: Vistas de nómina de trabajadores
# ============================================================================

from django.contrib import messages
from django.contrib.auth import get_user_model
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404

from apps.accounts.decorators import company_required
from .models import CompanyProfile, CompanyWorker

User = get_user_model()


def _get_company_profile(request):
    """Helper: obtener CompanyProfile del usuario actual."""
    try:
        return request.user.company_profile
    except CompanyProfile.DoesNotExist:
        return None


@company_required
def nomina_list(request):
    """Listado de trabajadores de la empresa con búsqueda y filtros."""
    cp = _get_company_profile(request)
    if not cp:
        messages.error(request, "No se encontró el perfil de empresa.")
        return redirect("dashboard:home")

    workers_qs = CompanyWorker.objects.filter(
        company=cp
    ).select_related('worker')

    # --- Búsqueda ---
    search = request.GET.get('q', '').strip()
    if search:
        workers_qs = workers_qs.filter(
            Q(worker__full_name__icontains=search) |
            Q(worker__first_name__icontains=search) |
            Q(worker__last_name__icontains=search) |
            Q(worker__cuil__icontains=search) |
            Q(worker__email__icontains=search) |
            Q(employee_code__icontains=search)
        )

    # --- Filtro por sector ---
    sector = request.GET.get('sector', '').strip()
    if sector:
        workers_qs = workers_qs.filter(department__icontains=sector)

    # --- Filtro por estado ---
    status_filter = request.GET.get('status', 'active')
    if status_filter == 'active':
        workers_qs = workers_qs.filter(is_active=True)
    elif status_filter == 'inactive':
        workers_qs = workers_qs.filter(is_active=False)
    # 'all' → no filtra

    # --- Stats ---
    all_workers = CompanyWorker.objects.filter(company=cp)
    stats = {
        'total_active': all_workers.filter(is_active=True).count(),
        'total_inactive': all_workers.filter(is_active=False).count(),
    }

    # --- Sectores únicos para el filtro ---
    departments = (
        CompanyWorker.objects.filter(company=cp)
        .exclude(department='')
        .values_list('department', flat=True)
        .distinct()
        .order_by('department')
    )

    return render(request, "company/nomina_list.html", {
        "workers": workers_qs,
        "stats": stats,
        "search": search,
        "sector": sector,
        "status_filter": status_filter,
        "departments": departments,
    })
