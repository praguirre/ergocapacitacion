# apps/training/urls.py

from django.urls import path
from . import views

app_name = "training"

urlpatterns = [
    # Esta ruta se convertirá en /capacitacion/ debido al prefijo global
    path("", views.training_home, name="training_home"),
]
