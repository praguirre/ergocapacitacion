He terminado la auditoría. Todo fue lectura: no toqué código, configuración ni datos. Las únicas escrituras posibles fueron sesiones anónimas de Django generadas por dos requests de verificación (un POST de CSRF sin datos), sin impacto funcional.

---

# INFORME TÉCNICO — AUDITORÍA DE ESTADO
## Proyecto ErgoSolutions (ergocapacitación) — Producción
**Fecha de auditoría:** 30 de julio de 2026
**Entorno auditado:** `https://www.ergosolutions.com.ar/` — VPS `vps-4625086-x`
**Alcance:** código desplegado, base de datos productiva, infraestructura de ejecución, documentación interna del repo, tráfico real registrado.

---

# 1. RESUMEN EJECUTIVO

ErgoSolutions es una plataforma Django 5.2 de capacitación laboral para profesionales de Seguridad e Higiene / Salud Ocupacional / Ergonomía. Está **operativa, estable y sirviendo tráfico**, pero se encuentra en un estado que se describe mejor como **"beta funcional congelada"**:

| Dimensión | Estado |
|---|---|
| Disponibilidad | ✅ Online, uptime del servicio 7 días (último restart 23/07/2026), respuestas en ~80 ms |
| Código desplegado | ⚠️ Congelado desde el **28/02/2026** (tag `v0.1.3-beta`, commit `660dc1b`), 5 meses sin cambios |
| Funcionalidad núcleo | ✅ Completa: doble portal, links, quiz, certificados PDF, emails, IA, presencial |
| Catálogo de contenido | 🔴 **1 de 6 módulos activo** (solo "Ergonomía"); los otros 5 son cáscaras sin video ni contenido |
| Uso real | 🔴 **Sin actividad de usuarios desde el 23/04/2026**. 18 usuarios, 15 certificados históricos |
| Roadmap propio | 🟡 Fases 1–6 implementadas; Fase 7 (Evaluaciones + Suscripciones) sin arrancar |
| Backups | 🔴 **No hay backup automatizado de la base de producción** (el único dump es manual, del 24/06/2026) |
| Rotación de logs | 🔴 Ausente: `gunicorn-access.log` acumula 23 MB sin rotar |
| Seguridad | 🟡 Sin incidentes; hay hardening pendiente y un certificado descargable sin autenticación por URL directa |

**Los dos hallazgos que más importan** son de operación, no de código: la ausencia de backup automático de `ergocapacitacion_db` (la app de al lado, CriaApp, sí lo tiene) y la falta de logrotate. El resto son deudas técnicas latentes que hoy no rompen nada.

---

# 2. IDENTIDAD Y ESTADO DEL DESPLIEGUE

### 2.1 Versionado

| Ítem | Valor |
|---|---|
| Repositorio | `git@github.com:praguirre/ergocapacitacion.git` |
| Directorio de código | `/srv/ergocapacitacion/app` |
| Estado de Git | **HEAD detached** en `v0.1.3-beta` = `660dc1bd1789b3efe346f78eb93777f14310f5c7` |
| Árbol de trabajo | **Limpio** (sin modificaciones locales, sin parches sin commitear) |
| Fecha del commit desplegado | 28/02/2026 19:24 -03 |
| Commit inicial del proyecto | 21/01/2026 |
| Total de commits | 41 |
| Tags existentes | `v0.1.0-beta`, `v0.1.1-beta`, `v0.1.2-beta`, `v0.1.3-beta` |

### 2.2 Ramas

| Rama | Último commit | Observación |
|---|---|---|
| `origin/release/beta` | 28/02/2026 (`660dc1b`) | **Es lo que corre en producción**; el tag apunta acá |
| `main` / `origin/main` | 02/02/2026 (`074fbab`, "Commit 8") | **Rama por defecto del repo, ~4 meses atrasada respecto de producción** |
| `origin/feature/ergosolutions-saas` | 20/02/2026 | Rama de trabajo histórica, sin mergear |
| `release/beta` (local) | 20/02/2026 | Puntero local atrasado respecto de `origin/release/beta` |

⚠️ **Divergencia relevante:** producción NO corre `main`. `main` está en el "Commit 8" (emails a empleador/SySO), mientras que producción tiene 20+ commits adicionales: toda la refactorización a `CustomUser`, landing, dashboard, presencial, links y capacitaciones personalizadas. Quien clone el repo y mire `main` verá una aplicación sustancialmente distinta de la que está en el aire.

### 2.3 Últimos 5 commits desplegados

```
660dc1b test(dashboard): cover personalized training visibility and access rules
0d00033 feat(training-admin): manage personalized training assignments from admin
db5fbf4 feat(dashboard): separate general and personalized trainings with access control
f16e867 feat(training): add personalized training fields to TrainingModule
0d08faa feat(content+quiz): canonical ergonomia content seed and robust quiz backup import
```

La última línea de trabajo fue el sistema de **capacitaciones personalizadas por cliente** (módulos visibles solo para profesionales asignados). Está implementado y testeado, pero **no se usa**: hay 0 filas en `training_trainingmodule_assigned_professionals`.

---

# 3. INFRAESTRUCTURA DE PRODUCCIÓN

### 3.1 Topología

```
Internet
   │
   ▼ :80  → 301 → :443
nginx (server block "ergosolutions", sin default_server)
   │
   ├── /static/  → alias /srv/ergocapacitacion/app/staticfiles/   (expires 30d)
   ├── /media/   → alias /srv/ergocapacitacion/app/media/         (expires 7d)
   └── /        → proxy_pass unix:/srv/ergocapacitacion/ergocapacitacion.sock
                     │
                     ▼
              gunicorn 25.1.0 — 3 workers sync, timeout 60s
              config.wsgi:application
                     │
                     ▼
              Django 5.2.11 (Python 3.10.12)
                     │
                     ▼
              PostgreSQL 14 @ 127.0.0.1:5432 — base ergocapacitacion_db
```

El VPS es **compartido** con la app CriaApp (beta), completamente aislada: server block nginx propio, base y rol Postgres propios, usuario de sistema propio (`criaapp`), unidades systemd propias. Ergo corre bajo el usuario `deploy`. Redis está instalado y corriendo, pero **ErgoSolutions no lo usa** (es de CriaApp).

### 3.2 Servicio systemd — `/etc/systemd/system/ergocapacitacion.service`

```ini
[Unit]
Description=Gunicorn service for ergocapacitacion (ErgoSolutions)
After=network.target

[Service]
User=deploy
Group=www-data
WorkingDirectory=/srv/ergocapacitacion/app
EnvironmentFile=/srv/ergocapacitacion/.env
Environment="PATH=/srv/ergocapacitacion/venv/bin"
UMask=007
ExecStart=/srv/ergocapacitacion/venv/bin/gunicorn \
  --workers 3 --timeout 60 \
  --bind unix:/srv/ergocapacitacion/ergocapacitacion.sock \
  --access-logfile /srv/ergocapacitacion/logs/gunicorn-access.log \
  --error-logfile  /srv/ergocapacitacion/logs/gunicorn-error.log \
  config.wsgi:application
Restart=always
RestartSec=3
[Install]
WantedBy=multi-user.target
```

**Estado actual:** `active (running)` desde el 23/07/2026 04:30 (1 semana), PID maestro 527, 217 MB de RSS, 2 min 26 s de CPU acumulada. Habilitado en boot. Sin reinicios inesperados: el `gunicorn-error.log` solo registra arranques/paradas limpias (10/06, 25/06, 23/07 — coincidentes con mantenimientos del VPS), **cero tracebacks**.

### 3.3 Nginx — `/etc/nginx/sites-available/ergosolutions`

