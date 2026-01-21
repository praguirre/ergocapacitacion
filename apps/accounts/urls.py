from django.urls import path
from . import views

urlpatterns = [
    # Se usa "health/" para no ocupar la raíz del sitio
    path("health/", views.health, name="health"),
]