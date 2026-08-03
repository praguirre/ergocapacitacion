from django.contrib import admin

from .models import ExportAudit, GeneratedReport


@admin.register(ExportAudit)
class ExportAuditAdmin(admin.ModelAdmin):
    list_display = ("creado_en", "evaluacion", "usuario", "tipo",
                    "detalle", "bytes_entregados")
    list_filter = ("tipo", "creado_en")
    search_fields = ("evaluacion__razon_social", "detalle")
    date_hierarchy = "creado_en"
    readonly_fields = [campo.name for campo in ExportAudit._meta.fields]

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False


@admin.register(GeneratedReport)
class GeneratedReportAdmin(admin.ModelAdmin):
    list_display = ("creado_en", "evaluacion", "factor_slug", "tipo", "estado",
                    "modelo_llm", "prompt_version", "duracion_ms")
    list_filter = ("estado", "tipo", "modelo_llm", "prompt_version")
    search_fields = ("evaluacion__razon_social", "factor_slug", "inputs_hash")
    date_hierarchy = "creado_en"
    # El contenido del informe y el payload no se editan desde el admin:
    # son evidencia de lo que se generó y con qué datos.
    readonly_fields = ("payload_json", "contenido_markdown", "inputs_hash",
                       "modelo_llm", "prompt_version", "duracion_ms",
                       "tokens_prompt", "tokens_respuesta", "creado_en",
                       "actualizado_en")

    def has_add_permission(self, request):
        return False
