# apps/dashboard/urls.py
# ============================================================================
# COMMIT 15: URLs del dashboard de profesionales
# ============================================================================

from django.urls import path

from . import views

app_name = "dashboard"

urlpatterns = [
    path("", views.home, name="home"),
    path("perfil/", views.profile, name="profile"),
]
