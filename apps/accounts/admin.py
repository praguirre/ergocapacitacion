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
        ("Datos", {"fields": ("full_name", "job_title", "company_name")}),
        ("Permisos", {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
        ("Fechas", {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = (
        (None, {"classes": ("wide",), "fields": ("cuil", "email", "password1", "password2")}),
    )
    search_fields = ("cuil", "email", "full_name", "company_name")
