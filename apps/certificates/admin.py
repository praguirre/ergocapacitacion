# apps/certificates/admin.py

from django.contrib import admin
from django.utils.html import format_html

from .models import Certificate


@admin.register(Certificate)
class CertificateAdmin(admin.ModelAdmin):
    """Admin para gestionar certificados emitidos."""
    
    list_display = (
        "id_short",
        "user_email",
        "module",
        "issued_at",
        "valid_until",
        "is_valid_display",
        "email_sent",
        "pdf_link",
    )
    list_filter = ("module", "email_sent", "issued_at")
    search_fields = ("user__email", "user__cuil", "user__first_name", "user__last_name")
    readonly_fields = ("id", "issued_at", "attempt")
    date_hierarchy = "issued_at"
    
    fieldsets = (
        ("Información del Certificado", {
            "fields": ("id", "user", "module", "attempt")
        }),
        ("Validez", {
            "fields": ("issued_at", "valid_until")
        }),
        ("Archivo PDF", {
            "fields": ("pdf_file",)
        }),
        ("Email", {
            "fields": ("email_sent", "email_sent_at", "email_error"),
            "classes": ("collapse",),
        }),
    )
    
    def id_short(self, obj):
        """Muestra solo los primeros 8 caracteres del UUID."""
        return str(obj.id)[:8]
    id_short.short_description = "ID"
    
    def user_email(self, obj):
        """Muestra el email del usuario."""
        return obj.user.email
    user_email.short_description = "Usuario"
    user_email.admin_order_field = "user__email"
    
    def is_valid_display(self, obj):
        """Muestra badge de estado de validez."""
        if obj.is_valid:
            return format_html('<span style="color: green;">✓ Vigente</span>')
        return format_html('<span style="color: red;">✗ Vencido</span>')
    is_valid_display.short_description = "Estado"
    
    def pdf_link(self, obj):
        """Link para descargar el PDF desde el admin."""
        if obj.pdf_file:
            return format_html(
                '<a href="{}" target="_blank">📄 Descargar</a>',
                obj.pdf_file.url
            )
        return "-"
    pdf_link.short_description = "PDF"
    
    def has_add_permission(self, request):
        """Los certificados se crean automáticamente al aprobar el quiz."""
        return False  # No permitir crear manualmente desde admin
    
    def has_delete_permission(self, request, obj=None):
        """Permitir eliminar solo a superusuarios."""
        return request.user.is_superuser