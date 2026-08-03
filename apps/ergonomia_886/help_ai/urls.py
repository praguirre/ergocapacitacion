# help_ai/urls.py

from django.urls import path
from .views import chat_view, guide_view

app_name = "help_ai"

# El nombre 'chat_ai' nos permitirá referenciar esta URL desde otras partes de Django
# de forma segura, por ejemplo, usando {% url 'chat_ai' slug='mi-slug' %}.
urlpatterns = [
    path("guide/<slug:slug>/", guide_view, name="help_guide"),
    path("chat/<slug:slug>/", chat_view, name="chat_ai"),
]
