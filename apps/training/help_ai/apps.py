from django.apps import AppConfig


class CapacitacionesHelpAiConfig(AppConfig):
    """Ayuda contextual del área de Capacitaciones.

    ⚠️ `label` explícito: Django deriva el label del último componente de
    `name`, y el paquete de ayuda del módulo 886 ya ocupa `help_ai`. Sin esta
    línea el registro de aplicaciones falla en el arranque y el proyecto no
    levanta.

    ⚠️ CF-1 bis: esta app NO se fusiona con la ayuda del módulo 886 ni con el
    asistente docente. Son tres productos distintos que comparten proveedor de
    modelo. Ver `checks.py` de este mismo paquete.

    ⚠️ Nomenclatura obligatoria en este paquete: ningún archivo `.py` de
    `apps/training/` —fuera de los de prueba— puede contener la ruta punteada
    completa del módulo 886. Una prueba preexistente del propio módulo 886
    (`evaluaciones/tests_sugerencias.py::test_apps_training_no_importa_el_modulo_886`)
    barre estos archivos como texto plano y falla ante esa cadena, aunque
    aparezca dentro de un comentario. Se nombra al módulo en prosa.
    """

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.training.help_ai"
    label = "capacitaciones_help_ai"
    verbose_name = "Capacitaciones · Ayuda contextual"

    def ready(self):
        # Registra el chequeo de aislamiento (CF-1 bis).
        from . import checks  # noqa: F401
