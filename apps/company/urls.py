# apps/company/urls.py
# ============================================================================
# COMMIT 36: URLs de empresa (nómina)
# ============================================================================

from django.urls import path
from . import views

app_name = 'company'

urlpatterns = [
    # --- Nómina ---
    path('nomina/', views.nomina_list, name='nomina_list'),
    path('nomina/agregar/', views.nomina_add_worker, name='nomina_add_worker'),
    path('nomina/<int:worker_id>/', views.nomina_detail, name='nomina_detail'),
]
