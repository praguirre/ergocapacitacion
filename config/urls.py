# config/urls.py

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),
    
    # Rutas de autenticación (CUIL/Email) en la raíz
    path("", include("apps.accounts.urls")),
    
    # Prefijo para toda la sección de capacitación
    path("capacitacion/", include("apps.training.urls")),
    
    # Prefijo para la API del chatbot
    path("ai/", include("apps.ergobot_ai.urls")),
    
    # Rutas del Quiz (Commit 5)
    path("quiz/", include("apps.quiz.urls")),
    
    # ✅ NUEVO (Commit 7): Rutas de Certificados
    path("certificados/", include("apps.certificates.urls")),
]

# Servir archivos media en desarrollo (NO usar en producción con Nginx/Apache)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)