# apps/presencial/urls.py
# ============================================================================
# COMMIT 18: URLs de capacitación presencial
# ============================================================================

from django.urls import path

from . import views

app_name = 'presencial'

urlpatterns = [
    path('<slug:module_slug>/', views.capacitacion_presencial, name='capacitacion'),
]
