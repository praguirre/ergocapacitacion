# config/settings.py
from pathlib import Path
import os
import environ
from django.core.exceptions import ImproperlyConfigured

BASE_DIR = Path(__file__).resolve().parent.parent

# Environ
env = environ.Env(DEBUG=(bool, False))
environ.Env.read_env(os.path.join(BASE_DIR, ".env"))

SECRET_KEY = env("SECRET_KEY")
DEBUG = env.bool("DEBUG", default=False)

ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=["127.0.0.1", "localhost"])

# nginx termina TLS y reemplaza X-Forwarded-Proto con el esquema real antes de
# enviar la request por el socket Unix. Django debe confiar explícitamente en
# esa cabecera: Gunicorn WSGI lo infería por defecto, pero Uvicorn no puede
# identificar el par de un socket Unix y dejaba request.is_secure() en False.
# El resultado era un 403 CSRF en todos los POST HTTPS bajo ASGI.
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
CSRF_TRUSTED_ORIGINS = [
    "https://ergosolutions.com.ar",
    "https://www.ergosolutions.com.ar",
]

# Para tests (django.test.Client usa host "testserver")
if DEBUG and "testserver" not in ALLOWED_HOSTS:
    ALLOWED_HOSTS.append("testserver")

# Apps
DJANGO_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]

THIRD_PARTY_APPS = [
    "django_bootstrap5",
    # opcional: evita que Django sirva static y lo haga WhiteNoise en runserver
    # "whitenoise.runserver_nostatic",
]

LOCAL_APPS = [
    "apps.accounts",
    'apps.landing',      # NUEVO
    'apps.dashboard',    # NUEVO
    "apps.presencial",   # NUEVO - Commit 18
    "apps.company",      # NUEVO - Etapa 3, Commit 30
    "apps.training",
    "apps.quiz",
    "apps.certificates",
    "apps.ergobot_ai",              # Chatbot docente. CF-1: NO se fusiona con help_ai

    # ========================================================================
    # Módulo de Ergonomía SRT 886/15
    # ========================================================================
    # `planillas` va primero: contiene el modelo raíz `Evaluacion`, del que
    # dependen las claves foráneas de las otras dos apps con modelos.
    "apps.ergonomia_886.planillas",
    "apps.ergonomia_886.evaluaciones",
    "apps.ergonomia_886.exportaciones",
    "apps.ergonomia_886.help_ai",   # Ayuda del protocolo. CF-1: NO se fusiona con ergobot_ai
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

# CSP bloqueante tras completar el recorrido Report-Only de la Fase 6.
# Puede volver temporalmente a observación mediante la variable de entorno.
CSP_REPORT_ONLY = env.bool("CSP_REPORT_ONLY", default=False)

# WhiteNoise 6.11 no declara `async_capable`, de modo que Django lo trata
# como sync-only (core/handlers/base.py usa getattr con default False) y,
# bajo ASGI, adapta con async_to_sync toda la cadena que tiene por debajo,
# incluida la vista SSE del Chat IA. En produccion nginx ya sirve /static/
# desde STATIC_ROOT, asi que el middleware no hace falta. En desarrollo queda
# activo por default con DEBUG=True; un runserver con DEBUG=False debe definir
# SERVE_STATIC_WITH_WHITENOISE=True de forma explícita.
#
# Esto NO desactiva el manifiesto con hash: eso lo aporta STORAGES, que queda
# intacto y es lo que resuelve {% static %}.
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "config.middleware.ContentSecurityPolicyMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

if env.bool("SERVE_STATIC_WITH_WHITENOISE", default=DEBUG):
    MIDDLEWARE.insert(1, "whitenoise.middleware.WhiteNoiseMiddleware")

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "apps.company.context_processors.company_context",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"

DATABASES = {
    "default": env.db("DATABASE_URL")
}

# =====================================================
# CACHÉ COMPARTIDA ENTRE PROCESOS
# =====================================================
# Imprescindible para que las cuotas del módulo de Ergonomía 886 (chat de
# ayuda, informes profesionales y descargas de documentos) sean globales y
# no por worker. Con LocMemCache cada proceso tendría su propio contador y
# las cuotas se multiplicarían por la cantidad de workers, sin ningún
# síntoma visible.
#
# ⚠️ PASO DE DESPLIEGUE OBLIGATORIO: la tabla NO se crea por migración.
#     python manage.py createcachetable
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.db.DatabaseCache",
        "LOCATION": "ergosolutions_cache",
        "TIMEOUT": 300,
        "OPTIONS": {"MAX_ENTRIES": 5000},
    }
}

