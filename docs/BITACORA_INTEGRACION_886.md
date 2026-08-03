# Bitácora de integración — Módulo de Ergonomía SRT 886/15

**Roadmap:** `docs/ROADMAP_INTEGRACION_ERGONOMIA_886.md`
**Diseño:** `docs/INTEGRACION_MODULO_ERGONOMIA_886_PROPUESTA_TECNICA.md`
**Inicio:** 2026-08-02
**Ejecutor:** Asistente IA de desarrollo
**Titular:** Pablo R. Aguirre

---

## Estado de partida verificado

| Proyecto | Rama | Suite | Migraciones |
|---|---|---|---|
| ErgoSolutions | `release/beta` → `feature/ergonomia-886` | `Ran 32 tests in 4.130s` — `OK` | `No changes detected` |
| ErgoApp SRT 886 | `main` | `Ran 160 tests in 2.227s` — `OK` | `No changes detected` |

---

## Registro de commits

## Commit 0.0 — Crear rama de integración y bitácora

| Campo | Valor |
|---|---|
| Fecha | 2026-08-02 |
| Repositorio | ergocapacitacion |
| Rama | `feature/ergonomia-886` |
| Hash | `1001b13` |
| Fase | 0 |
| Estado | ⚠️ Completado con desvíos |

### Qué se hizo
Se creó la rama de integración desde `release/beta`, preservando el árbol de
trabajo pendiente previsto por el roadmap. Se verificó el punto de partida de
los dos proyectos y se creó esta bitácora con la evidencia literal relevante.

### Archivos modificados
- `docs/BITACORA_INTEGRACION_886.md` — bitácora y estado de partida.
- `docs/ROADMAP_INTEGRACION_ERGONOMIA_886.md` — commit 0.0 marcado como completado.
- `README.md` — apertura formal de la integración SRT 886/15.

### Verificaciones ejecutadas

```text
cd /Users/praguirre/ergonomia_srt && ./venv/bin/python manage.py test --settings=ergonomia_srt.test_settings
Creating test database for alias 'default'...
...........................Tabla A de REBA inválida o inconsistente
Traceback (most recent call last):
  File "/Users/praguirre/ergonomia_srt/evaluaciones/calculators.py", line 1728, in calc_posturas_forzadas
    res_tabla_a = _reba_lookup_tabla_a(neck=cuello, legs=piernas, trunk=tronco)
KeyError: 'tabla corrupta'
.....................................................................................................................Timeout del Chat IA para slug=lmc
..........No se pudo leer el documento de ayuda /Users/praguirre/ergonomia_srt/static/ayuda/help_texts/slug-que-no-existe.md
......
----------------------------------------------------------------------
Ran 160 tests in 2.227s

OK
Destroying test database for alias 'default'...
Found 160 test(s).
System check identified no issues (0 silenced).

cd /Users/praguirre/ergonomia_srt && ./venv/bin/python manage.py makemigrations --check --dry-run
/Users/praguirre/ergonomia_srt/venv/lib/python3.11/site-packages/django/core/management/commands/makemigrations.py:161: RuntimeWarning: Got an error checking a consistent migration history performed for database connection 'default': connection to server at "localhost" (::1), port 5432 failed: Operation not permitted
  warnings.warn(
No changes detected

cd /Users/praguirre/ergocapacitacion && .venv/bin/python manage.py test apps
Creating test database for alias 'default'...
................................
----------------------------------------------------------------------
Ran 32 tests in 4.130s

OK
Destroying test database for alias 'default'...
Found 32 test(s).
System check identified no issues (0 silenced).

cd /Users/praguirre/ergocapacitacion && .venv/bin/python manage.py makemigrations --check --dry-run
/Users/praguirre/ergocapacitacion/.venv/lib/python3.11/site-packages/django/core/management/commands/makemigrations.py:161: RuntimeWarning: Got an error checking a consistent migration history performed for database connection 'default': connection is bad: connection to server at "127.0.0.1", port 5432 failed: Operation not permitted
  warnings.warn(
No changes detected

cd /Users/praguirre/ergocapacitacion && git branch --show-current
feature/ergonomia-886
```

### Desvíos respecto del roadmap
La sandbox bloqueó las conexiones locales a PostgreSQL durante ambos comandos
`makemigrations --check --dry-run`. Django emitió la advertencia literal
registrada arriba y completó la detección con `No changes detected`; las suites,
que usan bases efímeras, pasaron con los conteos esperados.

### Notas para el commit siguiente
El árbol sucio coincide con el inventario del commit 0.1 y se preservó sin
alteraciones. La documentación no trackeada del repositorio origen también se
mantiene intacta hasta su fase correspondiente.

## Commit 0.1 — Consolidar el árbol de trabajo pendiente

