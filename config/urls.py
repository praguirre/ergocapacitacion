# config/urls.py

from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    
    # Rutas de autenticación (CUIL/Email) en la raíz
    path("", include("apps.accounts.urls")),
    
    # NUEVA: Prefijo para toda la sección de capacitación
    path("capacitacion/", include("apps.training.urls")),
]