```nginx
server {                                  # HTTP → HTTPS
    listen 80; listen [::]:80;
    server_name ergosolutions.com.ar www.ergosolutions.com.ar;
    return 301 https://$host$request_uri;
}
server {
    listen 443 ssl http2; listen [::]:443 ssl http2;
    server_name ergosolutions.com.ar www.ergosolutions.com.ar;
    ssl_certificate     /etc/letsencrypt/live/ergosolutions.com.ar/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/ergosolutions.com.ar/privkey.pem;
    include /etc/letsencrypt/options-ssl-nginx.conf;
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem;
    client_max_body_size 25M;
    location = /favicon.ico { access_log off; log_not_found off; }
    location /static/ { alias /srv/ergocapacitacion/app/staticfiles/; access_log off; expires 30d; add_header Cache-Control "public"; }
    location /media/  { alias /srv/ergocapacitacion/app/media/;       expires 7d;  add_header Cache-Control "public"; }
    location /        { include proxy_params; proxy_pass http://unix:/srv/ergocapacitacion/ergocapacitacion.sock; }
}
```

`proxy_params` (estándar Ubuntu) envía `Host`, `X-Real-IP`, `X-Forwarded-For` y `X-Forwarded-Proto`.

**Nota técnica no obvia:** `settings.py` **no** define `SECURE_PROXY_SSL_HEADER`, con lo cual Django por sí solo no sabría que la conexión es HTTPS y **todos los POST de navegador fallarían con 403 por chequeo de Origin**. En la práctica no ocurre porque **gunicorn** traduce `X-Forwarded-Proto: https` a `wsgi.url_scheme = https` mediante sus `secure_scheme_headers` por defecto (el socket unix cuenta como proxy confiable). Lo verifiqué empíricamente: un POST real con cabecera `Origin: https://…` a través de nginx devuelve **302** (aceptado), mientras que el mismo POST simulado **sin** ese mecanismo devuelve **403**. Es decir: **funciona, pero por una dependencia implícita del servidor de aplicación, no por configuración explícita de Django.** Si se migra a uvicorn/ASGI, se cambia el proxy o se ajustan los `forwarded_allow_ips`, todos los formularios del sitio se rompen de golpe.

### 3.4 TLS

| Ítem | Valor |
|---|---|
| Emisor | Let's Encrypt (CN = YR1) |
| CN / SAN | `ergosolutions.com.ar`, `www.ergosolutions.com.ar` |
| Emitido | 19/07/2026 |
| **Vence** | **17/10/2026** |
| Renovación | `certbot.timer` activo (última corrida 30/07/2026 13:49, próxima 31/07 09:58) + `/etc/cron.d/certbot` |

### 3.5 Recursos del host

| Recurso | Estado |
|---|---|
| Disco `/` | 25 GB total, 11 GB usados, **15 GB libres (42%)** |
| RAM | 1963 MB total, 1189 MB en uso, 623 MB en caché, **570 MB disponibles** |
| Swap | 2048 MB, 142 MB en uso |
| Base de datos | **10 MB** (`ergocapacitacion_db`) |
| Media (certificados PDF) | **68 KB** (15 archivos) |
| Staticfiles | 5.2 MB |
| Logs de gunicorn | **23 MB** (access) + 16 KB (error) |

No hay presión de recursos. La RAM ajustada se explica por convivir con CriaApp (3 servicios: gunicorn + celery worker + celery beat) y Postgres/Redis.

---

# 4. CONFIGURACIÓN DE LA APLICACIÓN

### 4.1 `config/settings.py` (archivo único, sin split dev/prod)

Se usa `django-environ` leyendo `/srv/ergocapacitacion/app/.env` → symlink a `/srv/ergocapacitacion/.env` (permisos `600`, propietario `deploy`, correctamente ignorado por `.gitignore`; solo `.env.example` está versionado).

**Valores efectivos verificados en el proceso vivo:**

| Setting | Valor en producción |
|---|---|
| `DEBUG` | `False` ✅ |
| `ALLOWED_HOSTS` | `ergosolutions.com.ar`, `www.ergosolutions.com.ar`, `127.0.0.1`, `localhost` |
| `AUTH_USER_MODEL` | `accounts.CustomUser` |
| `LANGUAGE_CODE` / `TIME_ZONE` | `es-ar` / `America/Argentina/Buenos_Aires`, `USE_TZ=True` |
| `DATABASES` | `postgresql://…@127.0.0.1:5432/ergocapacitacion_db` (vía `DATABASE_URL`) |
| `EMAIL_BACKEND` | `smtp.EmailBackend` — Gmail SMTP `smtp.gmail.com:587` TLS, cuenta `consultaergosolutions@gmail.com` |
| `DEFAULT_FROM_EMAIL` | `ErgoSolutions <consultaergosolutions@gmail.com>` |
| `ADMIN_EMAIL` | `praguirre@gmail.com` (recibe copia de cada certificado) |
| `OPENAI_MODEL` | `gpt-4.1-mini-2025-04-14` |
| `STORAGES.staticfiles` | `whitenoise.storage.CompressedManifestStaticFilesStorage` |
| `X_FRAME_OPTIONS` | `DENY` ✅ |
| `SESSION_COOKIE_AGE` | 1 209 600 s (14 días) |
| `CSRF_TRUSTED_ORIGINS` | `[]` (vacío) |
| `SECURE_SSL_REDIRECT` | `False` (lo cubre nginx) |
| `SESSION_COOKIE_SECURE` | **`False`** ⚠️ |
| `CSRF_COOKIE_SECURE` | **`False`** ⚠️ |
| `SECURE_HSTS_SECONDS` | **`0`** ⚠️ |
| `SECURE_PROXY_SSL_HEADER` | **`None`** ⚠️ (ver §3.3) |

El propio `.env` documenta en un comentario que `CSRF_TRUSTED_ORIGINS` no se lee desde el entorno y deja escrita la línea a agregar — es una deuda conocida y anotada.

Hay una validación defensiva propia: si el backend es SMTP y `DEBUG=False`, `settings.py` levanta `ImproperlyConfigured` si faltan `EMAIL_HOST_USER` o `EMAIL_HOST_PASSWORD`. Buena práctica: la app no arranca con email mal configurado.

### 4.2 Middleware (orden real)

```
SecurityMiddleware → WhiteNoiseMiddleware → SessionMiddleware → CommonMiddleware
→ CsrfViewMiddleware → AuthenticationMiddleware → MessageMiddleware → XFrameOptionsMiddleware
```

WhiteNoise está activo aunque nginx ya sirve `/static/` — es redundancia inofensiva (WhiteNoise nunca ve esas requests) que además deja la app funcional si se sirviera sin nginx.

### 4.3 Dependencias

`requirements.txt` (9 líneas, todas con `>=`, **sin pins exactos**):

```
Django>=5.2 · psycopg[binary]>=3.2 · django-environ>=0.11 · django-bootstrap5>=25.1
whitenoise>=6.7 · reportlab>=4.0 · openai>=1.0 · openai-agents>=0.0.19 · uvicorn>=0.30.0
```

Instalado en `/srv/ergocapacitacion/venv` (Python 3.10.12): Django 5.2.11, psycopg 3.3.3, gunicorn 25.1.0, openai 2.21.0, openai-agents 0.9.2, django-bootstrap5 26.2, django-environ 0.13.0, reportlab, pillow 12.1.1, mcp 1.26.0.

⚠️ Dos observaciones:
- **Sin versiones fijadas**, un `pip install -r requirements.txt` en otra máquina puede producir un entorno distinto al de producción. En particular `openai-agents` pasó de `0.0.19` (mínimo declarado) a `0.9.2` (instalado) — un salto de API mayor entre versiones pre-1.0.
- `uvicorn` y `gunicorn` conviven en el venv, pero **producción corre `config.wsgi` bajo gunicorn con workers `sync`**, no ASGI. El README declara "Async: ASGI + Uvicorn", lo cual **no refleja el despliegue real**.

---

# 5. COMPOSICIÓN DEL PROYECTO

### 5.1 Inventario

- **8 aplicaciones Django** propias (~6.100 líneas de Python)
- **21 templates HTML** (~2.200 líneas)
- **2 archivos JS** propios (`quiz.js`, `ergobot_chat.js`) + 2 CSS
- **27 migraciones** aplicadas (7 propias del dominio)
- **20 tablas** en PostgreSQL
- **5 documentos** Markdown de planificación en el repo (1.583 líneas)

### 5.2 Mapa de aplicaciones

| App | Rol | Modelos | Vistas | Estado |
|---|---|---|---|---|
| `accounts` | Usuarios y autenticación dual | `CustomUser` | 8 (trainee) + 3 (profesional) | ✅ Completa |
| `landing` | Home institucional pública | — | 1 | ✅ Completa |
| `dashboard` | Panel del profesional | — | 7 | ✅ Completa |
| `training` | Módulos, links compartibles | `TrainingModule`, `CapacitacionLink`, `LinkShareLog` | 2 | ✅ Completa |
| `quiz` | Evaluación con reglas | `Question`, `Choice`, `QuizAttempt`, `QuizState` | 6 | ✅ Completa |
| `certificates` | Certificados PDF + emails | `Certificate` | 3 | 🟡 Falta template de listado |
| `presencial` | Modalidad presencial | `PresencialSession` | 5 | ✅ Completa |
| `ergobot_ai` | Chat IA con streaming SSE | — | 1 | ✅ Completa |

### 5.3 Modelo de datos (real, verificado contra la base)

**`accounts_customuser`** — modelo unificado sobre `AbstractBaseUser + PermissionsMixin`, `USERNAME_FIELD = email`:
- *Discriminador:* `user_type ∈ {professional, trainee}`
- *Comunes:* `email` (unique, indexado), `first_name`, `last_name`, `full_name` (legacy, sincronizado en `save()`)
- *Profesional:* `username` (unique, nullable), `dni` (validador 7-8 dígitos), `profession`, `license_number`
- *Trabajador:* `cuil` (unique, indexado), `job_title`, `company_name`, `employer_email`, `safety_responsible_email`
- *Suscripción (preparada, inactiva):* `subscription_tier ∈ {free,basic,premium}`, `subscription_status ∈ {none,active,expired,cancelled}`, `subscription_expires`
- *Control:* `is_active`, `is_staff`, `date_joined`
- *Manager custom:* `create_user`, `create_trainee` (fuerza `set_unusable_password()`), `create_professional` (exige password + username), `create_superuser`
- *Propiedades:* `is_professional`, `is_trainee`, `display_name`, `has_active_subscription`

**`training_trainingmodule`** — `slug` (unique), `title`, `description`, `youtube_id`, tres campos Markdown (`intro_md`, `material_md`, `transcript_md`), presentación (`icon` Bootstrap Icons, `color` hex, `order`), `is_active`, y el bloque de personalización: `is_personalized`, `requested_by` (FK profesional), `assigned_professionals` (M2M), `company_name_custom`, `custom_notes`. Tres *classmethods* de filtrado: `get_general_modules()`, `get_personalized_for_user()`, `get_all_for_user()`.

**`training_capacitacionlink`** — PK `UUIDv4`, FK a módulo y a profesional creador, `label`, `expires_at` (opcional), `is_active`, `access_count`. Propiedades `is_expired` / `is_usable`; `get_absolute_url()` → `/c/<slug>/?ref=<uuid>`.

**`training_linksharelog`** — auditoría de envíos: `link`, `shared_to_email`, `shared_at`.

**`quiz_question` / `quiz_choice`** — pregunta con `order` 1..10 y `explanation_correct`; opción con `label` (A–D), `is_correct` y `explanation_if_chosen` (feedback pedagógico por opción elegida). Constraints únicos `(module, order)` y `(question, label)`.

**`quiz_quizattempt`** — intento individual: `started_at`, `submitted_at`, `score`, `passed`, `answers` (JSONField `{question_id: choice_id}` para auditoría). Índice `(user, module, -started_at)`.

**`quiz_quizstate`** — estado por par usuario-módulo: `attempts_used`, `lockout_until`, `retake_available_at`, `last_completed_at`, `last_passed`. Constraint único `(user, module)`.

**`certificates_certificate`** — PK `UUIDv4`, FK usuario y módulo, **OneToOne con `QuizAttempt`** (un certificado por intento aprobado), `pdf_file` (FileField → `media/certificates/`), `issued_at`, `valid_until` (default: +365 días), y trazabilidad de email: `email_sent`, `email_sent_at`, `email_error`.

**`presencial_presencialsession`** — FK módulo y profesional, `session_date`, `location`, `participants_count`, `quiz_score`, `quiz_passed`, `notes`, `created_at`.

### 5.4 Mapa completo de URLs

| Ruta | App / Vista | Auth | Método | Descripción |
|---|---|---|---|---|
| `/` | `landing.home` | pública | GET | Home institucional; redirige autenticados a su área |
| `/admin/` | Django admin | staff | — | Panel de administración |
| **Portal profesional** |
| `/auth/registro/` | `views_professional.register` | pública | GET/POST | Alta de profesional (auto-login al crear) |
| `/auth/login/` | `views_professional.login_view` | pública | GET/POST | Login por email **o** username + password; soporta `?next=` con validación anti-`//` |
| `/auth/logout/` | `views_professional.logout_view` | sesión | POST | Cierre de sesión → landing |
| `/dashboard/` | `dashboard.home` | prof | GET | Panel con 3 KPIs + selector Evaluaciones (deshabilitado) / Capacitaciones |
| `/dashboard/capacitaciones/` | `capacitaciones_menu` | prof | GET | Grid de módulos generales + sección de personalizados |
| `/dashboard/capacitaciones/<slug>/` | `modalidad_selector` | prof | GET | Elección Presencial vs Online |
| `/dashboard/capacitaciones/<slug>/links/` | `online_links` | prof | GET | Listado de links propios del profesional |
| `/dashboard/capacitaciones/<slug>/links/generar/` | `generate_link` | prof | POST | Crea `CapacitacionLink` con etiqueta |
| `/dashboard/capacitaciones/<slug>/links/<uuid>/compartir/` | `share_link` | prof | GET/POST | Envío del link por email a N destinatarios |
| `/dashboard/perfil/` | `profile` | prof | GET/POST | Edición de datos + cambio de contraseña + stats |
| **Modalidad presencial** |
| `/dashboard/presencial/<slug>/` | `capacitacion_presencial` | prof | GET | Video + chat Ergobot para proyectar |
| `/dashboard/presencial/<slug>/quiz/` | `quiz_presencial` | prof | GET | Quiz grupal (sin reglas de intentos) |
| `/dashboard/presencial/<slug>/quiz/submit/` | `quiz_presencial_submit` | prof | POST | Corrección con detalle por pregunta |
| `/dashboard/presencial/<slug>/planilla/` | `planilla_pdf` | prof | GET | Genera planilla PDF de asistencia y registra la sesión |
| `/dashboard/presencial/historial/` | `historial_presencial` | prof | GET | Historial de sesiones del profesional |
| **Portal trabajador** |
| `/acceso/` | `accounts.landing` | pública | GET | Formularios de registro y login de trabajador |
| `/acceso/register/` | `register_post` | pública | POST | Valida y guarda en sesión → confirmación |
| `/acceso/confirm/` + `/acceso/confirm/post/` | `confirm_get/post` | pública | GET/POST | Confirmación de datos → crea usuario y auto-login |
| `/acceso/login/` | `login_post` | pública | POST | Autenticación **CUIL + email, sin contraseña** |
| `/acceso/logout/` | `logout_post` | sesión | POST | Cierre de sesión |
| `/acceso/health/` | `health` | pública | GET | Health check (texto plano `OK`) |
| `/capacitacion/` | `training_home` | login | GET | Página de capacitación: video + chat + quiz |
| `/c/<slug>/` | `views_public.public_landing` | pública | GET | Entrada vía link compartido: trackea `?ref=`, guarda en sesión y redirige |
| **Quiz (API JSON)** |
| `/quiz/<slug>/start/` | `start` | login | POST | Verifica bloqueo, crea intento, devuelve P1 |
| `/quiz/<slug>/question/<n>/` | `question` | login | GET | Devuelve pregunta n (1..10) |
| `/quiz/<slug>/answer/` | `answer` | login | POST | Responde una pregunta → feedback inmediato |
| `/quiz/<slug>/submit/` | `submit` | login | POST | Corrige, aplica reglas, dispara certificado |
| `/quiz/<slug>/result/<id>/` | `result_page` | login | GET | Pantalla HTML de resultado |
| `/quiz/<slug>/retake/` | `retake` | login | POST | Nuevo intento si las reglas lo permiten |
| **Certificados** |
| `/certificados/` | `my_certificates` | login | GET | **Devuelve JSON crudo** (sin template) |
| `/certificados/<uuid>/download/` | `download_certificate` | login | GET | Descarga con verificación de propiedad |
| `/certificados/<uuid>/view/` | `view_certificate` | login | GET | Visualización inline con verificación de propiedad |
| **IA** |
| `/ai/ergobot/<slug>/stream/` | `ergobot_stream` | login | GET | **Vista async**, streaming SSE token a token |

