from django.apps import AppConfig


class PlanillasConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.ergonomia_886.planillas'
    # `label` se omite deliberadamente: Django lo deriva como "planillas",
    # que no colisiona con ninguna app del destino. Declararlo cambiaria el
    # app_label y obligaria a reescribir las migraciones.
    verbose_name = "Ergonomía 886 · Protocolo documental"
