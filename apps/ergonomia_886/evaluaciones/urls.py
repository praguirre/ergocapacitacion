from django.urls import path

from . import views
from .catalog import FACTOR_DEFINITIONS


app_name = "evaluaciones"

urlpatterns = []

# Las dos variantes de cada ruta se materializan desde el catálogo: una
# histórica sin evaluación y la operativa ligada a una RiskEvaluation.
for definition in FACTOR_DEFINITIONS:
    view = getattr(views, definition.view_class).as_view()
    urlpatterns.extend(
        [
            path(
                definition.route,
                view,
                name=definition.route_name,
            ),
            path(
                f"<int:evaluacion_id>/{definition.route}",
                view,
                name=definition.route_name_by_eval,
            ),
        ]
    )

urlpatterns.extend(
    [
        path(
            "resumen/",
            views.WizardResumenView.as_view(),
            name="wizard_resumen",
        ),
        path(
            "<int:evaluacion_id>/resumen/",
            views.WizardResumenView.as_view(),
            name="wizard_resumen_by_eval",
        ),
        path(
            "start/<int:plan_eval_id>/<slug:factor>/",
            views.StartFactorRedirectView.as_view(),
            name="start_factor",
        ),
    ]
)