# CRÍTICO (antes del primer migrate)
AUTH_USER_MODEL = "accounts.CustomUser"

# ============================================================================
# Authentication Backends (COMMIT 10)
# ============================================================================
AUTHENTICATION_BACKENDS = [
    # Backend para profesionales (email/username + password, SOLO professional)
    "apps.accounts.backends.ProfessionalBackend",
    # Backend para trabajadores (CUIL + email, sin password, SOLO trainee)
    "apps.accounts.backends.CuilEmailBackend",
    # Fallback Django (admin/superuser/compatibilidad)
    "django.contrib.auth.backends.ModelBackend",
]

# URLs de login por defecto (trainees)
LOGIN_URL = "accounts:trainee_landing"
LOGIN_REDIRECT_URL = "training:training_home"

# URLs de login profesionales (para usar en decoradores/mixins/vistas).
# Deben ser nombres calificados: los planos no resuelven porque los includes
# de accounts declaran namespace.
PROFESSIONAL_LOGIN_URL = "accounts_professional:professional_login"
PROFESSIONAL_LOGIN_REDIRECT_URL = "dashboard:home"

# Password validators (los defaults; no molestan en commit 1)
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# i18n / tz (obligatorio para que no falten settings base)
LANGUAGE_CODE = "es-ar"
TIME_ZONE = "America/Argentina/Buenos_Aires"
USE_I18N = True
USE_TZ = True

# =====================================================
# STATIC FILES
# =====================================================
STATIC_URL = "static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"

STORAGES = {
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage"
    },
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
}

# =====================================================
# ✅ COMMIT 7: MEDIA FILES (para certificados PDF)
# =====================================================
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# Evidencia sensible del módulo SRT 886/15. Vive fuera de MEDIA_ROOT para que
# ni Django en DEBUG ni el servidor web puedan entregarla por /media/.
PRIVATE_ERGONOMIA_886_ROOT = BASE_DIR / "private_media" / "ergonomia_886"

# =====================================================
# ✅ COMMIT 7: EMAIL CONFIGURATION
# =====================================================
# Backend de email (console para desarrollo, smtp para producción)
EMAIL_BACKEND = env(
    "EMAIL_BACKEND",
    default="django.core.mail.backends.console.EmailBackend"
)

# Configuración SMTP (solo necesaria si usas smtp backend)
EMAIL_HOST = env("EMAIL_HOST", default="smtp.gmail.com")
EMAIL_PORT = env.int("EMAIL_PORT", default=587)
EMAIL_USE_TLS = env.bool("EMAIL_USE_TLS", default=True)
EMAIL_USE_SSL = env.bool("EMAIL_USE_SSL", default=False)
EMAIL_HOST_USER = env("EMAIL_HOST_USER", default="")
EMAIL_HOST_PASSWORD = env("EMAIL_HOST_PASSWORD", default="")

# Remitente por defecto
DEFAULT_FROM_EMAIL = env(
    "DEFAULT_FROM_EMAIL",
    default="Capacitación Ergonomía <no-reply@ergocap.local>"
)

# Para emails de error de Django (500 errors → ADMINS)
SERVER_EMAIL = env("SERVER_EMAIL", default=DEFAULT_FROM_EMAIL)

# Email del administrador que recibe copia de certificados
ADMIN_EMAIL = env("ADMIN_EMAIL", default="")

