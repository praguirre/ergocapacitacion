# apps/accounts/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # Ruta principal (Landing)
    path("", views.landing, name="landing"),

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