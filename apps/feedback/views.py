"""Vista síncrona y protegida para el canal de feedback de la beta."""

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from apps.accounts.decorators import professional_required

from .forms import FeedbackForm
from .services import FeedbackRateLimitExceeded, create_and_send_feedback


@professional_required
@login_required
def create_feedback(request):
    """Muestra el formulario y aplica POST/Redirect/GET tras persistirlo."""
    if request.method == "POST":
        form = FeedbackForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                report, delivered = create_and_send_feedback(
                    professional=request.user,
                    cleaned_data=form.cleaned_data,
                    user_agent=request.META.get("HTTP_USER_AGENT", ""),
                )
            except FeedbackRateLimitExceeded as exc:
                form.add_error(None, exc)
            else:
                if delivered:
                    messages.success(
                        request,
                        f"Recibimos tu comentario. Código: {report.tracking_code}. "
                        "Gracias por ayudarnos a mejorar la beta de ErgoSolutions.",
                    )
                else:
                    messages.warning(
                        request,
                        f"Tu comentario quedó guardado con el código "
                        f"{report.tracking_code}, pero el correo no pudo enviarse "
                        "en este momento. No hace falta que lo cargues de nuevo; "
                        "el equipo puede reintentar el envío.",
                    )
                return redirect("dashboard:feedback:create")
    else:
        form = FeedbackForm()

    if form.errors:
        form.apply_error_accessibility()
    return render(request, "feedback/create.html", {"form": form})
