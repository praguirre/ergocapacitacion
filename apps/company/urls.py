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
    path('nomina/exportar/', views.nomina_export_csv, name='nomina_export_csv'),
    path('nomina/<int:worker_id>/', views.nomina_detail, name='nomina_detail'),
    path('nomina/<int:worker_id>/editar/', views.nomina_edit, name='nomina_edit'),
    # --- Agenda ---
    path('agenda/', views.agenda_list, name='agenda_list'),
    path('agenda/crear/', views.agenda_create, name='agenda_create'),
    path('agenda/<int:event_id>/editar/', views.agenda_edit, name='agenda_edit'),
    path('agenda/<int:event_id>/completar/', views.agenda_complete, name='agenda_complete'),
]
