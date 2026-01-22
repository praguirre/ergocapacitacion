# apps/training/admin.py

from django.contrib import admin
from .models import TrainingModule

@admin.register(TrainingModule)
class TrainingModuleAdmin(admin.ModelAdmin):
    # Columnas que se verán en la lista principal
    list_display = ("title", "slug", "is_active", "updated_at")
    
    # Filtro lateral para separar activos de borradores
    list_filter = ("is_active",)
    
    # Buscador por texto
    search_fields = ("title", "slug", "youtube_id")
    
    # Generación automática del slug mientras escribes el título
    prepopulated_fields = {"slug": ("title",)}
    
     