---

# 6. FUNCIONALIDADES OFRECIDAS

## 6.1 Autenticación dual (dos portales independientes)

El sistema mantiene **dos flujos de identidad completamente separados** sobre un único modelo de usuario, mediante tres backends encadenados:

1. **`ProfessionalBackend`** (extiende `ModelBackend`): acepta email **o** username + password, filtrando `user_type='professional'`. Incluye mitigación de *timing attacks* (ejecuta el hasher aunque el usuario no exista).
2. **`CuilEmailBackend`**: autentica trabajadores con **CUIL + email y sin contraseña**, filtrando `user_type='trainee'`. Implementa variantes `aauthenticate`/`aget_user` para las vistas asíncronas.
3. **`ModelBackend`** de Django como fallback para el admin.

El CUIL se normaliza a 11 dígitos (se descartan guiones/puntos) tanto en registro como en login, lo que evita duplicados por formato.

**Decisión de diseño con implicancia de seguridad:** el acceso del trabajador es *knowledge-based* con datos no secretos (CUIL + email). Cualquiera que conozca ambos puede entrar y descargar certificados de esa persona. Es una elección deliberada de fricción cero, consistente con el caso de uso (capacitación obligatoria masiva), pero conviene tenerla explícita.

También cabe notar que **el registro de profesionales es abierto al público** (`/auth/registro/` sin invitación ni verificación de email ni aprobación). Hoy cualquiera puede crear una cuenta profesional y acceder al catálogo general de capacitaciones y a la generación de links. Con 2 profesionales registrados no ha sido un problema; si el producto se abre, es el primer control que hay que agregar.

## 6.2 Gestión de capacitaciones (profesional)

- **Dashboard** con tres KPIs calculados en vivo: sesiones presenciales realizadas, links generados y "trabajadores capacitados" (suma de `access_count` de sus links).
- **Menú de capacitaciones** que separa visualmente módulos **generales** de **personalizados** (estos últimos solo se listan si el profesional está asignado). Los módulos inactivos se muestran en gris, no enlazados.
- **Control de acceso por módulo** (`dashboard/utils.py::check_module_access`): los módulos personalizados devuelven `403 Forbidden` a profesionales no asignados. Se aplica consistentemente en las 4 vistas que reciben `module_slug`.

## 6.3 Modalidad ONLINE — links compartibles

1. El profesional genera un `CapacitacionLink` con una **etiqueta interna** (ej. *"Valle de las Leñas SA - 23/02/2026"*).
2. Obtiene una URL con UUID: `/c/<slug>/?ref=<uuid>`.
3. Puede **compartirla por email a múltiples destinatarios** en una sola operación (el formulario acepta separación por coma o punto y coma, valida cada dirección y permite un mensaje personalizado). Cada envío se registra en `LinkShareLog`.
4. Al abrirse el link se **incrementa atómicamente** `access_count` usando `F()` (sin condición de carrera), se guarda el módulo objetivo en sesión y se redirige al registro/login del trabajador.
5. Los links soportan **expiración opcional** (`expires_at`) y desactivación manual (`is_active`).

⚠️ La vista `public_landing` valida `link.is_usable` **solo para contabilizar el acceso**: si el link está vencido o desactivado, igual se redirige al trabajador al registro y este puede completar la capacitación. La expiración hoy **es un contador, no un candado**.

## 6.4 Modalidad PRESENCIAL

Pensada para proyectar en sala:
- Página con **video embebido + chat Ergobot** (sin registro de trabajadores).
- **Quiz grupal** que reutiliza el mismo banco de preguntas pero **sin reglas de intentos, sin persistencia y sin certificado**: se corrige en el momento y devuelve el detalle pregunta por pregunta (respuesta elegida, correcta, si acertó).
- **Planilla PDF de asistencia** generada con ReportLab (A4 vertical, 25 filas para firma), que además **registra la sesión** en `PresencialSession` con fecha, ubicación y cantidad de participantes.
- **Historial** de sesiones dictadas por el profesional.

## 6.5 Sistema de evaluación (quiz online)

Reglas de negocio centralizadas en `apps/quiz/services.py`, **aplicadas 100% en el servidor**:

| Constante | Valor |
|---|---|
| `TOTAL_QUESTIONS` | 10 |
| `PASS_SCORE` | 8 (80%) |
| `MAX_ATTEMPTS` | 3 por ventana |
| `LOCK_HOURS` | 24 |

Mecánica:
- Feedback **inmediato por pregunta**, con explicación diferenciada según la opción elegida (`explanation_if_chosen`) o la explicación de la correcta.
- Al enviar, el **score se recalcula desde la base de datos** leyendo `answers`, nunca se confía en el cliente.
- **Si falla 3 veces** → `lockout_until = ahora + 24 h`.
- **Si aprueba** → *cool-off* de 24 h (`retake_available_at`) para evitar re-rendir en cadena.
- `reset_if_unlocked()` limpia el estado automáticamente al vencer el plazo, reiniciando la ventana de intentos.
- Las operaciones críticas usan `transaction.atomic()` + `select_for_update()` sobre `QuizState`, previniendo el doble-click/doble-intento.
- Los payloads enviados al front **nunca incluyen cuál es la respuesta correcta**.

Es la pieza mejor construida del proyecto: reglas explícitas, servidor autoritativo y concurrencia contemplada.

## 6.6 Certificación automática

Al aprobar se dispara `_create_certificate()`, diseñado como **no bloqueante** (envuelto en try/except en dos niveles: un fallo de PDF o de email nunca invalida la aprobación del trabajador):

