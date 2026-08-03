# ESTADO TÉCNICO CONSOLIDADO — ErgoSolutions (ergocapacitacion)

**Documento:** Informe técnico integral y línea de base para la continuación del desarrollo
**Fecha de emisión:** 1 de agosto de 2026
**Autor del relevamiento:** Revisión técnica de código sobre el repositorio local de desarrollo
**Insumo primario:** [Informe técnico de auditoría de producción del 30/07/2026](INFORME_TECNICO_AUDITORIA_PRODUCCION_2026-07-30.md)
**Rama analizada:** `release/beta` @ `89ad9ef` (Commit 48, tag `v0.1.7-beta`)
**Entorno productivo de referencia:** `https://www.ergosolutions.com.ar/` — VPS `vps-4625086-x` @ `660dc1b` (tag `v0.1.3-beta`)

---

## Propósito y cómo leer este documento

Este documento cumple tres funciones, en este orden:

1. **Consolidar** la auditoría de producción del 30/07/2026 con el estado real del código en desarrollo, que la auditoría no cubrió.
2. **Verificar** cada hallazgo de aquella auditoría contra el código actual, indicando cuáles siguen vigentes, cuáles se corrigieron y cuáles empeoraron.
3. **Servir de punto de partida** para retomar el desarrollo: inventario completo, mapa de riesgos priorizado y plan de trabajo secuenciado.

> **Advertencia de alcance.** La auditoría del 30/07/2026 se ejecutó **sobre el servidor de producción** y describe con precisión el despliegue `v0.1.3-beta`. Este documento **no la reemplaza ni la contradice en lo que respecta a infraestructura**: los datos de VPS, nginx, systemd, TLS, tráfico y base de datos productiva se reproducen aquí como fueron reportados y **no fueron reverificados** (no se accedió al servidor en esta revisión). Lo que sí se verificó, ejecutando el código, es **todo lo relativo al repositorio de desarrollo**, que es donde vive la Etapa 3 que producción todavía no conoce.

### Convención de trazabilidad

Cada afirmación de este documento lleva implícito uno de tres orígenes:

| Marca | Significado |
|---|---|
| **[AUD]** | Proviene de la auditoría de producción del 30/07/2026. No reverificado en esta revisión. |
| **[VER]** | **Verificado empíricamente** en esta revisión ejecutando el código de desarrollo (Django 5.2.10 / Python 3.11.2, base de datos de test efímera). |
| **[COD]** | Verificado por lectura directa del código fuente en `release/beta` @ `89ad9ef`. |

---

# PARTE I — SÍNTESIS EJECUTIVA

## 1.1 El estado en una frase

ErgoSolutions tiene **dos versiones de sí mismo que no se hablan**: una en producción, estable, congelada hace cinco meses y sirviendo un solo curso a cero usuarios; y otra en desarrollo, con una etapa completa de funcionalidad empresarial construida, testeada y pusheada al repositorio remoto desde el 7 de marzo de 2026, que **nunca se desplegó** y que **contiene una regresión que devuelve HTTP 500 en seis rutas del backoffice**.

## 1.2 Cuadro de mando

| Dimensión | Producción (`v0.1.3-beta`) | Desarrollo (`v0.1.7-beta`) |
|---|---|---|
| Commit | `660dc1b` — 28/02/2026 **[AUD]** | `89ad9ef` — 07/03/2026 **[COD]** |
| Disponibilidad | ✅ Online, ~80 ms, uptime 7 días **[AUD]** | n/a |
| Apps Django | 8 **[AUD]** | **10** (+`company`, +`landing` ya contada) **[VER]** |
| Modelos de dominio | 9 **[AUD]** | **13** (+4 de empresa) **[VER]** |
| Migraciones propias | 9 **[COD]** | **15** (+6 sin aplicar en prod) **[VER]** |
| Templates | 21 **[AUD]** | **33** **[VER]** |
| Líneas de Python (sin migraciones) | ~6.100 **[AUD]** | **7.924** **[VER]** |
| Tests | 23, todos en verde **[AUD]** | **32, todos en verde** **[VER]** |
| Tipos de usuario | 2 (profesional, trabajador) | **3** (+empresa) **[COD]** |
| Catálogo de contenido | 🔴 1 de 6 módulos activo **[AUD]** | 🔴 Sin cambios — sigue 1 de 6 **[COD]** |
| Actividad de usuarios | 🔴 Ninguna desde el 23/04/2026 **[AUD]** | n/a |
| Backup automatizado de BD | 🔴 Inexistente **[AUD]** | n/a |
| Rotación de logs | 🔴 Inexistente **[AUD]** | n/a |
| Regresiones bloqueantes | Ninguna conocida | 🔴 **2 críticas verificadas** **[VER]** |

## 1.3 Los cinco hechos que gobiernan las decisiones

**1. Producción está 20 commits y 5 meses por detrás de su propia rama.**
El servidor corre `HEAD detached` en el tag `v0.1.3-beta`. La rama `origin/release/beta` — la misma de la que salió ese tag — ya contiene hasta el Commit 48. **Todo el trabajo de la Etapa 3 está pusheado al remoto desde el 07/03/2026 y nunca se desplegó.** **[VER]**

> **Corrección a la auditoría.** El informe del 30/07/2026 (§2.2) consigna `origin/release/beta` en `660dc1b` del 28/02/2026. Eso describe el estado del *clon del servidor*, cuyo `git fetch` estaba desactualizado, no el estado del repositorio remoto. El `reflog` local muestra los pushes de los Commits 44 a 48 hacia `origin/release/beta`. La rama remota real está en `89ad9ef`. **[VER]**

**2. La Etapa 3 no es desplegable hoy.**
Seis rutas del backoffice devuelven **HTTP 500 a cualquier usuario no autenticado**. No es una hipótesis: se reprodujo. La causa es la bomba de tiempo que la auditoría describió como latente (**H5**), que la Etapa 3 armó al usar `@company_required` y `@professional_required` sin el `@login_required` que hasta ahora la enmascaraba. **[VER]**

**3. Dos de los cuatro commits finales de la Etapa 3 son funcionalmente inertes.**
El directorio de profesionales (Commit 46) y las solicitudes de contacto (Commit 47) dependen del flag `is_visible_in_directory`, que nace en `False` y **no tiene ningún control que lo active**: no está en el admin de Django ni en el formulario de perfil profesional. El directorio siempre se verá vacío. Los tests pasan porque asignan el flag directamente en Python. **[VER]**

**4. El cuello de botella del negocio no cambió.**
La auditoría lo señaló como su hallazgo más significativo y sigue intacto: **una plataforma completa sirviendo un solo curso**. Los cinco módulos restantes siguen sin video, sin material y sin preguntas. La Etapa 3 agregó superficie de gestión, no contenido vendible. **[COD]**

**5. La deuda operativa de producción sigue sin tocarse.**
No hay backup automatizado de `ergocapacitacion_db`, no hay logrotate y los certificados PDF siguen siendo descargables sin autenticación por URL directa. Ninguno de estos tres puntos requiere tocar código de aplicación, y el primero es el único ítem de esta lista que califica como urgente. **[AUD]**

## 1.4 Recomendación de secuencia

