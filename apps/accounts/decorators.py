# apps/accounts/decorators.py
# ============================================================================
# COMMIT 10: Decoradores de permisos por tipo de usuario
# ============================================================================

from functools import wraps
from django.shortcuts import redirect
from django.urls import reverse
from django.http import HttpResponseForbidden


def professional_required(function=None, redirect_url=None, login_url=None):
    """
    Decorador que requiere que el usuario sea un profesional autenticado.

    Uso:
        @professional_required
        def my_view(request): ...

        @professional_required(redirect_url='landing')
        def my_view(request): ...
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                url = login_url or reverse('accounts_professional:professional_login')
                return redirect(f"{url}?next={request.get_full_path()}")

            # Defensa extra (como propuso el senior)
            if not request.user.is_active or not request.user.is_professional:
                if redirect_url:
                    return redirect(redirect_url)
                return HttpResponseForbidden(
                    "Acceso denegado. Esta sección es solo para profesionales."
                )

            return view_func(request, *args, **kwargs)
        return _wrapped_view

    if function:
        return decorator(function)
    return decorator


def trainee_required(function=None, redirect_url=None, login_url=None):
    """
    Decorador que requiere que el usuario sea un trabajador (trainee) autenticado.
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                url = login_url or reverse('trainee_landing')
                return redirect(f"{url}?next={request.get_full_path()}")

            # Defensa extra (como propuso el senior)
            if not request.user.is_active or not request.user.is_trainee:
                if redirect_url:
                    return redirect(redirect_url)
                return HttpResponseForbidden(
                    "Acceso denegado. Esta sección es solo para trabajadores en capacitación."
                )

            return view_func(request, *args, **kwargs)
        return _wrapped_view

    if function:
        return decorator(function)
    return decorator


def backoffice_required(function=None, redirect_url=None, login_url=None):
    """
    Decorador que requiere que el usuario sea de backoffice
    (professional O company) y esté autenticado.

    Este decorador unifica el acceso al dashboard para ambos tipos
    de usuario de gestión, evitando duplicar vistas.

    Uso:
        @backoffice_required
        def dashboard_view(request): ...

        @backoffice_required(redirect_url='landing:home')
        def dashboard_view(request): ...
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                url = login_url or reverse('accounts_professional:professional_login')
                return redirect(f"{url}?next={request.get_full_path()}")

            if not request.user.is_active or not request.user.is_backoffice_user:
                if redirect_url:
                    return redirect(redirect_url)
                return HttpResponseForbidden(
                    "Acceso denegado. Esta sección es para profesionales y empresas."
                )

            return view_func(request, *args, **kwargs)
        return _wrapped_view

    if function:
        return decorator(function)
    return decorator


def company_required(function=None, redirect_url=None, login_url=None):
    """
    Decorador que requiere que el usuario sea tipo empresa y esté autenticado.

    Uso:
        @company_required
        def nomina_view(request): ...
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                url = login_url or reverse('accounts_company:company_login')
                return redirect(f"{url}?next={request.get_full_path()}")

            if not request.user.is_active or not request.user.is_company:
                if redirect_url:
                    return redirect(redirect_url)
                return HttpResponseForbidden(
                    "Acceso denegado. Esta sección es solo para empresas."
                )

            return view_func(request, *args, **kwargs)
        return _wrapped_view

    if function:
        return decorator(function)
    return decorator


def subscription_required(tier='basic', redirect_url=None):
    """
    Decorador que requiere una suscripción activa de cierto nivel.
    Para uso futuro cuando se implemente el sistema de suscripciones.
    """
    tier_levels = {'free': 0, 'basic': 1, 'premium': 2}
    required_level = tier_levels.get(tier, 0)

    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('accounts_professional:professional_login')

            if not request.user.is_active or not request.user.is_professional:
                return HttpResponseForbidden("Solo para profesionales.")

            user_level = tier_levels.get(request.user.subscription_tier, 0)

            if not request.user.has_active_subscription or user_level < required_level:
                if redirect_url:
                    return redirect(redirect_url)
                return HttpResponseForbidden(
                    f"Esta función requiere suscripción {tier}."
                )

            return view_func(request, *args, **kwargs)
        return _wrapped_view

    return decorator
