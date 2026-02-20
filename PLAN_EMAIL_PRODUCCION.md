# Plan: Email real para beta — ErgoSolutions

## Contexto

El proyecto ErgoSolutions (Django + PostgreSQL) tiene toda la lógica de envío de emails implementada, pero usa `console.EmailBackend` (imprime en terminal). Para el deploy beta necesitamos que los emails se envíen de verdad. Los flujos afectados son:

1. **Certificados** (`apps/certificates/emailer.py`) — envía PDF adjunto a: trabajador, empleador, resp. SySO, admin
2. **Compartir links** (`apps/dashboard/views.py`) — envía link de capacitación a múltiples destinatarios

Además hay un **bug**: `.env` define `ADMIN_CERT_EMAIL` pero `settings.py` lee `ADMIN_EMAIL`, por lo que el admin nunca recibe copia de certificados.

---

## A) Diagnóstico

| Aspecto | Estado actual | Problema |
|---------|--------------|----------|
| `EMAIL_BACKEND` | Console (via env var) | No envía emails reales |
| SMTP config en settings.py | Ya lee env vars (HOST, PORT, TLS, USER, PASSWORD) | Falta `EMAIL_USE_SSL` y `SERVER_EMAIL` |
| `ADMIN_EMAIL` | settings.py lee `ADMIN_EMAIL`, .env define `ADMIN_CERT_EMAIL` | **Bug**: admin nunca recibe certificados |
| Validación de config | No existe | Si faltan credenciales SMTP en producción, falla silenciosamente |
| Comando de prueba | No existe | No hay forma de verificar la config SMTP |
| `.env.example` | Incompleto, variable ADMIN mal nombrada | Falta documentar variables SMTP |

---

## B) Proveedor recomendado para BETA: Gmail con App Password

**¿Por qué Gmail y no SendGrid/Mailgun/SES?**

- **Volumen beta**: Gmail permite 500 emails/día gratis. Incluso con 4 emails por certificado, necesitarías 125 completaciones/día para alcanzar el límite.
- **Costo cero**: Sin tarjeta ni billing.
- **Ya configurado**: settings.py ya tiene `smtp.gmail.com:587` como defaults.
- **Soporta adjuntos PDF**: Límite 25MB por mensaje (los certificados pesan ~100KB).
- **Sin configuración DNS**: SendGrid/Mailgun/SES requieren registros SPF/DKIM/DMARC y verificación de dominio.
- **Migración futura**: Cuando se supere el volumen beta, solo hay que cambiar las env vars a otro proveedor SMTP. Sin cambios de código.

**Setup requerido** (lo hace el usuario, no el código):
1. Activar 2FA en la cuenta Gmail
2. Google Account → Security → App passwords → generar password para "Mail"
3. Usar el password de 16 caracteres como `EMAIL_HOST_PASSWORD`

---

## C) Plan de ejecución — 6 pasos

### Paso 1: Fix bug `ADMIN_CERT_EMAIL` → `ADMIN_EMAIL`

**Archivos:**
- `.env` línea 10: cambiar `ADMIN_CERT_EMAIL=admin@ergocap.local` → `ADMIN_EMAIL=admin@ergocap.local`
- `.env.example` línea 6: mismo cambio

**Impacto**: El admin empezará a recibir copia de los certificados (cuando el email funcione).

---

### Paso 2: Agregar `EMAIL_USE_SSL`, `SERVER_EMAIL` y validación en `config/settings.py`

**2a) Agregar import** (top del archivo, después de `import environ`):
```python
from django.core.exceptions import ImproperlyConfigured
```

**2b) Agregar 2 settings** en el bloque de email (líneas 145-168):
```python
EMAIL_USE_SSL = env.bool("EMAIL_USE_SSL", default=False)   # Para proveedores que usan puerto 465
SERVER_EMAIL = env("SERVER_EMAIL", default=DEFAULT_FROM_EMAIL)  # Para emails de error de Django
```

**2c) Agregar bloque de validación** (después del bloque de email, antes de OPENAI):
```python
# Validar que las credenciales SMTP estén configuradas en producción
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
```

**Comportamiento**: Solo valida cuando `DEBUG=False` + backend SMTP. En desarrollo con console backend no hace nada.

---

### Paso 3: Actualizar `.env.example` completo

Reescribir con todas las variables documentadas, placeholders descriptivos y comentarios en español:

```ini
# --- Core Django ---
SECRET_KEY=change-me-to-a-random-50-char-string
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost

# --- Database ---
DATABASE_URL=postgres://USER:PASSWORD@127.0.0.1:5432/ergocapacitacion

# --- Email ---
# Backend: console para desarrollo, smtp para producción
# django.core.mail.backends.console.EmailBackend  (dev - imprime en terminal)
# django.core.mail.backends.smtp.EmailBackend     (prod - envía email real)
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_USE_SSL=False
EMAIL_HOST_USER=tu-email@gmail.com
EMAIL_HOST_PASSWORD=tu-app-password-de-gmail
DEFAULT_FROM_EMAIL=ErgoSolutions <tu-email@gmail.com>
# SERVER_EMAIL=tu-email@gmail.com
ADMIN_EMAIL=admin@example.com

# --- OpenAI (Ergobot AI) ---
OPENAI_API_KEY=
OPENAI_MODEL=gpt-5-mini-2025-08-07
```

