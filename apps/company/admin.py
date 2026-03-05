# apps/company/admin.py
# ============================================================================
# COMMIT 30: Admin para CompanyProfile
# ============================================================================

from django.contrib import admin
from .models import CompanyProfile


@admin.register(CompanyProfile)
class CompanyProfileAdmin(admin.ModelAdmin):
    list_display = (
        'razon_social',
        'nombre_comercial',
        'cuit',
        'contacto_nombre',
        'account_status',
        'cantidad_trabajadores',
        'created_at',
    )
    list_filter = ('account_status', 'provincia')
    search_fields = ('razon_social', 'nombre_comercial', 'cuit', 'contacto_nombre')
    readonly_fields = ('created_at', 'updated_at')

    fieldsets = (
        ('Datos de la Empresa', {
            'fields': (
                'user',
                'razon_social',
                'nombre_comercial',
                'cuit',
                'rubro',
                'cantidad_trabajadores',
            ),
        }),
        ('Contacto Principal', {
            'fields': (
                'contacto_nombre',
                'contacto_cargo',
                'contacto_telefono',
            ),
        }),
        ('Ubicación', {
            'fields': (
                'domicilio',
                'localidad',
                'provincia',
            ),
        }),
        ('Estado', {
            'fields': ('account_status', 'logo'),
        }),
        ('Metadatos', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )
