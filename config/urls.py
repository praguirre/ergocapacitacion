# config/urls.py
# ============================================================================
# COMMIT 12: URLs reorganizadas + Landing pública ErgoSolutions
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
    # Dashboard de Profesionales (requiere login)
    # =========================================================================
    path('dashboard/', include('apps.dashboard.urls', namespace='dashboard')),

    # =========================================================================
    # Landing Principal (ErgoSolutions) - Home pública institucional
    # La raíz '/' muestra la landing de ErgoSolutions.
    # Usuarios autenticados son redirigidos a su área correspondiente.
    # =========================================================================
    path('', include('apps.landing.urls', namespace='landing')),

    # =========================================================================
    # Área de Capacitaciones - TRABAJADORES (sistema actual)
    # Prefijo /acceso/ para registro/login de trainees (antes estaba en raíz)
    # =========================================================================
    path('acceso/', include('apps.accounts.urls')),  # Trainees: login/registro/confirm
    path('capacitacion/', include('apps.training.urls')),  # Páginas de capacitación
    path('quiz/', include('apps.quiz.urls')),  # Quiz
    path('certificados/', include('apps.certificates.urls')),  # Certificados
    path('ai/', include('apps.ergobot_ai.urls')),  # Chatbot

    # =========================================================================
    # Autenticación de Profesionales (Commit 13-14)
    # =========================================================================
    # path('auth/', include('apps.accounts.urls_professional')),

    # =========================================================================
    # Área de Capacitaciones - ACCESO VÍA LINK (Commit 22-25)
    # URL corta para links compartibles: /c/<slug>/
    # =========================================================================
    # path('c/', include('apps.training.urls_public')),

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
