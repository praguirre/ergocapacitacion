# apps/accounts/admin.py
# ============================================================================
# COMMIT 9: Admin actualizado para CustomUser
# ============================================================================

from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

User = get_user_model()


@admin.register(User)
class CustomUserAdmin(DjangoUserAdmin):
    """Admin personalizado para CustomUser con soporte dual."""
    
    model = User
    
    # Columnas en la lista
    list_display = (
        "email", 
        "user_type",
        "display_name_admin",
        "company_name", 
        "is_staff", 
        "is_active",
        "date_joined",
    )
    
    # Filtros laterales
    list_filter = (
        "user_type",
        "is_staff", 
        "is_active", 
        "is_superuser",
        "subscription_tier",
        "subscription_status",
    )
    
    # Búsqueda
    search_fields = (
        "email", 
        "username",
        "cuil", 
        "full_name",
        "first_name",
        "last_name",
        "company_name",
        "dni",
    )
    
    ordering = ("-date_joined",)
    
    # Campos en el formulario de edición
    fieldsets = (
        ("Acceso", {
            "fields": ("email", "username", "password", "user_type")
        }),
        ("Datos Personales", {
            "fields": ("first_name", "last_name", "full_name")
        }),
        ("Datos de Profesional", {
            "fields": ("dni", "profession", "license_number"),
            "classes": ("collapse",),
            "description": "Solo para usuarios tipo Profesional"
        }),
        ("Datos de Trabajador", {
            "fields": ("cuil", "job_title", "company_name"),
            "classes": ("collapse",),
            "description": "Solo para usuarios tipo Trabajador"
        }),
        ("Emails de Notificación (Trabajadores)", {
            "fields": ("employer_email", "safety_responsible_email"),
            "classes": ("collapse",),
        }),
        ("Suscripción (Futuro)", {
            "fields": ("subscription_tier", "subscription_status", "subscription_expires"),
            "classes": ("collapse",),
        }),
        ("Permisos", {
            "fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions"),
            "classes": ("collapse",),
        }),
        ("Fechas", {
            "fields": ("last_login", "date_joined"),
            "classes": ("collapse",),
        }),
    )
    
    # Campos en el formulario de creación
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": (
                "email", 
                "user_type",
                "username",
                "password1", 
                "password2",
                "first_name",
                "last_name",
            ),
        }),
    )
    
    def display_name_admin(self, obj):
        """Nombre para mostrar en el admin."""
        return obj.display_name
    display_name_admin.short_description = "Nombre"
    display_name_admin.admin_order_field = "full_name"

