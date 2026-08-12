# apps/training/help_ai/urls.py

from django.urls import path

from .views import chat_view, guide_view

app_name = "capacitaciones_help"

# Se monta desde apps/dashboard/urls.py bajo `capacitaciones/ayuda/`, de modo
# que el namespace completo queda `dashboard:capacitaciones_help:…`.
#
# Las variantes con `<modulo>` permiten que la pantalla informe qué módulo de
# capacitación está abierto SIN usar la query string, que el contrato del chat
# prohíbe. La plantilla arma el template de URL ya con el módulo incrustado; el
# JavaScript no necesita saber nada de esto.
urlpatterns = [
    path("guide/<slug:slug>/", guide_view, name="help_guide"),
    path("guide/<slug:slug>/<slug:modulo>/", guide_view, name="help_guide_modulo"),
    path("chat/<slug:slug>/", chat_view, name="chat_ai"),
    path("chat/<slug:slug>/<slug:modulo>/", chat_view, name="chat_ai_modulo"),
]
