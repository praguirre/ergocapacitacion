# apps/quiz/urls.py

from django.urls import path
from . import views

urlpatterns = [
    # Pantalla inicial "Comenzar Quiz" (instrucciones y botón Start)
    path("<slug:module_slug>/start/", views.start, name="quiz_start"),
    
    # Obtener pregunta individual (AJAX o carga normal)
    path("<slug:module_slug>/question/<int:order>/", views.question, name="quiz_question"),
    
    # Enviar respuesta individual (AJAX) - retorna feedback inmediato
    path("<slug:module_slug>/answer/", views.answer, name="quiz_answer"),
    
    # Finalizar intento y calcular nota
    path("<slug:module_slug>/submit/", views.submit, name="quiz_submit"),
    
    # Pantalla de resultados (Aprobado/Reprobado)
    path("<slug:module_slug>/result/<int:attempt_id>/", views.result_page, name="quiz_result"),
    
    # Acción para reiniciar el examen (si las reglas lo permiten)
    path("<slug:module_slug>/retake/", views.retake, name="quiz_retake"),
]