1. Crea el `Certificate` (UUID, vigencia 1 año).
2. Genera el **PDF con ReportLab**: A4 apaisado, encabezado "CERTIFICADO DE CAPACITACIÓN / ERGONOMÍA Y PREVENCIÓN DE RIESGOS LABORALES", nombre en mayúsculas, CUIL, título del módulo, tabla de fechas emisión/vencimiento, y bloque de firma **hardcodeado**: *"Pablo Ricardo Aguirre — Licenciado en Kinesiología - MN 10.027 — Especialista en Ergonomía"*.
3. Lo guarda en `media/certificates/certificado_<uuid>.pdf`.
4. **Envía hasta 4 emails** con el PDF adjunto y el archivo renombrado al nombre del trabajador:
   - **Al trabajador** (obligatorio; si falla, se propaga y se registra en `email_error`)
   - **Al empleador** (si cargó `employer_email`) — `fail_silently=True`
   - **Al responsable de SySO** (si cargó `safety_responsible_email`) — `fail_silently=True`
   - **Al admin** (`praguirre@gmail.com`) con resumen de a quién se notificó
5. Marca `email_sent` / `email_sent_at`.

⚠️ **Punto de fragilidad de rendimiento:** el envío SMTP es **síncrono dentro del request HTTP**. Cuatro emails con adjunto PDF contra Gmail pueden tardar varios segundos; con `--timeout 60` de gunicorn y 3 workers `sync`, un pico de aprobaciones simultáneas bloquea workers. No hay Celery en esta app (el que existe en el VPS es de CriaApp). Con el volumen actual (15 certificados en 5 meses) es irrelevante; con adopción real, es lo primero que hay que mover a background.

⚠️ **Hallazgo de seguridad — certificados públicos por URL:** nginx sirve `/media/` directamente, sin pasar por Django. Verifiqué que `GET https://www.ergosolutions.com.ar/media/certificates/certificado_<uuid>.pdf` **devuelve HTTP 200 y el PDF completo sin ninguna autenticación**. La verificación de propiedad que hacen `download_certificate` y `view_certificate` (`certificate.user != request.user → 404`) **se puede saltear** yendo a la ruta directa. La protección efectiva es únicamente la impredecibilidad del UUIDv4 (que es razonable), pero el certificado contiene nombre completo y CUIL — dato personal. El propio admin de Django expone esa URL directa en la columna "PDF".

## 6.7 Ergobot AI (asistente conversacional)

- **Vista asíncrona** (`async def`) con `StreamingHttpResponse` sobre **Server-Sent Events**, entregando la respuesta token a token.
- Construido sobre `openai-agents` (`Runner.run_streamed`), modelo `gpt-4.1-mini-2025-04-14`.
- **System prompt dinámico** (`prompts.py::build_system_prompt`): compone `prompts/system_base.md` + el `intro_md`, `material_md` y `transcript_md` **del módulo desde la base de datos** + un archivo opcional `prompts/modules/<slug>.md`. Es decir, el bot está *grounded* en el contenido real de la capacitación, no responde de conocimiento general.
- Usa `TrainingModule.objects.afirst()` (ORM async) y tiene fallback si el slug no existe.
- Mantiene el hilo de conversación **en el cliente** (`window.ergobotThread` en memoria del navegador) y lo reenvía por query string; **no hay persistencia de conversaciones** en la base.
- Cabeceras correctas para streaming: `Cache-Control: no-cache` y **`X-Accel-Buffering: no`** (imprescindible detrás de nginx).

⚠️ Nota sobre el modelo de ejecución: la vista es async pero corre bajo **workers `sync` de gunicorn/WSGI**. Django lo soporta (envuelve la corrutina en un event loop), pero **cada chat ocupa un worker completo durante toda la generación**. Con 3 workers, 3 conversaciones simultáneas dejan el sitio sin capacidad de atender nada más. El historial confirma que funciona (11 invocaciones, todas HTTP 200, respuestas de hasta 4.8 KB), pero es el cuello de botella estructural de la arquitectura actual — y el motivo por el cual `uvicorn` está en `requirements.txt` y `config/asgi.py` existe: **la migración a ASGI está preparada pero no ejecutada.**

## 6.8 Panel de administración

Django Admin fuertemente personalizado:
- **`CustomUserAdmin`**: fieldsets separados por tipo de usuario (Acceso / Personales / Profesional / Trabajador / Emails de notificación / Suscripción / Permisos / Fechas), filtros por `user_type` y estado de suscripción, búsqueda por email, username, CUIL, nombre, empresa y DNI.
- **`TrainingModuleAdmin`**: `list_editable` sobre `order` e `is_active` (reordenar sin entrar al detalle), `prepopulated_fields` para el slug, `filter_horizontal` para asignar profesionales, columna "Tipo" con badge de color General/Personalizada, y **los selectores de `requested_by` y `assigned_professionals` filtran solo usuarios `professional`**. Incluye `prefetch_related` para evitar N+1.
- **`CertificateAdmin`**: `has_add_permission = False` (los certificados solo nacen de una aprobación real), borrado **solo para superusuarios**, badge Vigente/Vencido, `date_hierarchy` por fecha de emisión.
- **`CapacitacionLinkAdmin` / `LinkShareLogAdmin`**: campos de auditoría en solo lectura.
- **`QuestionAdmin`**: edición de opciones inline (`ChoiceInline`).

## 6.9 Comandos de gestión

| Comando | Función |
|---|---|
| `seed_modules` | Crea/actualiza los 6 módulos del catálogo con icono, color y orden |
| `seed_module_content --module <slug> [--force]` | Carga `intro.md`, `material.md` y `transcript.txt` desde `apps/training/content/<slug>/` |
| `seed_quiz` | Carga el banco de preguntas y opciones |
| `import_quiz_backup` | Importación robusta desde `fixtures/backup_quiz_questions.json` (14 KB) |
| `send_test_email` | Verificación de la configuración SMTP |

---

# 7. DATOS REALES EN PRODUCCIÓN

### 7.1 Volumen por tabla

| Tabla | Filas |
|---|---|
| `auth_permission` | 60 |
| `quiz_choice` | 40 |
| `django_session` | 31 |
| `django_migrations` | 27 |
| **`quiz_quizattempt`** | **24** |
| **`accounts_customuser`** | **18** |
| `quiz_quizstate` | 16 |
| **`certificates_certificate`** | **15** |
| `django_content_type` | 15 |
| `quiz_question` | 10 |
| `training_trainingmodule` | 6 |
| `training_capacitacionlink` | 5 |
| `presencial_presencialsession` | 2 |
| `training_linksharelog` | **0** |
| `training_trainingmodule_assigned_professionals` | **0** |
| `django_admin_log` | 0 |

### 7.2 Usuarios

- **2 profesionales**: `praguirre@gmail.com` (superusuario, alta 20/02, último acceso 15/03) y `praguirre23@hotmail.com` (alta 20/02, **último acceso hoy 30/07/2026** — coincide con el POST de login exitoso registrado a las 13:19).
- **16 trabajadores**, altas concentradas entre el 23/02 y el 06/03/2026, con una última el 19/04/2026. **12 de los 16 pertenecen a un mismo cliente** (dominio `@laslenas.com` — Valle de las Leñas / Nieves de Mendoza).

### 7.3 Actividad de capacitación

- **24 intentos de quiz**, todos sobre el módulo `ergonomia` (id 5), **15 aprobados** (62,5% de tasa de aprobación).
- **15 certificados emitidos**, entre el 23/02 y el 19/04/2026, **los 15 con `email_sent = True`** — el pipeline de email funcionó al 100%, sin un solo `email_error`.
- **5 links generados**, con 43 accesos acumulados:

