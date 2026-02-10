# apps/accounts/urls_professional.py
# ============================================================================
# COMMIT 13-14: URLs de autenticación para profesionales
# ============================================================================

from django.urls import path

from . import views_professional

app_name = "accounts_professional"

urlpatterns = [
    path("registro/", views_professional.register, name="professional_register"),
    path("login/", views_professional.login_view, name="professional_login"),
    path("logout/", views_professional.logout_view, name="professional_logout"),
]
