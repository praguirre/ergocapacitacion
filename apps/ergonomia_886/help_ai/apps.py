from django.apps import AppConfig


class HelpAiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.ergonomia_886.help_ai'
    verbose_name = "Ergonomía 886 · Ayuda contextual"
    # CF-1: esta app NO se fusiona con apps.ergobot_ai. Son productos
    # distintos que comparten proveedor de modelo.
