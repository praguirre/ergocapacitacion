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
]
