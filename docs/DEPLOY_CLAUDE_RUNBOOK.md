# DEPLOY_CLAUDE_RUNBOOK.md
## ErgoCapacitación / ErgoSolutions — Deploy Ubuntu DonWeb (Django + PostgreSQL) asistido por Claude Code

### Objetivo
Realizar deploy completo de la app Django en un servidor Ubuntu (DonWeb), usando SSH, con:
- PostgreSQL
- Entorno virtual (venv)
- Gunicorn + systemd
- Nginx como reverse proxy
- Static/media configurados
- Variables de entorno seguras
- SSL (Let's Encrypt) opcional/recomendado
- Logs y estrategia de rollback

---

## 0) Reglas de trabajo (Claude: obligatorio)
1. **Plan antes de ejecutar**: proponé pasos y esperá aprobación.
2. **No credenciales en chat**: usar placeholders y pedir que el usuario las cargue en el server (ej: `.env` en el servidor).
3. **Cambios reversibles**: cada bloque debe poder deshacerse (backup de configs).
4. **Confirmación antes de comandos peligrosos**: `rm`, `dropdb`, cambios Nginx/systemd, migraciones destructivas.
5. **Siempre mostrar comandos exactos** y pedir que el usuario pegue la salida si hay errores.

---

## 1) Inputs necesarios (Checklist)
Claude debe pedir y registrar (sin passwords):
- Dominio o subdominio (ej: ergo.midominio.com) o IP pública
- Usuario SSH (ej: root o deploy)
- Puerto SSH si no es 22
- Ruta de deploy (ej: /srv/ergocapacitacion)
- Nombre del repo (GitHub) y rama objetivo (main)
- Versión Python deseada (3.11/3.12)
- Nombre DB, usuario DB
- Variables Django:
  - DJANGO_SETTINGS_MODULE
  - SECRET_KEY (se genera en server)
  - DEBUG=False en producción
  - ALLOWED_HOSTS (dominio + IP)
- Variables de Email (definidas en el punto 1 ya resuelto)
- (Opcional) Storage de media (local vs S3)

---

## 2) Estrategia recomendada de deploy
### Opción A (simple y sólida): 1 servidor
- Nginx (80/443) → Gunicorn socket → Django
- PostgreSQL local
- Media en disco
- Static via collectstatic + Nginx

### Estructura sugerida en server
- `/srv/ergocapacitacion/app` (código)
- `/srv/ergocapacitacion/venv` (virtualenv)
- `/srv/ergocapacitacion/.env` (variables)
- `/srv/ergocapacitacion/logs/` (gunicorn/django)
- `/srv/ergocapacitacion/media/` (MEDIA_ROOT)
- `/srv/ergocapacitacion/static/` (STATIC_ROOT)

---

## 3) Secuencia de ejecución por SSH (paso a paso)
> Claude: ejecutar en bloques. Después de cada bloque pedir output y validar.

### 3.1 Conexión SSH
- Comando sugerido:
  - `ssh usuario@IP`
  - o `ssh -p PUERTO usuario@IP`

### 3.2 Actualización base e instalación de paquetes
Instalar:
- git, python3, python3-venv, pip, build-essential
- nginx
- postgresql + contrib
- libpq-dev (para psycopg/psycopg2)

### 3.3 Crear usuario “deploy” (si aplica)
- crear usuario sin root directo
- agregar a sudoers si corresponde
- configurar SSH keys

### 3.4 PostgreSQL
- crear DB y usuario con password fuerte
- otorgar privilegios
- confirmar conexión

### 3.5 Clonar repo en /srv/ergocapacitacion/app
- `git clone ...`
- `git checkout rama`
- (Si ya existe) `git pull`

### 3.6 Virtualenv + dependencias
- `python3 -m venv /srv/ergocapacitacion/venv`
- `source /srv/ergocapacitacion/venv/bin/activate`
- `pip install -U pip`
- `pip install -r requirements.txt`

### 3.7 Variables de entorno (archivo .env en server)
- Crear `/srv/ergocapacitacion/.env` con:
  - SECRET_KEY
  - DEBUG=False
  - ALLOWED_HOSTS
  - DB creds
  - Email creds
  - cualquier API key necesaria
- Permisos recomendados:
  - owner deploy, modo 600

### 3.8 Configuración Django para producción
Claude debe verificar en el proyecto:
- `SECRET_KEY` desde env
- `DEBUG` desde env
- `ALLOWED_HOSTS` desde env
- `CSRF_TRUSTED_ORIGINS` si hay https + dominio
- `STATIC_ROOT` y `MEDIA_ROOT`
- logging básico (opcional pero recomendado)

### 3.9 Migraciones + collectstatic
- `python manage.py migrate`
- `python manage.py collectstatic --noinput`
- (si aplica) `python manage.py createsuperuser` (opcional)

### 3.10 Gunicorn
- Definir comando:
  - `gunicorn config.wsgi:application --bind unix:/srv/ergocapacitacion/gunicorn.sock`
- Crear service systemd:
  - `/etc/systemd/system/ergocapacitacion.service`
- Habilitar y arrancar:
  - `systemctl daemon-reload`
  - `systemctl enable --now ergocapacitacion`

### 3.11 Nginx
- Server block:
  - proxy_pass al socket de gunicorn
  - servir `/static/` y `/media/`
- `nginx -t` + `systemctl reload nginx`

### 3.12 SSL (recomendado)
- certbot + nginx plugin
- emitir certificado para dominio
- renovar automático

---

## 4) Verificación final (checklist)
- Home responde 200
- Login funciona
- Flujos críticos:
  - generar link
  - enviar email real (punto 1)
  - descargar certificados si aplica
- Logs:
  - `journalctl -u ergocapacitacion -f`
  - `/var/log/nginx/error.log`
- Seguridad básica:
  - DEBUG=False confirmado
  - SECRET_KEY no expuesto
  - `.env` no versionado y con permisos correctos
  - firewall/UFW (si corresponde)

---

## 5) Rollback plan (mínimo viable)
- Mantener tag o commit estable anterior
- Si falla deploy:
  - `git checkout <commit_estable>`
  - reinstalar deps si cambió requirements
  - migrate solo si es reversible
  - restart service
- Backup de DB antes de migraciones importantes:
  - `pg_dump ... > backup.sql`

---

## 6) Cómo debe trabajar Claude durante el deploy (prompt operativo)
Claude debe:
1) Pedir checklist (Sección 1).
2) Proponer plan por etapas (Sección 3).
3) Ejecutar una etapa por vez solicitando output.
4) En cada error: diagnosticar, proponer fix, reintentar.
5) Nunca pedir contraseñas por chat: usar placeholders y pedir que el usuario las cargue en el server.

---

## 7) Nota importante de seguridad
- Nunca subir `.env` al repo.
- Nunca dejar credenciales en settings.py.
- Preferir proveedor de email transaccional para producción (mejor deliverability que SMTP personal).
