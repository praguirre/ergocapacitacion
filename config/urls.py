from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    # Incluimos las rutas de accounts en la raíz, pero accounts define su propio prefijo /health/
    path("", include("apps.accounts.urls")),
]