# apps/training/admin.py
# ============================================================================
# COMMIT 16: Admin actualizado con campos de menu visual
# ============================================================================

from django.contrib import admin
from django.contrib.auth import get_user_model
from django.utils.html import format_html

from .models import CapacitacionLink, LinkShareLog, TrainingModule

User = get_user_model()


@admin.register(TrainingModule)
class TrainingModuleAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "slug",
        "training_type",
        "company_name_custom",
        "assigned_count",
        "icon",
        "order",
        "is_active",
        "updated_at",
    )
    list_filter = ("is_personalized", "is_active")
    list_editable = ("order", "is_active")
    search_fields = ("title", "slug", "youtube_id", "company_name_custom")
    prepopulated_fields = {"slug": ("title",)}
    filter_horizontal = ("assigned_professionals",)

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
            "Personalización",
            {
                "fields": (
                    "is_personalized",
                    "requested_by",
                    "assigned_professionals",
                    "company_name_custom",
                    "custom_notes",
                ),
                "description": (
                    "Si el módulo es personalizado, solo los profesionales asignados "
                    "podrán verlo y acceder a sus links."
                ),
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

    def training_type(self, obj):
        if obj.is_personalized:
            return format_html('<span style="color: #17a2b8;">Personalizada</span>')
        return format_html('<span style="color: #28a745;">General</span>')
    training_type.short_description = "Tipo"
    training_type.admin_order_field = "is_personalized"

    def assigned_count(self, obj):
        if not obj.is_personalized:
            return "-"
        return obj.assigned_professionals.count()
    assigned_count.short_description = "Asignados"

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.prefetch_related("assigned_professionals")

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "requested_by":
            kwargs["queryset"] = User.objects.filter(
                user_type=User.UserType.PROFESSIONAL
            )
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if db_field.name == "assigned_professionals":
            kwargs["queryset"] = User.objects.filter(
                user_type=User.UserType.PROFESSIONAL
            )
        return super().formfield_for_manytomany(db_field, request, **kwargs)


@admin.register(CapacitacionLink)
class CapacitacionLinkAdmin(admin.ModelAdmin):
    list_display = ("module", "label", "created_by", "created_at", "is_active", "access_count")
    list_filter = ("module", "is_active", "created_at")
    search_fields = ("label", "created_by__email")
    readonly_fields = ("id", "created_at", "access_count")


@admin.register(LinkShareLog)
class LinkShareLogAdmin(admin.ModelAdmin):
    list_display = ("link", "shared_to_email", "shared_at")
    list_filter = ("shared_at",)
    search_fields = ("shared_to_email", "link__module__title", "link__created_by__email")
    readonly_fields = ("link", "shared_to_email", "shared_at")