| Etiqueta | Fecha | Accesos |
|---|---|---|
| Valle de las Leñas SA / Nieves de Mendoza SA - 23/02/2026 | 23/02 | **30** |
| Osvaldo prueba | 23/02 | 5 |
| Capacitación Simdel turno tarde | 26/02 | 5 |
| (sin etiqueta) | 19/04 | 2 |
| Vialidad | 22/02 | 1 |

- **2 sesiones presenciales** registradas (22/02 y 26/02), ambas del módulo Ergonomía, con `participants_count = 0` (el campo no se completó).
- **0 registros en `LinkShareLog`**: la función de compartir por email **nunca se usó** en producción; los links se distribuyeron por otro canal (WhatsApp/email manual).
- **11 conversaciones con Ergobot**, todas HTTP 200, última el 19/04/2026. Preguntas reales de usuarios: *"Según el video, ¿cuál es el peso máximo que se puede levantar?"*, *"Cuanto peso se puede levantar"*.

### 7.4 Análisis de tráfico (log completo: 20/02/2026 → 30/07/2026, 158.261 líneas)

**La aplicación no recibe usuarios reales desde el 23/04/2026.** El último request funcional de un trabajador fue una descarga de certificado el 19/04 y dos visitas a `/capacitacion/` el 20 y 23/04. Desde entonces, el tráfico se compone de:

| Tipo de tráfico | Volumen (últimas 20.000 líneas) |
|---|---|
| **404** (escaneo automatizado) | 12.947 (65%) |
| **400** (payloads malformados de bots) | 4.880 (24%) |
| 200 legítimos (mayormente `/` y `/robots.txt`) | 1.957 |
| 403 | 83 |
| 302 | 75 |

Los escaneos buscan WordPress (`/wp-login.php`, `/xmlrpc.php`, `wlwmanifest.xml`), PHP (`/index.php`, `eval-stdin.php` de PHPUnit), y **secretos** (`/.env` — 95 intentos, `/.git/config` — 104 intentos, `/config/database.yml`, `/credentials.json`). **Ninguno tuvo éxito**: `.env` está fuera del `DocumentRoot` (nginx solo expone `/static/` y `/media/` por alias) y `.git` no es accesible por HTTP. Es ruido de fondo de internet, no un ataque dirigido. No hay evidencia de intentos de fuerza bruta sobre `/auth/login/` ni `/admin/login/`.

Actividad humana residual reciente: hoy 30/07 hubo un login profesional exitoso y visitas a la home desde iPhone.

---

# 8. CATÁLOGO DE CONTENIDO

| ID | Slug | Título | Activo | Orden | YouTube | Intro | Material | Transcripción |
|---|---|---|---|---|---|---|---|---|
| 5 | `ergonomia` | **Ergonomía** | ✅ **Sí** | 1 | `IIgZp_NbsAE` | 1.936 car. | **13.810 car.** | 6.903 car. |
| 6 | `ruido` | Ruido | ❌ No | 2 | — | 0 | 0 | 0 |
| 1 | `riesgo-electrico` | Riesgo Eléctrico | ❌ No | 3 | — | 0 | 0 | 0 |
| 2 | `trabajo-en-altura` | Trabajo en Altura | ❌ No | 4 | — | 0 | 0 | 0 |
| 3 | `prevencion-incendios` | Prevención de Incendios | ❌ No | 5 | — | 0 | 0 | 0 |
| 4 | `elementos-proteccion-personal` | Elementos de Protección Personal | ❌ No | 6 | — | 0 | 0 | 0 |

**Este es el principal limitante de negocio del producto.** Toda la maquinaria (links, quiz, certificados, IA, presencial, personalización) está construida y probada, pero **opera sobre un único módulo de contenido**. Los otros cinco existen como placeholders con icono y color asignados, sin video, sin material y **sin preguntas** (las 10 preguntas y 40 opciones cargadas pertenecen todas a `ergonomia`).

El contenido canónico de Ergonomía vive versionado en el repo (`apps/training/content/ergonomia/`: `intro.md` 2 KB, `material.md` 14 KB, `transcript.txt` 7 KB) y se carga con `seed_module_content` — un patrón replicable y ordenado para los módulos futuros.

---

# 9. CALIDAD Y TESTING

| App | Tests | Clases | Líneas |
|---|---|---|---|
| `dashboard` | **13** | 3 | 245 |
| `accounts` | 6 | 2 | 96 |
| `presencial` | 3 | 1 | 65 |
| `training` | 1 | 1 | 13 |
| `quiz` | **0** | 0 | 3 |
| `certificates` | **0** | 0 | 3 |
| `ergobot_ai` | **0** | 0 | 3 |
| `landing` | **0** | 0 | 3 |
| **Total** | **23** | 7 | — |

**Cobertura desbalanceada frente al riesgo.** Los tests existentes se concentran en el último trabajo realizado (visibilidad y control de acceso de capacitaciones personalizadas, autenticación). Quedan **sin ningún test**:

- El **motor de reglas del quiz** (`services.py`) — lockouts de 24 h, ventana de 3 intentos, cool-off tras aprobar, resets automáticos. Es la lógica de negocio más compleja y sutil del sistema, con manejo de tiempo y concurrencia.
- La **generación de certificados** — creación, PDF, guardado y los 4 destinatarios de email.
- El **chat Ergobot**.

No ejecuté la suite: hacerlo en este servidor requiere crear una base de datos de test, lo cual excede el alcance de una auditoría de solo lectura sobre producción. El README documenta `python manage.py test apps.accounts apps.dashboard apps.presencial` — nótese que **el propio comando documentado ya omite `quiz` y `certificates`**.

No hay CI configurado en el repo, ni linter, ni formateador, ni pre-commit.

**Deuda de mantenibilidad menor pero visible:** `apps/certificates/views.py` y `apps/certificates/pdf.py` contienen **versiones anteriores completas del archivo comentadas como docstring gigante al final** (duplicando ~200 líneas cada uno). Los comentarios de todo el código están anclados a números de commit ("COMMIT 8", "COMMIT 16", "COMMIT 21") que ya no se corresponden con el historial real de Git.

---

# 10. LO QUE FIGURA COMO PENDIENTE EN EL PROPIO PROYECTO

Fuente: `ERGOSOLUTIONS_ARQUITECTURA_ROADMAP.md` (827 líneas, fechado febrero 2026), `MAPA_CONCEPTUAL_VISUAL.md`, `PLAN_EMAIL_PRODUCCION.md`, `DEPLOY_CLAUDE_RUNBOOK.md` y marcadores en el código.

### 10.1 Estado del roadmap declarado

| Fase | Alcance | Estado real verificado |
|---|---|---|
| **1. Fundamentos** | `CustomUser`, auth dual, reorganización de URLs | ✅ **Completa** |
| **2. Landing + auth profesional** | Landing, registro, login | ✅ **Completa** |
| **3. Dashboard + menú** | Panel, grid de capacitaciones, selector de modalidad | ✅ **Completa** |
| **4. Modo presencial** | Página, planilla PDF, `PresencialSession` | ✅ **Completa** |
| **5. Modo online** | `CapacitacionLink`, compartir, rutas `/c/<slug>/` | ✅ **Completa** |
| **6. Mejoras y pulido** | Perfil, más capacitaciones, testing | 🟡 **Parcial**: perfil ✅ / **contenido adicional ❌** / **testing parcial** |
| **7. Futuro** | Evaluaciones + Suscripciones + Pagos + Facturación | 🔴 **No iniciada** |

### 10.2 Pendientes explícitos

