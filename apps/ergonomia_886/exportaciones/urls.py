from django.urls import path

from . import views

app_name = "exportaciones"

urlpatterns = [
    path(
        "<int:evaluacion_id>/",
        views.PanelExportacionView.as_view(),
        name="panel",
    ),
    path(
        "<int:evaluacion_id>/oficial/protocolo-completo.pdf",
        views.ProtocoloCompletoPDFView.as_view(),
        name="protocolo_completo",
    ),
    path(
        "<int:evaluacion_id>/oficial/<slug:planilla_slug>.pdf",
        views.PlanillaOficialPDFView.as_view(),
        name="planilla_oficial",
    ),
    path(
        "<int:evaluacion_id>/detalle/todos.pdf",
        views.FactoresDetalleTodosPDFView.as_view(),
        name="factores_detalle_todos",
    ),
    path(
        "<int:evaluacion_id>/detalle/<slug:factor_slug>.pdf",
        views.FactorDetallePDFView.as_view(),
        name="factor_detalle",
    ),
    path(
        "<int:evaluacion_id>/informe/<slug:factor_slug>/",
        views.InformeFactorView.as_view(),
        name="informe_factor",
    ),
    path(
        "<int:evaluacion_id>/paquete.zip",
        views.PaqueteZipView.as_view(),
        name="paquete_zip",
    ),
    path(
        "<int:evaluacion_id>/evidencia/vce/<int:vce_id>/<slug:tipo>/",
        views.EvidenciaVCEView.as_view(),
        name="evidencia_vce",
    ),
]
