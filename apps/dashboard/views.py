# apps/dashboard/views.py
# ============================================================================
# COMMIT 15-23: Dashboard, Capacitaciones y Links Online
# ============================================================================

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.conf import settings as django_settings
from django.core.mail import send_mail
from django.db import models
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from apps.accounts.decorators import professional_required
from apps.presencial.models import PresencialSession
from apps.training.models import CapacitacionLink, LinkShareLog, TrainingModule

from .forms import ShareLinkForm


@login_required
@professional_required
def home(request):
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
    }

    return render(request, "dashboard/home.html", {
        "stats": stats,
    })


@login_required
@professional_required
def capacitaciones_menu(request):
    """
    Menu de capacitaciones disponibles.
    Muestra grid de cards con iconos y estados.
    """
    modules = TrainingModule.objects.all()

    return render(request, "dashboard/capacitaciones_menu.html", {
        "modules": modules,
    })


@login_required
@professional_required
def modalidad_selector(request, module_slug):
    """
    Selector de modalidad: Presencial u Online.
    """
    module = get_object_or_404(TrainingModule, slug=module_slug, is_active=True)

    return render(request, "dashboard/modalidad_selector.html", {
        "module": module,
    })


@login_required
@professional_required
def online_links(request, module_slug):
    """
    Gestión de links para una capacitación online.
    Lista links existentes y permite crear nuevos.
    """
    module = get_object_or_404(TrainingModule, slug=module_slug, is_active=True)

    links = CapacitacionLink.objects.filter(
        module=module,
        created_by=request.user,
    ).order_by("-created_at")

    return render(request, "dashboard/online_links.html", {
        "module": module,
        "links": links,
    })


@login_required
@professional_required
@require_POST
def generate_link(request, module_slug):
    """Genera un nuevo link de capacitación."""
    module = get_object_or_404(TrainingModule, slug=module_slug, is_active=True)

    label = request.POST.get("label", "").strip()

    CapacitacionLink.objects.create(
        module=module,
        created_by=request.user,
        label=label,
    )

    messages.success(request, "Link generado exitosamente.")
    return redirect("dashboard:online_links", module_slug=module_slug)


@login_required
@professional_required
def share_link(request, module_slug, link_id):
    """
    Formulario para compartir link por email.
    """
    module = get_object_or_404(TrainingModule, slug=module_slug, is_active=True)
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
@professional_required
def profile(request):
    """Perfil del profesional (placeholder - se completa en Commit 26)."""
    return render(request, "dashboard/profile.html")
