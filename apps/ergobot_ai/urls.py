# apps/ergobot_ai/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # Esta ruta coincide con el fetch que hará el JavaScript
    path("ergobot/<slug:module_slug>/stream/", views.ergobot_stream, name="ergobot_stream"),
]