**A) Módulo de EVALUACIONES — el segundo pilar del producto, sin construir**
El roadmap lo define como una de las dos patas de la plataforma (*"Evaluaciones de riesgos ergonómicos, iluminación, ruido y más, todo según normativa vigente"*). Hoy es una **card gris con badge "Próximamente"** en `templates/dashboard/home.html`. No existe la app `evaluaciones`, ni modelos, ni rutas. El roadmap contemplaba `/evaluaciones/` y `/evaluaciones/<tipo>/`.

**B) Sistema de SUSCRIPCIONES — infraestructura lista, lógica ausente**
Está **preparado y desactivado**, deliberadamente:
- `CustomUser` ya tiene `subscription_tier`, `subscription_status`, `subscription_expires` y la propiedad `has_active_subscription` (que valida estado + vencimiento).
- Existe el decorador `@subscription_required(tier='basic')` y el mixin `SubscriptionRequiredMixin` con jerarquía `free(0) < basic(1) < premium(2)`.
- **Ninguna vista los usa.** No hay pasarela de pago, planes, facturación ni gestión de ciclo de vida de la suscripción.

**C) Capacitaciones adicionales (Fase 6.2)** — 5 módulos definidos sin video, contenido ni preguntas. Es trabajo de contenido, no de código.

**D) TODO explícito en el código** — `apps/certificates/views.py`:
```python
def my_certificates(request):
    """... TODO: Implementar template si se necesita una vista de lista."""
```
`/certificados/` devuelve **JSON crudo** al navegador. Un trabajador que llegue a esa URL ve un volcado técnico, no una página. Es la única ruta con una experiencia claramente inacabada.

**E) `prompts/modules/<slug>.md`** — `build_system_prompt` busca instrucciones específicas por módulo en ese directorio, que **no existe**. Es un punto de extensión previsto, sin usar.

**F) Pendientes de infraestructura anotados en el `.env`** — la línea de `CSRF_TRUSTED_ORIGINS` está escrita como comentario, junto con la nota de que `settings.py` no la lee.

**G) `PLAN_EMAIL_PRODUCCION.md`** — este plan **sí se ejecutó completo**: el bug `ADMIN_CERT_EMAIL` vs `ADMIN_EMAIL` está corregido, `EMAIL_USE_SSL` y `SERVER_EMAIL` están en `settings.py`, la validación de credenciales SMTP está implementada, `.env.example` está completo y existe `send_test_email`. Documento cerrado.

---

# 11. HALLAZGOS TÉCNICOS Y RIESGOS

Ordenados por severidad. Los clasifico entre **operativos** (afectan la continuidad hoy), **latentes** (bugs reales que no se disparan con el uso actual) y **de deuda**.

### 🔴 CRÍTICO — Operativo

**H1. No existe backup automatizado de la base de datos de producción.**
`/etc/cron.d/` contiene únicamente `criaapp-backup` (la app beta vecina, con dump diario a las 03:30 y retención de 7 días). **ErgoSolutions, que es la aplicación productiva, no tiene ninguno.** No hay crontab del usuario `deploy`, ni timer systemd, ni script de backup. El único dump existente es `/home/deploy/backup_pre_criaapp_20260624_205004/ergocapacitacion_db.dump` (95 KB), tomado **manualmente el 24/06/2026** como precaución antes de instalar CriaApp — hoy tiene **36 días de antigüedad**.

Concretamente: una pérdida del volumen implicaría perder los 15 certificados emitidos, los 18 usuarios y todo el historial de evaluaciones, con recuperación posible solo hasta el 24/06. Los PDFs en `media/` tampoco están respaldados (aunque son regenerables desde los datos). La base pesa 10 MB: un backup diario cuesta prácticamente nada.

### 🟠 ALTO

**H2. Los certificados PDF son descargables sin autenticación.** (detalle en §6.6)
Verificado en vivo: `GET /media/certificates/certificado_<uuid>.pdf` → **HTTP 200**, PDF completo, sin sesión. El control de propiedad implementado en las vistas de Django queda anulado por el `alias` de nginx. Los PDFs contienen **nombre completo y CUIL** — datos personales. La única barrera es lo impredecible del UUIDv4.

**H3. Ausencia de rotación de logs.**
`gunicorn-access.log` acumula **23 MB / 158.261 líneas desde el 20/02/2026** sin rotar jamás. No hay entrada en `/etc/logrotate.d/` para ergocapacitación (sí la hay para nginx, postgres, redis). Con el 65% del tráfico siendo escaneo de bots, el crecimiento es constante e independiente del uso real. No es urgente con 15 GB libres, pero es un archivo que solo crece y que además hace más lento cualquier diagnóstico.

**H4. `main` está 4 meses y ~20 commits detrás de producción.**
Riesgo de que un futuro trabajo (propio o de terceros) parta de `main` y regenere/pise funcionalidad ya desplegada. Producción corre `release/beta`, no la rama por defecto del repositorio.

### 🟡 MEDIO — Bugs latentes confirmados

Los siguientes son fallos **reales y verificados** en el código, que hoy **no se manifiestan** porque el orden de los decoradores los enmascara. Cualquier refactor que altere ese orden los activa.

**H5. `reverse('professional_login')` lanza `NoReverseMatch`.**
Verificado ejecutando `reverse()` contra el URLconf en vivo:

| Nombre invocado en el código | Resultado |
|---|---|
| `reverse('professional_login')` | ❌ **NoReverseMatch** |
| `reverse('landing')` | ❌ **NoReverseMatch** |
| `reverse('dashboard')` | ❌ **NoReverseMatch** |
| `reverse('accounts_professional:professional_login')` | ✅ `/auth/login/` |
| `reverse('trainee_landing')` | ✅ `/acceso/` |
| `reverse('dashboard:home')` | ✅ `/dashboard/` |

La causa es que `urls_professional.py` se incluye con `namespace="accounts_professional"`, por lo que el nombre plano dejó de existir; y `landing` fue renombrado a `trainee_landing` en el Commit 12 (para no colisionar con el namespace de la app institucional), pero los decoradores y mixins quedaron con el nombre viejo.

Puntos afectados: `accounts/decorators.py::professional_required` (rama de usuario no autenticado), `::trainee_required`, `::subscription_required`, `accounts/mixins.py::ProfessionalRequiredMixin.get_login_url()` y `.handle_no_permission()` (`redirect('dashboard')`), `TraineeRequiredMixin.get_login_url()`.

**Por qué no explota hoy:** todas las vistas del dashboard y de presencial se declaran como `@login_required` **antes** de `@professional_required`, de modo que el usuario anónimo es redirigido por `login_required` y la rama defectuosa nunca se ejecuta. Los mixins no se usan (todas las vistas son basadas en función). Es una **bomba de tiempo**: quitar un `@login_required`, o migrar cualquier vista a CBV, produce un HTTP 500.

**H6. El portal profesional redirige al login equivocado.**
Consecuencia directa de lo anterior. Verificado en vivo:
```
GET /dashboard/  (sin sesión)  →  302  →  /acceso/?next=/dashboard/
```
`settings.LOGIN_URL = "trainee_landing"`, así que un **profesional** que abre un enlace directo al dashboard con la sesión vencida aterriza en el **formulario de CUIL + email de trabajadores**, no en `/auth/login/`. Igual ocurre con `/dashboard/perfil/`, `/dashboard/capacitaciones/…` y todas las rutas de presencial. Es un defecto de experiencia de usuario en producción, hoy activo y observable.

**H7. Los links vencidos siguen dando acceso.** (detalle en §6.3) `expires_at` e `is_active` solo gobiernan el contador de accesos, no el acceso en sí.

