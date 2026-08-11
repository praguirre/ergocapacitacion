"""Administración de sólo lectura para reportes y metadatos de adjuntos."""

from django.contrib import admin

from .models import FeedbackAttachment, FeedbackReport


class FeedbackAttachmentInline(admin.TabularInline):
    """Expone metadatos seguros sin enlaces al archivo privado."""

    model = FeedbackAttachment
    extra = 0
    can_delete = False
    fields = (
        "id",
        "original_name",
        "content_type",
        "size_bytes",
        "sha256",
        "created_at",
        "purged_at",
    )
    readonly_fields = fields

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(FeedbackReport)
class FeedbackReportAdmin(admin.ModelAdmin):
    """Consulta operativa del estado, sin edición ni acciones destructivas."""

    list_display = (
        "tracking_code",
        "category",
        "email_status",
        "email_attempts",
        "created_at",
    )
    list_filter = ("category", "email_status", "created_at")
    search_fields = ("=id",)
    date_hierarchy = "created_at"
    inlines = (FeedbackAttachmentInline,)
    actions = None

    def get_readonly_fields(self, request, obj=None):
        return tuple(field.name for field in self.model._meta.fields)

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(FeedbackAttachment)
class FeedbackAttachmentAdmin(admin.ModelAdmin):
    """Vista independiente de metadatos, siempre sin URL ni edición."""

    list_display = ("id", "report", "content_type", "size_bytes", "created_at", "purged_at")
    list_filter = ("content_type", "created_at", "purged_at")
    search_fields = ("=id", "=report__id", "sha256")
    actions = None

    def get_readonly_fields(self, request, obj=None):
        return tuple(field.name for field in self.model._meta.fields)

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
