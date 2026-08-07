# apps/dashboard/views.py
# ============================================================================
# COMMIT 15-26: Dashboard, Capacitaciones, Links y Perfil
# ============================================================================

from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.conf import settings as django_settings
from django.core.mail import send_mail
from django.db import models
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_POST

from apps.accounts.decorators import backoffice_required, professional_required
from apps.company.models import CompanyProfile, ContactRequest
from apps.presencial.models import PresencialSession
from apps.training.models import CapacitacionLink, LinkShareLog, TrainingModule

from .forms import (
    ChangePasswordForm, CompanyProfileEditForm,
    ProfessionalProfileForm, ShareLinkForm,
)
from .evaluaciones_catalog import get_evaluation_modules
from .utils import check_module_access


@login_required
@backoffice_required
def home(request):
    """
    Dashboard home: despacha al dashboard correcto según tipo.
    """
    if request.user.is_company:
        return _company_dashboard(request)
    return _professional_dashboard(request)


def _professional_dashboard(request):
    """
    Dashboard principal del profesional.
    Muestra selector de Evaluaciones / Capacitaciones y stats basicas.
    """
    presencial_count = PresencialSession.objects.filter(
        professional=request.user
    ).count()
    links_count = CapacitacionLink.objects.filter(created_by=request.user).count()
    total_accesses = (
        CapacitacionLink.objects.filter(created_by=request.user)
        .aggregate(total=models.Sum("access_count"))["total"]
        or 0
    )

    stats = {
        "capacitaciones_total": presencial_count,
        "links_generados": links_count,
        "trabajadores_capacitados": total_accesses,
        "evaluaciones_ergonomicas": _contar_evaluaciones_ergonomicas(
            request.user
        ),
    }

    return render(request, "dashboard/home.html", {
        "stats": stats,
    })


def _contar_evaluaciones_ergonomicas(user):
    """Cuenta evaluaciones sin acoplar el dashboard al módulo 886.

    Además del import diferido se consulta ``INSTALLED_APPS``: si el paquete
    sigue presente en disco pero la app fue desmontada, importar el modelo no
    es una prueba suficiente de que Django pueda utilizarlo.
    """
    if "apps.ergonomia_886.planillas" not in django_settings.INSTALLED_APPS:
        return None

    try:
        from apps.ergonomia_886.planillas.models import Evaluacion
    except (ImportError, RuntimeError):
        return None

    return Evaluacion.objects.filter(usuario=user).count()


def _company_dashboard(request):
    """Dashboard para empresas con panel de vencimientos y agenda."""
    from apps.company.models import CompanyWorker, AgendaEvent
    from apps.certificates.models import Certificate
    from apps.training.models import CapacitacionLink

    user = request.user
    try:
        cp = user.company_profile
    except CompanyProfile.DoesNotExist:
        return render(request, "dashboard/home.html", {})

    now = timezone.now()

    total_workers = CompanyWorker.objects.filter(
        company=cp, is_active=True
    ).count()

    events_pending = AgendaEvent.objects.filter(
        company=cp, status='pending'
    ).count()
    events_overdue = AgendaEvent.objects.filter(
        company=cp, status='pending', due_at__lt=now
    ).count()
    upcoming_events = AgendaEvent.objects.filter(
        company=cp, status='pending', due_at__gte=now
    ).order_by('due_at')[:5]

    workers_with_certs = Certificate.objects.filter(
        user__company_assignments__company=cp,
        user__company_assignments__is_active=True,
    ).values('user').distinct().count()
    coverage = round(workers_with_certs / total_workers * 100, 1) if total_workers > 0 else 0

    links_count = CapacitacionLink.objects.filter(created_by=user).count()

    return render(request, "dashboard/home_company.html", {
        "company_profile": cp,
        "stats": {
            "total_workers": total_workers,
            "events_pending": events_pending,
            "events_overdue": events_overdue,
            "coverage": coverage,
            "links_count": links_count,
        },
        "upcoming_events": upcoming_events,
    })


@login_required
@backoffice_required
def capacitaciones_menu(request):
    """
    Menu de capacitaciones disponibles.
    Muestra grid de cards con iconos y estados.
    """
    general_modules = TrainingModule.get_general_modules()
    personalized_modules = TrainingModule.get_personalized_for_user(request.user)

    return render(request, "dashboard/capacitaciones_menu.html", {
        "general_modules": general_modules,
        "personalized_modules": personalized_modules,
        "has_personalized": personalized_modules.exists(),
    })