| Campo | Valor |
|---|---|
| Fecha | 2026-08-02 23:29 |
| Repositorio | ergocapacitacion |
| Rama | `feature/ergonomia-886` |
| Hash | `0e364ac` |
| Fase | 0 |
| Estado | ✅ Completado |

### Qué se hizo
Se verificó que los cuatro Markdown retirados de la raíz existen en `docs/` y
se consolidó el árbol documental pendiente, incluida la actualización de
`.gitignore`. También se completó un smoke test real del servidor Django.

### Archivos modificados
- `.gitignore` — actualización preexistente consolidada.
- `DEPLOY_CLAUDE_RUNBOOK.md`, `ERGOSOLUTIONS_ARQUITECTURA_ROADMAP.md`, `MAPA_CONCEPTUAL_VISUAL.md` y `PLAN_EMAIL_PRODUCCION.md` — movimientos desde la raíz.
- `docs/` — documentos técnicos y operativos centralizados, incluidos los cuatro movimientos verificados.
- `docs/BITACORA_INTEGRACION_886.md` — entrada del commit y hash del commit anterior.
- `docs/ROADMAP_INTEGRACION_ERGONOMIA_886.md` — commit 0.1 marcado como completado.
- `README.md` — registro de la consolidación documental.

### Verificaciones ejecutadas

```text
for f in DEPLOY_CLAUDE_RUNBOOK ERGOSOLUTIONS_ARQUITECTURA_ROADMAP MAPA_CONCEPTUAL_VISUAL PLAN_EMAIL_PRODUCCION; do test -f "docs/$f.md" && echo "OK  docs/$f.md" || echo "FALTA docs/$f.md"; done
OK  docs/DEPLOY_CLAUDE_RUNBOOK.md
OK  docs/ERGOSOLUTIONS_ARQUITECTURA_ROADMAP.md
OK  docs/MAPA_CONCEPTUAL_VISUAL.md
OK  docs/PLAN_EMAIL_PRODUCCION.md

.venv/bin/python manage.py check
System check identified no issues (0 silenced).

.venv/bin/python manage.py runserver 127.0.0.1:8001 --noreload
Performing system checks...
System check identified no issues (0 silenced).
August 02, 2026 - 23:28:46
Django version 5.2.10, using settings 'config.settings'
Starting development server at http://127.0.0.1:8001/

curl -s -o /dev/null -w 'GET / -> HTTP %{http_code}\n' http://127.0.0.1:8001/
GET / -> HTTP 200

git status --short
<sin archivos sin agregar después de git add -A>
```

### Desvíos respecto del roadmap
El puerto 8000 ya estaba ocupado, por lo que el smoke test se ejecutó en el
puerto 8001. El contenido y el criterio de aceptación no cambiaron: el servidor
arrancó sin issues y `GET /` devolvió HTTP 200.

### Notas para el commit siguiente
Ninguna.

## Commit 0.2 — Corregir nombres de URL rotos en los decoradores (N1)

| Campo | Valor |
|---|---|
| Fecha | 2026-08-02 23:31 |
| Repositorio | ergocapacitacion |
| Rama | `feature/ergonomia-886` |
| Hash | `ce5ebd3` |
| Fase | 0 |
| Estado | ✅ Completado |

### Qué se hizo
Se corrigieron los cinco nombres de URL inexistentes usados por los decoradores
de cuentas. Cada tipo de usuario anónimo ahora es enviado al login real que le
corresponde, eliminando la causa raíz de N1.

### Archivos modificados
- `apps/accounts/decorators.py` — cinco nombres de URL corregidos.
- `docs/BITACORA_INTEGRACION_886.md` — entrada y evidencia del commit.
- `docs/ROADMAP_INTEGRACION_ERGONOMIA_886.md` — commit 0.2 marcado como completado.
- `README.md` — registro de la corrección N1, parte 1.

### Verificaciones ejecutadas

```text
.venv/bin/python -c "<script reverse() del roadmap>"
accounts_professional:professional_login      -> /auth/login/
accounts_company:company_login                -> /empresa/auth/login/
trainee_landing                               -> /acceso/

rg -n "reverse\\('professional_login'\\)|reverse\\('landing'\\)" apps/accounts/decorators.py
<sin salida>

.venv/bin/python manage.py check
System check identified no issues (0 silenced).

.venv/bin/python manage.py test apps
................................
----------------------------------------------------------------------
Ran 32 tests in 4.182s

OK
Destroying test database for alias 'default'...
Found 32 test(s).
System check identified no issues (0 silenced).

.venv/bin/python manage.py runserver 127.0.0.1:8002 --noreload
Performing system checks...
System check identified no issues (0 silenced).
Starting development server at http://127.0.0.1:8002/

curl -s -o /dev/null -w 'GET / -> HTTP %{http_code}\n' http://127.0.0.1:8002/
GET / -> HTTP 200
```

### Desvíos respecto del roadmap
Ninguno.

