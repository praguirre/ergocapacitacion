# apps/dashboard/urls.py
# ============================================================================
# COMMIT 15-24: URLs del dashboard de profesionales
# ============================================================================

from django.urls import include, path

from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.home, name='home'),
    path('capacitaciones/', views.capacitaciones_menu, name='capacitaciones_menu'),
    path('capacitaciones/<slug:module_slug>/', views.modalidad_selector, name='modalidad_selector'),
    path('capacitaciones/<slug:module_slug>/links/', views.online_links, name='online_links'),
    path('capacitaciones/<slug:module_slug>/links/generar/', views.generate_link, name='generate_link'),
    path('capacitaciones/<slug:module_slug>/links/<uuid:link_id>/compartir/', views.share_link, name='share_link'),
    path('presencial/', include('apps.presencial.urls')),
    path('perfil/', views.profile, name='profile'),
]