# Validar credenciales SMTP en producción
_is_smtp_backend = "smtp" in EMAIL_BACKEND.lower()
if _is_smtp_backend and not DEBUG:
    _missing = []
    if not EMAIL_HOST_USER:
        _missing.append("EMAIL_HOST_USER")
    if not EMAIL_HOST_PASSWORD:
        _missing.append("EMAIL_HOST_PASSWORD")
    if _missing:
        raise ImproperlyConfigured(
            f"SMTP email backend activo pero falta{'n' if len(_missing) > 1 else ''}: "
            f"{', '.join(_missing)}. Agregalos al archivo .env"
        )

# =====================================================
# OPENAI API (para Ergobot)
# =====================================================
OPENAI_API_KEY = env("OPENAI_API_KEY", default="")
OPENAI_MODEL = env("OPENAI_MODEL", default="gpt-4.1-mini-2025-04-14")

# =====================================================
# MÓDULO DE ERGONOMÍA SRT 886/15
# =====================================================
# Modelo de lenguaje del módulo. Por defecto usa el de la organización, de
# modo que hay un solo lugar donde decidir qué modelo se usa. Definir
# CHAT_AI_MODEL en el .env sólo para que el módulo use uno distinto.
#
# ⚠️ CF-1: esto es una unificación de CONFIGURACIÓN, no de código. `help_ai`
#    y `ergobot_ai` siguen siendo apps separadas que no se conocen. Es la
#    única unificación que la condición admite.
CHAT_AI_MODEL = env("CHAT_AI_MODEL", default=OPENAI_MODEL)

# --- Chat de ayuda contextual (help_ai) ------------------------------------
CHAT_AI_AGENT_CACHE_SIZE = env.int("CHAT_AI_AGENT_CACHE_SIZE", default=64)
CHAT_AI_RATE_LIMIT = env.int("CHAT_AI_RATE_LIMIT", default=20)
CHAT_AI_RATE_WINDOW_SECONDS = env.int("CHAT_AI_RATE_WINDOW_SECONDS", default=60)
CHAT_AI_STREAM_TIMEOUT_SECONDS = env.int("CHAT_AI_STREAM_TIMEOUT_SECONDS", default=120)
CHAT_AI_HEARTBEAT_SECONDS = env.int("CHAT_AI_HEARTBEAT_SECONDS", default=10)
CHAT_AI_MAX_QUESTION_CHARS = env.int("CHAT_AI_MAX_QUESTION_CHARS", default=2000)
CHAT_AI_MAX_THREAD_MESSAGES = env.int("CHAT_AI_MAX_THREAD_MESSAGES", default=20)
CHAT_AI_MAX_MESSAGE_CHARS = env.int("CHAT_AI_MAX_MESSAGE_CHARS", default=4000)

# --- Informes profesionales (exportaciones.reports) ------------------------
REPORT_AI_TIMEOUT_SECONDS = env.int("REPORT_AI_TIMEOUT_SECONDS", default=90)
REPORT_AI_RATE_LIMIT = env.int("REPORT_AI_RATE_LIMIT", default=10)
REPORT_AI_RATE_WINDOW_SECONDS = env.int("REPORT_AI_RATE_WINDOW_SECONDS", default=3600)

# --- Descarga de documentos oficiales --------------------------------------
EXPORT_RATE_LIMIT = env.int("EXPORT_RATE_LIMIT", default=60)
EXPORT_RATE_WINDOW_SECONDS = env.int("EXPORT_RATE_WINDOW_SECONDS", default=300)

# =====================================================
# LOGGING
# =====================================================
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{levelname} {asctime} {module} {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
    },
    "loggers": {
        "apps.certificates": {
            "handlers": ["console"],
            "level": "INFO",
        },
        "apps.quiz": {
            "handlers": ["console"],
            "level": "INFO",
        },
        # --- Módulo de Ergonomía SRT 886/15 ---
        # Los logs registran identificadores y métricas, NUNCA payloads ni
        # contenido de informes (CF-4).
        "apps.ergonomia_886": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
        "apps.ergonomia_886.exportaciones.reports": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
        "apps.ergonomia_886.help_ai": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
    },
}

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
