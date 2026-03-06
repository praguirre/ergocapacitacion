# apps/company/views.py
# ============================================================================
# COMMIT 36: Vistas de nómina de trabajadores
# ============================================================================

from django.contrib import messages
from django.contrib.auth import get_user_model
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404

from apps.accounts.decorators import company_required
from apps.quiz.models import QuizAttempt, QuizState
from apps.certificates.models import Certificate
from apps.training.models import TrainingModule
from .forms import AddWorkerForm, EditWorkerForm
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


@company_required
def nomina_add_worker(request):
    """Agregar un trabajador a la nómina."""
    cp = _get_company_profile(request)
    if not cp:
        messages.error(request, "No se encontró el perfil de empresa.")
        return redirect("dashboard:home")

    if request.method == "POST":
        form = AddWorkerForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            cuil = cd['cuil']
            email = cd['email'].strip().lower()

            # 1. Buscar trainee existente por CUIL
            worker = User.objects.filter(
                cuil=cuil, user_type='trainee'
            ).first()

            # 2. Si no encontró por CUIL, buscar por email
            if not worker:
                worker = User.objects.filter(
                    email__iexact=email, user_type='trainee'
                ).first()

            # 3. Si no existe, crear nuevo trainee
            if not worker:
                parts = cd['full_name'].strip().split(' ', 1)
                first = parts[0]
                last = parts[1] if len(parts) > 1 else ''

                worker = User.objects.create_trainee(
                    cuil=cuil,
                    email=email,
                    full_name=cd['full_name'],
                    first_name=first,
                    last_name=last,
                    job_title=cd.get('job_title', ''),
                    company_name=cp.razon_social,
                )

            # 4. Verificar si ya está en la nómina
            if CompanyWorker.objects.filter(company=cp, worker=worker).exists():
                messages.warning(
                    request,
                    f"{worker.display_name} ya está en tu nómina."
                )
                return render(request, "company/nomina_add.html", {"form": form})

            # 5. Crear la relación
            CompanyWorker.objects.create(
                company=cp,
                worker=worker,
                employee_code=cd.get('employee_code', ''),
                department=cd.get('department', ''),
                position=cd.get('position', ''),
                start_date=cd.get('start_date'),
                notes=cd.get('notes', ''),
            )

            messages.success(
                request,
                f"{worker.display_name} agregado a la nómina exitosamente."
            )
            return redirect("dashboard:company:nomina_list")
    else:
        form = AddWorkerForm()

    return render(request, "company/nomina_add.html", {"form": form})


@company_required
def nomina_detail(request, worker_id):
    """Ficha individual de un trabajador con historial de capacitaciones."""
    cp = _get_company_profile(request)
    if not cp:
        messages.error(request, "No se encontró el perfil de empresa.")
        return redirect("dashboard:home")

    assignment = get_object_or_404(CompanyWorker, company=cp, id=worker_id)
    worker = assignment.worker

    # Últimos intentos de quiz
    quiz_attempts = QuizAttempt.objects.filter(
        user=worker
    ).select_related('module').order_by('-started_at')[:20]

    # Certificados obtenidos
    certificates = Certificate.objects.filter(
        user=worker
    ).select_related('module').order_by('-issued_at')

    # Estado por módulo general activo
    modules = TrainingModule.objects.filter(
        is_active=True, is_personalized=False
    )
    module_status = []
    for mod in modules:
        qs = QuizState.objects.filter(user=worker, module=mod).first()
        cert = Certificate.objects.filter(user=worker, module=mod).first()
        from django.utils import timezone
        module_status.append({
            'module': mod,
            'quiz_state': qs,
            'certificate': cert,
            'is_approved': qs.is_approved if qs else False,
            'is_valid': cert and cert.valid_until and cert.valid_until > timezone.now() if cert else False,
        })

    return render(request, "company/nomina_detail.html", {
        "assignment": assignment,
        "worker": worker,
        "quiz_attempts": quiz_attempts,
        "certificates": certificates,
        "module_status": module_status,
    })


@company_required
def nomina_edit(request, worker_id):
    """Editar datos laborales de un trabajador."""
    cp = _get_company_profile(request)
    if not cp:
        return redirect("dashboard:home")

    assignment = get_object_or_404(CompanyWorker, company=cp, id=worker_id)

    if request.method == "POST":
        form = EditWorkerForm(request.POST, assignment=assignment)
        if form.is_valid():
            cd = form.cleaned_data
            assignment.employee_code = cd.get('employee_code', '')
            assignment.department = cd.get('department', '')
            assignment.position = cd.get('position', '')
            assignment.start_date = cd.get('start_date')
            assignment.end_date = cd.get('end_date')
            assignment.is_active = cd.get('is_active', True)
            assignment.notes = cd.get('notes', '')
            assignment.save()
            messages.success(request, "Datos laborales actualizados correctamente.")
            return redirect("dashboard:company:nomina_detail", worker_id=worker_id)
    else:
        form = EditWorkerForm(assignment=assignment)

    return render(request, "company/nomina_edit.html", {
        "form": form,
        "assignment": assignment,
    })