@login_required
@backoffice_required
def evaluaciones_menu(request):
    """Menú de protocolos disponibles y planificados."""
    modules = [
        {
            "slug": module.slug,
            "title": module.title,
            "description": module.description,
            "icon": module.icon,
            "color": module.color,
            "is_active": module.is_active,
            "url": reverse(module.url_name) if module.url_name else "",
        }
        for module in get_evaluation_modules()
    ]

    return render(
        request,
        "dashboard/evaluaciones_menu.html",
        {"evaluation_modules": modules},
    )


@login_required
@backoffice_required
def modalidad_selector(request, module_slug):
    """
    Selector de modalidad: Presencial u Online.
    """
    module = get_object_or_404(TrainingModule, slug=module_slug, is_active=True)
    access_error = check_module_access(module, request.user)
    if access_error:
        return access_error

    return render(request, "dashboard/modalidad_selector.html", {
        "module": module,
    })


@login_required
@backoffice_required
def online_links(request, module_slug):
    """
    Gestión de links para una capacitación online.
    Lista links existentes y permite crear nuevos.
    """
    module = get_object_or_404(TrainingModule, slug=module_slug, is_active=True)
    access_error = check_module_access(module, request.user)
    if access_error:
        return access_error

    links = CapacitacionLink.objects.filter(
        module=module,
        created_by=request.user,
    ).order_by("-created_at")

    return render(request, "dashboard/online_links.html", {
        "module": module,
        "links": links,
    })


@login_required
@backoffice_required
@require_POST
def generate_link(request, module_slug):
    """Genera un nuevo link de capacitación."""
    module = get_object_or_404(TrainingModule, slug=module_slug, is_active=True)
    access_error = check_module_access(module, request.user)
    if access_error:
        return access_error

    label = request.POST.get("label", "").strip()

    CapacitacionLink.objects.create(
        module=module,
        created_by=request.user,
        label=label,
    )

    messages.success(request, "Link generado exitosamente.")
    return redirect("dashboard:online_links", module_slug=module_slug)


@login_required
@backoffice_required
def share_link(request, module_slug, link_id):
    """
    Formulario para compartir link por email.
    """
    module = get_object_or_404(TrainingModule, slug=module_slug, is_active=True)
    access_error = check_module_access(module, request.user)
    if access_error:
        return access_error

    link = get_object_or_404(
        CapacitacionLink, id=link_id, module=module, created_by=request.user
    )

    if request.method == "POST":
        form = ShareLinkForm(request.POST)
        if form.is_valid():
            emails = form.cleaned_data["emails"]
            custom_message = form.cleaned_data.get("message", "")

            link_url = f"{request.scheme}://{request.get_host()}{link.get_absolute_url()}"

            sent_count = 0
            for email in emails:
                try:
                    subject = f"Capacitación: {module.title} - ErgoSolutions"
                    body = (
                        f"Hola,\n\n"
                        f"{request.user.display_name} te envía la siguiente capacitación:\n\n"
                        f"📚 {module.title}\n\n"
                    )
                    if custom_message:
                        body += f"Mensaje: {custom_message}\n\n"
                    body += (
                        f"Accedé al siguiente link para realizar la capacitación:\n"
                        f"{link_url}\n\n"
                        f"---\n"
                        f"ErgoSolutions - Plataforma de Capacitación\n"
                    )

                    send_mail(
                        subject=subject,
                        message=body,
                        from_email=django_settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[email],
                        fail_silently=True,
                    )

                    LinkShareLog.objects.create(
                        link=link,
                        shared_to_email=email,
                    )
                    sent_count += 1

                except Exception:
                    pass  # No bloquear por fallos individuales

            messages.success(request, f"Link enviado a {sent_count} email(s).")
            return redirect("dashboard:online_links", module_slug=module_slug)
    else:
        form = ShareLinkForm()

    return render(request, "dashboard/share_link.html", {
        "module": module,
        "link": link,
        "form": form,
    })


@login_required
@backoffice_required
def profile(request):
    """Perfil unificado: despacha al correcto según tipo de usuario."""
    if request.user.is_company:
        return _company_profile_view(request)
    return _professional_profile_view(request)


