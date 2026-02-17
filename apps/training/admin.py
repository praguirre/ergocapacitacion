# apps/training/admin.py
# ============================================================================
# COMMIT 16: Admin actualizado con campos de menu visual
# ============================================================================

from django.contrib import admin

from .models import CapacitacionLink, TrainingModule


@admin.register(TrainingModule)
class TrainingModuleAdmin(admin.ModelAdmin):
    list_display = ("title", "slug", "icon", "order", "is_active", "updated_at")
    list_filter = ("is_active",)
    list_editable = ("order", "is_active")
    search_fields = ("title", "slug", "youtube_id")
    prepopulated_fields = {"slug": ("title",)}

    fieldsets = (
        (
            "Información básica",
            {
                "fields": ("title", "slug", "description", "youtube_id", "is_active"),
            },
        ),
        (
            "Apariencia en menú",
            {
                "fields": ("icon", "color", "order"),
                "description": "Configuración visual para el menú de capacitaciones",
            },
        ),
        (
            "Contenido",
            {
                "fields": ("intro_md", "material_md", "transcript_md"),
                "classes": ("collapse",),
            },
        ),
    )


@admin.register(CapacitacionLink)
class CapacitacionLinkAdmin(admin.ModelAdmin):
    list_display = ("module", "label", "created_by", "created_at", "is_active", "access_count")
    list_filter = ("module", "is_active", "created_at")
    search_fields = ("label", "created_by__email")
    readonly_fields = ("id", "created_at", "access_count")
