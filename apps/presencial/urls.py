# apps/presencial/urls.py
# ============================================================================
# COMMIT 18-21: URLs de capacitación presencial completas
# ============================================================================

from django.urls import path

from . import views

app_name = 'presencial'

urlpatterns = [
    path('historial/', views.historial_presencial, name='historial'),
    path('<slug:module_slug>/', views.capacitacion_presencial, name='capacitacion'),
    path('<slug:module_slug>/quiz/', views.quiz_presencial, name='quiz'),
    path('<slug:module_slug>/quiz/submit/', views.quiz_presencial_submit, name='quiz_submit'),
    path('<slug:module_slug>/planilla/', views.planilla_pdf, name='planilla_pdf'),
]