def _professional_profile_view(request):
    """Lógica de perfil para profesional (preserva funcionalidad existente)."""
    user = request.user

    profile_form = ProfessionalProfileForm(user=user)
    password_form = ChangePasswordForm(user=user)

    if request.method == "POST":
        action = request.POST.get("action")

        if action == "update_profile":
            profile_form = ProfessionalProfileForm(request.POST, user=user)
            if profile_form.is_valid():
                user.first_name = profile_form.cleaned_data["first_name"]
                user.last_name = profile_form.cleaned_data["last_name"]
                user.email = profile_form.cleaned_data["email"]
                user.profession = profile_form.cleaned_data.get("profession", "")
                user.license_number = profile_form.cleaned_data.get("license_number", "")
                user.dni = profile_form.cleaned_data.get("dni", "")
                user.save()
                messages.success(request, "Perfil actualizado correctamente.")
                return redirect("dashboard:profile")

        elif action == "change_password":
            password_form = ChangePasswordForm(request.POST, user=user)
            if password_form.is_valid():
                user.set_password(password_form.cleaned_data["new_password1"])
                user.save()
                # Re-autenticar para no cerrar sesión
                update_session_auth_hash(request, user)
                messages.success(request, "Contraseña actualizada correctamente.")
                return redirect("dashboard:profile")

    # Stats
    presencial_count = PresencialSession.objects.filter(professional=user).count()
    links_count = CapacitacionLink.objects.filter(created_by=user).count()
    shares_count = LinkShareLog.objects.filter(link__created_by=user).count()

    return render(request, "dashboard/profile.html", {
        "profile_form": profile_form,
        "password_form": password_form,
        "stats": {
            "presencial": presencial_count,
            "links": links_count,
            "shares": shares_count,
        },
    })


def _company_profile_view(request):
    """Lógica de perfil para empresa."""
    user = request.user
    try:
        cp = user.company_profile
    except CompanyProfile.DoesNotExist:
        messages.error(request, "No se encontró el perfil de empresa.")
        return redirect("dashboard:home")

    profile_form = CompanyProfileEditForm(company_profile=cp, user=user)
    password_form = ChangePasswordForm(user=user)

    if request.method == "POST":
        action = request.POST.get("action")
        if action == "update_profile":
            profile_form = CompanyProfileEditForm(
                request.POST, company_profile=cp, user=user,
            )
            if profile_form.is_valid():
                cd = profile_form.cleaned_data
                cp.razon_social = cd["razon_social"]
                cp.nombre_comercial = cd.get("nombre_comercial", "")
                cp.rubro = cd.get("rubro", "")
                cp.cantidad_trabajadores = cd.get("cantidad_trabajadores") or 0
                cp.contacto_nombre = cd["contacto_nombre"]
                cp.contacto_cargo = cd.get("contacto_cargo", "")
                cp.contacto_telefono = cd.get("contacto_telefono", "")
                cp.domicilio = cd.get("domicilio", "")
                cp.provincia = cd.get("provincia", "")
                cp.save()
                user.email = cd["email"]
                user.save()
                messages.success(request, "Perfil de empresa actualizado correctamente.")
                return redirect("dashboard:profile")
        elif action == "change_password":
            password_form = ChangePasswordForm(request.POST, user=user)
            if password_form.is_valid():
                user.set_password(password_form.cleaned_data["new_password1"])
                user.save()
                update_session_auth_hash(request, user)
                messages.success(request, "Contraseña actualizada correctamente.")
                return redirect("dashboard:profile")

    links_count = CapacitacionLink.objects.filter(created_by=user).count()

    return render(request, "dashboard/company_profile.html", {
        "profile_form": profile_form,
        "password_form": password_form,
        "company_profile": cp,
        "stats": {"links": links_count},
    })


@login_required
@professional_required
def my_contact_requests(request):
    """Profesional ve solicitudes pendientes."""
    pending_requests = ContactRequest.objects.filter(
        professional=request.user,
        status=ContactRequest.RequestStatus.PENDING,
    ).select_related('company').order_by('-created_at')

    return render(request, "dashboard/my_contact_requests.html", {
        "pending_requests": pending_requests,
    })


@login_required
@professional_required
def respond_contact_request(request, request_id):
    """Profesional acepta o rechaza solicitud."""
    contact_request = get_object_or_404(
        ContactRequest,
        id=request_id,
        professional=request.user,
        status=ContactRequest.RequestStatus.PENDING,
    )

    if request.method != "POST":
        messages.error(request, "Método no permitido para responder solicitud.")
        return redirect("dashboard:my_contact_requests")

    response_action = request.POST.get("response_action", "").strip().lower()
    if response_action not in {"accepted", "rejected"}:
        messages.error(request, "Respuesta inválida.")
        return redirect("dashboard:my_contact_requests")

    contact_request.status = response_action
    contact_request.responded_at = timezone.now()
    contact_request.response_message = request.POST.get("response_message", "").strip()
    contact_request.save(update_fields=["status", "responded_at", "response_message"])

    messages.success(request, "Solicitud respondida correctamente.")
    return redirect("dashboard:my_contact_requests")
