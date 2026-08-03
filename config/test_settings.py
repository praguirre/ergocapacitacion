"""Configuracion aislada para la suite automatizada de ErgoSolutions.

Evita que las pruebas dependan de permisos para crear bases PostgreSQL y
garantiza que nunca operen sobre la base configurada en `.env`.

Replica el patron de `ergonomia_srt/test_settings.py`, del que provienen
las 160 pruebas del modulo de Ergonomia 886.

Uso:
    .venv/bin/python manage.py test --settings=config.test_settings
"""

import os

from .settings import *  # noqa: F403


# Base de datos efimera: no requiere permisos de creacion en PostgreSQL
# y nunca toca la base de desarrollo.
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": os.environ.get("ERGOSOLUTIONS_TEST_DATABASE_NAME", ":memory:"),
    }
}

# La tabla de DatabaseCache es infraestructura de despliegue y no forma parte
# de las migraciones. La suite usa memoria aislada para permanecer
# autocontenida. Ver commit 0.8.
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "ergosolutions-tests",
    }
}

# Hashing rapido: las pruebas crean muchos usuarios.
PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.MD5PasswordHasher",
]

# Las pruebas de render no ejecutan collectstatic, de modo que el backend
# manifestado de WhiteNoise fallaria al resolver {% static %}.
# Produccion conserva el manifestado definido en settings.py.
STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
    },
}

# Ningun correo sale del proceso durante las pruebas.
EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"

# La suite conserva la compuerta histórica que exige la cabecera bloqueante.
# Los tests de config cubren por separado el modo Report-Only de observación.
CSP_REPORT_ONLY = False

# `testserver` debe estar permitido siempre, no solo con DEBUG=True.
if "testserver" not in ALLOWED_HOSTS:  # noqa: F405
    ALLOWED_HOSTS.append("testserver")  # noqa: F405