---

### Paso 4: Crear management command `send_test_email`

**Archivos nuevos:**
- `apps/certificates/management/__init__.py` (vacío)
- `apps/certificates/management/commands/__init__.py` (vacío)
- `apps/certificates/management/commands/send_test_email.py` (~90 líneas)

**Uso:**
```bash
python manage.py send_test_email destinatario@example.com
python manage.py send_test_email destinatario@example.com --with-attachment
```

**Funcionalidad:**
1. Muestra la configuración actual (password enmascarado)
2. Avisa si está usando console backend
3. Envía email de prueba (opcionalmente con PDF adjunto de prueba)
4. Usa `fail_silently=False` para mostrar errores claros

El flag `--with-attachment` es importante porque testea el mismo code path que los certificados (`EmailMessage` + `.attach()`).

---

### Paso 5: Actualizar `.env` local

- Renombrar `ADMIN_CERT_EMAIL` → `ADMIN_EMAIL`
- NO cambiar `EMAIL_BACKEND` (sigue en console para desarrollo)

---

### Paso 6: NO hacer (fuera de scope beta)

- Templates HTML para emails (plain text es suficiente para beta)
- Celery/async (volumen bajo, envío síncrono OK)
- SPF/DKIM/DMARC (no aplica con Gmail directo)
- Bounce tracking (requiere SendGrid/Mailgun API)
- Rate limiting (Gmail limita a 500/día naturalmente)

---

## D) Resumen de archivos a tocar

| Archivo | Acción | Cambio |
|---------|--------|--------|
| `config/settings.py` | Editar | +1 import, +2 settings (`EMAIL_USE_SSL`, `SERVER_EMAIL`), +bloque validación (~15 líneas) |
| `.env` | Editar | Renombrar `ADMIN_CERT_EMAIL` → `ADMIN_EMAIL` |
| `.env.example` | Reescribir | Versión completa con todas las variables SMTP |
| `apps/certificates/management/__init__.py` | Crear | Vacío |
| `apps/certificates/management/commands/__init__.py` | Crear | Vacío |
| `apps/certificates/management/commands/send_test_email.py` | Crear | ~90 líneas |

---

## E) Verificación — Cómo probar

### En local (console backend):
```bash
python manage.py send_test_email test@example.com
python manage.py send_test_email test@example.com --with-attachment
# → Ambos imprimen el email en terminal
```

### En local con SMTP real (antes de deploy):
1. Setear en `.env`:
   ```
   EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
   EMAIL_HOST_USER=tu-email@gmail.com
   EMAIL_HOST_PASSWORD=xxxx-xxxx-xxxx-xxxx
   DEFAULT_FROM_EMAIL=ErgoSolutions <tu-email@gmail.com>
   ```
2. Ejecutar:
   ```bash
   python manage.py send_test_email tu-email-real@gmail.com
   python manage.py send_test_email tu-email-real@gmail.com --with-attachment
   ```
3. Verificar que lleguen a la bandeja de entrada

### Validación de seguridad:
```bash
# Con DEBUG=False y sin credenciales → debe fallar con error claro
DEBUG=False EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend python manage.py check
# → ImproperlyConfigured: SMTP email backend activo pero faltan: EMAIL_HOST_USER, EMAIL_HOST_PASSWORD
```

### En producción:
1. Configurar `.env` del servidor con credenciales Gmail reales
2. `python manage.py send_test_email admin@tudominio.com --with-attachment`
3. Probar flujo real: completar un quiz → verificar que llega el certificado por email
4. Probar flujo real: compartir link desde dashboard → verificar que llega el email

### Qué logs mirar si falla:
- Terminal/Gunicorn logs: los loggers `apps.certificates` y `apps.quiz` imprimen info/warning/error
- Gmail: verificar "Actividad reciente de seguridad" si bloquea el acceso
- El campo `email_error` del modelo `Certificate` guarda errores de envío

---

## F) Checklist de datos que necesito del usuario

Para configurar el envío real, necesitás tener listo:

- [ ] **Cuenta Gmail** dedicada para el envío (puede ser nueva o existente)
- [ ] **2FA activado** en esa cuenta Gmail
- [ ] **App Password generado** (16 caracteres, formato: `xxxx xxxx xxxx xxxx`)
- [ ] **Email del admin** que recibirá copia de certificados
- [ ] **Nombre de remitente** deseado (ej: `ErgoSolutions <email@gmail.com>`)

> No necesito que pegues las credenciales acá. El plan es que vos las pongas directamente en el archivo `.env`.
