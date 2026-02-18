# config/urls.py
# ============================================================================
# COMMIT 12: URLs reorganizadas + Landing pública ErgoSolutions
# ============================================================================

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    # =========================================================================
    # Admin
    # =========================================================================
    path("admin/", admin.site.urls),

    # =========================================================================
    # Dashboard de Profesionales (requiere login)
    # =========================================================================
    path("dashboard/", include("apps.dashboard.urls", namespace="dashboard")),

    # =========================================================================
    # Landing Principal (ErgoSolutions) - Home pública institucional
    # =========================================================================
    path("", include("apps.landing.urls", namespace="landing")),

    # =========================================================================
    # Área de Capacitaciones - TRABAJADORES (sistema actual)
    # =========================================================================
    path("acceso/", include("apps.accounts.urls")),  # Trainees: login/registro/confirm
    path("capacitacion/", include("apps.training.urls")),  # Páginas de capacitación
    path("quiz/", include("apps.quiz.urls")),  # Quiz
    path("certificados/", include("apps.certificates.urls")),  # Certificados
    path("ai/", include("apps.ergobot_ai.urls")),  # Chatbot

    # =========================================================================
    # Autenticación de Profesionales (Commit 13-14) - CON NAMESPACE
    # =========================================================================
    path(
        "auth/",
        include(
            ("apps.accounts.urls_professional", "accounts_professional"),
            namespace="accounts_professional",
        ),
    ),

    # =========================================================================
    # Área de Capacitaciones - ACCESO VÍA LINK (Commit 22-25)
    # =========================================================================
    path("c/", include("apps.training.urls_public")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
