# apps/accounts/urls.py
# ============================================================================
# COMMIT 12: Renombrado 'landing' → 'trainee_landing' para evitar
# colisión con el namespace 'landing' de la app landing institucional.
# ============================================================================

from django.urls import path

from . import views

urlpatterns = [
    # Ruta principal - Formulario de registro/login para trainees
    path("", views.landing, name="trainee_landing"),

    # Rutas de procesamiento (POST)
    path("register/", views.register_post, name="register_post"),
    path("login/", views.login_post, name="login_post"),
    path("logout/", views.logout_post, name="logout_post"),

    # Rutas de confirmación
    path("confirm/", views.confirm_get, name="confirm"),
    path("confirm/post/", views.confirm_post, name="confirm_post"),

    # Health check
    path("health/", views.health, name="health"),
]