**H8. Campo inexistente en el quiz presencial.**
`apps/presencial/views.py`, en la construcción del detalle de corrección:
```python
"explanation": q.explanation if hasattr(q, "explanation") else "",
```
El modelo `Question` **no tiene** el campo `explanation` (se llama `explanation_correct`). El `hasattr` evita el crash, pero el resultado es que **la explicación siempre llega vacía** en el modo presencial: la retroalimentación pedagógica que sí existe en el modo online simplemente no se muestra en la capacitación grupal.

**H9. Umbral de aprobación duplicado.**
El modo presencial usa `passed = correct >= 8` **hardcodeado**, en lugar de importar `PASS_SCORE` de `apps.quiz.services`. Si mañana se cambia el umbral, las dos modalidades quedan desalineadas silenciosamente.

**H10. Dependencia implícita de gunicorn para el manejo de HTTPS.** (detalle en §3.3) Sin `SECURE_PROXY_SSL_HEADER`, cualquier cambio de servidor de aplicación rompe todos los POST del sitio con 403.

**H11. Envío de email síncrono dentro del request.** (detalle en §6.6) Hasta 4 emails con adjunto contra Gmail bloqueando 1 de 3 workers, con timeout de 60 s.

**H12. Vista async sobre workers WSGI sync.** (detalle en §6.7) Cada conversación con Ergobot inmoviliza un worker completo; 3 chats concurrentes agotan la capacidad del sitio.

### 🔵 BAJO — Hardening y deuda

| # | Hallazgo |
|---|---|
| H13 | `SESSION_COOKIE_SECURE=False` y `CSRF_COOKIE_SECURE=False`: las cookies no llevan flag `Secure`. Mitigado por el redirect 301 de nginx, pero no es defensa en profundidad. |
| H14 | `SECURE_HSTS_SECONDS=0`: sin HSTS. |
| H15 | `CSRF_TRUSTED_ORIGINS` vacío (anotado como pendiente en el propio `.env`). |
| H16 | **Registro de profesionales abierto al público**, sin verificación de email ni aprobación. |
| H17 | Sin protección contra fuerza bruta en los logins (no hay `django-axes` ni rate limiting en nginx). No se observan intentos en el log, pero tampoco hay defensa. |
| H18 | Sin fijado de versiones en `requirements.txt`; `openai-agents` declarado `>=0.0.19` con 0.9.2 instalado. |
| H19 | Sin monitoreo ni alertas: no hay Sentry, ni healthcheck externo, ni notificación de caída. `/acceso/health/` existe pero nadie lo consulta. |
| H20 | Datos de firma del certificado **hardcodeados** en `pdf.py` (nombre, matrícula y especialidad de Pablo Aguirre). Bloquea que otro profesional emita certificados con su propia firma — incompatible con el modelo SaaS multi-profesional que plantea el roadmap. |
| H21 | `certificates/views.py` y `pdf.py` arrastran copias completas del archivo anterior comentadas al final (~400 líneas muertas). |
| H22 | `/certificados/` devuelve JSON crudo (TODO reconocido en el código). |
| H23 | `send_mail(..., fail_silently=True)` en `share_link` con `except: pass`: si el envío falla, el contador informa "enviado a N emails" igualmente. Los `LinkShareLog` se crean aunque el email no haya salido. |
| H24 | `participants_count` se recibe por **query string** (`?participants=`) en `planilla_pdf`, y quedó en 0 en las 2 sesiones registradas. El dato de negocio se está perdiendo. |
| H25 | Comentarios de código anclados a "COMMIT N" que ya no mapean al historial real de Git. |
| H26 | `README.md` declara "Async: ASGI + Uvicorn", que no es el despliegue real (WSGI + gunicorn sync). |
| H27 | Sin CI, sin linter, sin formateador, sin pre-commit hooks. |

---

# 12. RECOMENDACIONES PRIORIZADAS

Ninguna de estas acciones fue ejecutada. Las dejo ordenadas por relación impacto/esfuerzo.

### Inmediato (esta semana, sin tocar código)
1. **Backup diario de `ergocapacitacion_db`** replicando el patrón ya probado de CriaApp: `pg_dump` custom + retención de 7 días vía `/etc/cron.d/`. Incluir `media/certificates/`. Es la única recomendación que califico como urgente. *(≈30 min)*
2. **Logrotate para `/srv/ergocapacitacion/logs/*.log`**: rotación semanal, 8 copias, `copytruncate` (gunicorn no reabre descriptores con SIGHUP por defecto). *(≈10 min)*
3. **Restringir `/media/`**: mover los certificados detrás de Django (`X-Accel-Redirect` con `internal;` en nginx) para que la verificación de propiedad sea efectiva. *(≈1 h)*

### Corto plazo (correcciones de código, sin cambio funcional)
4. Corregir los nombres de URL en `decorators.py` y `mixins.py` (`professional_login` → `accounts_professional:professional_login`, `landing` → `trainee_landing`, `dashboard` → `dashboard:home`) — **H5**.
5. Redirigir el área profesional a su propio login: pasar `login_url` explícito en los `@login_required` del dashboard/presencial, o resolver el destino según el tipo de usuario — **H6**.
6. Hacer que `expires_at` / `is_active` efectivamente bloqueen el acceso en `public_landing` — **H7**.
7. `explanation_correct` en el quiz presencial e importar `PASS_SCORE` en lugar del `8` literal — **H8/H9**.
8. Agregar `SECURE_PROXY_SSL_HEADER`, `CSRF_TRUSTED_ORIGINS`, `SESSION_COOKIE_SECURE`, `CSRF_COOKIE_SECURE` y HSTS a `settings.py` — **H10/H13/H14/H15**.
9. Alinear `main` con `release/beta` (o declarar formalmente `release/beta` como rama de producción y documentarlo) — **H4**.

### Medio plazo (habilitan crecimiento)
10. **Tests del motor de reglas del quiz y del pipeline de certificados** — las dos piezas de mayor riesgo con cobertura cero.
11. **Cargar contenido de los 5 módulos inactivos.** Es el desbloqueo de negocio de mayor retorno: la plataforma está construida y solo tiene un curso para vender.
12. **Migrar a ASGI (uvicorn)** — ya está preparado — y **mover los emails a background**. Sin esto, la app no soporta uso concurrente real de Ergobot ni picos de certificación — **H11/H12**.
13. **Parametrizar la firma del certificado** por profesional (nombre, matrícula, especialidad, y eventualmente logo) — prerequisito estructural para el modelo SaaS — **H20**.
14. Cerrar el registro abierto de profesionales (invitación o verificación de email) y agregar rate limiting en los logins — **H16/H17**.
15. Monitoreo mínimo: healthcheck externo sobre `/acceso/health/` + alerta, y fijado de versiones en `requirements.txt`.

### Estratégico (Fase 7 del roadmap)
16. Módulo de **Evaluaciones** — el segundo pilar declarado del producto, hoy inexistente.
17. Activar **Suscripciones**: la estructura de datos y los decoradores ya existen; falta pasarela de pago, planes y ciclo de vida.

---

## Nota de cierre

El proyecto está **técnicamente sano y bien diseñado** en su núcleo: separación clara de responsabilidades, reglas de negocio del lado del servidor, manejo correcto de concurrencia en el quiz, control de acceso consistente en el dashboard, y un pipeline de certificación con degradación elegante ante fallos. Los defectos que encontré son mayormente **latentes** (enmascarados por el orden de los decoradores) o de **operación** (backups, rotación de logs), no fallas de arquitectura.

El cuello de botella real no es el código: es que **una plataforma completa está sirviendo un solo curso y no registra usuarios desde hace tres meses**. La brecha entre lo construido y lo utilizado es el hallazgo más significativo de esta auditoría.
