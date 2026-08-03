# planillas/urls.py
from django.urls import path
from . import views

app_name = "planillas"

urlpatterns = [
    # URL para crear una nueva evaluación (Ej: /planillas/crear/)
    path('crear/', views.crear_evaluacion_view, name='crear_evaluacion'),

    # URL para ver el detalle de una evaluación (Ej: /planillas/1/)
    path('<int:evaluacion_id>/', views.detalle_evaluacion_view, name='detalle_evaluacion'),

    # URLs para cada una de las planillas
    path('<int:evaluacion_id>/planilla1/', views.planilla1_view, name='planilla1'),
    path('<int:evaluacion_id>/planilla2a/', views.planilla2a_view, name='planilla2a'),
    path('<int:evaluacion_id>/planilla2b/', views.planilla2b_view, name='planilla2b'),
    path('<int:evaluacion_id>/planilla2c/', views.planilla2c_view, name='planilla2c'),
    path('<int:evaluacion_id>/planilla2d/', views.planilla2d_view, name='planilla2d'),
    path('<int:evaluacion_id>/planilla2e/', views.planilla2e_view, name='planilla2e'),
    path('<int:evaluacion_id>/planilla2f/', views.planilla2f_view, name='planilla2f'),
    path('<int:evaluacion_id>/planilla2g/', views.planilla2g_view, name='planilla2g'),
    path('<int:evaluacion_id>/planilla2h/', views.planilla2h_view, name='planilla2h'),
    path('<int:evaluacion_id>/planilla2i/', views.planilla2i_view, name='planilla2i'),
    
    # --- INICIO: NUEVAS RUTAS PARA PLANILLA 3 Y 4 ---
    path('<int:evaluacion_id>/planilla3/', views.Planilla3UpdateView.as_view(), name='planilla3'),
    path('<int:evaluacion_id>/planilla4/', views.Planilla4UpdateView.as_view(), name='planilla4'),
    # --- FIN: NUEVAS RUTAS ---
]