El orden que se desprende del análisis, y que se desarrolla en la [Parte VII](#parte-vii--plan-de-trabajo):

```
Bloque 0  →  Backup + logrotate en producción           (sin tocar código, ~40 min)
Bloque 1  →  Reparar las regresiones de Etapa 3         (bloquea cualquier deploy)
Bloque 2  →  Cerrar hallazgos H5–H10 heredados          (misma familia de defectos)
Bloque 3  →  Endurecer settings + /media/               (seguridad)
Bloque 4  →  Desplegar v0.1.8-beta a producción         (primer deploy en 5 meses)
Bloque 5  →  Contenido de los 5 módulos                 (desbloqueo comercial)
Bloque 6  →  ASGI + emails en background                (escalabilidad)
Bloque 7  →  Evaluaciones y Suscripciones (Fase 7)      (producto)
```

---

# PARTE II — METODOLOGÍA

## 2.1 Qué se hizo en esta revisión

| Actividad | Detalle |
|---|---|
| Lectura de código | Totalidad de `apps/`, `config/`, `templates/`, más `README.md` y `AGENTS.md` |
| Análisis de historia Git | Ramas, tags, reflog, diffs entre `660dc1b` y `89ad9ef` |
| Resolución de URLs | Ejecución de `reverse()` contra el URLconf real, 12 nombres probados |
| Pruebas funcionales | Cliente de test de Django contra base de datos efímera, con usuarios de los tres tipos |
| Suite de tests | `python manage.py test apps` completa |
| Chequeo de despliegue | `manage.py check --deploy` con `DEBUG=False` |
| Inventario cuantitativo | Conteo de archivos, líneas, modelos, migraciones, templates |

## 2.2 Qué NO se hizo

- **No se accedió al servidor de producción.** Toda la Parte IV es reproducción de la auditoría del 30/07/2026.
- **No se modificó ningún archivo del proyecto.** La única escritura fue este documento.
- **No se ejecutaron migraciones ni comandos de seed** contra la base de datos de desarrollo. Las pruebas usaron bases de datos de test creadas y destruidas en el mismo proceso.
- **No se corrigió ningún defecto.** Este documento es diagnóstico; las correcciones se proponen, no se aplican.

## 2.3 Entorno de verificación

| Componente | Valor local | Valor en producción **[AUD]** |
|---|---|---|
| Python | 3.11.2 | 3.10.12 |
| Django | 5.2.10 | 5.2.11 |
| Base de datos | PostgreSQL local `ergocapacitacion` | PostgreSQL 14 `ergocapacitacion_db` |
| `DEBUG` | `True` | `False` |

> **Nota sobre la diferencia de intérprete.** Desarrollo corre Python 3.11 y producción 3.10. No se detectó uso de sintaxis exclusiva de 3.11, pero la divergencia no está declarada en ningún archivo del repositorio (no hay `.python-version`, `runtime.txt` ni `pyproject.toml`) y conviene fijarla antes del próximo despliegue.

---

# PARTE III — LA BRECHA PRODUCCIÓN ↔ DESARROLLO

## 3.1 Mapa de versiones

| Tag | Commit | Fecha | Contenido | ¿En producción? |
|---|---|---|---|---|
| `v0.1.0-beta` | `a146613` | 20/02/2026 | Runbook de despliegue y docs de operación | — |
| `v0.1.1-beta` | `7e4c544` | 22/02/2026 | `seed_modules` canónico e idempotente | — |
| `v0.1.2-beta` | `0d08faa` | 22/02/2026 | Contenido canónico de Ergonomía + import robusto de quiz | — |
| `v0.1.3-beta` | `660dc1b` | 28/02/2026 | Tests de visibilidad de capacitaciones personalizadas | ✅ **Es lo que corre** |
| `v0.1.4-beta` | `d0d15a1` | 05/03/2026 | Etapa 3A completa — Perfil de Empresa | ❌ |
| `v0.1.5-beta` | `93b4783` | 06/03/2026 | Etapa 3B completa — Nómina | ❌ |
| `v0.1.6-beta` | `3283a17` | 06/03/2026 | Etapa 3C completa — Agenda y vencimientos | ❌ |
| `v0.1.7-beta` | `89ad9ef` | 07/03/2026 | Etapa 3D completa — Directorio, contacto y testing | ❌ |

## 3.2 Estado de las ramas

| Rama | Commit | Fecha | Situación |
|---|---|---|---|
| `release/beta` (local) | `89ad9ef` | 07/03/2026 | Rama de trabajo activa |
| `origin/release/beta` | `89ad9ef` | 07/03/2026 | **Sincronizada con local** — contiene toda la Etapa 3 |
| `main` / `origin/main` | `074fbab` | 02/02/2026 | 🔴 **Rama por defecto del repositorio, 40 commits y 6 meses atrás** |
| `feature/ergosolutions-saas` | — | 20/02/2026 | Rama histórica sin mergear |
| `claude/nice-blackwell` | — | — | Rama auxiliar local |

**El problema de `main` empeoró.** La auditoría lo reportó como "4 meses y ~20 commits detrás". Hoy son **6 meses y 40 commits**. `main` está en el "Commit 8" (emails a empleador y SySO) y desconoce por completo la refactorización a `CustomUser`, la landing, el dashboard, el modo presencial, los links compartibles, las capacitaciones personalizadas **y toda la Etapa 3 de empresas**. Cualquier clon nuevo del repositorio aterriza por defecto en una aplicación que no se parece ni a la que está en el aire ni a la que está en desarrollo. **[VER]**

## 3.3 Los 20 commits que producción no tiene

| # | Commit | Descripción | Etapa |
|---|---|---|---|
| 29 | `14ad38c` | `user_type='company'` en `CustomUser` | 3A |
| 30 | `e783ebb` | Modelo `CompanyProfile` y nueva app `apps.company` | 3A |
| 31 | `4ad25a8` | Decoradores y permisos para backoffice multi-tipo | 3A |
| 32 | `373858b` | Registro y autenticación de Empresa (`/empresa/auth/`) | 3A |
| 33 | `dccba25` | Refactorización del dashboard para backoffice multi-tipo | 3A |
| 34 | `d0d15a1` | Perfil de Empresa (edición y vista) | 3A |
| 35 | `b778daf` | Modelo `CompanyWorker` | 3B |
| 36 | `b56a58f` | Vista de Nómina con búsqueda y filtros | 3B |
| 37 | `0c37bbb` | Alta manual de trabajadores en nómina | 3B |
| 38 | `068b90f` | Ficha individual del trabajador | 3B |
| 39 | `595739b` | Edición de datos laborales | 3B |
| 40 | `93b4783` | Exportación de nómina a CSV | 3B |
| 41 | `252b43b` | Modelo `AgendaEvent` | 3C |
| 42 | `e409731` | Vista de Agenda — listado y filtros | 3C |
| 43 | `7e1ef36` | CRUD de eventos de agenda | 3C |
| 44 | `02f52fd` | Comando `generate_cert_expiry_events` | 3C |
| 45 | `3283a17` | Panel de vencimientos en dashboard de empresa | 3C |
| 46 | `721d5e2` | Directorio básico de profesionales | 3D |
| 47 | `e13d180` | Solicitudes de contacto empresa↔profesional | 3D |
| 48 | `89ad9ef` | Testing integral de Etapa 3 | 3D |

**Volumen del cambio:** 44 archivos tocados, **+3.883 / −17 líneas**, 33 archivos nuevos. **[VER]**

## 3.4 Migraciones pendientes de aplicar en producción

Un despliegue de `v0.1.7-beta` requiere aplicar **6 migraciones** sobre `ergocapacitacion_db`: **[VER]**

```
apps/accounts/migrations/0002_add_company_user_type.py
apps/accounts/migrations/0003_add_is_visible_in_directory.py
apps/company/migrations/0001_create_company_profile.py
apps/company/migrations/0002_create_company_worker.py
apps/company/migrations/0003_create_agenda_event.py
apps/company/migrations/0004_create_contact_request.py
```

Las seis son **aditivas** (nuevas tablas y nuevas columnas con `default`). No hay renombrados, borrados de columna ni `RunPython` destructivo, por lo que el riesgo de la migración en sí es bajo. Aun así, **no debe ejecutarse sin un dump previo**, que hoy no existe de forma automatizada (ver [H1](#h1--crítico--sin-backup-automatizado-de-la-base-de-producción)).

## 3.5 Cambios sin commitear en el árbol de trabajo

`git status` muestra trabajo de reorganización documental **no commiteado**: **[VER]**

| Archivo | Estado | Observación |
|---|---|---|
| `docs/` | Sin trackear | Directorio nuevo con 11 documentos, incluida la auditoría |
| `DEPLOY_CLAUDE_RUNBOOK.md` | Borrado | Movido a `docs/` |
| `ERGOSOLUTIONS_ARQUITECTURA_ROADMAP.md` | Borrado | Movido a `docs/` |
| `MAPA_CONCEPTUAL_VISUAL.md` | Borrado | Movido a `docs/` |
| `PLAN_EMAIL_PRODUCCION.md` | Borrado | Movido a `docs/` |
| `README.md` | Modificado | +17 líneas: sección de documentación y registro de cambios |
| `.gitignore` | Modificado | Deja de ignorar los planes maestros; pasa a ignorar `AGENTS.md`, `backup_contenido.json` y `training_modules.json` |

**Consecuencia relevante del cambio en `.gitignore`:** los planes maestros (`PLAN_MAESTRO_*`, ~11.000 líneas) dejan de estar ignorados y, al commitear, entrarán al repositorio. Es un cambio deseable para la trazabilidad, pero conviene que sea una decisión consciente y no un efecto colateral.

---

# PARTE IV — ESTADO DE PRODUCCIÓN

> Toda esta parte reproduce la auditoría del 30/07/2026. **[AUD]** salvo indicación en contrario.

## 4.1 Identidad del despliegue

| Ítem | Valor |
|---|---|
| Repositorio | `git@github.com:praguirre/ergocapacitacion.git` |
| Directorio de código | `/srv/ergocapacitacion/app` |
| Estado de Git | `HEAD detached` en `v0.1.3-beta` = `660dc1bd1789b3efe346f78eb93777f14310f5c7` |
| Árbol de trabajo | Limpio, sin modificaciones locales |
| Fecha del commit desplegado | 28/02/2026 19:24 -03 |
| Commit inicial del proyecto | 21/01/2026 |
| Usuario de sistema | `deploy` |

## 4.2 Topología de ejecución

```
Internet
   │
   ▼ :80  → 301 → :443
nginx (server block "ergosolutions", sin default_server)
   │
   ├── /static/  → alias /srv/ergocapacitacion/app/staticfiles/   (expires 30d)
   ├── /media/   → alias /srv/ergocapacitacion/app/media/         (expires 7d)   ⚠️ ver H2
   └── /        → proxy_pass unix:/srv/ergocapacitacion/ergocapacitacion.sock
                     │
                     ▼
              gunicorn 25.1.0 — 3 workers sync, timeout 60 s
              config.wsgi:application
                     │
                     ▼
              Django 5.2.11 (Python 3.10.12)
                     │
                     ▼
              PostgreSQL 14 @ 127.0.0.1:5432 — ergocapacitacion_db
```

El VPS es **compartido** con la aplicación CriaApp (beta), completamente aislada: server block de nginx propio, base y rol de PostgreSQL propios, usuario de sistema propio (`criaapp`) y unidades systemd propias. Redis está instalado y corriendo, pero **ErgoSolutions no lo usa** — pertenece a CriaApp.

### 4.2.1 Unidad systemd

`/etc/systemd/system/ergocapacitacion.service`

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

**Estado al 30/07/2026:** `active (running)` desde el 23/07/2026 04:30, PID maestro 527, 217 MB de RSS, 2 min 26 s de CPU acumulada. Habilitado en boot. El `gunicorn-error.log` registra únicamente arranques y paradas limpias (10/06, 25/06, 23/07, coincidentes con mantenimientos del VPS) y **cero tracebacks**.

### 4.2.2 La dependencia implícita de HTTPS

Este es el detalle de infraestructura más importante del informe original y merece repetirse íntegro.

`settings.py` **no define** `SECURE_PROXY_SSL_HEADER`. Sin ese ajuste, Django detrás de un proxy no sabe que la conexión original fue HTTPS y **todos los POST de navegador deberían fallar con 403** por el chequeo de `Origin`. En la práctica no ocurre porque **gunicorn** traduce la cabecera `X-Forwarded-Proto: https` a `wsgi.url_scheme = https` mediante sus `secure_scheme_headers` por defecto, y el socket Unix cuenta como proxy confiable.

Se verificó empíricamente en su momento: un POST real con cabecera `Origin: https://…` a través de nginx devuelve **302** (aceptado), mientras que el mismo POST sin ese mecanismo devuelve **403**.

> **Funciona, pero por una dependencia implícita del servidor de aplicación, no por configuración explícita de Django.** Si se migra a uvicorn/ASGI, se cambia el proxy o se ajustan los `forwarded_allow_ips`, **todos los formularios del sitio se rompen de golpe.** Dado que la migración a ASGI figura en el plan de trabajo, este ítem deja de ser teórico.

### 4.2.3 TLS

| Ítem | Valor |
|---|---|
| Emisor | Let's Encrypt |
| CN / SAN | `ergosolutions.com.ar`, `www.ergosolutions.com.ar` |
| Emitido | 19/07/2026 |
| **Vence** | **17/10/2026** |
| Renovación | `certbot.timer` activo + `/etc/cron.d/certbot` |

### 4.2.4 Recursos del host

| Recurso | Estado |
|---|---|
| Disco `/` | 25 GB total, 11 GB usados, **15 GB libres (42 %)** |
| RAM | 1.963 MB total, 1.189 MB en uso, 623 MB en caché, **570 MB disponibles** |
| Swap | 2.048 MB, 142 MB en uso |
| Base de datos | **10 MB** |
| Media (certificados PDF) | **68 KB** (15 archivos) |
| Staticfiles | 5,2 MB |
| Logs de gunicorn | **23 MB** (access) + 16 KB (error) |

No hay presión de recursos. La RAM ajustada se explica por convivir con CriaApp (gunicorn + celery worker + celery beat) más PostgreSQL y Redis.

> **Proyección para la Etapa 3.** El despliegue de `v0.1.7-beta` no cambia el perfil de memoria de forma significativa (siguen siendo 3 workers sync), pero sí agrega 4 tablas y un `ImageField` para logos de empresa que escribirá en `media/company_logos/`. El espacio en disco es holgado; el punto de atención es el de siempre: **`media/` no está respaldado**.

## 4.3 Configuración efectiva de la aplicación

Archivo único `config/settings.py`, sin separación dev/prod, leyendo `/srv/ergocapacitacion/app/.env` (symlink a `/srv/ergocapacitacion/.env`, permisos `600`, propietario `deploy`, correctamente ignorado por `.gitignore`).

| Setting | Valor en producción | Valor en desarrollo **[VER]** |
|---|---|---|
| `DEBUG` | `False` ✅ | `True` |
| `ALLOWED_HOSTS` | `ergosolutions.com.ar`, `www.…`, `127.0.0.1`, `localhost` | `127.0.0.1`, `localhost` |
| `AUTH_USER_MODEL` | `accounts.CustomUser` | ídem |
| `LANGUAGE_CODE` / `TIME_ZONE` | `es-ar` / `America/Argentina/Buenos_Aires`, `USE_TZ=True` | ídem |
| `EMAIL_BACKEND` | `smtp.EmailBackend` — Gmail `smtp.gmail.com:587` TLS | `smtp.EmailBackend` |
| `DEFAULT_FROM_EMAIL` | `ErgoSolutions <consultaergosolutions@gmail.com>` | — |
| `ADMIN_EMAIL` | `praguirre@gmail.com` | — |
| `OPENAI_MODEL` | `gpt-4.1-mini-2025-04-14` | ídem (default) |
| `STORAGES.staticfiles` | `whitenoise.storage.CompressedManifestStaticFilesStorage` | ídem |
| `X_FRAME_OPTIONS` | `DENY` ✅ | ídem |
| `SESSION_COOKIE_AGE` | 1.209.600 s (14 días) | ídem |
| `CSRF_TRUSTED_ORIGINS` | `[]` ⚠️ | `[]` ⚠️ |
| `SECURE_SSL_REDIRECT` | `False` (lo cubre nginx) | ídem |
| `SESSION_COOKIE_SECURE` | **`False`** ⚠️ | ídem ⚠️ |
| `CSRF_COOKIE_SECURE` | **`False`** ⚠️ | ídem ⚠️ |
| `SECURE_HSTS_SECONDS` | **`0`** ⚠️ | ídem ⚠️ |
| `SECURE_PROXY_SSL_HEADER` | **`None`** ⚠️ | ídem ⚠️ |

**Ninguno de los ajustes de endurecimiento pendientes se incorporó en la Etapa 3.** El `manage.py check --deploy` sobre el código actual con `DEBUG=False` sigue arrojando las mismas advertencias: **[VER]**

```
security.W004  SECURE_HSTS_SECONDS no configurado
security.W008  SECURE_SSL_REDIRECT no está en True
security.W012  SESSION_COOKIE_SECURE no está en True
security.W016  CSRF_COOKIE_SECURE no está en True
```

*(Una quinta advertencia, `security.W009` sobre la longitud del `SECRET_KEY`, corresponde al `.env` local de desarrollo y no describe producción.)*

**Buena práctica que conviene preservar:** `settings.py` incorpora una validación defensiva propia — si el backend de email es SMTP y `DEBUG=False`, levanta `ImproperlyConfigured` cuando faltan `EMAIL_HOST_USER` o `EMAIL_HOST_PASSWORD`. La aplicación no arranca con el email mal configurado. **[COD]**

## 4.4 Datos reales al 30/07/2026

### 4.4.1 Volumen por tabla

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

### 4.4.2 Usuarios

- **2 profesionales**: `praguirre@gmail.com` (superusuario, alta 20/02, último acceso 15/03) y `praguirre23@hotmail.com` (alta 20/02, último acceso 30/07/2026).
- **16 trabajadores**, altas concentradas entre el 23/02 y el 06/03/2026, con una última el 19/04/2026. **12 de los 16 pertenecen a un mismo cliente** (dominio `@laslenas.com` — Valle de las Leñas / Nieves de Mendoza).

### 4.4.3 Actividad de capacitación

- **24 intentos de quiz**, todos sobre `ergonomia`, **15 aprobados** (62,5 % de tasa de aprobación).
- **15 certificados emitidos** entre el 23/02 y el 19/04/2026, **los 15 con `email_sent = True`** y sin un solo `email_error`. El pipeline de email funcionó al 100 %.
- **5 links generados**, 43 accesos acumulados:

| Etiqueta | Fecha | Accesos |
|---|---|---|
| Valle de las Leñas SA / Nieves de Mendoza SA - 23/02/2026 | 23/02 | **30** |
| Osvaldo prueba | 23/02 | 5 |
| Capacitación Simdel turno tarde | 26/02 | 5 |
| *(sin etiqueta)* | 19/04 | 2 |
| Vialidad | 22/02 | 1 |

- **2 sesiones presenciales** (22/02 y 26/02), ambas de Ergonomía, con `participants_count = 0` — el campo no se completó (ver [H24](#h24--participants_count-por-query-string)).
- **0 registros en `LinkShareLog`**: la función de compartir por email **nunca se usó**; los links se distribuyeron por otro canal.
- **11 conversaciones con Ergobot**, todas HTTP 200, última el 19/04/2026. Preguntas reales: *"Según el video, ¿cuál es el peso máximo que se puede levantar?"*.

### 4.4.4 Lectura de negocio de estos datos

Tres conclusiones que condicionan el roadmap:

1. **El producto funcionó cuando se usó.** 30 accesos desde un solo link, 15 certificados emitidos sin un fallo de email, 62,5 % de aprobación. El flujo completo — link → registro → video → chat IA → quiz → certificado → notificación — se ejecutó de punta a punta con usuarios reales.
2. **Toda la tracción vino de un cliente.** 12 de 16 trabajadores son del mismo grupo empresario. No hubo adquisición orgánica.
3. **Las funciones construidas más recientemente son las menos usadas.** `LinkShareLog` en 0, capacitaciones personalizadas asignadas en 0, y ahora la Etapa 3 completa sin desplegar. Existe un patrón de construcción por delante de la validación que conviene romper deliberadamente.

## 4.5 Análisis de tráfico

Log completo del 20/02/2026 al 30/07/2026: **158.261 líneas**.

**La aplicación no recibe usuarios reales desde el 23/04/2026.** El último request funcional de un trabajador fue una descarga de certificado el 19/04 y dos visitas a `/capacitacion/` el 20 y el 23/04.

| Tipo de tráfico | Volumen (últimas 20.000 líneas) |
|---|---|
| **404** (escaneo automatizado) | 12.947 (65 %) |
| **400** (payloads malformados de bots) | 4.880 (24 %) |
| 200 legítimos (mayormente `/` y `/robots.txt`) | 1.957 |
| 403 | 83 |
| 302 | 75 |

Los escaneos buscan WordPress (`/wp-login.php`, `/xmlrpc.php`), PHP (`eval-stdin.php` de PHPUnit) y **secretos** (`/.env` — 95 intentos; `/.git/config` — 104 intentos). **Ninguno tuvo éxito**: `.env` está fuera del `DocumentRoot` y `.git` no es accesible por HTTP. Es ruido de fondo de internet, no un ataque dirigido. No hay evidencia de fuerza bruta sobre `/auth/login/` ni `/admin/login/`.

## 4.6 Catálogo de contenido — sin cambios desde febrero

| ID | Slug | Título | Activo | Orden | YouTube | Intro | Material | Transcripción |
|---|---|---|---|---|---|---|---|---|
| 5 | `ergonomia` | **Ergonomía** | ✅ **Sí** | 1 | `IIgZp_NbsAE` | 1.936 car. | **13.810 car.** | 6.903 car. |
| 6 | `ruido` | Ruido | ❌ No | 2 | — | 0 | 0 | 0 |
| 1 | `riesgo-electrico` | Riesgo Eléctrico | ❌ No | 3 | — | 0 | 0 | 0 |
| 2 | `trabajo-en-altura` | Trabajo en Altura | ❌ No | 4 | — | 0 | 0 | 0 |
| 3 | `prevencion-incendios` | Prevención de Incendios | ❌ No | 5 | — | 0 | 0 | 0 |
| 4 | `elementos-proteccion-personal` | Elementos de Protección Personal | ❌ No | 6 | — | 0 | 0 | 0 |

**Este es el principal limitante de negocio del producto y no se movió en cinco meses.** Toda la maquinaria — links, quiz, certificados, IA, presencial, personalización, y ahora nómina, agenda y directorio — opera sobre **un único módulo de contenido**. Los otros cinco existen como placeholders con icono y color, sin video, sin material y **sin preguntas**: las 10 preguntas y 40 opciones cargadas pertenecen todas a `ergonomia`.

El contenido canónico de Ergonomía vive versionado en el repositorio (`apps/training/content/ergonomia/`: `intro.md`, `material.md`, `transcript.txt`) y se carga con `seed_module_content`. **Es un patrón replicable y ordenado**: producir un módulo nuevo es escribir tres archivos Markdown, cargar el `youtube_id`, sembrar 10 preguntas y activar el módulo. El costo es de contenido, no de ingeniería. **[COD]**

---

# PARTE V — ESTADO DEL CÓDIGO EN DESARROLLO

## 5.1 Inventario cuantitativo **[VER]**

| Métrica | Valor |
|---|---|
| Aplicaciones Django propias | **10** |
| Archivos Python (sin migraciones) | 103 |
| Líneas de Python (sin migraciones) | **7.924** |
| Migraciones propias | 15 |
| Modelos de dominio | **13** |
| Templates HTML | 33 (3.645 líneas) |
| Archivos JS propios | 2 (`quiz.js`, `ergobot_chat.js`) |
| Archivos CSS propios | 2 (`app.css`, `dashboard.css`) |
| Tests | **32** (todos en verde) |
| Documentos Markdown en `docs/` | 11 (~15.400 líneas) |

## 5.2 Mapa de aplicaciones

| App | Rol | Modelos | Estado | Novedad Etapa 3 |
|---|---|---|---|---|
| `accounts` | Usuarios y autenticación triple | `CustomUser` | ✅ Completa | +`user_type='company'`, +`is_visible_in_directory`, +`views_company`, +`urls_company` |
| `landing` | Home institucional pública | — | ✅ Completa | — |
| `dashboard` | Panel multi-tipo (profesional + empresa) | — | ✅ Completa | Refactorizado: despacho por tipo, +solicitudes de contacto |
| **`company`** | **Backoffice de empresa** | `CompanyProfile`, `CompanyWorker`, `AgendaEvent`, `ContactRequest` | 🟡 **Con defectos** | **App nueva completa** |
| `training` | Módulos y links compartibles | `TrainingModule`, `CapacitacionLink`, `LinkShareLog` | ✅ Completa | — |
| `quiz` | Evaluación con reglas de negocio | `Question`, `Choice`, `QuizAttempt`, `QuizState` | ✅ Completa | — |
| `certificates` | Certificados PDF y emails | `Certificate` | 🟡 Falta template de listado | — |
| `presencial` | Modalidad presencial | `PresencialSession` | ✅ Completa | — |
| `ergobot_ai` | Chat IA con streaming SSE | — | ✅ Completa | — |

## 5.3 Modelo de datos completo

### 5.3.1 Núcleo de identidad — `accounts_customuser`

Modelo unificado sobre `AbstractBaseUser + PermissionsMixin`, con `USERNAME_FIELD = email`. **[COD]**

| Grupo | Campos |
|---|---|
| **Discriminador** | `user_type ∈ {professional, trainee, company}` ← *`company` es nuevo* |
| **Comunes** | `email` (unique, indexado), `first_name`, `last_name`, `full_name` (legacy, sincronizado en `save()`) |
| **Profesional** | `username` (unique, nullable), `dni` (validador 7–8 dígitos), `profession`, `license_number` |
| **Trabajador** | `cuil` (unique, indexado), `job_title`, `company_name`, `employer_email`, `safety_responsible_email` |
| **Suscripción** *(preparada, inactiva)* | `subscription_tier ∈ {free,basic,premium}`, `subscription_status ∈ {none,active,expired,cancelled}`, `subscription_expires` |
| **Control** | `is_active`, `is_staff`, `date_joined`, **`is_visible_in_directory`** ← *nuevo, default `False`* |

**Manager custom:** `create_user`, `create_trainee` (fuerza `set_unusable_password()`), `create_professional` (exige password + username), **`create_company`** *(nuevo, exige password, username opcional)*, `create_superuser`.

**Propiedades:** `is_professional`, `is_trainee`, **`is_company`** *(nueva)*, **`is_backoffice_user`** *(nueva — `professional` ∪ `company`)*, `display_name`, `has_active_subscription`.

### 5.3.2 Dominio de empresa *(Etapa 3, íntegro)*

**`company_companyprofile`** — Relación `OneToOne` con `CustomUser` limitada a `user_type='company'`.

| Grupo | Campos |
|---|---|
| Empresa | `razon_social`, `nombre_comercial`, `cuit` (**unique**), `rubro`, `cantidad_trabajadores` |
| Contacto | `contacto_nombre`, `contacto_cargo`, `contacto_telefono` |
| Ubicación | `domicilio`, `localidad`, `provincia` |
| Estado | `account_status ∈ {active, pending_validation, suspended, inactive}` |
| Imagen | `logo` (`ImageField` → `media/company_logos/`) |
| Metadatos | `created_at`, `updated_at` |

**`company_companyworker`** — Relación formal empresa ↔ trabajador. FK a `CompanyProfile` y a `CustomUser` (limitado a `trainee`), más `employee_code` (legajo), `department` (sector), `position` (puesto), `is_active`, `start_date`, `end_date`, `notes`. Constraint único `(company, worker)`.

**`company_agendaevent`** — Evento genérico de agenda empresarial.

| Grupo | Campos |
|---|---|
| Relaciones | `company` (FK), `worker` (FK nullable), `created_by`, `assigned_professional` |
| Contenido | `title`, `description` |
| Clasificación | `event_type ∈ {training_due, certificate_expiry, professional_visit, evaluation_due, reminder, other}` |
| Estado | `status ∈ {pending, completed, overdue, cancelled}`, `priority ∈ {low, medium, high, urgent}` |
| Temporalidad | `start_at` (nullable), `due_at` (**obligatorio**) |
| Vínculo genérico | `related_object_type`, `related_object_id` |

Índices compuestos en `(company, status, due_at)` y `(company, event_type, due_at)`. Propiedad `is_overdue`.

> **Observación de diseño.** El campo `status` tiene el valor `overdue` en sus choices, pero **nada lo escribe jamás**: la vencimiento se calcula en tiempo real con `due_at < now()` tanto en la propiedad `is_overdue` como en las estadísticas de las vistas. El valor `overdue` es, en la práctica, código muerto en el enum. Conviene o poblarlo con un job, o retirarlo para que el modelo no sugiera un estado que no existe. **[COD]**

**`company_contactrequest`** — Solicitud de contacto empresa → profesional. FK a `CompanyProfile` y a `CustomUser` (limitado a `professional`), `message`, `status ∈ {pending, accepted, rejected, cancelled}`, `response_message`, `created_at`, `responded_at`. Constraint único parcial `(company, professional)` **condicionado a `status='pending'`** — permite reintentar tras un rechazo, que es el comportamiento correcto.

### 5.3.3 Dominio de capacitación *(sin cambios respecto de producción)*

**`training_trainingmodule`** — `slug` (unique), `title`, `description`, `youtube_id`, tres campos Markdown (`intro_md`, `material_md`, `transcript_md`), presentación (`icon`, `color`, `order`), `is_active`, y el bloque de personalización: `is_personalized`, `requested_by`, `assigned_professionals` (M2M), `company_name_custom`, `custom_notes`. Tres classmethods de filtrado: `get_general_modules()`, `get_personalized_for_user()`, `get_all_for_user()`.

**`training_capacitacionlink`** — PK `UUIDv4`, FK a módulo y a profesional creador, `label`, `expires_at` (opcional), `is_active`, `access_count`. Propiedades `is_expired` / `is_usable`; `get_absolute_url()` → `/c/<slug>/?ref=<uuid>`.

**`training_linksharelog`** — Auditoría de envíos: `link`, `shared_to_email`, `shared_at`.

**`quiz_question` / `quiz_choice`** — Pregunta con `order` 1..10 y `explanation_correct`; opción con `label` (A–D), `is_correct` y `explanation_if_chosen` (feedback pedagógico por opción elegida). Constraints únicos `(module, order)` y `(question, label)`.

**`quiz_quizattempt`** — Intento individual: `started_at`, `submitted_at`, `score`, `passed`, `answers` (JSONField `{question_id: choice_id}` para auditoría). Índice `(user, module, -started_at)`.

**`quiz_quizstate`** — Estado por par usuario-módulo: `attempts_used`, `lockout_until`, `retake_available_at`, `last_completed_at`, `last_passed`. Constraint único `(user, module)`.

> **Atención — este modelo NO tiene una propiedad `is_approved`.** Verificado: los campos son exactamente `attempts_used`, `lockout_until`, `retake_available_at`, `last_completed_at`, `last_passed`. La Etapa 3 introdujo código que la invoca. Ver [N2](#n2--crítico--la-ficha-del-trabajador-rompe-con-http-500). **[VER]**

**`certificates_certificate`** — PK `UUIDv4`, FK usuario y módulo, **OneToOne con `QuizAttempt`**, `pdf_file` (FileField → `media/certificates/`), `issued_at`, `valid_until` (default +365 días), y trazabilidad de email: `email_sent`, `email_sent_at`, `email_error`. Propiedades `is_valid` y `days_until_expiry`.

**`presencial_presencialsession`** — FK módulo y profesional, `session_date`, `location`, `participants_count`, `quiz_score`, `quiz_passed`, `notes`, `created_at`.

## 5.4 Mapa completo de URLs

> Las filas marcadas **[E3]** son nuevas de la Etapa 3.

### Público

| Ruta | Vista | Auth | Método | Descripción |
|---|---|---|---|---|
| `/` | `landing.home` | pública | GET | Home institucional; redirige autenticados a su área |
| `/admin/` | Django admin | staff | — | Panel de administración |

### Portal profesional

| Ruta | Vista | Auth | Método | Descripción |
|---|---|---|---|---|
| `/auth/registro/` | `views_professional.register` | pública | GET/POST | Alta de profesional (auto-login) |
| `/auth/login/` | `views_professional.login_view` | pública | GET/POST | Login por email **o** username + password; `?next=` con validación anti-`//` |
| `/auth/logout/` | `views_professional.logout_view` | sesión | POST | Cierre de sesión → landing |

### Portal empresa **[E3]**

| Ruta | Vista | Auth | Método | Descripción |
|---|---|---|---|---|
| `/empresa/auth/registro/` | `views_company.company_register` | pública | GET/POST | Alta de empresa: crea `CustomUser` + `CompanyProfile` + auto-login |
| `/empresa/auth/login/` | `views_company.company_login` | pública | GET/POST | Login de empresa con verificación explícita de `is_company` |
| `/empresa/auth/logout/` | `views_professional.logout_view` | sesión | POST | Reutiliza el logout profesional |

### Backoffice compartido (profesional + empresa)

| Ruta | Vista | Auth | Método | Descripción |
|---|---|---|---|---|
| `/dashboard/` | `dashboard.home` | backoffice | GET | **Despacha por tipo**: panel profesional o panel de empresa **[E3]** |
| `/dashboard/capacitaciones/` | `capacitaciones_menu` | backoffice | GET | Grid de módulos generales + personalizados |
| `/dashboard/capacitaciones/<slug>/` | `modalidad_selector` | backoffice | GET | Elección Presencial vs Online |
| `/dashboard/capacitaciones/<slug>/links/` | `online_links` | backoffice | GET | Listado de links propios |
| `/dashboard/capacitaciones/<slug>/links/generar/` | `generate_link` | backoffice | POST | Crea `CapacitacionLink` |
| `/dashboard/capacitaciones/<slug>/links/<uuid>/compartir/` | `share_link` | backoffice | GET/POST | Envío del link por email a N destinatarios |
| `/dashboard/perfil/` | `profile` | backoffice | GET/POST | **Despacha por tipo**: perfil profesional o de empresa **[E3]** |

### Modalidad presencial (solo profesional)

| Ruta | Vista | Auth | Método | Descripción |
|---|---|---|---|---|
| `/dashboard/presencial/<slug>/` | `capacitacion_presencial` | prof | GET | Video + chat Ergobot para proyectar |
| `/dashboard/presencial/<slug>/quiz/` | `quiz_presencial` | prof | GET | Quiz grupal, sin reglas de intentos |
| `/dashboard/presencial/<slug>/quiz/submit/` | `quiz_presencial_submit` | prof | POST | Corrección con detalle por pregunta |
| `/dashboard/presencial/<slug>/planilla/` | `planilla_pdf` | prof | GET | Planilla PDF de asistencia + registra la sesión |
| `/dashboard/presencial/historial/` | `historial_presencial` | prof | GET | Historial de sesiones del profesional |

### Backoffice de empresa **[E3]**

| Ruta | Vista | Auth | Método | Descripción |
|---|---|---|---|---|
| `/dashboard/empresa/nomina/` | `company.nomina_list` | empresa | GET | Nómina con búsqueda, filtro por sector y por estado |
| `/dashboard/empresa/nomina/agregar/` | `nomina_add_worker` | empresa | GET/POST | Alta manual: busca trainee por CUIL, luego por email, o lo crea |
| `/dashboard/empresa/nomina/exportar/` | `nomina_export_csv` | empresa | GET | CSV con BOM UTF-8 para Excel |
| `/dashboard/empresa/nomina/<id>/` | `nomina_detail` | empresa | GET | Ficha con historial de quiz, certificados y estado por módulo |
| `/dashboard/empresa/nomina/<id>/editar/` | `nomina_edit` | empresa | GET/POST | Edición de datos laborales |
| `/dashboard/empresa/agenda/` | `agenda_list` | empresa | GET | Agenda con filtros por tipo, estado y rango de fechas |
| `/dashboard/empresa/agenda/crear/` | `agenda_create` | empresa | GET/POST | Alta de evento |
| `/dashboard/empresa/agenda/<id>/editar/` | `agenda_edit` | empresa | GET/POST | Edición de evento |
| `/dashboard/empresa/agenda/<id>/completar/` | `agenda_complete` | empresa | **GET/POST** ⚠️ | Marca completado — ver [N7](#n7--medio--agenda_complete-muta-estado-por-get) |
| `/dashboard/empresa/directorio/` | `directorio_profesionales` | empresa | GET | Directorio filtrado por `is_visible_in_directory` |
| `/dashboard/empresa/directorio/<id>/contactar/` | `send_contact_request` | empresa | POST | Envía `ContactRequest` |
| `/dashboard/solicitudes-contacto/` | `my_contact_requests` | prof | GET | Bandeja de solicitudes recibidas |
| `/dashboard/solicitudes-contacto/<id>/responder/` | `respond_contact_request` | prof | POST | Acepta o rechaza |

### Portal trabajador

| Ruta | Vista | Auth | Método | Descripción |
|---|---|---|---|---|
| `/acceso/` | `accounts.landing` | pública | GET | Formularios de registro y login de trabajador |
| `/acceso/register/` | `register_post` | pública | POST | Valida y guarda en sesión → confirmación |
| `/acceso/confirm/` + `/acceso/confirm/post/` | `confirm_get/post` | pública | GET/POST | Confirmación → crea usuario y auto-login |
| `/acceso/login/` | `login_post` | pública | POST | Autenticación **CUIL + email, sin contraseña** |
| `/acceso/logout/` | `logout_post` | sesión | POST | Cierre de sesión |
| `/acceso/health/` | `health` | pública | GET | Health check (texto plano `OK`) |
| `/capacitacion/` | `training_home` | login | GET | Video + chat + quiz |
| `/c/<slug>/` | `views_public.public_landing` | pública | GET | Entrada vía link: trackea `?ref=`, guarda sesión y redirige |

### Quiz (API JSON)

| Ruta | Vista | Auth | Método | Descripción |
|---|---|---|---|---|
| `/quiz/<slug>/start/` | `start` | login | POST | Verifica bloqueo, crea intento, devuelve P1 |
| `/quiz/<slug>/question/<n>/` | `question` | login | GET | Devuelve pregunta n (1..10) |
| `/quiz/<slug>/answer/` | `answer` | login | POST | Responde una pregunta → feedback inmediato |
| `/quiz/<slug>/submit/` | `submit` | login | POST | Corrige, aplica reglas, dispara certificado |
| `/quiz/<slug>/result/<id>/` | `result_page` | login | GET | Pantalla HTML de resultado |
| `/quiz/<slug>/retake/` | `retake` | login | POST | Nuevo intento si las reglas lo permiten |

### Certificados e IA

| Ruta | Vista | Auth | Método | Descripción |
|---|---|---|---|---|
| `/certificados/` | `my_certificates` | login | GET | **Devuelve JSON crudo** (sin template) |
| `/certificados/<uuid>/download/` | `download_certificate` | login | GET | Descarga con verificación de propiedad |
| `/certificados/<uuid>/view/` | `view_certificate` | login | GET | Visualización inline con verificación de propiedad |
| `/ai/ergobot/<slug>/stream/` | `ergobot_stream` | login | GET | **Vista async**, streaming SSE token a token |

## 5.5 Arquitectura de autenticación y permisos

### 5.5.1 Backends encadenados

`AUTHENTICATION_BACKENDS` en orden de evaluación: **[COD]**

1. **`ProfessionalBackend`** (extiende `ModelBackend`) — email **o** username + password, filtrando **`user_type='professional'`**. Incluye mitigación de *timing attacks*: ejecuta el hasher aunque el usuario no exista.
2. **`CuilEmailBackend`** — CUIL + email, sin contraseña, filtrando `user_type='trainee'`. Implementa `aauthenticate`/`aget_user` para las vistas asíncronas.
3. **`ModelBackend`** de Django — fallback para el admin.

> **Consecuencia no evidente y verificada.** Ningún backend propio contempla `user_type='company'`. Las empresas se autentican **exclusivamente a través del `ModelBackend` de fallback**, que no filtra por tipo de usuario. Ver [N4](#n4--alto--el-login-de-empresa-depende-del-backend-de-fallback). **[VER]**

### 5.5.2 Decoradores disponibles

| Decorador | Requiere | Uso |
|---|---|---|
| `professional_required` | `is_professional` | Presencial, solicitudes de contacto |
| `trainee_required` | `is_trainee` | *(sin uso actual)* |
| **`backoffice_required`** | `is_backoffice_user` | Dashboard y capacitaciones **[E3]** |
| **`company_required`** | `is_company` | Todo el backoffice de empresa **[E3]** |
| `subscription_required(tier)` | Suscripción activa | *(sin uso — preparado para Fase 7)* |

**Los cinco resuelven la URL de login con `reverse('professional_login')`, que no existe.** Ver [H5](#h5--el-nombre-de-url-professional_login-no-existe) y [N1](#n1--crítico--seis-rutas-del-backoffice-devuelven-http-500-a-usuarios-anónimos).

### 5.5.3 Mixins para vistas basadas en clase

`ProfessionalRequiredMixin`, `TraineeRequiredMixin`, `BackofficeRequiredMixin`, `CompanyRequiredMixin`, `SubscriptionRequiredMixin`. **Ninguno se usa**: todas las vistas del proyecto son basadas en función. Arrastran los mismos nombres de URL rotos. **[COD]**

### 5.5.4 Matriz de acceso verificada

Resultado de probar cada tipo de usuario contra cada área. **[VER]**

| Ruta | Anónimo | Trabajador | Profesional | Empresa |
|---|---|---|---|---|
| `/dashboard/` | 302 → `/acceso/` ⚠️ | 302/403 | 200 | 200 |
| `/dashboard/capacitaciones/` | 302 → `/acceso/` ⚠️ | 302/403 | 200 | **200** |
| `/dashboard/capacitaciones/<slug>/` | 302 → `/acceso/` ⚠️ | 302/403 | 200 | **200** |
| `/dashboard/presencial/<slug>/` | 302 → `/acceso/` ⚠️ | 302/403 | 200 | **403** ⚠️ |
| `/dashboard/presencial/historial/` | 302 → `/acceso/` ⚠️ | 302/403 | 200 | **403** |
| `/dashboard/perfil/` | 302 → `/acceso/` ⚠️ | 302/403 | 200 | 200 |
| `/dashboard/empresa/nomina/` | 🔴 **500** | 🔴 **500** | 403 | 200 |
| `/dashboard/empresa/agenda/` | 🔴 **500** | 🔴 **500** | 403 | 200 |
| `/dashboard/empresa/directorio/` | 🔴 **500** | 🔴 **500** | 403 | 200 |
| `/dashboard/solicitudes-contacto/` | 🔴 **500** | 🔴 **500** | 200 | 403 |

**Lectura de la matriz:**

- ⚠️ **Columna anónimo, filas 302:** el redirect va a `/acceso/` (login de trabajadores por CUIL) incluso para rutas exclusivamente profesionales. Es [H6](#h6--el-portal-profesional-redirige-al-login-de-trabajadores), sigue vigente.
- 🔴 **Los HTTP 500:** son [N1](#n1--crítico--seis-rutas-del-backoffice-devuelven-http-500-a-usuarios-anónimos), la regresión bloqueante.
- ⚠️ **Fila presencial, columna empresa:** una empresa recorre el menú de capacitaciones (200), elige un módulo (200), elige "Presencial" y recibe **403**. Es [N6](#n6--medio--callejón-sin-salida-empresa--presencial).
- **El aislamiento entre tipos funciona correctamente** en las rutas exclusivas: profesional no entra a empresa (403) y empresa no entra a solicitudes de contacto (403).

## 5.6 Funcionalidades — inventario descriptivo

### 5.6.1 Autenticación triple

El sistema mantiene **tres flujos de identidad independientes** sobre un único modelo de usuario:

| Portal | Ruta | Credencial | Fricción |
|---|---|---|---|
| Profesional | `/auth/login/` | email **o** username + password | Estándar |
| Empresa **[E3]** | `/empresa/auth/login/` | email + password | Estándar |
| Trabajador | `/acceso/` | **CUIL + email, sin contraseña** | Cero |

El CUIL se normaliza a 11 dígitos (se descartan guiones y puntos) tanto en registro como en login, lo que evita duplicados por formato. El CUIT de empresa recibe el mismo tratamiento (`normalize_cuit`).

**Decisión de diseño con implicancia de seguridad, heredada y deliberada:** el acceso del trabajador es *knowledge-based* con datos no secretos. Cualquiera que conozca CUIL y email de una persona puede entrar y descargar sus certificados. Es coherente con el caso de uso (capacitación obligatoria masiva, fricción cero), pero conviene tenerla explícita al documentar el producto.

**El registro sigue siendo abierto al público en los dos portales de gestión.** `/auth/registro/` y `/empresa/auth/registro/` no exigen invitación, verificación de email ni aprobación. Con 2 profesionales registrados nunca fue un problema; si el producto se abre, es el primer control a agregar — y ahora hay **dos** puertas en vez de una.

### 5.6.2 Backoffice de empresa **[E3]**

**Nómina.** Listado con búsqueda libre (nombre, CUIL, email, legajo), filtro por sector y por estado (activo/inactivo/todos), más estadísticas de activos e inactivos. El alta manual implementa una cascada de resolución sensata: busca un trainee existente por CUIL, si no lo encuentra busca por email, y si tampoco existe lo crea con `create_trainee` heredando la razón social de la empresa. Verifica duplicados antes de crear la relación. Exportación a CSV con BOM UTF-8 para que Excel respete los acentos.

**Ficha individual.** Historial de los últimos 20 intentos de quiz, certificados obtenidos y estado por módulo general activo. 🔴 **Esta vista está rota** — ver [N2](#n2--crítico--la-ficha-del-trabajador-rompe-con-http-500).

**Agenda.** Eventos con seis tipos, cuatro estados y cuatro prioridades. Filtros por tipo, estado y rango de fechas. Métricas de pendientes, vencidos y próximos 7 días. CRUD completo salvo borrado.

**Vencimientos automáticos.** El comando `generate_cert_expiry_events --days N [--dry-run]` recorre los certificados que vencen en la ventana indicada, y por cada trabajador activo en una nómina crea un `AgendaEvent` de tipo `certificate_expiry` con prioridad alta. Es **idempotente**: verifica la existencia previa por `(company, event_type, worker, related_object_type, related_object_id)` antes de crear. Bien construido. 🟡 **Sin planificador** — ver [N9](#n9--medio--generate_cert_expiry_events-sin-planificador).

**Panel de empresa.** Dashboard propio (`home_company.html`) con total de trabajadores activos, eventos pendientes, eventos vencidos, **cobertura de capacitación** (porcentaje de trabajadores con al menos un certificado) y los próximos 5 eventos.

**Directorio y contacto.** Listado de profesionales con `is_visible_in_directory=True`, filtrable por nombre y profesión, con envío de solicitud de contacto y bandeja de respuesta del lado profesional. 🔴 **Funcionalmente inalcanzable** — ver [N3](#n3--alto--el-directorio-de-profesionales-es-inalcanzable).

### 5.6.3 Modalidad ONLINE — links compartibles

1. El profesional genera un `CapacitacionLink` con una **etiqueta interna** (ej. *"Valle de las Leñas SA - 23/02/2026"*).
2. Obtiene una URL con UUID: `/c/<slug>/?ref=<uuid>`.
3. Puede **compartirla por email a múltiples destinatarios** en una sola operación (separación por coma o punto y coma, validación por dirección, mensaje personalizado opcional). Cada envío se registra en `LinkShareLog`.
4. Al abrirse el link se **incrementa atómicamente** `access_count` usando `F()`, se guarda el módulo objetivo en sesión y se redirige al registro/login del trabajador.
5. Los links soportan **expiración opcional** (`expires_at`) y desactivación manual (`is_active`).

⚠️ La expiración **hoy es un contador, no un candado** — ver [H7](#h7--los-links-vencidos-siguen-dando-acceso).

### 5.6.4 Modalidad PRESENCIAL

Pensada para proyectar en sala: página con video embebido y chat Ergobot (sin registro de trabajadores); **quiz grupal** que reutiliza el mismo banco de preguntas pero sin reglas de intentos, sin persistencia y sin certificado; **planilla PDF de asistencia** generada con ReportLab (A4 vertical, 25 filas para firma) que además registra la sesión en `PresencialSession`; e **historial** de sesiones dictadas.

### 5.6.5 Sistema de evaluación — la pieza mejor construida

Reglas de negocio centralizadas en `apps/quiz/services.py` y **aplicadas 100 % en el servidor**: **[COD]**

| Constante | Valor |
|---|---|
| `TOTAL_QUESTIONS` | 10 |
| `PASS_SCORE` | 8 (80 %) |
| `MAX_ATTEMPTS` | 3 por ventana |
| `LOCK_HOURS` | 24 |

Mecánica:

- Feedback **inmediato por pregunta**, con explicación diferenciada según la opción elegida (`explanation_if_chosen`) o la explicación de la correcta.
- Al enviar, el **score se recalcula desde la base de datos** leyendo `answers`; nunca se confía en el cliente.
- **Si falla 3 veces** → `lockout_until = ahora + 24 h`.
- **Si aprueba** → *cool-off* de 24 h (`retake_available_at`) para evitar re-rendir en cadena.
- `reset_if_unlocked()` limpia el estado automáticamente al vencer el plazo, reiniciando la ventana de intentos.
- Las operaciones críticas usan `transaction.atomic()` + `select_for_update()` sobre `QuizState`, previniendo el doble-click y el doble-intento.
- Los payloads enviados al front **nunca incluyen cuál es la respuesta correcta**.

> Reglas explícitas, servidor autoritativo, concurrencia contemplada. **Y cero tests.** La combinación es el desbalance de riesgo más grande del proyecto — ver [§6.3](#63-el-desbalance-central).

### 5.6.6 Certificación automática

Al aprobar se dispara `_create_certificate()`, diseñado como **no bloqueante** (try/except en dos niveles: un fallo de PDF o de email nunca invalida la aprobación del trabajador):

1. Crea el `Certificate` (UUID, vigencia 1 año).
2. Genera el **PDF con ReportLab**: A4 apaisado, encabezado "CERTIFICADO DE CAPACITACIÓN / ERGONOMÍA Y PREVENCIÓN DE RIESGOS LABORALES", nombre en mayúsculas, CUIL, título del módulo, tabla de fechas y bloque de firma **hardcodeado**.
3. Lo guarda en `media/certificates/certificado_<uuid>.pdf`.
4. **Envía hasta 4 emails** con el PDF adjunto, renombrado al nombre del trabajador:
   - **Al trabajador** — obligatorio; si falla, se propaga y se registra en `email_error`.
   - **Al empleador** — si cargó `employer_email`; `fail_silently=True`.
   - **Al responsable de SySO** — si cargó `safety_responsible_email`; `fail_silently=True`.
   - **Al admin** — con resumen de a quién se notificó.
5. Marca `email_sent` / `email_sent_at`.

⚠️ El envío SMTP es **síncrono dentro del request HTTP** — ver [H11](#h11--envío-de-email-síncrono-dentro-del-request).
⚠️ La firma está **hardcodeada** — ver [H20](#h20--firma-del-certificado-hardcodeada).
🔵 **Brecha funcional nueva:** ahora que existe `CompanyWorker`, el pipeline **no notifica a la empresa** de la que el trabajador forma parte. Ver [N11](#n11--bajo--el-pipeline-de-certificados-ignora-a-la-empresa).

### 5.6.7 Ergobot AI

- **Vista asíncrona** (`async def`) con `StreamingHttpResponse` sobre **Server-Sent Events**, entregando la respuesta token a token.
- Construida sobre `openai-agents` (`Runner.run_streamed`), modelo `gpt-4.1-mini-2025-04-14`.
- **System prompt dinámico** (`prompts.py::build_system_prompt`): compone `prompts/system_base.md` + el `intro_md`, `material_md` y `transcript_md` **del módulo desde la base de datos** + un archivo opcional `prompts/modules/<slug>.md`. El bot está *grounded* en el contenido real de la capacitación.
- Usa `TrainingModule.objects.afirst()` (ORM async) con fallback si el slug no existe.
- El hilo de conversación se mantiene **en el cliente** y se reenvía por query string; **no hay persistencia de conversaciones**.
- Cabeceras correctas para streaming: `Cache-Control: no-cache` y **`X-Accel-Buffering: no`** (imprescindible detrás de nginx).

⚠️ La vista es async pero corre bajo **workers `sync` de gunicorn/WSGI** — ver [H12](#h12--vista-async-sobre-workers-wsgi-sync).

### 5.6.8 Panel de administración

Django Admin fuertemente personalizado. **[COD]**

| Admin | Personalización |
|---|---|
| `CustomUserAdmin` | Fieldsets por tipo de usuario, filtros por `user_type` y suscripción, búsqueda por 8 campos. ⚠️ **No expone `is_visible_in_directory`** — ver [N3](#n3--alto--el-directorio-de-profesionales-es-inalcanzable) |
| `TrainingModuleAdmin` | `list_editable` sobre `order` e `is_active`, `prepopulated_fields` para el slug, `filter_horizontal` para asignar profesionales, badge General/Personalizada, `prefetch_related` contra N+1 |
| `CertificateAdmin` | `has_add_permission = False`, borrado solo para superusuarios, badge Vigente/Vencido, `date_hierarchy` |
| `CapacitacionLinkAdmin` / `LinkShareLogAdmin` | Campos de auditoría en solo lectura |
| `QuestionAdmin` | Edición de opciones inline |
| **`CompanyProfileAdmin`** **[E3]** | Fieldsets por bloque, filtros por estado y provincia, búsqueda por razón social/CUIT |
| **`CompanyWorkerAdmin`** **[E3]** | `raw_id_fields` para empresa y trabajador, filtros por estado y sector |
| **`AgendaEventAdmin`** **[E3]** | Filtros por tipo, estado, prioridad y empresa |
| **`ContactRequest`** | 🔴 **No registrado** — ver [N10](#n10--bajo--contactrequest-no-está-registrado-en-el-admin) |

### 5.6.9 Comandos de gestión

| Comando | App | Función |
|---|---|---|
| `seed_modules` | `training` | Crea/actualiza los 6 módulos del catálogo con icono, color y orden. Idempotente |
| `seed_module_content --module <slug> [--force]` | `training` | Carga `intro.md`, `material.md` y `transcript.txt` desde `apps/training/content/<slug>/` |
| `seed_quiz` | `quiz` | Carga el banco de preguntas y opciones |
| `import_quiz_backup` | `quiz` | Importación robusta desde `fixtures/backup_quiz_questions.json` |
| `send_test_email` | `certificates` | Verificación de la configuración SMTP |
| **`generate_cert_expiry_events`** **[E3]** | `company` | Genera eventos de agenda por vencimiento próximo de certificados |

---

# PARTE VI — VERIFICACIÓN DE LOS HALLAZGOS DE LA AUDITORÍA

## 6.1 Tablero de estado

| # | Hallazgo | Severidad original | Estado en desarrollo | Evidencia |
|---|---|---|---|---|
| H1 | Sin backup automatizado de la BD | 🔴 Crítico | 🔴 **Vigente** | Operativo, fuera del repo |
| H2 | Certificados PDF sin autenticación por URL | 🟠 Alto | 🔴 **Vigente** | Config de nginx **[AUD]** |
| H3 | Sin rotación de logs | 🟠 Alto | 🔴 **Vigente** | Operativo, fuera del repo |
| H4 | `main` desactualizada | 🟠 Alto | 🔴 **Empeoró**: 40 commits | **[VER]** |
| H5 | `reverse('professional_login')` → `NoReverseMatch` | 🟡 Medio (latente) | 🔴 **Se activó** — ver N1 | **[VER]** |
| H6 | Portal profesional redirige al login de trabajadores | 🟡 Medio | 🔴 **Vigente** | **[VER]** |
| H7 | Links vencidos siguen dando acceso | 🟡 Medio | 🔴 **Vigente** | **[COD]** |
| H8 | Campo `explanation` inexistente en quiz presencial | 🟡 Medio | 🔴 **Vigente** | **[VER]** |
| H9 | Umbral de aprobación duplicado (`8` literal) | 🟡 Medio | 🔴 **Vigente** | **[COD]** |
| H10 | Dependencia implícita de gunicorn para HTTPS | 🟡 Medio | 🔴 **Vigente** | **[VER]** |
| H11 | Email síncrono dentro del request | 🟡 Medio | 🔴 **Vigente** | **[COD]** |
| H12 | Vista async sobre workers WSGI sync | 🟡 Medio | 🔴 **Vigente** | **[COD]** |
| H13 | Cookies sin flag `Secure` | 🔵 Bajo | 🔴 **Vigente** | **[VER]** |
| H14 | Sin HSTS | 🔵 Bajo | 🔴 **Vigente** | **[VER]** |
| H15 | `CSRF_TRUSTED_ORIGINS` vacío | 🔵 Bajo | 🔴 **Vigente** | **[VER]** |
| H16 | Registro de profesionales abierto | 🔵 Bajo | 🔴 **Empeoró**: ahora dos portales abiertos | **[COD]** |
| H17 | Sin protección contra fuerza bruta | 🔵 Bajo | 🔴 **Vigente** | **[COD]** |
| H18 | Sin fijado de versiones en `requirements.txt` | 🔵 Bajo | 🔴 **Empeoró** — ver N8 | **[VER]** |
| H19 | Sin monitoreo ni alertas | 🔵 Bajo | 🔴 **Vigente** | Operativo |
| H20 | Firma del certificado hardcodeada | 🔵 Bajo | 🔴 **Vigente** | **[COD]** |
| H21 | Código muerto en `certificates/` | 🔵 Bajo | 🔴 **Vigente** (~280 líneas) | **[VER]** |
| H22 | `/certificados/` devuelve JSON crudo | 🔵 Bajo | 🔴 **Vigente** | **[COD]** |
| H23 | `share_link` reporta envíos que pueden no haber salido | 🔵 Bajo | 🔴 **Vigente** | **[COD]** |
| H24 | `participants_count` por query string | 🔵 Bajo | 🔴 **Vigente** | **[COD]** |
| H25 | Comentarios anclados a "COMMIT N" | 🔵 Bajo | 🔴 **Vigente** | **[COD]** |
| H26 | README declara "Async: ASGI + Uvicorn" | 🔵 Bajo | 🔴 **Vigente** | **[VER]** |
| H27 | Sin CI, linter, formateador ni pre-commit | 🔵 Bajo | 🔴 **Vigente** | **[VER]** |

**Resumen: 27 hallazgos, 0 corregidos, 4 agravados.** La Etapa 3 se construyó sobre la deuda existente sin saldar ninguna parte de ella.

## 6.2 Detalle de los hallazgos que requieren precisión adicional

### H1 — 🔴 CRÍTICO — Sin backup automatizado de la base de producción

`/etc/cron.d/` contiene únicamente `criaapp-backup` (la aplicación beta vecina, con dump diario a las 03:30 y retención de 7 días). **ErgoSolutions, que es la aplicación productiva, no tiene ninguno.** No hay crontab del usuario `deploy`, ni timer de systemd, ni script de backup. El único dump existente es `/home/deploy/backup_pre_criaapp_20260624_205004/ergocapacitacion_db.dump` (95 KB), tomado **manualmente el 24/06/2026** antes de instalar CriaApp. **[AUD]**

Una pérdida del volumen implicaría perder los 15 certificados emitidos, los 18 usuarios y todo el historial de evaluaciones, con recuperación posible solo hasta el 24/06. Los PDF en `media/` tampoco están respaldados (aunque son regenerables desde los datos). La base pesa 10 MB: un backup diario cuesta prácticamente nada.

> **Este hallazgo se vuelve bloqueante para el plan de trabajo.** El Bloque 4 propone desplegar la Etapa 3, lo que implica ejecutar 6 migraciones sobre la base productiva. **No se debe migrar sin backup verificado.** Por eso el backup es el Bloque 0 y no una tarea de mantenimiento diferible.

### H2 — 🟠 ALTO — Certificados PDF descargables sin autenticación

nginx sirve `/media/` directamente mediante `alias`, sin pasar por Django. Se verificó en su momento que `GET https://www.ergosolutions.com.ar/media/certificates/certificado_<uuid>.pdf` **devuelve HTTP 200 y el PDF completo sin ninguna sesión**. La verificación de propiedad que hacen `download_certificate` y `view_certificate` (`certificate.user != request.user → 404`) **se puede saltear** yendo a la ruta directa. **[AUD]**

La protección efectiva es únicamente la impredecibilidad del UUIDv4 —que es razonable como barrera— pero el certificado contiene **nombre completo y CUIL**, datos personales. El propio admin de Django expone esa URL directa en la columna "PDF".

> **Agravante nuevo de la Etapa 3:** `CompanyProfile.logo` es un `ImageField` que escribe en `media/company_logos/`. Cuando se desplieguen las empresas, los logos quedarán igualmente expuestos. El logo de una empresa no es un dato sensible, pero amplía la superficie del mismo defecto de configuración.

**Corrección recomendada:** servir `media/certificates/` a través de Django usando `X-Accel-Redirect` con `internal;` en el location de nginx, de modo que la verificación de propiedad sea efectiva.

### H4 — 🟠 ALTO — `main` desactualizada

Ya desarrollado en [§3.2](#32-estado-de-las-ramas). Pasó de 20 a **40 commits** de retraso.

**Decisión pendiente:** o se alinea `main` con `release/beta`, o se declara formalmente `release/beta` como rama de producción, se la marca como rama por defecto en GitHub y se lo documenta en el README. La segunda opción es más barata; la primera es más convencional. Lo que no es sostenible es el estado actual, en el que la rama por defecto del repositorio describe una aplicación que no existe en ningún lado.

### H5 — El nombre de URL `professional_login` no existe

Verificado ejecutando `reverse()` contra el URLconf real en desarrollo: **[VER]**

| Nombre invocado en el código | Resultado |
|---|---|
| `reverse('professional_login')` | ❌ **NoReverseMatch** |
| `reverse('landing')` | ❌ **NoReverseMatch** |
| `reverse('dashboard')` | ❌ **NoReverseMatch** |
| `reverse('accounts_professional:professional_login')` | ✅ `/auth/login/` |
| `reverse('accounts_company:company_login')` | ✅ `/empresa/auth/login/` |
| `reverse('trainee_landing')` | ✅ `/acceso/` |
| `reverse('dashboard:home')` | ✅ `/dashboard/` |
| `reverse('dashboard:company:nomina_list')` | ✅ `/dashboard/empresa/nomina/` |
| `reverse('landing:home')` | ✅ `/` |

**Causa:** `urls_professional.py` se incluye con `namespace="accounts_professional"`, por lo que el nombre plano dejó de existir; y `landing` fue renombrado a `trainee_landing` en el Commit 12 para no colisionar con el namespace de la app institucional. Los decoradores y mixins quedaron con los nombres viejos.

**Puntos afectados — inventario completo:** **[COD]**

| Archivo | Línea | Invocación rota |
|---|---|---|
| `apps/accounts/decorators.py` | 27 | `professional_required` → `reverse('professional_login')` |
| `apps/accounts/decorators.py` | 54 | `trainee_required` → `reverse('landing')` |
| `apps/accounts/decorators.py` | 92 | **`backoffice_required`** → `reverse('professional_login')` **[E3]** |
| `apps/accounts/decorators.py` | 122 | **`company_required`** → `reverse('professional_login')` **[E3]** |
| `apps/accounts/decorators.py` | 152 | `subscription_required` → `redirect('professional_login')` |
| `apps/accounts/mixins.py` | 22 | `ProfessionalRequiredMixin.get_login_url()` |
| `apps/accounts/mixins.py` | 31 | `ProfessionalRequiredMixin.handle_no_permission()` → `redirect('dashboard')` |
| `apps/accounts/mixins.py` | 46 | `TraineeRequiredMixin.get_login_url()` → `reverse('landing')` |
| `apps/accounts/mixins.py` | 61 | **`BackofficeRequiredMixin.get_login_url()`** **[E3]** |
| `apps/accounts/mixins.py` | 79 | **`CompanyRequiredMixin.get_login_url()`** **[E3]** |
| `config/settings.py` | 109 | `PROFESSIONAL_LOGIN_URL = "professional_login"` |
| `config/settings.py` | 110 | `PROFESSIONAL_LOGIN_REDIRECT_URL = "dashboard"` |

**En producción sigue latente**, porque todas las vistas del dashboard y de presencial se declaran como `@login_required` **antes** de `@professional_required`: el usuario anónimo es redirigido por `login_required` y la rama defectuosa nunca se ejecuta.

**En desarrollo ya explotó.** Ver [N1](#n1--crítico--seis-rutas-del-backoffice-devuelven-http-500-a-usuarios-anónimos).

### H6 — El portal profesional redirige al login de trabajadores

Consecuencia directa de H5 combinada con `settings.LOGIN_URL = "trainee_landing"`. Verificado en desarrollo: **[VER]**

```
GET /dashboard/                    (sin sesión)  →  302  →  /acceso/?next=/dashboard/
GET /dashboard/perfil/             (sin sesión)  →  302  →  /acceso/?next=/dashboard/perfil/
GET /dashboard/capacitaciones/     (sin sesión)  →  302  →  /acceso/?next=/dashboard/capacitaciones/
GET /dashboard/presencial/historial/ (sin sesión) → 302  →  /acceso/?next=/dashboard/presencial/historial/
```

Un **profesional** —o ahora una **empresa**— que abre un enlace directo al dashboard con la sesión vencida aterriza en el **formulario de CUIL + email de trabajadores**. Es un defecto de experiencia de usuario activo y observable, que la Etapa 3 amplió a un tercer tipo de usuario.

### H7 — Los links vencidos siguen dando acceso

En `apps/training/views_public.py`, la vista `public_landing` valida `link.is_usable` **solo dentro del bloque que contabiliza el acceso**: **[COD]**

```python
if ref_id:
    try:
        link = CapacitacionLink.objects.get(id=ref_id, module=module)
        if link.is_usable:                       # ← la validación solo gobierna el contador
            CapacitacionLink.objects.filter(id=link.id).update(
                access_count=models.F("access_count") + 1
            )
            request.session["capacitacion_ref"] = str(link.id)
    except (CapacitacionLink.DoesNotExist, ValueError, TypeError):
        pass

# ...y acá se redirige igual, haya sido usable o no
return redirect("trainee_landing")
```

Si el link está vencido o desactivado, el trabajador **igual es redirigido al registro y puede completar la capacitación y obtener su certificado**. `expires_at` e `is_active` son hoy metadatos de reporte, no controles de acceso.

### H8 — Campo `explanation` inexistente en el quiz presencial

`apps/presencial/views.py:108`: **[COD]**

```python
"explanation": q.explanation if hasattr(q, "explanation") else "",
```

Verificado: el modelo `Question` expone `id`, `module`, `order`, `text`, `explanation_correct` y `choices`. **No tiene `explanation`.** **[VER]**

El `hasattr` evita el crash, pero el resultado es que **la explicación siempre llega vacía** en el modo presencial: la retroalimentación pedagógica que sí existe en el modo online no se muestra en la capacitación grupal. Es una pérdida de valor didáctico silenciosa — el modo presencial es justamente donde un profesional explica las respuestas frente a un grupo.

### H9 — Umbral de aprobación duplicado

`apps/presencial/views.py:112`: `passed = correct >= 8`, con el 8 **literal**, en lugar de importar `PASS_SCORE` de `apps.quiz.services` (donde vale 8). Si mañana se cambia el umbral, las dos modalidades quedan desalineadas en silencio. **[COD]**

### H10 — Dependencia implícita de gunicorn para HTTPS

Ya desarrollado en [§4.2.2](#422-la-dependencia-implícita-de-https). Se confirma que `settings.py` en desarrollo sigue **sin** `SECURE_PROXY_SSL_HEADER`. **[VER]**

> **Este hallazgo se cruza con el Bloque 6 del plan.** La migración a ASGI/uvicorn está recomendada por [H12](#h12--vista-async-sobre-workers-wsgi-sync), y uvicorn **no** replica el comportamiento de `secure_scheme_headers` de gunicorn. Migrar a ASGI sin agregar antes `SECURE_PROXY_SSL_HEADER` rompe **todos los formularios del sitio** de forma inmediata. El orden entre estas dos tareas no es negociable.

### H11 — Envío de email síncrono dentro del request

Cuatro emails con adjunto PDF contra Gmail, dentro del ciclo de request, con `--timeout 60` de gunicorn y 3 workers `sync`. Un pico de aprobaciones simultáneas bloquea workers. No hay Celery en esta aplicación (el que existe en el VPS es de CriaApp). Con el volumen actual (15 certificados en 5 meses) es irrelevante; con adopción real, es lo primero a mover a background. **[COD]**

### H12 — Vista async sobre workers WSGI sync

La vista `ergobot_stream` es `async def` pero corre bajo **workers `sync` de gunicorn/WSGI**. Django lo soporta envolviendo la corrutina en un event loop, pero **cada chat ocupa un worker completo durante toda la generación**. Con 3 workers, 3 conversaciones simultáneas dejan el sitio sin capacidad de atender nada más. **[COD]**

Es el cuello de botella estructural de la arquitectura actual, y el motivo por el cual `uvicorn` está en `requirements.txt` y `config/asgi.py` existe: **la migración a ASGI está preparada pero no ejecutada.**

### H16 — Registro abierto — ahora en dos portales

Tanto `/auth/registro/` como `/empresa/auth/registro/` **[E3]** son públicos, sin invitación, verificación de email ni aprobación. Cualquiera puede crear una cuenta de empresa, cargar una nómina con CUIL y emails de personas reales, y consultar el historial de capacitación de esos trabajadores. **[COD]**

> Con la Etapa 3 desplegada, este hallazgo cambia de naturaleza: deja de ser "acceso al catálogo de capacitaciones" y pasa a ser **acceso a datos personales de terceros**. El alta de empresa debería requerir validación —el modelo ya tiene `account_status='pending_validation'` previsto para eso, y hoy nadie lo usa: el default es `active`.

### H18 — Sin fijado de versiones — agravado

`requirements.txt` sigue con 9 líneas, todas con `>=`, sin pins exactos: **[VER]**

```
Django>=5.2 · psycopg[binary]>=3.2 · django-environ>=0.11 · django-bootstrap5>=25.1
whitenoise>=6.7 · reportlab>=4.0 · openai>=1.0 · openai-agents>=0.0.19 · uvicorn>=0.30.0
```

Dos observaciones heredadas y una nueva:

- **Sin versiones fijadas**, un `pip install -r requirements.txt` en otra máquina puede producir un entorno distinto al de producción. En particular `openai-agents` está declarado `>=0.0.19` con **0.9.2 instalado** — un salto de API mayor entre versiones pre-1.0.
- `uvicorn` y `gunicorn` conviven, pero producción corre `config.wsgi` bajo gunicorn con workers `sync`. **`gunicorn` no figura en `requirements.txt`** aunque es el servidor real de producción.
- 🆕 **La Etapa 3 agregó una dependencia dura no declarada:** ver [N8](#n8--medio--pillow-es-dependencia-obligatoria-y-no-está-declarada).

### H20 — Firma del certificado hardcodeada

`apps/certificates/pdf.py`, líneas 121–123: **[COD]**

```python
story.append(Paragraph("Pablo Ricardo Aguirre", styles["signature_name"]))
story.append(Paragraph("Licenciado en Kinesiología - MN 10.027", styles["signature_title"]))
story.append(Paragraph("Especialista en Ergonomía", styles["signature_title"]))
```

Bloquea que otro profesional emita certificados con su propia firma. **Es incompatible con el modelo SaaS multi-profesional que plantea el roadmap** y, ahora, con el modelo multi-empresa de la Etapa 3: una empresa que capacita a su nómina emite certificados firmados por un tercero que no participó.

El `CustomUser` ya tiene los campos necesarios (`first_name`, `last_name`, `profession`, `license_number`). Parametrizar la firma es una tarea acotada con alto retorno estructural.

### H21 — Código muerto en `certificates/`

Verificado: **[VER]**

| Archivo | Total | Código vivo | Bloque muerto |
|---|---|---|---|
| `apps/certificates/views.py` | 197 líneas | 1–113 | **120–197** (docstring gigante con la versión anterior completa) |
| `apps/certificates/pdf.py` | 417 líneas | 1–234 | **235–417** (ídem) |

Son ~280 líneas de versiones anteriores completas del archivo, comentadas como docstring al final. Confunden la lectura y hacen que las búsquedas por texto devuelvan resultados de código que no se ejecuta.

### H26 — El README describe una arquitectura que no existe

`README.md` declara bajo "Tecnologías": **"Async: ASGI + Uvicorn"**. El despliegue real es **WSGI + gunicorn con workers sync**. **[VER]**

Además, la sección de tests documenta:

```bash
python manage.py test apps.accounts apps.dashboard apps.presencial
```

que **omite `apps.company`** —los 9 tests de la Etapa 3— además de `quiz` y `certificates`. El comando documentado ejecuta 22 de los 32 tests existentes.

### H27 — Sin CI, linter, formateador ni pre-commit

No hay `.github/workflows/`, ni configuración de `ruff`/`flake8`/`black`, ni `.pre-commit-config.yaml`. **[VER]**

> **Este hallazgo es la causa raíz de N1.** Un pipeline de CI que ejecutara la suite en cada push habría estado en verde igual —los tests no cubren el caso anónimo— pero un chequeo automático de `reverse()` sobre los nombres usados en decoradores, o simplemente un smoke test de rutas sin sesión, habría detectado los seis HTTP 500 antes del Commit 48.

---

## 6.3 El desbalance central

La cobertura de tests, cruzada contra el riesgo de cada componente: **[VER]**

| App | Tests | Clases | Líneas | Complejidad del dominio | Riesgo |
|---|---|---|---|---|---|
| `dashboard` | **13** | 3 | 245 | Media | 🟢 Cubierta |
| **`company`** | **9** | 3 | 265 | Alta | 🟡 Parcial — falta la ficha, que es la que rompe |
| `accounts` | 6 | 2 | 96 | Alta | 🟡 Parcial |
| `presencial` | 3 | 1 | 65 | Baja | 🟢 Suficiente |
| `training` | 1 | 1 | 13 | Media | 🟡 Mínima |
| **`quiz`** | **0** | 0 | 3 | 🔴 **Muy alta** | 🔴 **Descubierta** |
| **`certificates`** | **0** | 0 | 3 | 🔴 **Alta** | 🔴 **Descubierta** |
| `ergobot_ai` | **0** | 0 | 3 | Media | 🔴 Descubierta |
| `landing` | **0** | 0 | 3 | Nula | 🟢 No requiere |
| **Total** | **32** | **10** | — | | |

**El motor de reglas del quiz tiene cero tests.** Es la lógica de negocio más compleja y sutil del sistema: lockouts de 24 h, ventana de 3 intentos, cool-off tras aprobar, resets automáticos, manejo de zona horaria y concurrencia con `select_for_update()`. Es también la pieza mejor construida. La combinación "código sofisticado sin red de seguridad" es exactamente donde un refactor futuro introduce un defecto silencioso: un usuario que no puede rendir cuando debería, o que puede rendir infinitas veces.

**La generación de certificados tiene cero tests.** Creación del registro, generación del PDF, guardado en disco y los 4 destinatarios de email. Es el entregable final del producto —lo que el cliente efectivamente compra— y no hay ninguna prueba de que siga funcionando después de un cambio.

### 6.3.1 Por qué los 32 tests en verde no detectaron las regresiones

Un patrón concreto y corregible: **todos los tests autentican con `force_login()`**. **[VER]**

```python
self.client.force_login(self.company_user)
response = self.client.get(reverse('dashboard:company:nomina_list'))
```

Ningún test ejerce el camino del **usuario anónimo**, que es precisamente la rama de código que falla. Los tests de aislamiento entre tipos (`test_professional_cannot_access_nomina`) aceptan `[302, 403]`, cubriendo el caso del usuario autenticado del tipo equivocado, pero nunca el del usuario sin sesión.

Complementariamente, **la ficha individual del trabajador (`nomina_detail`) no tiene ningún test**, que es la vista que rompe con `AttributeError`. Los tests de `company` cubren listar, agregar, duplicar y exportar, pero no la lectura de detalle.

**Los tres tests que faltan y que habrían detectado todo:**

```python
def test_anon_redirects_to_login(self):
    """Cualquier ruta de backoffice redirige (no 500) sin sesión."""
    for name in ['dashboard:company:nomina_list',
                 'dashboard:company:agenda_list',
                 'dashboard:company:directorio',
                 'dashboard:my_contact_requests']:
        r = Client().get(reverse(name))
        self.assertEqual(r.status_code, 302)     # hoy: 500

def test_nomina_detail_with_quiz_state(self):
    """La ficha renderiza cuando el trabajador ya rindió."""
    QuizState.objects.create(user=self.trainee, module=self.module)
    r = self.client.get(reverse('dashboard:company:nomina_detail',
                                args=[self.assignment.id]))
    self.assertEqual(r.status_code, 200)          # hoy: 500

def test_directory_flag_is_reachable_from_admin(self):
    """El flag de visibilidad está expuesto en algún formulario."""
    self.assertIn('is_visible_in_directory',
                  [f for fs in CustomUserAdmin.fieldsets for f in fs[1]['fields']])
```

---

# PARTE VII — HALLAZGOS NUEVOS DE LA ETAPA 3

> Once hallazgos que la auditoría de producción no pudo ver porque este código no estaba desplegado. Los identificados como **N1** y **N2** son bloqueantes para cualquier despliegue.

## N1 — 🔴 CRÍTICO — Seis rutas del backoffice devuelven HTTP 500 a usuarios anónimos

**Estado:** Verificado y reproducido. **[VER]**

### Evidencia

```
GET /dashboard/empresa/nomina/                  →  500
GET /dashboard/empresa/nomina/agregar/          →  500
GET /dashboard/empresa/nomina/exportar/         →  500
GET /dashboard/empresa/nomina/<id>/             →  500
GET /dashboard/empresa/agenda/                  →  500
GET /dashboard/empresa/agenda/crear/            →  500
GET /dashboard/empresa/directorio/              →  500
GET /dashboard/solicitudes-contacto/            →  500
GET /dashboard/solicitudes-contacto/<id>/responder/ → 500
```

Excepción capturada:

```
django.urls.exceptions.NoReverseMatch:
Reverse for 'professional_login' not found.
'professional_login' is not a valid view function or pattern name.
```

*(Nueve rutas afectadas en total; "seis" se refiere a las seis vistas distintas de `apps/company/views.py` más las dos de `dashboard`.)*

### Causa raíz

Es [H5](#h5--el-nombre-de-url-professional_login-no-existe), que la auditoría describió como *"una bomba de tiempo: quitar un `@login_required`, o migrar cualquier vista a CBV, produce un HTTP 500"*.

**La Etapa 3 hizo exactamente eso.** Todas las vistas anteriores apilaban los decoradores así:

```python
@login_required          # ← intercepta al anónimo y redirige limpio
@professional_required   # ← la rama rota nunca se alcanza
def historial_presencial(request): ...
```

Las vistas nuevas omiten `@login_required`:

```python
@company_required        # ← el anónimo llega hasta acá
def nomina_list(request):
    if not request.user.is_authenticated:
        url = login_url or reverse('professional_login')   # 💥 NoReverseMatch
```

Lo mismo en `dashboard/views.py:373` y `:386`, que usan `@professional_required` sin `@login_required`.

### Impacto

Cualquier visitante sin sesión que abra un enlace al backoffice de empresa —compartido por email, guardado en favoritos, indexado, o simplemente con la sesión vencida— recibe una **página de error 500**. Con `DEBUG=False` en producción sería la página de error genérica de Django; con `DEBUG=True` expondría un traceback completo con rutas del sistema de archivos.

Adicionalmente, los 500 contaminan cualquier monitoreo futuro y, si se configuraran `ADMINS`, generarían un email de error por cada bot que escanee esas rutas — y el 65 % del tráfico del sitio es escaneo automatizado.

### Corrección

Dos capas, ambas necesarias:

```python
# 1) apps/accounts/decorators.py — corregir los nombres en los 5 decoradores
url = login_url or reverse('accounts_professional:professional_login')
# y en trainee_required:
url = login_url or reverse('trainee_landing')

# 2) apps/company/views.py y apps/dashboard/views.py — restaurar el orden defensivo
@login_required
@company_required
def nomina_list(request): ...
```

La capa 1 corrige el defecto; la capa 2 restaura la defensa en profundidad que enmascaraba el problema. Conviene aplicar ambas: la primera para que el código sea correcto, la segunda para que un futuro error equivalente vuelva a fallar de forma benigna.

Para el backoffice de empresa, además, el destino natural no es el login profesional sino `accounts_company:company_login`.

---

## N2 — 🔴 CRÍTICO — La ficha del trabajador rompe con HTTP 500

**Estado:** Verificado y reproducido. **[VER]**

### Evidencia

```
Ficha SIN QuizState  →  HTTP 200   ✅
Ficha CON QuizState  →  HTTP 500   🔴

AttributeError: 'QuizState' object has no attribute 'is_approved'
```

### Causa

`apps/company/views.py:202`:

```python
module_status.append({
    'module': mod,
    'quiz_state': qs,
    'certificate': cert,
    'is_approved': qs.is_approved if qs else False,   # 💥 la propiedad no existe
    ...
})
```

El modelo `QuizState` expone `attempts_used`, `lockout_until`, `retake_available_at`, `last_completed_at` y `last_passed`. **No tiene `is_approved`.** El campo que expresa esa semántica es **`last_passed`**.

### Por qué no lo detectaron los tests ni el uso manual

- No existe ningún test para `nomina_detail`.
- La rama solo se ejecuta cuando existe un `QuizState` para el par `(trabajador, módulo)`, es decir, **cuando el trabajador ya rindió al menos un quiz** — que es exactamente el caso para el que la ficha fue construida.
- Con una nómina recién cargada y trabajadores que aún no rindieron, la vista devuelve 200 y parece correcta.

En producción, con 16 trabajadores y 16 filas en `quiz_quizstate`, **prácticamente todas las fichas romperían**.

### Corrección

```python
'is_approved': bool(qs.last_passed) if qs else False,
```

Y, en la línea siguiente, conviene simplificar la expresión de vigencia del certificado, que hoy es innecesariamente enrevesada:

```python
# actual
'is_valid': cert and cert.valid_until and cert.valid_until > timezone.now() if cert else False,
# propuesto — el modelo ya tiene la propiedad
'is_valid': cert.is_valid if cert else False,
```

### Nota adicional de eficiencia

El bucle ejecuta **dos consultas por módulo** (`QuizState` y `Certificate`). Con 6 módulos son 12 consultas por ficha, más las de intentos y certificados. Con un catálogo mayor escala linealmente. Es prescindible optimizarlo ahora, pero conviene anotarlo: un `in_bulk()` previo sobre ambos modelos lo reduce a 2 consultas totales.

---

## N3 — 🟠 ALTO — El directorio de profesionales es inalcanzable

**Estado:** Verificado. **[VER]**

### El problema

El directorio (Commit 46) y las solicitudes de contacto (Commit 47) —los dos últimos commits funcionales de la Etapa 3— filtran por:

```python
professionals = User.objects.filter(
    user_type='professional',
    is_visible_in_directory=True,
    is_active=True,
)
```

El campo `is_visible_in_directory` se declara con **`default=False`**. Y **no existe ningún control en toda la aplicación para activarlo**:

| Superficie | ¿Expone el flag? |
|---|---|
| `CustomUserAdmin.fieldsets` | ❌ No aparece en ninguno de los 9 fieldsets |
| `CustomUserAdmin.list_display` / `list_editable` | ❌ No |
| `ProfessionalProfileForm` (`/dashboard/perfil/`) | ❌ No — el formulario tiene `first_name`, `last_name`, `email`, `profession`, `license_number`, `dni` |
| Formulario de registro profesional | ❌ No |
| Comando de gestión | ❌ No existe |

**Consecuencia:** el directorio siempre se renderiza vacío. Ninguna empresa puede encontrar ni contactar a ningún profesional. Los Commits 46 y 47 son funcionalmente inertes hasta que alguien edite la base de datos a mano o abra un `manage.py shell`.

### Por qué los tests no lo detectaron

El test lo pasa como argumento directo al constructor, saltándose por completo la cuestión de si existe una forma de activarlo desde la aplicación:

```python
professional = User.objects.create_professional(
    email='procontact@test.com', ...,
    is_visible_in_directory=True,   # ← nunca ocurre en la vida real
)
```

### Corrección

Dos opciones, no excluyentes:

1. **Control administrativo** — agregar `is_visible_in_directory` al fieldset "Datos de Profesional" del `CustomUserAdmin`, y a `list_display` + `list_editable` para poder activarlo en lote desde la lista.
2. **Autogestión** — agregar un checkbox al `ProfessionalProfileForm` con una etiqueta del tipo *"Quiero aparecer en el directorio de profesionales visible para empresas"*. Es la opción correcta desde la perspectiva de protección de datos: el profesional consiente explícitamente aparecer en un listado público-interno con su nombre, profesión y matrícula.

Recomendación: implementar ambas, con la autogestión como camino principal.

---

## N4 — 🟠 ALTO — El login de empresa depende del backend de fallback

**Estado:** Verificado. **[VER]**

### Evidencia

```
authenticate(username='empresa@test.com', password=...)
  → resuelto por: django.contrib.auth.backends.ModelBackend

authenticate(username='prof@test.com', password=...)
  → resuelto por: apps.accounts.backends.ProfessionalBackend
```

### El problema

`ProfessionalBackend` filtra explícitamente `user_type='professional'`:

```python
user = User.objects.get(email__iexact=username, user_type='professional')
```

`CuilEmailBackend` filtra `user_type='trainee'`. **Ningún backend propio contempla `company`.** Las empresas se autentican únicamente porque la cadena termina en el `ModelBackend` de Django, que fue incorporado —según el propio comentario del código— como *"fallback Django (admin/superuser/compatibilidad)"*.

### Consecuencias

1. **Fragilidad.** Retirar `ModelBackend` de `AUTHENTICATION_BACKENDS` —una limpieza razonable que cualquiera podría intentar al endurecer la autenticación— **deja a todas las empresas fuera del sistema sin ningún error visible**: `authenticate()` simplemente devuelve `None` y el formulario dice "Email o contraseña incorrectos".

2. **Incoherencia semántica declarada.** `company_register` fuerza explícitamente un backend que jamás autenticaría a ese usuario:

   ```python
   login(request, user, backend='apps.accounts.backends.ProfessionalBackend')
   ```

   Funciona porque `login()` solo persiste la ruta del backend en la sesión, y el `get_user()` de `ProfessionalBackend` no filtra por tipo. Pero deja escrito en la sesión de cada empresa que fue autenticada por un backend que la rechaza.

3. **`ModelBackend` no discrimina por tipo**, lo que habilita [N5](#n5--medio--login-cruzado-asimétrico-entre-portales).

### Corrección

Crear un `CompanyBackend` análogo a `ProfessionalBackend` (filtrando `user_type='company'`), registrarlo en `AUTHENTICATION_BACKENDS` antes del fallback, y usarlo explícitamente en `company_register`. Con eso, `ModelBackend` vuelve a ser lo que dice ser: el fallback del admin.

---

## N5 — 🟡 MEDIO — Login cruzado asimétrico entre portales

**Estado:** Verificado. **[VER]**

### Evidencia

```
Empresa en /auth/login/          (portal profesional)  →  302 → /dashboard/   ✅ ENTRA
Profesional en /empresa/auth/login/ (portal empresa)   →  200 (rechazado)     ❌ NO ENTRA
```

### Causa

`company_login` verifica el tipo después de autenticar:

```python
if not user.is_company:
    messages.error(request, "Esta cuenta no es de empresa. ...")
    return render(...)
```

`login_view` (profesional) **no hace la verificación equivalente**: autentica y hace `login()` sin comprobar `is_professional`. Como `ModelBackend` no filtra por tipo, una empresa entra por la puerta de los profesionales.

### Impacto

No es una escalación de privilegios: la matriz de acceso ([§5.5.4](#554-matriz-de-acceso-verificada)) muestra que los decoradores siguen aplicando el aislamiento correcto una vez dentro. Es un defecto de **coherencia de producto y de experiencia**: dos puertas de entrada que se comportan de forma distinta ante el mismo error del usuario, y una de ellas acepta silenciosamente credenciales del portal equivocado.

### Corrección

Agregar en `login_view` el chequeo simétrico:

```python
if user is not None:
    if not user.is_professional:
        messages.error(request, "Esta cuenta no es de profesional. "
                                "Si sos empresa, ingresá desde el portal de empresas.")
        return render(request, "accounts/professional/login.html", {"form": form})
    login(request, user)
```

Alternativa más elegante: un único punto de entrada que detecte el tipo y redirija al área correspondiente, eliminando la duplicación de formularios. Es más trabajo y conviene evaluarlo como decisión de producto, no como corrección de defecto.

---

## N6 — 🟡 MEDIO — Callejón sin salida empresa → presencial

**Estado:** Verificado. **[VER]**

### Evidencia — recorrido real de un usuario empresa

```
/dashboard/capacitaciones/               →  200   ✅  ve el grid de módulos
/dashboard/capacitaciones/ergonomia/     →  200   ✅  ve "Presencial | Online"
/dashboard/capacitaciones/ergonomia/links/ → 200  ✅  puede generar links
/dashboard/presencial/ergonomia/         →  403   🔴  "Acceso denegado"
/dashboard/presencial/historial/         →  403   🔴
```

### Causa

El Commit 33 migró las vistas de capacitaciones de `@professional_required` a `@backoffice_required` para que las empresas accedieran, pero **las vistas de `apps/presencial/` quedaron en `@professional_required`**. El selector de modalidad ofrece dos caminos y uno de ellos termina en un muro.

### Decisión de producto pendiente

No es obvio cuál es el comportamiento correcto, y por eso conviene decidirlo explícitamente:

| Opción | Implicancia |
|---|---|
| **A — Las empresas también dictan presencial** | Migrar las 5 vistas de `presencial` a `@backoffice_required`. Requiere revisar `PresencialSession.professional`, que es una FK semánticamente atada al profesional |
| **B — Presencial es exclusivo del profesional** | Ocultar la tarjeta "Presencial" en `modalidad_selector.html` cuando `is_company_user` es verdadero. El context processor ya provee ese flag |

La opción B es más barata y más coherente con el modelo de negocio (la modalidad presencial supone un profesional matriculado dictando la capacitación). La opción A tiene sentido si una empresa con su propio servicio interno de higiene y seguridad quisiera usar la herramienta.

**Sea cual sea la decisión, el estado actual —ofrecer una opción y luego negarla— no es aceptable.**

---

## N7 — 🟡 MEDIO — `agenda_complete` muta estado por GET

**Estado:** Verificado. **[VER]**

```
GET /dashboard/empresa/agenda/<id>/completar/  →  302
Estado del evento tras el GET: 'completed'
```

### El problema

La vista no tiene `@require_POST` ni ninguna comprobación de `request.method`:

```python
@company_required
def agenda_complete(request, event_id):
    event = get_object_or_404(AgendaEvent, company=cp, id=event_id)
    event.status = AgendaEvent.EventStatus.COMPLETED
    event.save()
```

Un GET modifica estado persistente. Esto significa que:

- La protección CSRF **no aplica** (Django solo la exige en métodos no seguros).
- Cualquier precargador de enlaces, escáner o extensión de navegador que siga el enlace marca eventos como completados.
- Un tercero puede provocar la acción incrustando `<img src="https://…/completar/">` en un email o página que la empresa abra con sesión activa.

El impacto real es acotado —marcar un recordatorio como completado no destruye datos y es reversible desde la edición—, pero es una violación clara de la semántica HTTP y un patrón que no conviene dejar como precedente en el código.

Nótese que el resto del proyecto es correcto en este punto: `send_contact_request` y `respond_contact_request` sí verifican `request.method != "POST"`, y `generate_link` usa `@require_POST`. Es una omisión puntual, no un criterio del proyecto.

### Corrección

```python
from django.views.decorators.http import require_POST

@login_required
@company_required
@require_POST
def agenda_complete(request, event_id):
    ...
```

Y verificar que `templates/company/agenda_list.html` dispare la acción con un `<form method="post">` y su `{% csrf_token %}`, no con un enlace.

---

## N8 — 🟡 MEDIO — Pillow es dependencia obligatoria y no está declarada

**Estado:** Verificado. **[VER]**

`CompanyProfile.logo` es un `models.ImageField`. Django exige **Pillow** para los `ImageField`: sin él, el system check falla con `fields.E210` y **la aplicación no arranca**.

`requirements.txt` **no menciona Pillow**. Hoy está satisfecho de forma transitiva (`reportlab` lo arrastra; en el venv local hay Pillow 12.1.0 y en producción 12.1.1), pero es una dependencia dura que descansa en un detalle de instalación de otro paquete.

### Riesgo concreto

Si en algún momento se reemplaza ReportLab por otro generador de PDF, o si una versión futura de ReportLab deja de depender de Pillow, `apps.company` deja de importar y **toda la aplicación cae al arrancar**, no de forma degradada sino total.

### Corrección

Agregar `Pillow>=10.0` a `requirements.txt` y, en el mismo movimiento, agregar `gunicorn` —que es el servidor real de producción y tampoco está declarado— y fijar versiones exactas ([H18](#h18--sin-fijado-de-versiones--agravado)):

```
Django==5.2.11
psycopg[binary]==3.3.3
django-environ==0.13.0
django-bootstrap5==26.2
whitenoise==6.9.0
reportlab==4.2.5
Pillow==12.1.1
openai==2.21.0
openai-agents==0.9.2
gunicorn==25.1.0
uvicorn==0.35.0
```

*(Versiones tomadas de las reportadas como instaladas en producción; conviene confirmarlas con `pip freeze` en el servidor antes de fijar.)*

---

## N9 — 🟡 MEDIO — `generate_cert_expiry_events` sin planificador

**Estado:** Verificado por lectura. **[COD]**

El comando está bien construido: acepta `--days` y `--dry-run`, es idempotente, usa `select_related` y reporta un resumen de creados y omitidos.

**Pero nada lo ejecuta.** No hay entrada en `/etc/cron.d/` para ErgoSolutions, ni timer de systemd, ni Celery beat en esta aplicación. Todo el panel de vencimientos del dashboard de empresa (Commit 45) depende de que existan `AgendaEvent` de tipo `certificate_expiry`, y esos eventos solo nacen si alguien corre el comando a mano.

**Consecuencia:** la funcionalidad estrella de la Etapa 3C —avisar a la empresa que se le vencen las capacitaciones— no ocurre nunca por sí sola.

### Corrección

Un cron diario junto al backup del Bloque 0:

```
# /etc/cron.d/ergocapacitacion
30 4 * * * deploy cd /srv/ergocapacitacion/app && /srv/ergocapacitacion/venv/bin/python manage.py generate_cert_expiry_events --days 45 >> /srv/ergocapacitacion/logs/cron-agenda.log 2>&1
```

*(La ventana de 45 días da margen para coordinar una recapacitación antes del vencimiento; el default del comando es 30.)*

Nótese que el archivo de log resultante también necesita entrar en el logrotate de [H3](#h3--sin-rotación-de-logs).

---

## N10 — 🔵 BAJO — `ContactRequest` no está registrado en el admin

**Estado:** Verificado. **[VER]**

`apps/company/admin.py` importa y registra `CompanyProfile`, `CompanyWorker` y `AgendaEvent`. **`ContactRequest` no se importa ni se registra.**

No hay forma de inspeccionar, moderar ni depurar las solicitudes de contacto desde el panel de administración. Dado que es un canal de comunicación entre dos partes externas —una empresa escribiéndole a un profesional— la falta de visibilidad administrativa es relevante para soporte y para moderación de abuso.

Corrección trivial: agregar `ContactRequest` al import y un `ContactRequestAdmin` con `list_display`, filtro por `status` y campos de auditoría en solo lectura.

---

## N11 — 🔵 BAJO — El pipeline de certificados ignora a la empresa

**Estado:** Verificado por lectura. **[COD]**

`send_certificate_emails()` notifica hasta cuatro destinatarios: trabajador, `employer_email`, `safety_responsible_email` y admin. Los dos del medio son **campos de texto libre cargados por el propio trabajador** en su registro.

Ahora que existe `CompanyWorker` —una relación formal, validada, entre una empresa con cuenta y un trabajador— el pipeline **no la consulta**. Una empresa que cargó a sus 50 trabajadores en la nómina no recibe ninguna notificación cuando uno de ellos se certifica, salvo que ese trabajador haya escrito a mano el email correcto en su registro meses atrás.

Es una brecha de integración entre las dos etapas, no un defecto de ninguna de las dos. Vale la pena registrarla porque **es justamente el valor que una empresa esperaría del módulo de nómina**.

### Corrección sugerida

En `_create_certificate`, resolver los destinatarios adicionales consultando `CompanyWorker.objects.filter(worker=user, is_active=True)` y agregando el email de contacto de cada `CompanyProfile` asociado. Conviene hacerlo junto con el movimiento de los emails a background ([H11](#h11--envío-de-email-síncrono-dentro-del-request)), ya que sumar destinatarios a un envío síncrono agrava el bloqueo de workers.

---

## N12 — 🔵 BAJO — Registro de empresa: CUIT duplicado deja un usuario huérfano

**Estado:** Verificado y reproducido. **[VER]**

### Evidencia

```
Alta 1 (CUIT 20-12345678-9)            →  usuarios: 1  |  perfiles: 1   ✅
Alta 2 (mismo CUIT, otro email)        →  HTTP 500
                                          usuarios: 2  |  perfiles: 1   🔴
Usuario huérfano creado sin perfil: True
```

### Causa

`CompanyRegisterForm.clean_email()` valida unicidad del email contra `CustomUser`. **`clean_cuit()` solo normaliza a 11 dígitos y no valida unicidad** contra `CompanyProfile.cuit`, que es `unique=True` a nivel de base de datos.

Además, `company_register` crea el usuario y el perfil en **dos operaciones sin transacción**:

```python
user = User.objects.create_company(...)      # ← se persiste
CompanyProfile.objects.create(...)           # ← IntegrityError si el CUIT existe
```

### Impacto

El usuario queda creado, con contraseña válida, `user_type='company'` y **sin `CompanyProfile`**. Ese usuario puede iniciar sesión y entra a un sistema roto: el dashboard de empresa cae en el `except CompanyProfile.DoesNotExist` y renderiza el template del profesional con contexto vacío; todas las rutas de nómina y agenda lo redirigen con "No se encontró el perfil de empresa". Y como el email quedó ocupado por la restricción de unicidad, **la empresa no puede volver a registrarse con la misma dirección**.

### Corrección

Las dos piezas:

```python
# 1) Validación en el formulario
def clean_cuit(self):
    cuit = normalize_cuit(self.cleaned_data['cuit'])
    from apps.company.models import CompanyProfile
    if CompanyProfile.objects.filter(cuit=cuit).exists():
        raise forms.ValidationError('Ya existe una empresa registrada con este CUIT.')
    return cuit

# 2) Atomicidad en la vista
from django.db import transaction

with transaction.atomic():
    user = User.objects.create_company(...)
    CompanyProfile.objects.create(user=user, ...)
```

La validación cubre el caso esperable; la transacción cubre la condición de carrera entre dos altas simultáneas con el mismo CUIT.

---

## N13 — 🔵 BAJO — Listados sin paginación

**Estado:** Verificado por lectura. **[COD]**

| Vista | Comportamiento |
|---|---|
| `nomina_list` | Sin paginación ni límite — renderiza la nómina completa |
| `agenda_list` | `events_qs[:100]` — **trunca en silencio** |

En la agenda, el corte a 100 no se comunica en ninguna parte de la interfaz: una empresa con más de 100 eventos ve una lista incompleta sin ningún indicio de que falten filas. Es peor que no tener límite, porque induce a confiar en un dato parcial.

Con nóminas grandes —el caso de uso explícito del módulo— la ausencia de paginación en `nomina_list` produce páginas de cientos de filas y consultas cada vez más lentas.

**Corrección:** `django.core.paginator.Paginator` en ambas vistas, con controles de navegación en los templates. Es trabajo acotado y conviene hacerlo antes de que haya datos reales, no después.

---

# PARTE VIII — LO QUE FIGURA COMO PENDIENTE EN EL PROPIO PROYECTO

Fuente: `docs/ERGOSOLUTIONS_ARQUITECTURA_ROADMAP.md`, `docs/MAPA_CONCEPTUAL_VISUAL.md`, `docs/PLAN_MAESTRO_ETAPA_3_PERFIL_EMPRESA.md` y marcadores en el código.

## 8.1 Estado del roadmap declarado

| Fase | Alcance | Estado verificado |
|---|---|---|
| **1. Fundamentos** | `CustomUser`, auth dual, reorganización de URLs | ✅ **Completa** |
| **2. Landing + auth profesional** | Landing, registro, login | ✅ **Completa** |
| **3. Dashboard + menú** | Panel, grid de capacitaciones, selector de modalidad | ✅ **Completa** |
| **4. Modo presencial** | Página, planilla PDF, `PresencialSession` | ✅ **Completa** |
| **5. Modo online** | `CapacitacionLink`, compartir, rutas `/c/<slug>/` | ✅ **Completa** |
| **6. Mejoras y pulido** | Perfil, más capacitaciones, testing | 🟡 **Parcial**: perfil ✅ / **contenido ❌** / testing parcial |
| **Etapa 3. Perfil Empresa** | Commits 29–48: empresa, nómina, agenda, directorio | 🟡 **Código completo, con defectos, sin desplegar** |
| **7. Futuro** | Evaluaciones + Suscripciones + Pagos + Facturación | 🔴 **No iniciada** |

## 8.2 Pendientes explícitos

### A) Módulo de EVALUACIONES — el segundo pilar del producto, sin construir

El roadmap lo define como una de las dos patas de la plataforma: *"Evaluaciones de riesgos ergonómicos, iluminación, ruido y más, todo según normativa vigente"*. Hoy es una **tarjeta gris con badge "Próximamente"** en `templates/dashboard/home.html:81-92`. **[VER]**

No existe la app `evaluaciones`, ni modelos, ni rutas. El roadmap contemplaba `/evaluaciones/` y `/evaluaciones/<tipo>/`.

> **Nota de la Etapa 3:** `AgendaEvent.EventType` ya incluye `evaluation_due` ('Evaluación pendiente'). El modelo de datos anticipa el módulo que todavía no existe.

### B) Sistema de SUSCRIPCIONES — infraestructura lista, lógica ausente

Está **preparado y desactivado**, deliberadamente:

- `CustomUser` ya tiene `subscription_tier`, `subscription_status`, `subscription_expires` y la propiedad `has_active_subscription` (que valida estado + vencimiento).
- Existe el decorador `@subscription_required(tier='basic')` y el mixin `SubscriptionRequiredMixin` con jerarquía `free(0) < basic(1) < premium(2)`.
- **Ninguna vista los usa.** No hay pasarela de pago, planes, facturación ni gestión de ciclo de vida.

> **Nota:** el decorador `subscription_required` exige `is_professional`. Con la Etapa 3, el modelo de monetización más probable pasa por las **empresas**, no por los profesionales. Cuando se active la Fase 7 habrá que revisar esa restricción.

### C) Capacitaciones adicionales (Fase 6.2)

Cinco módulos definidos sin video, contenido ni preguntas. Es trabajo de contenido, no de código. **Es el desbloqueo comercial de mayor retorno del proyecto.**

### D) TODO explícito en el código

`apps/certificates/views.py:93`: **[VER]**

```python
def my_certificates(request):
    """... TODO: Implementar template si se necesita una vista de lista."""
```

`/certificados/` devuelve **JSON crudo** al navegador. Un trabajador que llegue a esa URL ve un volcado técnico, no una página. Es la única ruta con una experiencia claramente inacabada.

### E) `prompts/modules/<slug>.md`

`build_system_prompt` busca instrucciones específicas por módulo en ese directorio, que **no existe**. Es un punto de extensión previsto, sin usar. Se volverá relevante al cargar los 5 módulos faltantes, donde cada uno puede necesitar matices de tono o alcance para Ergobot.

### F) `CSRF_TRUSTED_ORIGINS` anotado en el `.env`

El propio `.env` documenta en un comentario que no se lee desde el entorno, y deja escrita la línea a agregar. Es deuda conocida y anotada, no resuelta.

### G) `PLAN_EMAIL_PRODUCCION.md` — documento cerrado

Este plan **sí se ejecutó completo**: el bug `ADMIN_CERT_EMAIL` vs `ADMIN_EMAIL` está corregido, `EMAIL_USE_SSL` y `SERVER_EMAIL` están en `settings.py`, la validación de credenciales SMTP está implementada, `.env.example` está completo y existe `send_test_email`. Se conserva por trazabilidad.

---

# PARTE IX — RIESGOS CONSOLIDADOS

## 9.1 Matriz de priorización

Ordenada por el producto de impacto × probabilidad × facilidad de corrección.

| Prioridad | ID | Riesgo | Impacto | Esfuerzo |
|---|---|---|---|---|
| **1** | H1 | Pérdida total de datos por ausencia de backup | Catastrófico | ~30 min |
| **2** | N1 | HTTP 500 en 9 rutas del backoffice | Bloquea el deploy | ~1 h |
| **3** | N2 | Ficha del trabajador rota | Bloquea el módulo de nómina | ~15 min |
| **4** | H2 | Datos personales (nombre + CUIL) accesibles sin auth | Alto — exposición | ~1 h |
| **5** | N3 | Directorio inalcanzable | 2 commits inertes | ~30 min |
| **6** | H3 | Log sin rotar, 23 MB y creciendo | Medio — operativo | ~10 min |
| **7** | H5/H6 | Nombres de URL rotos y redirect al login equivocado | Medio — UX y latencia de fallos | ~1 h |
| **8** | N4 | Login de empresa sobre backend de fallback | Medio — fragilidad | ~45 min |
| **9** | N12 | Usuario huérfano por CUIT duplicado | Medio — integridad | ~20 min |
| **10** | H7 | Links vencidos siguen dando acceso | Medio — control de negocio | ~15 min |
| **11** | H10 | Sin `SECURE_PROXY_SSL_HEADER` | Medio — bloquea ASGI | ~10 min |
| **12** | H13/H14/H15 | Cookies sin `Secure`, sin HSTS, `CSRF_TRUSTED_ORIGINS` vacío | Medio — hardening | ~20 min |
| **13** | N6 | Callejón sin salida empresa → presencial | Medio — UX | ~30 min |
| **14** | N9 | Vencimientos automáticos sin planificador | Medio — funcionalidad inerte | ~15 min |
| **15** | N7 | Mutación de estado por GET | Bajo — semántica HTTP | ~10 min |
| **16** | H4 | `main` 40 commits atrás | Bajo — confusión | ~15 min |
| **17** | H8/H9 | Quiz presencial sin explicaciones, umbral duplicado | Bajo — valor didáctico | ~15 min |
| **18** | N8/H18 | Dependencias sin fijar, Pillow no declarado | Bajo — reproducibilidad | ~20 min |
| **19** | H16/H17 | Registro abierto, sin rate limiting | Bajo hoy, alto al abrir el producto | ~3 h |
| **20** | — | Quiz y certificados sin tests | Alto a mediano plazo | ~1 día |
| **21** | H11/H12 | Email síncrono, async sobre WSGI | Alto bajo carga real | ~2 días |
| **22** | H20 | Firma hardcodeada | Bloquea el modelo SaaS | ~4 h |

## 9.2 Riesgos que no son técnicos

Tres observaciones que exceden el código y que conviene tener presentes al planificar:

**1. El producto no tiene usuarios.** Cero actividad desde el 23/04/2026. Cualquier inversión en funcionalidad nueva —incluida la Etapa 3— compite contra la inversión en conseguir que alguien use lo ya construido.

**2. La plataforma tiene un solo curso.** El esfuerzo de ingeniería acumulado (7.924 líneas de Python, 13 modelos, 3 tipos de usuario) sirve un catálogo de un ítem. La relación entre capacidad construida y capacidad vendible es la anomalía más grande del proyecto.

**3. Existe un patrón de construir por delante de validar.** `LinkShareLog` en 0 usos. Capacitaciones personalizadas: 0 asignaciones. Etapa 3 completa: sin desplegar. Tres funcionalidades consecutivas terminadas y no ejercitadas. El plan de la Parte VII intenta romper ese patrón poniendo el despliegue —y por lo tanto el contacto con la realidad— antes que la construcción nueva.

---

# PARTE X — PLAN DE TRABAJO

> Secuencia propuesta. Cada bloque es autocontenido y verificable. Los bloques 0 a 4 deberían ejecutarse en orden; a partir del 5 hay margen para reordenar según prioridad comercial.

## Bloque 0 — Operación de producción (sin tocar código)

**Objetivo:** que un fallo del VPS deje de ser catastrófico. **Prerrequisito de todo lo demás.**

| # | Tarea | Hallazgo | Esfuerzo |
|---|---|---|---|
| 0.1 | **Backup diario de `ergocapacitacion_db`** replicando el patrón ya probado de CriaApp: `pg_dump` en formato custom, retención de 7 días, vía `/etc/cron.d/`. **Incluir `media/`** (certificados y, a futuro, logos) | H1 | 30 min |
| 0.2 | **Verificar la restauración** en una base descartable. Un backup no probado no es un backup | H1 | 20 min |
| 0.3 | **Logrotate** para `/srv/ergocapacitacion/logs/*.log`: rotación semanal, 8 copias, `copytruncate` (gunicorn no reabre descriptores con SIGHUP por defecto) | H3 | 10 min |
| 0.4 | **Healthcheck externo** sobre `/acceso/health/` con alerta por email o Telegram | H19 | 20 min |

**Criterio de finalización:** existe un dump de menos de 24 horas, se restauró con éxito al menos una vez, y `gunicorn-access.log` está rotando.

---

## Bloque 1 — Reparar las regresiones de la Etapa 3

**Objetivo:** que `v0.1.7-beta` sea desplegable. **Bloquea el Bloque 4.**

| # | Tarea | Hallazgo | Esfuerzo |
|---|---|---|---|
| 1.1 | Corregir los nombres de URL en `decorators.py` (5 ocurrencias) y `mixins.py` (5 ocurrencias) | H5 / N1 | 30 min |
| 1.2 | Restaurar `@login_required` delante de `@company_required` y `@professional_required` en las 8 vistas que lo omiten | N1 | 20 min |
| 1.3 | Corregir `qs.is_approved` → `qs.last_passed` y simplificar `is_valid` en `nomina_detail` | N2 | 15 min |
| 1.4 | Exponer `is_visible_in_directory` en el admin y en `ProfessionalProfileForm` | N3 | 30 min |
| 1.5 | Validar unicidad de CUIT y envolver el registro de empresa en `transaction.atomic()` | N12 | 20 min |
| 1.6 | `@require_POST` en `agenda_complete` y ajuste del template | N7 | 10 min |
| 1.7 | Resolver el callejón empresa → presencial (decisión de producto: ocultar u habilitar) | N6 | 30 min |
| 1.8 | **Tests de regresión**: acceso anónimo a todas las rutas de backoffice, `nomina_detail` con `QuizState`, alcanzabilidad del flag de directorio | §6.3.1 | 1 h |

**Criterio de finalización:** ninguna ruta del proyecto devuelve 500 a un usuario anónimo; la ficha del trabajador renderiza con datos reales; el directorio muestra profesionales activables desde la interfaz.

---

## Bloque 2 — Cerrar los hallazgos heredados de la misma familia

**Objetivo:** eliminar el resto de la deuda que comparte causa raíz con lo anterior.

| # | Tarea | Hallazgo | Esfuerzo |
|---|---|---|---|
| 2.1 | Redirigir cada área a su propio login: `login_url` explícito según el tipo de área, o resolución por tipo de usuario | H6 | 45 min |
| 2.2 | Hacer que `expires_at` / `is_active` bloqueen efectivamente el acceso en `public_landing` | H7 | 15 min |
| 2.3 | `explanation_correct` en el quiz presencial e importar `PASS_SCORE` en lugar del `8` literal | H8 / H9 | 15 min |
| 2.4 | Crear `CompanyBackend` y usarlo explícitamente en el registro y login de empresa | N4 | 45 min |
| 2.5 | Chequeo simétrico de tipo en el login profesional | N5 | 15 min |
| 2.6 | Cron diario para `generate_cert_expiry_events --days 45` | N9 | 15 min |
| 2.7 | Registrar `ContactRequest` en el admin | N10 | 10 min |
| 2.8 | Paginación en `nomina_list` y `agenda_list` | N13 | 45 min |
| 2.9 | Eliminar los ~280 líneas de código muerto en `certificates/views.py` y `pdf.py` | H21 | 10 min |

---

## Bloque 3 — Seguridad y configuración

| # | Tarea | Hallazgo | Esfuerzo |
|---|---|---|---|
| 3.1 | Agregar `SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")` — **antes de cualquier cambio de servidor de aplicación** | H10 | 10 min |
| 3.2 | `CSRF_TRUSTED_ORIGINS`, `SESSION_COOKIE_SECURE=True`, `CSRF_COOKIE_SECURE=True`, `SECURE_HSTS_SECONDS` (empezar en 3600 y escalar) | H13/H14/H15 | 20 min |
| 3.3 | **Mover `media/certificates/` detrás de Django** con `X-Accel-Redirect` e `internal;` en nginx, para que la verificación de propiedad sea efectiva | H2 | 1 h |
| 3.4 | Fijar versiones en `requirements.txt`, agregando `Pillow` y `gunicorn` | H18 / N8 | 20 min |
| 3.5 | Declarar la versión de Python (`.python-version` o `pyproject.toml`) y alinear dev con producción | §2.3 | 15 min |
| 3.6 | Validación de alta de empresa: usar `account_status='pending_validation'` como default y requerir aprobación | H16 | 1 h |
| 3.7 | Rate limiting en los tres logins (`django-axes` o `limit_req` en nginx) | H17 | 2 h |

**Criterio de finalización:** `manage.py check --deploy` con `DEBUG=False` sin advertencias, y `GET /media/certificates/<archivo>.pdf` devuelve 403 sin sesión.

---

## Bloque 4 — Desplegar `v0.1.8-beta`

**Objetivo:** el primer despliegue en cinco meses. Es el bloque que convierte todo lo anterior en valor real.

| # | Tarea |
|---|---|
| 4.1 | Backup verificado inmediatamente antes (Bloque 0 ya lo garantiza, pero se toma uno puntual) |
| 4.2 | Decidir y ejecutar la estrategia de ramas: alinear `main` con `release/beta` o declarar formalmente `release/beta` como rama de producción y cambiar la rama por defecto en GitHub — **[H4]** |
| 4.3 | Commitear la reorganización documental pendiente ([§3.5](#35-cambios-sin-commitear-en-el-árbol-de-trabajo)), revisando conscientemente el efecto del `.gitignore` sobre los planes maestros |
| 4.4 | Actualizar `README.md`: corregir "Async: ASGI + Uvicorn" e incluir `apps.company` en el comando de tests — **[H26]** |
| 4.5 | Tag `v0.1.8-beta` |
| 4.6 | En el servidor: `git fetch`, checkout del tag, `pip install -r requirements.txt`, **`migrate` (6 migraciones)**, `collectstatic`, `systemctl restart ergocapacitacion` |
| 4.7 | Smoke test: los tres logins, dashboard de cada tipo, alta de empresa, alta en nómina, ficha del trabajador, generación de link, quiz completo con emisión de certificado |
| 4.8 | Verificar que ninguna ruta devuelve 500 anónimamente en el entorno real |

---

## Bloque 5 — Contenido: el desbloqueo comercial

**Objetivo:** pasar de 1 a 6 cursos vendibles. **Es el trabajo de mayor retorno del proyecto y no requiere ingeniería.**

Por cada uno de los 5 módulos inactivos (`ruido`, `riesgo-electrico`, `trabajo-en-altura`, `prevencion-incendios`, `elementos-proteccion-personal`):

| # | Tarea |
|---|---|
| 5.1 | Grabar o seleccionar el video y cargar el `youtube_id` |
| 5.2 | Escribir `apps/training/content/<slug>/intro.md`, `material.md` y `transcript.txt` siguiendo el patrón de `ergonomia` |
| 5.3 | Redactar 10 preguntas con 4 opciones, `explanation_correct` y `explanation_if_chosen` por opción |
| 5.4 | Ejecutar `seed_module_content --module <slug>` y sembrar el quiz |
| 5.5 | Opcionalmente, crear `apps/ergobot_ai/prompts/modules/<slug>.md` con los matices de tono del módulo — **[Pendiente E]** |
| 5.6 | Activar el módulo (`is_active=True`) y probar el flujo completo de punta a punta |

**Recomendación de secuencia:** empezar por **uno solo** —el de mayor demanda comercial— y recorrer el flujo completo con un cliente real antes de producir los otros cuatro. Es la forma concreta de romper el patrón identificado en [§9.2](#92-riesgos-que-no-son-técnicos).

---

## Bloque 6 — Escalabilidad

**Objetivo:** que la aplicación soporte uso concurrente real.

| # | Tarea | Hallazgo | Nota |
|---|---|---|---|
| 6.1 | **Tests del motor de reglas del quiz**: lockout de 24 h, ventana de 3 intentos, cool-off, resets automáticos, concurrencia | §6.3 | La pieza de mayor riesgo con cobertura cero |
| 6.2 | **Tests del pipeline de certificados**: creación, PDF, guardado, 4 destinatarios, manejo de fallos | §6.3 | — |
| 6.3 | Mover el envío de emails a background | H11 | Requiere decidir Celery + Redis (ya instalado para CriaApp) o `django-q`/`huey` |
| 6.4 | Incluir a la empresa entre los destinatarios del certificado vía `CompanyWorker` | N11 | Hacer junto con 6.3 |
| 6.5 | **Migrar a ASGI con uvicorn** | H12 | ⚠️ **Requiere 3.1 aplicado**, o todos los formularios del sitio devuelven 403 |
| 6.6 | CI en GitHub Actions: suite de tests + `check --deploy` + linter en cada push | H27 | Cierra la causa raíz de N1 |

---

## Bloque 7 — Producto (Fase 7 del roadmap)

| # | Tarea | Nota |
|---|---|---|
| 7.1 | **Parametrizar la firma del certificado** por profesional (nombre, matrícula, especialidad, logo) | Prerrequisito estructural del modelo SaaS y del modelo multi-empresa — **[H20]** |
| 7.2 | Template HTML para `/certificados/` en lugar del JSON crudo | **[H22]** |
| 7.3 | **Módulo de Evaluaciones** — el segundo pilar declarado del producto | `AgendaEvent.EventType.EVALUATION_DUE` ya lo anticipa |
| 7.4 | **Activar Suscripciones**: pasarela de pago, planes, ciclo de vida | Revisar que `subscription_required` no siga restringido a `is_professional` |

---

# ANEXOS

## Anexo A — Comandos de verificación

Los siguientes comandos reproducen las verificaciones de este documento.

**Suite de tests completa** (32 tests, incluye `apps.company`, que el README omite):

```bash
python manage.py test apps
```

**Chequeo de despliegue:**

```bash
DEBUG=False python manage.py check --deploy
```

**Verificar que ninguna ruta de backoffice devuelve 500 sin sesión** (reproduce N1):

```bash
python -c "
import os, django; os.environ['DJANGO_SETTINGS_MODULE']='config.settings'; django.setup()
from django.test import Client
c = Client(raise_request_exception=False)
for p in ['/dashboard/', '/dashboard/empresa/nomina/', '/dashboard/empresa/agenda/',
          '/dashboard/empresa/directorio/', '/dashboard/solicitudes-contacto/']:
    print(p, '->', c.get(p, HTTP_HOST='127.0.0.1').status_code)
"
```

**Verificar los nombres de URL usados en decoradores** (reproduce H5):

```bash
python -c "
import os, django; os.environ['DJANGO_SETTINGS_MODULE']='config.settings'; django.setup()
from django.urls import reverse, NoReverseMatch
for n in ['professional_login', 'landing', 'dashboard',
          'accounts_professional:professional_login', 'trainee_landing', 'dashboard:home']:
    try: print('OK  ', n, '->', reverse(n))
    except NoReverseMatch: print('FAIL', n)
"
```

**Estado de las migraciones pendientes:**

```bash
python manage.py showmigrations accounts company
```

## Anexo B — Índice de hallazgos

### Heredados de la auditoría de producción (H1–H27)

| ID | Título | Severidad |
|---|---|---|
| [H1](#h1--crítico--sin-backup-automatizado-de-la-base-de-producción) | Sin backup automatizado de la base de producción | 🔴 Crítico |
| [H2](#h2--alto--certificados-pdf-descargables-sin-autenticación) | Certificados PDF descargables sin autenticación | 🟠 Alto |
| H3 | Sin rotación de logs | 🟠 Alto |
| [H4](#h4--alto--main-desactualizada) | `main` desactualizada | 🟠 Alto |
| [H5](#h5--el-nombre-de-url-professional_login-no-existe) | `reverse('professional_login')` → `NoReverseMatch` | 🟡 Medio |
| [H6](#h6--el-portal-profesional-redirige-al-login-de-trabajadores) | Portal profesional redirige al login de trabajadores | 🟡 Medio |
| [H7](#h7--los-links-vencidos-siguen-dando-acceso) | Links vencidos siguen dando acceso | 🟡 Medio |
| [H8](#h8--campo-explanation-inexistente-en-el-quiz-presencial) | Campo `explanation` inexistente en quiz presencial | 🟡 Medio |
| [H9](#h9--umbral-de-aprobación-duplicado) | Umbral de aprobación duplicado | 🟡 Medio |
| [H10](#h10--dependencia-implícita-de-gunicorn-para-https) | Dependencia implícita de gunicorn para HTTPS | 🟡 Medio |
| [H11](#h11--envío-de-email-síncrono-dentro-del-request) | Email síncrono dentro del request | 🟡 Medio |
| [H12](#h12--vista-async-sobre-workers-wsgi-sync) | Vista async sobre workers WSGI sync | 🟡 Medio |
| H13–H15 | Cookies sin `Secure`, sin HSTS, `CSRF_TRUSTED_ORIGINS` vacío | 🔵 Bajo |
| [H16](#h16--registro-abierto--ahora-en-dos-portales) | Registro abierto — ahora en dos portales | 🔵 Bajo |
| H17 | Sin protección contra fuerza bruta | 🔵 Bajo |
| [H18](#h18--sin-fijado-de-versiones--agravado) | Sin fijado de versiones | 🔵 Bajo |
| H19 | Sin monitoreo ni alertas | 🔵 Bajo |
| [H20](#h20--firma-del-certificado-hardcodeada) | Firma del certificado hardcodeada | 🔵 Bajo |
| [H21](#h21--código-muerto-en-certificates) | Código muerto en `certificates/` | 🔵 Bajo |
| H22 | `/certificados/` devuelve JSON crudo | 🔵 Bajo |
| H23 | `share_link` reporta envíos no confirmados | 🔵 Bajo |
| H24 | `participants_count` por query string | 🔵 Bajo |
| H25 | Comentarios anclados a "COMMIT N" | 🔵 Bajo |
| [H26](#h26--el-readme-describe-una-arquitectura-que-no-existe) | README describe una arquitectura inexistente | 🔵 Bajo |
| [H27](#h27--sin-ci-linter-formateador-ni-pre-commit) | Sin CI, linter, formateador ni pre-commit | 🔵 Bajo |

### Nuevos de la Etapa 3 (N1–N13)

| ID | Título | Severidad |
|---|---|---|
| [N1](#n1--crítico--seis-rutas-del-backoffice-devuelven-http-500-a-usuarios-anónimos) | HTTP 500 en rutas de backoffice para anónimos | 🔴 Crítico |
| [N2](#n2--crítico--la-ficha-del-trabajador-rompe-con-http-500) | Ficha del trabajador rompe con HTTP 500 | 🔴 Crítico |
| [N3](#n3--alto--el-directorio-de-profesionales-es-inalcanzable) | Directorio de profesionales inalcanzable | 🟠 Alto |
| [N4](#n4--alto--el-login-de-empresa-depende-del-backend-de-fallback) | Login de empresa sobre backend de fallback | 🟠 Alto |
| [N5](#n5--medio--login-cruzado-asimétrico-entre-portales) | Login cruzado asimétrico entre portales | 🟡 Medio |
| [N6](#n6--medio--callejón-sin-salida-empresa--presencial) | Callejón sin salida empresa → presencial | 🟡 Medio |
| [N7](#n7--medio--agenda_complete-muta-estado-por-get) | `agenda_complete` muta estado por GET | 🟡 Medio |
| [N8](#n8--medio--pillow-es-dependencia-obligatoria-y-no-está-declarada) | Pillow es dependencia obligatoria no declarada | 🟡 Medio |
| [N9](#n9--medio--generate_cert_expiry_events-sin-planificador) | `generate_cert_expiry_events` sin planificador | 🟡 Medio |
| [N10](#n10--bajo--contactrequest-no-está-registrado-en-el-admin) | `ContactRequest` no registrado en el admin | 🔵 Bajo |
| [N11](#n11--bajo--el-pipeline-de-certificados-ignora-a-la-empresa) | Pipeline de certificados ignora a la empresa | 🔵 Bajo |
| [N12](#n12--bajo--registro-de-empresa-cuit-duplicado-deja-un-usuario-huérfano) | CUIT duplicado deja usuario huérfano | 🔵 Bajo |
| [N13](#n13--bajo--listados-sin-paginación) | Listados sin paginación | 🔵 Bajo |

## Anexo C — Documentos relacionados

| Documento | Contenido |
|---|---|
| [`INFORME_TECNICO_AUDITORIA_PRODUCCION_2026-07-30.md`](INFORME_TECNICO_AUDITORIA_PRODUCCION_2026-07-30.md) | Auditoría original del despliegue `v0.1.3-beta`. Fotografía histórica |
| [`ERGOSOLUTIONS_ARQUITECTURA_ROADMAP.md`](ERGOSOLUTIONS_ARQUITECTURA_ROADMAP.md) | Arquitectura y roadmap de escalamiento (Fases 1–7) |
| [`MAPA_CONCEPTUAL_VISUAL.md`](MAPA_CONCEPTUAL_VISUAL.md) | Mapa conceptual del producto |
| [`PLAN_MAESTRO_COMMITS_GENERAL_FASES_1_2.md`](PLAN_MAESTRO_COMMITS_GENERAL_FASES_1_2.md) | Plan de implementación de las Fases 1 y 2 |
| [`PLAN_MAESTRO_COMMITS_FASES_3_4_5_6.md`](PLAN_MAESTRO_COMMITS_FASES_3_4_5_6.md) | Plan de implementación de las Fases 3 a 6 |
| [`PLAN_MAESTRO_ETAPA_3_PERFIL_EMPRESA.md`](PLAN_MAESTRO_ETAPA_3_PERFIL_EMPRESA.md) | Plan de los Commits 29–48 (Etapa 3) |
| [`PLAN_CAPACITACIONES_PERSONALIZADAS.md`](PLAN_CAPACITACIONES_PERSONALIZADAS.md) | Plan de capacitaciones personalizadas por cliente |
| [`DEPLOY_CLAUDE_RUNBOOK.md`](DEPLOY_CLAUDE_RUNBOOK.md) | Runbook de despliegue |
| [`PLAN_EMAIL_PRODUCCION.md`](PLAN_EMAIL_PRODUCCION.md) | Plan de email de producción — ejecutado y cerrado |
| [`project_tree.md`](project_tree.md) | Inventario de la estructura del proyecto |

---

## Nota de cierre

El diagnóstico de la auditoría original se sostiene y conviene repetirlo, porque sigue siendo exacto: **el proyecto está técnicamente sano y bien diseñado en su núcleo.** Separación clara de responsabilidades, reglas de negocio del lado del servidor, manejo correcto de concurrencia en el quiz, control de acceso consistente, y un pipeline de certificación con degradación elegante ante fallos. La Etapa 3 mantiene ese nivel: modelos bien normalizados, constraints correctos —incluido un índice único parcial condicionado por estado, que es un detalle de artesanía—, índices compuestos pensados para las consultas reales y un comando de generación de eventos idempotente.

Lo que cambia respecto de julio es la naturaleza del riesgo. La auditoría describió defectos **latentes**, enmascarados por el orden de los decoradores, y deuda **operativa**. Cinco meses después, uno de esos defectos latentes se activó: la Etapa 3 construyó nueve rutas sobre una función de resolución de URL que no funciona, y ninguna de las 32 pruebas lo detectó porque ninguna ejerce el camino del usuario anónimo. **El defecto no es el HTTP 500; el defecto es que un error conocido, documentado y con corrección propuesta desde julio siguió disponible para que el código nuevo lo pisara.**

La conclusión práctica es que el orden importa más que el volumen. Hay 40 hallazgos en este documento, pero solo cuatro cosas que hacer antes que cualquier otra: **respaldar la base, reparar las dos regresiones, endurecer `/media/` y desplegar.** Con eso, ErgoSolutions pasa de tener dos versiones de sí mismo que no se hablan a tener una sola, en producción, con backup, sirviendo el triple de superficie funcional que hoy.

Y entonces queda el hallazgo que la auditoría llamó el más significativo y que sigue siéndolo, ahora con más fuerza: **una plataforma completa, con tres tipos de usuario, gestión de nómina, agenda de vencimientos y directorio profesional, sirve un solo curso y no registra usuarios desde hace más de tres meses.** Toda la ingeniería de este documento importa menos que cerrar esa brecha.

---

*Documento generado el 1 de agosto de 2026 · ErgoSolutions © 2026*
