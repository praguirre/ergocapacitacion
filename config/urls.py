# config/urls.py
# ============================================================================
# COMMIT 11: URLs reorganizadas para ErgoSolutions
# ============================================================================

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # =========================================================================
    # Admin
    # =========================================================================
    path('admin/', admin.site.urls),
    
    # =========================================================================
    # Landing Principal (ErgoSolutions)
    # =========================================================================
    # path('', include('apps.landing.urls')),  # Descomentar en Commit 12
    
    # =========================================================================
    # Autenticación de Profesionales
    # =========================================================================
    # path('auth/', include('apps.accounts.urls_professional')),  # Commit 13-14
    
    # =========================================================================
    # Dashboard de Profesionales (requiere login)
    # =========================================================================
    path('dashboard/', include('apps.dashboard.urls', namespace='dashboard')),
    
    # =========================================================================
    # Área de Capacitaciones - TRABAJADORES (sistema actual)
    # La raíz '/' va al landing de capacitaciones (registro/login trainees)
    # =========================================================================
    path('', include('apps.accounts.urls')),  # Landing actual de trainees
    path('capacitacion/', include('apps.training.urls')),  # Páginas de capacitación
    path('quiz/', include('apps.quiz.urls')),  # Quiz
    path('certificados/', include('apps.certificates.urls')),  # Certificados
    path('ai/', include('apps.ergobot_ai.urls')),  # Chatbot
    
    # =========================================================================
    # Área de Capacitaciones - ACCESO VÍA LINK (Commit 22-25)
    # URL corta para links compartibles: /c/<slug>/
    # =========================================================================
    # path('c/', include('apps.training.urls_public')),  # Commit 25
    
    # =========================================================================
    # Gestión de Capacitaciones - PROFESIONALES (Commit 16-21)
    # =========================================================================
    # path('capacitaciones/', include('apps.dashboard.urls_capacitaciones')),
    
    # =========================================================================
    # Evaluaciones - PROFESIONALES (Futuro)
    # =========================================================================
    # path('evaluaciones/', include('apps.evaluaciones.urls')),
]

# Servir archivos de media en desarrollo
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
