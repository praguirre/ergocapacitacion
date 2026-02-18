from django.urls import path

from . import views_public

urlpatterns = [
    path("<slug:module_slug>/", views_public.public_landing, name="training_public"),
]
