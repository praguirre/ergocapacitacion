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
    "apps.training",
    "apps.quiz",
    "apps.certificates",
    "apps.ergobot_ai",
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

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
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"

DATABASES = {
    "default": env.db("DATABASE_URL")
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
LOGIN_URL = "trainee_landing"
LOGIN_REDIRECT_URL = "training_home"

# URLs de login profesionales (para usar en decoradores/mixins/vistas)
PROFESSIONAL_LOGIN_URL = "professional_login"
PROFESSIONAL_LOGIN_REDIRECT_URL = "dashboard"

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
    },
}

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