### Notas para el commit siguiente
Ninguna.

## Commit 0.3 — Restaurar `@login_required` en 13 vistas de backoffice (N1)

| Campo | Valor |
|---|---|
| Fecha | 2026-08-02 23:33 |
| Repositorio | ergocapacitacion |
| Rama | `feature/ergonomia-886` |
| Hash | `59eefc7` |
| Fase | 0 |
| Estado | ✅ Completado |

### Qué se hizo
Se restauró `@login_required` antes del decorador de rol en once vistas de
empresa y dos vistas profesionales. La capa exterior intercepta al usuario
anónimo antes de evaluar permisos específicos y refuerza la corrección N1.

### Archivos modificados
- `apps/company/views.py` — `@login_required` en once vistas de empresa.
- `apps/dashboard/views.py` — `@login_required` en dos vistas profesionales.
- `docs/BITACORA_INTEGRACION_886.md` — entrada y evidencia del commit.
- `docs/ROADMAP_INTEGRACION_ERGONOMIA_886.md` — commit 0.3 marcado como completado.
- `README.md` — registro de la corrección N1, parte 2.

### Verificaciones ejecutadas

```text
grep -c "@login_required" apps/company/views.py
11
grep -c "@company_required" apps/company/views.py
11

.venv/bin/python -c "<script de acceso anónimo del roadmap>"
OK  /dashboard/                                   -> 302
OK  /dashboard/empresa/nomina/                    -> 302
OK  /dashboard/empresa/nomina/agregar/            -> 302
OK  /dashboard/empresa/nomina/exportar/           -> 302
OK  /dashboard/empresa/agenda/                    -> 302
OK  /dashboard/empresa/agenda/crear/              -> 302
OK  /dashboard/empresa/directorio/                -> 302
OK  /dashboard/solicitudes-contacto/              -> 302

RESULTADO: SIN 500

.venv/bin/python manage.py check
System check identified no issues (0 silenced).

.venv/bin/python manage.py test apps
................................
----------------------------------------------------------------------
Ran 32 tests in 4.146s

OK
Destroying test database for alias 'default'...
Found 32 test(s).
System check identified no issues (0 silenced).

.venv/bin/python manage.py runserver 127.0.0.1:8003 --noreload
System check identified no issues (0 silenced).
Starting development server at http://127.0.0.1:8003/

curl -s -o /dev/null -w 'GET /dashboard/empresa/nomina/ -> HTTP %{http_code}\n' http://127.0.0.1:8003/dashboard/empresa/nomina/
GET /dashboard/empresa/nomina/ -> HTTP 302
```

### Desvíos respecto del roadmap
Ninguno.

### Notas para el commit siguiente
Ninguna.

## Commit 0.4 — Corregir los settings de redirección profesional (H-F)

| Campo | Valor |
|---|---|
| Fecha | 2026-08-02 23:35 |
| Repositorio | ergocapacitacion |
| Rama | `feature/ergonomia-886` |
| Hash | Se completa después del commit |
| Fase | 0 |
| Estado | ✅ Completado |

### Qué se hizo
Se calificaron con namespace los settings de login y redirección profesional.
Los cuatro settings de autenticación configurados resuelven ahora a rutas
existentes.

### Archivos modificados
- `config/settings.py` — nombres de URL profesionales calificados.
- `docs/BITACORA_INTEGRACION_886.md` — entrada y evidencia del commit.
- `docs/ROADMAP_INTEGRACION_ERGONOMIA_886.md` — commit 0.4 marcado como completado.
- `README.md` — registro del cierre de H-F.

### Verificaciones ejecutadas

```text
.venv/bin/python -c "<script de resolución de settings del roadmap>"
LOGIN_URL                           = 'trainee_landing'                                  -> /acceso/
LOGIN_REDIRECT_URL                  = 'training_home'                                    -> /capacitacion/
PROFESSIONAL_LOGIN_URL              = 'accounts_professional:professional_login'         -> /auth/login/
PROFESSIONAL_LOGIN_REDIRECT_URL     = 'dashboard:home'                                   -> /dashboard/

.venv/bin/python manage.py check
System check identified no issues (0 silenced).

.venv/bin/python manage.py test apps
................................
----------------------------------------------------------------------
Ran 32 tests in 4.083s

OK
Destroying test database for alias 'default'...
Found 32 test(s).
System check identified no issues (0 silenced).

.venv/bin/python manage.py runserver 127.0.0.1:8004 --noreload
System check identified no issues (0 silenced).
Starting development server at http://127.0.0.1:8004/

curl -s -o /dev/null -w 'GET /auth/login/ -> HTTP %{http_code}\n' http://127.0.0.1:8004/auth/login/
GET /auth/login/ -> HTTP 200
```

### Desvíos respecto del roadmap
Ninguno.

### Notas para el commit siguiente
Ninguna.
