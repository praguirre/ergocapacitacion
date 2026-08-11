"""Rutas namespaced del formulario profesional de feedback."""

from django.urls import path

from . import views


app_name = "feedback"

urlpatterns = [
    path("", views.create_feedback, name="create"),
]
