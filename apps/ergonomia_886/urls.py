# apps/ergonomia_886/urls.py
"""URLs del módulo de Evaluación Ergonómica SRT 886/15.

Se montan bajo el prefijo `/evaluacion-ergonomica/` desde `config/urls.py`.

⚠️ Este URLconf NO declara `app_name`. Los namespaces de las sub-apps quedan
   planos: `planillas:`, `evaluaciones:`, `exportaciones:`, `help_ai:`.

   Es una decisión deliberada. Anidar (`ergonomia_886:planillas:planilla1`)
   obligaría a reescribir 31 referencias adicionales que hoy ya funcionan con
   namespace propio, multiplicando el trabajo mecánico —que es justamente
   donde está el riesgo de esta integración— sin beneficio proporcional.
   El agrupamiento físico bajo apps/ergonomia_886/ ya da identidad al módulo.

⚠️ CF-1: `help_ai` se monta acá y no bajo `/ai/`, que pertenece al chatbot
   docente `apps.ergobot_ai`. Son dos productos distintos en dos lugares
   distintos.
"""

from django.urls import include, path

from .planillas import views as planillas_views


root_urlpatterns = [
    path("", planillas_views.evaluacion_list_view, name="evaluacion_list"),
    path(
        "<int:evaluacion_id>/eliminar/",
        planillas_views.eliminar_evaluacion_view,
        name="eliminar_evaluacion",
    ),
]


urlpatterns = [
    # Aterrizaje del módulo: listado de evaluaciones ergonómicas del usuario.
    # Reimplanta core.dashboard_view con su búsqueda, filtros y paginación.
    # Se implementa en el commit 3.6; hasta entonces la ruta no existe.
    # El namespace sólo envuelve las rutas raíz. Los namespaces de las cuatro
    # sub-apps permanecen planos por la decisión de integración 2.9.
    path(
        "",
        include(
            (root_urlpatterns, "ergonomia_886"),
            namespace="ergonomia_886",
        ),
    ),

    path("protocolo/", include("apps.ergonomia_886.planillas.urls")),
    path("factores/", include("apps.ergonomia_886.evaluaciones.urls")),
    path("documentos/", include("apps.ergonomia_886.exportaciones.urls")),
    path("ayuda/", include("apps.ergonomia_886.help_ai.urls")),
]
