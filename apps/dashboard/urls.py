# apps/dashboard/urls.py
# ============================================================================
# COMMIT 15-17: URLs del dashboard de profesionales
# ============================================================================

from django.urls import path

from . import views

app_name = "dashboard"

urlpatterns = [
    path("", views.home, name="home"),
    path("capacitaciones/", views.capacitaciones_menu, name="capacitaciones_menu"),
    path("capacitaciones/<slug:module_slug>/", views.modalidad_selector, name="modalidad_selector"),
    path("perfil/", views.profile, name="profile"),
]
