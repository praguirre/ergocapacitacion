# apps/accounts/admin.py
# ============================================================================
# COMMIT 8: Agregados campos employer_email y safety_responsible_email
# ============================================================================
from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

User = get_user_model()

@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    model = User
    list_display = ("cuil", "email", "full_name", "company_name", "is_staff", "is_active")
    ordering = ("cuil",)
    fieldsets = (
        (None, {"fields": ("cuil", "email", "password")}),
        ("Datos personales", {"fields": ("full_name", "job_title", "company_name")}),
        # =====================================================================
        # ✅ COMMIT 8: Nueva sección para emails de notificación de certificados
        # =====================================================================
        ("Emails para notificación de certificados", {
            "fields": ("employer_email", "safety_responsible_email"),
            "description": "Estos emails recibirán copia del certificado cuando el usuario apruebe."
        }),
        # =====================================================================
        ("Permisos", {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
        ("Fechas", {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = (
        (None, {"classes": ("wide",), "fields": ("cuil", "email", "password1", "password2")}),
    )
    search_fields = ("cuil", "email", "full_name", "company_name")
    # =========================================================================
    # ✅ COMMIT 8: Agregar filtros para los nuevos campos
    # =========================================================================
    list_filter = ("is_staff", "is_active", "is_superuser")
    # =========================================================================
