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
| Hash | `9123f54` |
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

## Commit 0.5 — Corregir `QuizState.is_approved` inexistente (N2)

| Campo | Valor |
|---|---|
| Fecha | 2026-08-02 23:37 |
| Repositorio | ergocapacitacion |
| Rama | `feature/ergonomia-886` |
| Hash | `d3eecb4` |
| Fase | 0 |
| Estado | ✅ Completado |

### Qué se hizo
La ficha del trabajador ahora toma la aprobación desde `QuizState.last_passed`
y la vigencia desde `Certificate.is_valid`. Se retiró el import de `timezone`
ubicado dentro del bucle.

### Archivos modificados
- `apps/company/views.py` — corrección de N2 y simplificación de vigencia.
- `docs/BITACORA_INTEGRACION_886.md` — entrada y evidencia del commit.
- `docs/ROADMAP_INTEGRACION_ERGONOMIA_886.md` — commit 0.5 marcado como completado.
- `README.md` — registro de la corrección N2.

### Verificaciones ejecutadas

```text
grep -n "is_approved\\|is_valid" apps/company/views.py
205:            # QuizState no tiene `is_approved`: el campo con esa semantica
207:            'is_approved': bool(qs.last_passed) if qs else False,
208:            # El modelo Certificate ya expone la propiedad `is_valid`.
209:            'is_valid': cert.is_valid if cert else False,

rg -n 'qs\\.is_approved|^[[:space:]]+from django\\.utils import timezone' apps/company/views.py
<sin salida>

.venv/bin/python manage.py check
System check identified no issues (0 silenced).

.venv/bin/python manage.py test apps
................................
----------------------------------------------------------------------
Ran 32 tests in 4.057s

OK
Destroying test database for alias 'default'...
Found 32 test(s).
System check identified no issues (0 silenced).

.venv/bin/python manage.py runserver 127.0.0.1:8005 --noreload
System check identified no issues (0 silenced).
Starting development server at http://127.0.0.1:8005/

curl -s -o /dev/null -w 'GET /dashboard/empresa/nomina/ -> HTTP %{http_code}\n' http://127.0.0.1:8005/dashboard/empresa/nomina/
GET /dashboard/empresa/nomina/ -> HTTP 302
```

### Desvíos respecto del roadmap
Ninguno.

### Notas para el commit siguiente
Ninguna.

## Commit 0.6 — Tests de regresión de N1 y N2

| Campo | Valor |
|---|---|
| Fecha | 2026-08-02 23:40 |
| Repositorio | ergocapacitacion |
| Rama | `feature/ergonomia-886` |
| Hash | `3e1df5c` |
| Fase | 0 |
| Estado | ⚠️ Completado con desvíos |

### Qué se hizo
Se agregaron cuatro pruebas de regresión: diez rutas anónimas contra HTTP 500,
destino de login resoluble y ficha del trabajador con y sin `QuizState`. Se
reintrodujo N2 temporalmente y la prueba falló con el `AttributeError` esperado.

### Archivos modificados
- `apps/company/tests_regresion.py` — cuatro pruebas nuevas para N1 y N2.
- `docs/BITACORA_INTEGRACION_886.md` — entrada, fallos iniciales y evidencia final.
- `docs/ROADMAP_INTEGRACION_ERGONOMIA_886.md` — commit 0.6 marcado como completado.
- `README.md` — registro de las nuevas regresiones automáticas.

### Verificaciones ejecutadas

```text
.venv/bin/python manage.py test apps.company.tests_regresion -v 2  # primera ejecución literal relevante
Found 4 test(s).
FAIL: test_el_anonimo_es_redirigido_a_un_login_que_existe
AssertionError: '/empresa/auth/login/' not found in '/acceso/?next=/dashboard/empresa/nomina/'
ERROR: test_ficha_sin_quizstate_responde_200
ValueError: Missing staticfiles manifest entry for 'css/dashboard.css'
test_ficha_con_quizstate_responde_200 ... skipped 'No hay modulos de capacitacion activos en la base de test'
Ran 4 tests in 0.146s
FAILED (failures=1, errors=1, skipped=1)

.venv/bin/python manage.py test apps.company.tests_regresion -v 2  # después de adaptar a la realidad
test_el_anonimo_es_redirigido_a_un_login_que_existe ... ok
test_ninguna_ruta_de_backoffice_devuelve_500_a_un_anonimo ... ok
test_ficha_con_quizstate_responde_200 ... ok
test_ficha_sin_quizstate_responde_200 ... ok
----------------------------------------------------------------------
Ran 4 tests in 0.153s

OK

# N2 reintroducida temporalmente para verificar la sensibilidad de la prueba
.venv/bin/python manage.py test apps.company.tests_regresion.FichaTrabajadorConQuizStateTests.test_ficha_con_quizstate_responde_200 -v 2
ERROR: test_ficha_con_quizstate_responde_200
AttributeError: 'QuizState' object has no attribute 'is_approved'
----------------------------------------------------------------------
Ran 1 test in 0.125s
FAILED (errors=1)

# Corrección restaurada; suite completa
.venv/bin/python manage.py test apps
....................................
----------------------------------------------------------------------
Ran 36 tests in 4.252s

OK
Destroying test database for alias 'default'...
Found 36 test(s).
System check identified no issues (0 silenced).

.venv/bin/python manage.py runserver 127.0.0.1:8006 --noreload
System check identified no issues (0 silenced).
Starting development server at http://127.0.0.1:8006/

curl -s -o /dev/null -w 'GET /dashboard/ -> HTTP %{http_code}\n' http://127.0.0.1:8006/dashboard/
GET /dashboard/ -> HTTP 302
```

### Desvíos respecto del roadmap
La prueba propuesta asumía que el decorador de empresa era la primera capa,
pero el commit 0.3 exige `@login_required` por fuera y por eso el destino real
es `settings.LOGIN_URL`. Se verificó ese destino resoluble. La base efímera no
contenía módulos activos, por lo que se creó uno explícitamente para evitar un
`skipTest`. Finalmente, el storage manifestado requería `collectstatic`; se
aisló `StaticFilesStorage` solo en la clase que renderiza la ficha. Ninguna
aserción existente fue modificada ni relajada.

### Notas para el commit siguiente
El commit 0.7 centraliza a nivel de settings de prueba el mismo aislamiento de
storage que esta regresión necesita localmente.

## Commit 0.7 — Crear `config/test_settings.py` (B8)

| Campo | Valor |
|---|---|
| Fecha | 2026-08-02 23:43 |
| Repositorio | ergocapacitacion |
| Rama | `feature/ergonomia-886` |
| Hash | `1d7542a` |
| Fase | 0 |
| Estado | ⚠️ Completado con desvíos |

### Qué se hizo
Se creó la configuración aislada de pruebas con SQLite en memoria, caché local,
hashing rápido, storage no manifestado y correo en memoria. El plan A funcionó:
las 36 pruebas pasaron tanto con la configuración nueva como con la normal.

### Archivos modificados
- `config/test_settings.py` — settings aislados de la suite.
- `docs/BITACORA_INTEGRACION_886.md` — entrada y evidencia del commit.
- `docs/ROADMAP_INTEGRACION_ERGONOMIA_886.md` — commit 0.7 marcado como completado.
- `README.md` — documentación del comando de prueba aislado.

### Verificaciones ejecutadas

```text
.venv/bin/python manage.py check --settings=config.test_settings
System check identified no issues (0 silenced).

.venv/bin/python manage.py test apps --settings=config.test_settings -v 2
Creating test database for alias 'default' ('file:memorydb_default?mode=memory&cache=shared')...
Found 36 test(s).
...
----------------------------------------------------------------------
Ran 36 tests in 0.179s

OK
Destroying test database for alias 'default' ('file:memorydb_default?mode=memory&cache=shared')...
System check identified no issues (0 silenced).

.venv/bin/python manage.py test apps
....................................
----------------------------------------------------------------------
Ran 36 tests in 4.232s

OK
Destroying test database for alias 'default'...
Found 36 test(s).
System check identified no issues (0 silenced).

.venv/bin/python manage.py runserver 127.0.0.1:8007 --noreload --settings=config.test_settings
System check identified no issues (0 silenced).
You have 33 unapplied migration(s).
Starting development server at http://127.0.0.1:8007/

curl -s -o /dev/null -w 'GET / -> HTTP %{http_code}\n' http://127.0.0.1:8007/
GET / -> HTTP 200
```

### Desvíos respecto del roadmap
El smoke test con la base SQLite en memoria advirtió 33 migraciones sin aplicar,
lo esperable al iniciar un servidor fuera del runner de tests. `GET /` no
requiere base y respondió 200. Durante la publicación del commit 0.6 GitHub
emitió una vez `Error in the HTTP2 framing layer`; el reintento confirmó
`Everything up-to-date` y la rama remota quedó sincronizada.

### Notas para el commit siguiente
Se usó el plan A (SQLite); no fue necesario solicitar permisos de PostgreSQL.

## Commit 0.8 — Configurar `CACHES` con `DatabaseCache` (B4)

| Campo | Valor |
|---|---|
| Fecha | 2026-08-02 23:46 |
| Repositorio | ergocapacitacion |
| Rama | `feature/ergonomia-886` |
| Hash | `6d4e05d` |
| Fase | 0 |
| Estado | ⚠️ Completado con desvíos |

### Qué se hizo
Se configuró `DatabaseCache` para compartir cuotas y cerrojos entre procesos,
se creó idempotentemente la tabla `ergosolutions_cache` en desarrollo y se
documentó `createcachetable` antes del arranque de procesos en el runbook.

### Archivos modificados
- `config/settings.py` — backend `DatabaseCache` compartido.
- `docs/DEPLOY_CLAUDE_RUNBOOK.md` — paso obligatorio `createcachetable`.
- `docs/BITACORA_INTEGRACION_886.md` — entrada y evidencia del commit.
- `docs/ROADMAP_INTEGRACION_ERGONOMIA_886.md` — commit 0.8 marcado como completado.
- `README.md` — registro operativo de caché.

### Verificaciones ejecutadas

```text
.venv/bin/python manage.py createcachetable
<sin salida; ejecución exitosa e idempotente>

.venv/bin/python -c "<script de cerrojo del roadmap>"
Backend : ConnectionProxy
Lectura : ok
add()   : False (False = el cerrojo funciona)

.venv/bin/python -c "<inspección del backend real>"
Backend real: DatabaseCache
Tabla       : ergosolutions_cache

.venv/bin/python manage.py check
System check identified no issues (0 silenced).

.venv/bin/python manage.py makemigrations --check --dry-run
RuntimeWarning: Got an error checking a consistent migration history ... Operation not permitted
No changes detected

.venv/bin/python manage.py test apps --settings=config.test_settings
....................................
----------------------------------------------------------------------
Ran 36 tests in 0.182s

OK
Destroying test database for alias 'default'...
Found 36 test(s).
System check identified no issues (0 silenced).

.venv/bin/python manage.py runserver 127.0.0.1:8008 --noreload
System check identified no issues (0 silenced).
Starting development server at http://127.0.0.1:8008/

curl -s -o /dev/null -w 'GET / -> HTTP %{http_code}\n' http://127.0.0.1:8008/
GET / -> HTTP 200
```

### Desvíos respecto del roadmap
El script propuesto imprime la clase del proxy global de Django y por eso
mostró `ConnectionProxy`, no la implementación. La inspección de
`caches['default']` confirmó `DatabaseCache` y la tabla correcta. La primera
ejecución de `createcachetable` dentro de la sandbox no pudo conectar a
PostgreSQL; repetida con permiso de conexión local, completó sin salida.

### Notas para el commit siguiente
La tabla de caché de desarrollo existe; producción deberá ejecutar el paso
documentado durante el despliegue.

## Commit 0.9 — Declarar `pypdf` y `pillow` (B7, N8)

| Campo | Valor |
|---|---|
| Fecha | 2026-08-02 23:48 |
| Repositorio | ergocapacitacion |
| Rama | `feature/ergonomia-886` |
| Hash | `5494a53` |
| Fase | 0 |
| Estado | ⚠️ Completado con desvíos |

### Qué se hizo
Se declararon `pypdf` y `pillow`, se fijaron cotas superiores para las
dependencias verificadas y se instaló `pypdf 6.14.2`. También se confirmó la
API de `openai-agents` que sostiene CF-4.

### Archivos modificados
- `requirements.txt` — dependencias nuevas y cotas superiores.
- `docs/BITACORA_INTEGRACION_886.md` — entrada y versiones verificadas.
- `docs/ROADMAP_INTEGRACION_ERGONOMIA_886.md` — commit 0.9 marcado como completado.
- `README.md` — registro de dependencias del módulo.

### Verificaciones ejecutadas

```text
.venv/bin/pip install -r requirements.txt
Collecting pypdf<7.0,>=5.0
Downloading pypdf-6.14.2-py3-none-any.whl (349 kB)
Installing collected packages: pypdf
Successfully installed pypdf-6.14.2

.venv/bin/python -c "<script de API del roadmap>"
pypdf     : 6.14.2
pillow    : 12.1.0
reportlab : 4.4.9

agents.Agent        OK
agents.Runner       OK
agents.RunConfig    OK
agents.ItemHelpers  OK

trace_include_sensitive_data (CF-4): OK

.venv/bin/python manage.py check
System check identified no issues (0 silenced).

.venv/bin/python manage.py test apps --settings=config.test_settings
....................................
----------------------------------------------------------------------
Ran 36 tests in 0.166s

OK
Destroying test database for alias 'default'...
Found 36 test(s).
System check identified no issues (0 silenced).

.venv/bin/python manage.py runserver 127.0.0.1:8009 --noreload
System check identified no issues (0 silenced).
Starting development server at http://127.0.0.1:8009/

curl -s -o /dev/null -w 'GET / -> HTTP %{http_code}\n' http://127.0.0.1:8009/
GET / -> HTTP 200
```

### Desvíos respecto del roadmap
El primer `pip install` no pudo resolver PyPI por la red restringida de la
sandbox; repetido con acceso de red autorizado, instaló la versión compatible.
En el commit 0.8 se corrigió antes del push un mensaje donde el shell había
interpretado backticks; el hash publicado es `6d4e05d` y el mensaje coincide
con el roadmap.

### Notas para el commit siguiente
Ninguna.

## Commit 0.10 — Agregar `app_name` a los 5 includes sin namespace (H-D)

| Campo | Valor |
|---|---|
| Fecha | 2026-08-02 23:53 |
| Repositorio | ergocapacitacion |
| Rama | `feature/ergonomia-886` |
| Hash | `8faa8c2` |
| Fase | 0 |
| Estado | ⚠️ Completado con desvíos |

### Qué se hizo
Se declararon namespaces para `accounts`, `training`, `quiz`, `certificates` y
`ergobot_ai`, calificando sus referencias Python, templates, tests y settings.
También se aisló `training_public`; sus paths `/c/` permanecen byte por byte.

### Archivos modificados
- `apps/accounts/urls.py` y referencias — namespace `accounts` (19 referencias calificadas).
- `apps/training/urls.py` y referencias — namespace `training` (10 referencias calificadas).
- `apps/quiz/urls.py` y referencias — namespace `quiz` (3 referencias calificadas; las cuatro URLs construidas por JS mantienen su path).
- `apps/certificates/urls.py` y referencias — namespace `certificates` (3 referencias calificadas).
- `apps/ergobot_ai/urls.py` — namespace `ergobot_ai`; el JS conserva `/ai/ergobot/<slug>/stream/`.
- `apps/training/urls_public.py` — namespace adicional `training_public`, sin cambiar `/c/`.
- `docs/BITACORA_INTEGRACION_886.md` — inventario, decisión y verificaciones.
- `docs/ROADMAP_INTEGRACION_ERGONOMIA_886.md` — commit 0.10 marcado como completado.
- `README.md` — registro de los namespaces.

### Verificaciones ejecutadas

```text
# Suite ejecutada después de cada app
.venv/bin/python manage.py test apps --settings=config.test_settings
Ran 36 tests in 0.145s — OK  # accounts
Ran 36 tests in 0.142s — OK  # training
Ran 36 tests in 0.142s — OK  # quiz
Ran 36 tests in 0.142s — OK  # certificates
Ran 36 tests in 0.142s — OK  # ergobot_ai

.venv/bin/python -c "<resolución de namespaces>"
ergobot_ai:ergobot_stream                     -> /ai/ergobot/ergonomia/stream/
accounts:trainee_landing                      -> /acceso/
training:training_home                        -> /capacitacion/
quiz:quiz_start                               -> /quiz/ergonomia/start/
certificates:certificates_list                -> /certificados/
training_public:training_public               -> /c/ergonomia/
accounts_professional:professional_login      -> /auth/login/
accounts_company:company_login                -> /empresa/auth/login/
dashboard:home                                -> /dashboard/

.venv/bin/python manage.py check
System check identified no issues (0 silenced).

.venv/bin/python manage.py test apps --settings=config.test_settings
....................................
----------------------------------------------------------------------
Ran 36 tests in 0.157s

OK
Destroying test database for alias 'default'...
Found 36 test(s).
System check identified no issues (0 silenced).

# Respuesta local del view Ergobot, sin invocar al proveedor
Status      : 200
Content-Type: text/event-stream
SSE         : data: {"error": "empty"}

.venv/bin/python manage.py runserver 127.0.0.1:8010 --noreload
System check identified no issues (0 silenced).
Starting development server at http://127.0.0.1:8010/

GET /capacitacion/ -> HTTP 302
GET /ai/ergobot/ergonomia/stream/ -> HTTP 302

# Compuerta de cierre de Fase 0
.venv/bin/python manage.py check
System check identified no issues (0 silenced).
.venv/bin/python manage.py makemigrations --check --dry-run
No changes detected
.venv/bin/python manage.py migrate --check
<sin salida; código 0>
.venv/bin/python manage.py createcachetable
Cache table 'ergosolutions_cache' already exists.

/dashboard/                                   -> 302
/dashboard/capacitaciones/                    -> 302
/dashboard/perfil/                            -> 302
/dashboard/empresa/nomina/                    -> 302
/dashboard/empresa/nomina/agregar/            -> 302
/dashboard/empresa/nomina/exportar/           -> 302
/dashboard/empresa/agenda/                    -> 302
/dashboard/empresa/agenda/crear/              -> 302
/dashboard/empresa/directorio/                -> 302
/dashboard/solicitudes-contacto/              -> 302
```

### Desvíos respecto del roadmap
Se agregó `app_name = "training_public"`: no existe ninguna referencia interna
al nombre plano y los enlaces enviados se construyen por path en
`CapacitacionLink.get_absolute_url`, por lo que el namespace elimina otra
posible colisión sin cambiar URLs externas. La prueba funcional no envió una
consulta real a OpenAI porque requeriría una credencial P-1 y generaría consumo;
se verificaron el reverse, el path JS sin cambios, la protección HTTP y una
respuesta SSE 200 de la vista antes de la rama que llama al proveedor.

### Notas para el commit siguiente
Fase 0 lista para ejecutar su compuerta completa de aceptación.

## Commit 1.0 — Registrar las 7 aprobaciones profesionales (CF-3)

| Campo | Valor |
|---|---|
| Fecha | 2026-08-02 23:58 |
| Repositorio | ergonomia_srt |
| Rama | `feature/preparacion-integracion` |
| Hash | `104d9ed` |
| Fase | 1 |
| Estado | ⚠️ Completado con desvíos |

### Qué se hizo
Se registraron nominalmente las siete aprobaciones otorgadas por Lic. Pablo R.
Aguirre — MN 10.027, con fecha, alcance y provenance definitivo. Los seis
artefactos de transcripción literal permanecen en `not_recorded`.

### Archivos modificados
- `evaluaciones/data/bipedestacion_limites.json` — método interno aprobado.
- `evaluaciones/data/confort_termico_umbrales.json` — digitalización aprobada.
- `evaluaciones/data/estres_contacto_criterios.json` — matriz interna aprobada.
- `evaluaciones/data/traccion_inicial.json` — ajuste de 140 N aprobado.
- `evaluaciones/data/transporte_limites.json` — tabla corregida aprobada.
- `evaluaciones/data/vibracion_cuerpo_entero_limites.json` — método A(8) adoptado.
- `evaluaciones/data/vibracion_mano_brazo_limites.json` — banda interna aprobada.
- `docs/VALIDACION_PROFESIONAL_FUENTES_EVALUACIONES_2026-07-31.md` — cierre ERGO-P2-026.
- `README.md` — registro profesional del cierre.
- `docs/BITACORA_INTEGRACION_886.md` del destino — esta entrada central.
- `docs/ROADMAP_INTEGRACION_ERGONOMIA_886.md` del destino — commit 1.0 marcado como completado.

### Verificaciones ejecutadas

```text
./venv/bin/python -c "<script de aprobaciones del roadmap>"
APROBADO bipedestacion_limites.json                    approved por Lic. Pablo R. Aguirre — MN 10.027
APROBADO confort_termico_umbrales.json                 approved por Lic. Pablo R. Aguirre — MN 10.027
         empuje_inicial.json                           not_recorded
         empuje_sostenida.json                         not_recorded
APROBADO estres_contacto_criterios.json                approved por Lic. Pablo R. Aguirre — MN 10.027
         lmc_tablas.json                               not_recorded
         posturas_forzadas_puntajes.json               not_recorded
         repetitivos_ms_limites.json                   not_recorded
APROBADO traccion_inicial.json                         approved por Lic. Pablo R. Aguirre — MN 10.027
         traccion_sostenida.json                       not_recorded
APROBADO transporte_limites.json                       approved por Lic. Pablo R. Aguirre — MN 10.027
APROBADO vibracion_cuerpo_entero_limites.json          approved por Lic. Pablo R. Aguirre — MN 10.027
APROBADO vibracion_mano_brazo_limites.json             approved por Lic. Pablo R. Aguirre — MN 10.027

Aprobados: 7 | Restantes en not_recorded: 6

Provenance pendientes: 0

OK  bipedestacion_limites                         1.1.0
OK  confort_termico_umbrales                      1.1.0
OK  estres_contacto_criterios                     1.1.0
OK  traccion_inicial                              1.1.0
OK  transporte_limites                            1.1.0
OK  vibracion_cuerpo_entero_limites               1.1.0
OK  vibracion_mano_brazo_limites                  1.1.0

./venv/bin/python manage.py makemigrations --check --dry-run
No changes detected

./venv/bin/python manage.py test --settings=ergonomia_srt.test_settings
----------------------------------------------------------------------
Ran 160 tests in 2.172s

OK
Destroying test database for alias 'default'...
Found 160 test(s).
System check identified no issues (0 silenced).

./venv/bin/python manage.py runserver 127.0.0.1:8011 --noreload --settings=ergonomia_srt.test_settings
System check identified no issues (0 silenced).
Starting development server at http://127.0.0.1:8011/
GET / -> HTTP 302
```

### Desvíos respecto del roadmap
El `grep -l "pending"` propuesto también encuentra tres valores descriptivos
de `source_validation.status`; no son `provenance_status`. Se verificó el campo
correcto con JSON y el resultado fue cero pendientes. El primer intento de
levantar el servidor fue bloqueado por la sandbox; con permiso local arrancó y
respondió. La identidad se tomó de la aprobación explícita del encargo y del
pie del proyecto: `Lic. Pablo R. Aguirre — MN 10.027`.

### Notas para el commit siguiente
Los siete `data_version` siguen en `1.1.0`; solo cambiaron metadatos y SHA-256.

## Commit 1.1 — `Evaluacion.usuario` → `settings.AUTH_USER_MODEL` (B1)

| Campo | Valor |
|---|---|
| Fecha | 2026-08-03 00:01 |
| Repositorio | ergonomia_srt |
| Rama | `feature/preparacion-integracion` |
| Hash | `8ff0706` |
| Fase | 1 |
| Estado | ⚠️ Completado con desvíos |

### Qué se hizo
`Evaluacion.usuario` dejó de importar `auth.User` y referencia ahora el modelo
configurado en `settings.AUTH_USER_MODEL`. El campo conserva su nombre y estado
de migración existentes.

### Archivos modificados
- `planillas/models.py` — FK de usuario convertida a referencia swappable.
- `README.md` del origen — compatibilidad con `accounts.CustomUser` registrada.
- `docs/BITACORA_INTEGRACION_886.md` del destino — esta entrada central.
- `docs/ROADMAP_INTEGRACION_ERGONOMIA_886.md` — hallazgo y avance 1.1.
- `docs/INTEGRACION_MODULO_ERGONOMIA_886_PROPUESTA_TECNICA.md` — corrección del diseño sobre `verbose_name`.

### Verificaciones ejecutadas

```text
grep -rn "from django.contrib.auth.models import User" --include="*.py" . | grep -v venv
<sin salida>

# Primera comprobación con el verbose_name propuesto
./venv/bin/python manage.py makemigrations --check --dry-run
Migrations for 'planillas':
  planillas/migrations/0002_alter_evaluacion_usuario.py
    ~ Alter field usuario on evaluacion

# Comprobación después de retirar el cambio cosmético
./venv/bin/python manage.py makemigrations --check --dry-run
No changes detected

./venv/bin/python manage.py test --settings=ergonomia_srt.test_settings
----------------------------------------------------------------------
Ran 160 tests in 2.272s

OK
Destroying test database for alias 'default'...
Found 160 test(s).
System check identified no issues (0 silenced).

./venv/bin/python manage.py runserver 127.0.0.1:8012 --noreload --settings=ergonomia_srt.test_settings
System check identified no issues (0 silenced).
Starting development server at http://127.0.0.1:8012/
GET / -> HTTP 302
```

### Desvíos respecto del roadmap
El `verbose_name="Profesional responsable"` del ejemplo altera el estado del
campo y contradice la premisa “no genera migración”. Se retiró por ser cosmético
y se conservaron tanto el objetivo B1 como el criterio crítico de cero
migraciones. El hallazgo quedó incorporado al roadmap y a la propuesta técnica.

### Notas para el commit siguiente
No se creó ningún archivo `0002`; la migración mostrada fue solo el resultado
de `--check --dry-run` antes de corregir el desvío.

## Commit 1.2 — `app_name` en `planillas` + 24 referencias (B3)

| Campo | Valor |
|---|---|
| Fecha | 2026-08-03 00:06 |
| Repositorio | ergonomia_srt |
| Rama | `feature/preparacion-integracion` |
| Hash | `503f9ba` |
| Fase | 1 |
| Estado | ⚠️ Completado con desvíos |

### Qué se hizo
Se declaró el namespace `planillas` y se calificaron 19 referencias de
templates, cinco redirects y nueve nombres dinámicos de la prueba de rutas.
Los 14 nombres planos dejaron de resolver.

### Archivos modificados
- `planillas/urls.py` — `app_name = "planillas"`.
- `planillas/views.py` — cinco redirects calificados.
- `planillas/tests.py` — nueve nombres dinámicos calificados, sin tocar aserciones.
- `planillas/templates/`, `core/templates/` y `exportaciones/templates/` — 19 referencias calificadas.
- `README.md` del origen — namespace documentado.
- `docs/BITACORA_INTEGRACION_886.md`, roadmap y propuesta del destino — trazabilidad e inventario real.

### Verificaciones ejecutadas

```text
planillas:crear_evaluacion             -> /planillas/crear/
planillas:detalle_evaluacion           -> /planillas/1/
planillas:planilla1                    -> /planillas/1/planilla1/
planillas:planilla2a                   -> /planillas/1/planilla2a/
planillas:planilla2i                   -> /planillas/1/planilla2i/
planillas:planilla3                    -> /planillas/1/planilla3/
planillas:planilla4                    -> /planillas/1/planilla4/
OK  detalle_evaluacion ya no resuelve sin namespace
OK  planilla1 ya no resuelve sin namespace

# Primera suite, antes de descubrir las referencias dinámicas
Ran 160 tests in 2.108s
FAILED (errors=9)
NoReverseMatch: Reverse for 'planilla2a' not found.

./venv/bin/python manage.py test planillas --settings=ergonomia_srt.test_settings -v 2
Ran 1 test in 0.065s
OK

./venv/bin/python manage.py test --settings=ergonomia_srt.test_settings
----------------------------------------------------------------------
Ran 160 tests in 2.168s

OK
Destroying test database for alias 'default'...
Found 160 test(s).
System check identified no issues (0 silenced).

./venv/bin/python manage.py makemigrations --check --dry-run
No changes detected

./venv/bin/python manage.py runserver 127.0.0.1:8013 --noreload --settings=ergonomia_srt.test_settings
System check identified no issues (0 silenced).
Starting development server at http://127.0.0.1:8013/
GET /planillas/1/planilla2a/ -> HTTP 302
```

### Desvíos respecto del roadmap
El inventario de 24 omitía nueve nombres generados con f-string en
`planillas/tests.py`. La suite los detectó; se antepuso `planillas:` al valor
dinámico sin cambiar una sola aserción. El inventario corregido de 33 quedó
registrado también en la propuesta técnica.

### Notas para el commit siguiente
Las cadenas `planilla2a`…`planilla2i` que permanecen en vistas, catálogos y
serializadores son slugs de dominio, no nombres de URL.

## Commit 1.3 — `app_name` en `help_ai` + 11 referencias (B3, CF-1)

| Campo | Valor |
|---|---|
| Fecha | 2026-08-03 00:09 |
| Repositorio | ergonomia_srt |
| Rama | `feature/preparacion-integracion` |
| Hash | `9aef28d` |
| Fase | 1 |
| Estado | ✅ Completado |

### Qué se hizo
Se declaró `app_name = "help_ai"`, se calificaron dos atributos `data-*` del
template base y exactamente nueve `reverse()` protegidos por CF-1. No se
modificó ninguna aserción, patch, cuota ni caso.

### Archivos modificados
- `help_ai/urls.py` — namespace `help_ai`.
- `templates/base.html` — dos URLs calificadas.
- `help_ai/tests.py` — nueve sustituciones mecánicas de namespace.
- `README.md` del origen — cumplimiento CF-1 registrado.
- bitácora y roadmap del destino — trazabilidad y avance 1.3.

### Verificaciones ejecutadas

```text
git diff --numstat help_ai/tests.py
9       9       help_ai/tests.py

git diff help_ai/tests.py
@@ -140,11 +140,11 @@
- reverse("chat_ai", kwargs={"slug": slug})
+ reverse("help_ai:chat_ai", kwargs={"slug": slug})
- reverse("help_guide", kwargs={"slug": slug})
+ reverse("help_ai:help_guide", kwargs={"slug": slug})
@@ -187,7 +187,7 @@
- reverse("chat_ai", kwargs={"slug": "lmc"})
+ reverse("help_ai:chat_ai", kwargs={"slug": "lmc"})
@@ -199,7 +199,7 @@
- reverse("chat_ai", kwargs={"slug": "slug-inexistente"})
+ reverse("help_ai:chat_ai", kwargs={"slug": "slug-inexistente"})
@@ -210,7 +210,7 @@
- reverse("help_guide", kwargs={"slug": "lmc"})
+ reverse("help_ai:help_guide", kwargs={"slug": "lmc"})
@@ -224,7 +224,7 @@
- url = reverse("chat_ai", kwargs={"slug": "lmc"})
+ url = reverse("help_ai:chat_ai", kwargs={"slug": "lmc"})
@@ -244,7 +244,7 @@
- reverse("help_guide", kwargs={"slug": "lmc"})
+ reverse("help_ai:help_guide", kwargs={"slug": "lmc"})
@@ -254,7 +254,7 @@
- reverse("chat_ai", kwargs={"slug": "lmc"})
+ reverse("help_ai:chat_ai", kwargs={"slug": "lmc"})
@@ -480,7 +480,7 @@
- reverse("chat_ai", kwargs={"slug": "lmc"})
+ reverse("help_ai:chat_ai", kwargs={"slug": "lmc"})

help_ai:help_guide        -> /ai/guide/lmc/
help_ai:chat_ai           -> /ai/chat/lmc/
OK  help_guide ya no resuelve sin namespace
OK  chat_ai ya no resuelve sin namespace

./venv/bin/python manage.py test help_ai --settings=ergonomia_srt.test_settings -v 2
----------------------------------------------------------------------
Ran 22 tests in 0.307s
OK

./venv/bin/python manage.py test --settings=ergonomia_srt.test_settings
----------------------------------------------------------------------
Ran 160 tests in 2.159s
OK

./venv/bin/python manage.py makemigrations --check --dry-run
No changes detected

./venv/bin/python manage.py runserver 127.0.0.1:8014 --noreload --settings=ergonomia_srt.test_settings
System check identified no issues (0 silenced).
Starting development server at http://127.0.0.1:8014/
GET /ai/guide/lmc/ -> HTTP 401
```

### Desvíos respecto del roadmap
Ninguno. El HTTP 401 del smoke anónimo es la protección esperada de la guía.

### Notas para el commit siguiente
La evidencia completa del diff confirma el criterio reformulado de CF-1.

## Commit 1.4 — Retirar `django-cors-headers`

| Campo | Valor |
|---|---|
| Fecha | 2026-08-03 00:11 |
| Repositorio | ergonomia_srt |
| Rama | `feature/preparacion-integracion` |
| Hash | `1d314c7` |
| Fase | 1 |
| Estado | ✅ Completado |

### Qué se hizo
Se retiraron la app, el middleware, el bloque limitado a localhost y la
dependencia `django-cors-headers`, reduciendo superficie sin alterar rutas.

### Archivos modificados
- `ergonomia_srt/settings.py` — referencias CORS retiradas.
- `requirements.txt` — dependencia retirada.
- `README.md` del origen — decisión documentada.
- bitácora y roadmap del destino — trazabilidad y avance 1.4.

### Verificaciones ejecutadas

```text
grep -rn "corsheaders\|CORS_ALLOWED" --include="*.py" . | grep -v venv
<sin salida>

./venv/bin/python manage.py check
System check identified no issues (0 silenced).

./venv/bin/python manage.py makemigrations --check --dry-run
No changes detected

./venv/bin/python manage.py test --settings=ergonomia_srt.test_settings
----------------------------------------------------------------------
Ran 160 tests in 2.186s
OK

./venv/bin/python manage.py runserver 127.0.0.1:8015 --noreload --settings=ergonomia_srt.test_settings
System check identified no issues (0 silenced).
Starting development server at http://127.0.0.1:8015/
GET / -> HTTP 302
```

### Desvíos respecto del roadmap
Ninguno.

### Notas para el commit siguiente
Ninguna.

## Commit 1.5 — Limpiar dependencias no usadas

| Campo | Valor |
|---|---|
| Fecha | 2026-08-03 00:15 |
| Repositorio | ergonomia_srt |
| Rama | `feature/preparacion-integracion` |
| Hash | `76f1c92` |
| Fase | 1 |
| Estado | ✅ Completado |

### Qué se hizo
Se alineó la declaración de dependencias con el destino: psycopg 3 reemplaza
a psycopg2, se retiró `sse-starlette`, se declaró Pillow y se documentó el
descarte histórico de WeasyPrint. El venv del origen no se reinstaló.

### Archivos modificados
- `requirements.txt` — driver y dependencias declaradas ajustados.
- `docs/INFORME_TECNICO_ESTADO_PROYECTO_2026-07-31.md` — descartes documentados.
- `README.md` del origen — cambio registrado.
- bitácora y roadmap del destino — trazabilidad y avance 1.5.

### Verificaciones ejecutadas

```text
grep -rn "sse_starlette\|from sse" --include="*.py" . --exclude-dir=venv
<sin salida>

grep -rn "weasyprint" --include="*.py" . --exclude-dir=venv
<sin salida>

./venv/bin/python manage.py check
System check identified no issues (0 silenced).

./venv/bin/python manage.py makemigrations --check --dry-run
RuntimeWarning: connection to server at "localhost", port 5432 failed:
Operation not permitted
No changes detected

./venv/bin/python manage.py test --settings=ergonomia_srt.test_settings
----------------------------------------------------------------------
Ran 160 tests in 2.666s
OK
Destroying test database for alias 'default'...
Found 160 test(s).
System check identified no issues (0 silenced).

./venv/bin/python manage.py runserver 127.0.0.1:8015 --noreload
System check identified no issues (0 silenced).
Starting development server at http://127.0.0.1:8015/
GET /planillas/ -> 404
GET /planillas/crear/ -> 302
```

### Desvíos respecto del roadmap
El primer smoke apuntó a `/planillas/`, ruta que el URLconf no declara, y
devolvió 404. Se corrigió el objetivo a la ruta real `/planillas/crear/`, que
respondió 302 por la autenticación esperada. El warning de PostgreSQL en
`makemigrations` es una restricción de red del sandbox; el comando terminó en
éxito con `No changes detected`.

### Notas para el commit siguiente
El cambio de driver se hará efectivo recién al integrar en el destino.

## Commit 1.6 — `LANGUAGE_CODE = 'es-ar'` (D-8)

| Campo | Valor |
|---|---|
| Fecha | 2026-08-03 00:17 |
| Repositorio | ergonomia_srt |
| Rama | `feature/preparacion-integracion` |
| Hash | `47bdec5` |
| Fase | 1 |
| Estado | ✅ Completado |

### Qué se hizo
Se alineó `LANGUAGE_CODE` con la interfaz en español y el destino mediante
`es-ar`. Se verificaron en forma focalizada las exportaciones y se ejecutó el
criterio de aceptación completo de la Fase 1.

### Archivos modificados
- `ergonomia_srt/settings.py` — locale regional argentino.
- `README.md` del origen — D-8 cerrado.
- bitácora y roadmap del destino — trazabilidad y avance 1.6.

### Verificaciones ejecutadas

```text
grep -rn "date_format\|localize\|floatformat\|intcomma" --include="*.py" --include="*.html" . --exclude-dir=venv
./evaluaciones/templates/evaluaciones/estres_contacto_form.html:246:
{{ object.calc_data.presion_kpa|floatformat:1 }}

./venv/bin/python manage.py test exportaciones.tests.test_official_pdf exportaciones.tests.test_serializers --settings=ergonomia_srt.test_settings -v 2
test_las_fechas_salen_en_formato_argentino ... ok
test_formato_argentino_de_fecha_y_numero ... ok
----------------------------------------------------------------------
Ran 47 tests in 0.194s
OK

./venv/bin/python manage.py test --settings=ergonomia_srt.test_settings
----------------------------------------------------------------------
Ran 160 tests in 2.644s
OK
Destroying test database for alias 'default'...
Found 160 test(s).
System check identified no issues (0 silenced).

./venv/bin/python manage.py check
System check identified no issues (0 silenced).

./venv/bin/python manage.py makemigrations --check --dry-run
RuntimeWarning: connection to server at "localhost", port 5432 failed:
Operation not permitted
No changes detected

# Criterio de aceptación de Fase 1
auth.models.User imports: <sin salida>
planillas/urls.py:5:app_name = "planillas"
help_ai/urls.py:6:app_name = "help_ai"
git show --numstat --format= 9aef28d -- help_ai/tests.py
9       9       help_ai/tests.py
approved=7 not_recorded=6
bipedestacion_limites.json | Lic. Pablo R. Aguirre — MN 10.027 | 2026-08-02 | True
confort_termico_umbrales.json | Lic. Pablo R. Aguirre — MN 10.027 | 2026-08-02 | True
estres_contacto_criterios.json | Lic. Pablo R. Aguirre — MN 10.027 | 2026-08-02 | True
traccion_inicial.json | Lic. Pablo R. Aguirre — MN 10.027 | 2026-08-02 | True
transporte_limites.json | Lic. Pablo R. Aguirre — MN 10.027 | 2026-08-02 | True
vibracion_cuerpo_entero_limites.json | Lic. Pablo R. Aguirre — MN 10.027 | 2026-08-02 | True
vibracion_mano_brazo_limites.json | Lic. Pablo R. Aguirre — MN 10.027 | 2026-08-02 | True
requirements.txt paquetes retirados: no declarados (solo comentario explicativo de sse-starlette)
ergonomia_srt/settings.py:178:LANGUAGE_CODE = 'es-ar'

./venv/bin/python manage.py runserver 127.0.0.1:8016 --noreload
System check identified no issues (0 silenced).
Starting development server at http://127.0.0.1:8016/
GET /planillas/crear/ -> 302
```

### Desvíos respecto del roadmap
El primer inventario ad hoc de aprobaciones consultó erróneamente una clave
plana `approval_status` y devolvió cero. La estructura real es
`meta.professional_approval.status`; corregida la consulta, confirmó 7
aprobados y 6 `not_recorded`. No hubo impacto de locale en fechas, números ni
PDF. El warning PostgreSQL vuelve a corresponder al aislamiento de red.

### Notas para el commit siguiente
Fase 1 cerrada. El origen queda congelado en cuanto este commit sea publicado;
la ejecución vuelve al repositorio destino para la Fase 2.

## Commit 2.1 — Crear el paquete contenedor

| Campo | Valor |
|---|---|
| Fecha | 2026-08-03 00:20 |
| Repositorio | ergocapacitacion |
| Rama | `feature/ergonomia-886` |
| Hash | `329f379` |
| Fase | 2 |
| Estado | ✅ Completado |

### Qué se hizo
Se creó el paquete desmontable `apps.ergonomia_886` con el docstring completo
que identifica las cuatro apps y vincula expresamente CF-1 a CF-6. También se
consolidó en el destino la trazabilidad documental de los siete commits de la
Fase 1 ya publicados en el origen.

### Archivos modificados
- `apps/ergonomia_886/__init__.py` — paquete contenedor y contrato vinculante.
- `docs/BITACORA_INTEGRACION_886.md` — entradas 1.0 a 2.1 consolidadas.
- `docs/ROADMAP_INTEGRACION_ERGONOMIA_886.md` — avance 1.0 a 2.1.
- `docs/INTEGRACION_MODULO_ERGONOMIA_886_PROPUESTA_TECNICA.md` — inventarios corregidos tras los desvíos 1.1 y 1.2.
- `README.md` — cierre de Fase 1 y creación del contenedor registrados.

### Verificaciones ejecutadas

```text
test -f apps/ergonomia_886/__init__.py && echo OK
OK

.venv/bin/python -c "import apps.ergonomia_886; print(apps.ergonomia_886.__doc__[:80])"
Módulo de Evaluación Ergonómica — Protocolo SRT 886/15.

Digitaliza de punta a p

.venv/bin/python manage.py check --settings=config.test_settings
System check identified no issues (0 silenced).

.venv/bin/python manage.py makemigrations --check --dry-run --settings=config.test_settings
No changes detected

.venv/bin/python manage.py test apps --settings=config.test_settings
----------------------------------------------------------------------
Ran 36 tests in 0.153s
OK
Destroying test database for alias 'default'...
Found 36 test(s).
System check identified no issues (0 silenced).

.venv/bin/python manage.py runserver 127.0.0.1:8017 --noreload --settings=config.test_settings
System check identified no issues (0 silenced).
You have 33 unapplied migration(s).
Starting development server at http://127.0.0.1:8017/
GET / -> 200
```

### Desvíos respecto del roadmap
Ninguno. El aviso de 33 migraciones al levantar el servidor corresponde a la
base SQLite en memoria nueva de ese proceso; `makemigrations --check` y la
suite —que crea y migra su propia base efímera— cerraron correctamente.

### Notas para el commit siguiente
El commit 2.2 vuelve excepcionalmente al origen para actualizar las 48 cadenas
de importación antes de mover los archivos.

## Commit 2.2 — Actualizar las 48 rutas declarativas ANTES de mover (B2)

| Campo | Valor |
|---|---|
| Fecha | 2026-08-03 00:23 |
| Repositorio | ergonomia_srt |
| Rama | `feature/preparacion-integracion` |
| Hash | `dea4f57` |
| Fase | 2 |
| Estado | ✅ Completado |

### Qué se hizo
Se reapuntaron antes del trasplante las 48 rutas declarativas resueltas con
`import_string()` y las dos apariciones del recurso de datos. El origen queda
intencionalmente no ejecutable porque el paquete `apps` solo existe en el
destino, tal como prevé el roadmap.

### Archivos modificados
- `evaluaciones/catalog.py` — 13 formularios y 13 modelos.
- `evaluaciones/calculators.py` — dos apariciones del recurso de datos.
- `exportaciones/official/catalog.py` — 12 modelos oficiales.
- `exportaciones/serializers.py` — 9 modelos de Planilla 2.
- `README.md` del origen — punto de no retorno documentado.
- bitácora y roadmap del destino — trazabilidad y avance 2.2.

### Verificaciones ejecutadas

```text
catalog.py forms  : 13
catalog.py models : 13
official/catalog  : 12
serializers       : 9
calculators data  : 2

rg -n '"evaluaciones\.(forms|models|data)|"planillas\.models\.' --glob '*.py' --glob '!venv/**' .
<sin salida>

./venv/bin/python manage.py test --settings=ergonomia_srt.test_settings
Creating test database for alias 'default'...
Destroying test database for alias 'default'...
Found 160 test(s).
Traceback (most recent call last):
  File "evaluaciones/views.py", line 658, in _install_catalog_view_classes
    "form_class": import_string(definition.form_path),
  File "django/utils/module_loading.py", line 15, in cached_import
    module = import_module(module_path)
ModuleNotFoundError: No module named 'apps'
```

### Desvíos respecto del roadmap
Ninguno. La suite falla exactamente por la causa esperada. `check`,
`makemigrations` y un smoke del origen atraviesan el mismo URLconf y quedan
deliberadamente bloqueados hasta completar el trasplante en el destino.

### Notas para el commit siguiente
Copiar las cuatro apps desde este estado exacto; no ejecutar nuevas pruebas en
el origen independiente.

## Commit 2.3 — Copiar las 4 apps con migraciones y templates

| Campo | Valor |
|---|---|
| Fecha | 2026-08-03 00:26 |
| Repositorio | ergocapacitacion |
| Rama | `feature/ergonomia-886` |
| Hash | `9b6f577` |
| Fase | 2 |
| Estado | ✅ Completado |

### Qué se hizo
Se copiaron byte a byte las cuatro apps completas, se retiraron únicamente
cachés compilados arrastrados y se compararon los árboles contra el origen.
`core` no se copió. Los artefactos de CF-3 y CF-6 permanecen idénticos.

### Archivos modificados
- `apps/ergonomia_886/{planillas,evaluaciones,exportaciones,help_ai}/` — 4 apps completas.
- `README.md` — inventario y SHA oficial registrados.
- `docs/ROADMAP_INTEGRACION_ERGONOMIA_886.md` — avance y rótulo del inventario corregidos.
- `docs/BITACORA_INTEGRACION_886.md` — evidencia literal 2.3.

### Verificaciones ejecutadas

```text
=== planillas
  identico
=== evaluaciones
  identico
=== exportaciones
  identico
=== help_ai
  identico

=== PDF oficial de la SRT (CF-6) ===
bc0d0753943888779abd0936f6c4dc2e128766c7cf6370a4a2fb19073aad59f4  /Users/praguirre/ergonomia_srt/exportaciones/official/templates_bin/res_srt_886_15-formulario.pdf
bc0d0753943888779abd0936f6c4dc2e128766c7cf6370a4a2fb19073aad59f4  apps/ergonomia_886/exportaciones/official/templates_bin/res_srt_886_15-formulario.pdf
251599 bytes

=== 13 artefactos normativos (CF-3) ===
identicos
=== 12 mapas de calibracion (CF-6) ===
identicos

python_cuatro_apps_total=71
python_sin_directorios_migrations=58
migraciones_numeradas=10
templates_html=24
artefactos_json=13
mapas_json=12
pdf_oficial=1
pycache=0

.venv/bin/python manage.py check --settings=config.test_settings
System check identified no issues (0 silenced).

.venv/bin/python manage.py makemigrations --check --dry-run --settings=config.test_settings
No changes detected

# Descubrimiento amplio en el estado intermedio
.venv/bin/python manage.py test apps --settings=config.test_settings
Ran 44 tests in 0.179s
FAILED (errors=8)
ModuleNotFoundError: No module named 'planillas'
ModuleNotFoundError: No module named 'exportaciones'
ModuleNotFoundError: No module named 'evaluaciones'
RuntimeError: Model class apps.ergonomia_886.planillas.models.Evaluacion
doesn't declare an explicit app_label and isn't in INSTALLED_APPS.

# Suite preexistente aislada por sus nueve labels
.venv/bin/python manage.py test apps.accounts apps.certificates apps.company apps.dashboard apps.ergobot_ai apps.landing apps.presencial apps.quiz apps.training --settings=config.test_settings
----------------------------------------------------------------------
Ran 36 tests in 0.150s
OK
Destroying test database for alias 'default'...
Found 36 test(s).
System check identified no issues (0 silenced).

.venv/bin/python manage.py runserver 127.0.0.1:8018 --noreload --settings=config.test_settings
System check identified no issues (0 silenced).
Starting development server at http://127.0.0.1:8018/
GET / -> 200
```

### Desvíos respecto del roadmap
El inventario rotulaba 71 archivos Python «sin migraciones». El desglose real
de la propuesta —10 + 20 + 28 + 13— sí suma 71, pero incluye diez migraciones
numeradas y cuatro `migrations/__init__.py`; excluyendo esos directorios quedan
58. Se corrigió el rótulo del roadmap, sin alterar la propuesta ya correcta.

Además, `test apps` descubre por filesystem las apps copiadas aunque todavía
no estén registradas y arroja ocho errores de importación esperables antes de
2.4, 2.5 y 2.8. Las 36 pruebas preexistentes, ejecutadas por sus nueve labels,
continúan verdes y el destino responde HTTP 200.

`git diff --cached --check` informa espacios finales heredados en varios
archivos del origen. No se normalizaron en este commit porque 2.3 exige una
copia idéntica y los cuatro `diff -r` son la verificación de aceptación; su
limpieza sería un cambio separado, ajeno al trasplante byte a byte.

### Notas para el commit siguiente
Actualizar únicamente los cuatro `AppConfig.name`; no registrar todavía las
apps en settings.

## Commit 2.4 — Actualizar `name` en los 4 `apps.py`

| Campo | Valor |
|---|---|
| Fecha | 2026-08-03 00:28 |
| Repositorio | ergocapacitacion |
| Rama | `feature/ergonomia-886` |
| Hash | `d17a3e3` |
| Fase | 2 |
| Estado | ✅ Completado |

### Qué se hizo
Los cuatro `AppConfig.name` se actualizaron a su ruta punteada bajo
`apps.ergonomia_886`. Se agregaron nombres administrativos descriptivos y se
documentó por qué no se declara `label`, preservando migraciones y CF-1.

### Archivos modificados
- `apps/ergonomia_886/{planillas,evaluaciones,exportaciones,help_ai}/apps.py` — rutas y nombres administrativos.
- `README.md` — labels preservados documentados.
- `docs/ROADMAP_INTEGRACION_ERGONOMIA_886.md` — avance 2.4.
- `docs/BITACORA_INTEGRACION_886.md` — evidencia literal 2.4.

### Verificaciones ejecutadas

```text
grep -n 'name = ' apps/ergonomia_886/*/apps.py
apps/ergonomia_886/evaluaciones/apps.py:7:    name = 'apps.ergonomia_886.evaluaciones'
apps/ergonomia_886/exportaciones/apps.py:6:    name = "apps.ergonomia_886.exportaciones"
apps/ergonomia_886/help_ai/apps.py:6:    name = 'apps.ergonomia_886.help_ai'
apps/ergonomia_886/planillas/apps.py:6:    name = 'apps.ergonomia_886.planillas'

grep -n '^[[:space:]]*label = ' apps/ergonomia_886/*/apps.py
label explicito: ninguno

AppConfig.create(...)
apps.ergonomia_886.planillas -> label=planillas
apps.ergonomia_886.evaluaciones -> label=evaluaciones
apps.ergonomia_886.exportaciones -> label=exportaciones
apps.ergonomia_886.help_ai -> label=help_ai

.venv/bin/python manage.py check --settings=config.test_settings
System check identified no issues (0 silenced).

.venv/bin/python manage.py makemigrations --check --dry-run --settings=config.test_settings
No changes detected

.venv/bin/python manage.py test apps.accounts apps.certificates apps.company apps.dashboard apps.ergobot_ai apps.landing apps.presencial apps.quiz apps.training --settings=config.test_settings
----------------------------------------------------------------------
Ran 36 tests in 0.165s
OK
Destroying test database for alias 'default'...
Found 36 test(s).
System check identified no issues (0 silenced).

.venv/bin/python manage.py runserver 127.0.0.1:8019 --noreload --settings=config.test_settings
System check identified no issues (0 silenced).
Starting development server at http://127.0.0.1:8019/
GET / -> 200
```

### Desvíos respecto del roadmap
Ninguno. La suite amplia `test apps` conserva el estado intermedio ya
documentado en 2.3 hasta reescribir imports y registrar las apps.

### Notas para el commit siguiente
Reescribir los imports absolutos con inventario antes/después, sin modificar
las migraciones.

## Commit 2.5 — Reescribir los 102 imports absolutos (B2)

| Campo | Valor |
|---|---|
| Fecha | 2026-08-03 00:32 |
| Repositorio | ergocapacitacion |
| Rama | `feature/ergonomia-886` |
| Hash | `e018d0d` |
| Fase | 2 |
| Estado | ✅ Completado |

### Qué se hizo
Se reescribieron mecánicamente los 101 imports presentes en las cuatro apps
trasplantadas, incluidos los indentados. El import 102 del inventario original
pertenecía a `core/views.py`, descartado en 2.3. Las migraciones permanecieron
intactas y la propuesta técnica quedó reconciliada con la ejecución.

### Archivos modificados
- 15 fuentes bajo `apps/ergonomia_886/` — prefijos absolutos reescritos.
- `README.md` — inventario efectivo documentado.
- `docs/ROADMAP_INTEGRACION_ERGONOMIA_886.md` — avance e inventario corregidos.
- `docs/INTEGRACION_MODULO_ERGONOMIA_886_PROPUESTA_TECNICA.md` — hallazgo de ejecución registrado.
- `docs/BITACORA_INTEGRACION_886.md` — evidencia literal 2.5.

### Verificaciones ejecutadas

```text
imports_viejos=0
imports_nuevos=101
apps/ergonomia_886/exportaciones/tests/test_serializers.py:39
apps/ergonomia_886/exportaciones/tests/test_official_pdf.py:15
apps/ergonomia_886/exportaciones/tests/test_permissions.py:12
apps/ergonomia_886/exportaciones/tests/test_reports_llm.py:12
apps/ergonomia_886/exportaciones/tests/test_reports_pdf.py:7
apps/ergonomia_886/exportaciones/serializers.py:3
apps/ergonomia_886/exportaciones/views.py:3
apps/ergonomia_886/evaluaciones/tests.py:2
apps/ergonomia_886/exportaciones/packaging.py:2
apps/ergonomia_886/evaluaciones/admin.py:1
apps/ergonomia_886/evaluaciones/models.py:1
apps/ergonomia_886/evaluaciones/views.py:1
apps/ergonomia_886/exportaciones/models.py:1
apps/ergonomia_886/help_ai/catalog.py:1
apps/ergonomia_886/planillas/views.py:1
migraciones_modificadas=0

AST sobre todos los .py
Archivos con error de sintaxis: 0

.venv/bin/python manage.py check --settings=config.test_settings
System check identified no issues (0 silenced).

.venv/bin/python manage.py makemigrations --check --dry-run --settings=config.test_settings
No changes detected

.venv/bin/python manage.py test apps --settings=config.test_settings
Ran 44 tests in 0.167s
FAILED (errors=8)
RuntimeError: Model class apps.ergonomia_886.planillas.models.Evaluacion
doesn't declare an explicit app_label and isn't in INSTALLED_APPS.
AttributeError: 'Settings' object has no attribute 'CHAT_AI_AGENT_CACHE_SIZE'

.venv/bin/python manage.py test apps.accounts apps.certificates apps.company apps.dashboard apps.ergobot_ai apps.landing apps.presencial apps.quiz apps.training --settings=config.test_settings
----------------------------------------------------------------------
Ran 36 tests in 0.143s
OK
Destroying test database for alias 'default'...
Found 36 test(s).
System check identified no issues (0 silenced).

.venv/bin/python manage.py runserver 127.0.0.1:8020 --noreload --settings=config.test_settings
System check identified no issues (0 silenced).
Starting development server at http://127.0.0.1:8020/
GET / -> 200
```

### Desvíos respecto del roadmap
La suma del propio inventario del commit daba 101, no 102: el número 102 de
la propuesta incluía `core/views.py`, correctamente descartado. También había
87 imports en suites y no 85 al incluir los dos de `evaluaciones/tests.py`.
Roadmap y propuesta quedaron aclarados; el mensaje de Git se conserva literal.

Contrario a la nota del plan, `manage.py check` no falla: Django ignora las
apps aún no registradas. El descubrimiento amplio sí falla al importarlas y
confirma los dos pendientes previstos para 2.8 (registro y settings de ayuda).

### Notas para el commit siguiente
Corregir el cálculo de la ruta de ayuda antes de registrar las apps.

## Commit 2.6 — Corregir la ruta de los documentos de ayuda (B6)

| Campo | Valor |
|---|---|
| Fecha | 2026-08-03 00:41 |
| Repositorio | ergocapacitacion |
| Rama | `feature/ergonomia-886` |
| Hash | `2d0c9f6` |
| Fase | 2 |
| Estado | ✅ Completado |

### Qué se hizo
`HELP_TEXTS_PATH` quedó anclado a `settings.BASE_DIR`, sin depender de la
profundidad del paquete. Se mantuvo la carga estricta: nombres inválidos y
documentos ausentes siguen lanzando `HelpContentError`.

### Archivos modificados
- `apps/ergonomia_886/help_ai/prompts.py` — ruta estable desde settings.
- `README.md` — bloqueo B6 documentado.
- `docs/ROADMAP_INTEGRACION_ERGONOMIA_886.md` — avance 2.6.
- `docs/BITACORA_INTEGRACION_886.md` — evidencia literal 2.6.

### Verificaciones ejecutadas

```text
Ruta   : /Users/praguirre/ergocapacitacion/static/ayuda/help_texts
Existe : False
Archivos .md: 0 (esperado 33 tras 2.7)
Nombre invalido: HelpContentError Nombre de ayuda inválido: '../invalido'
Ausencia estricta: HelpContentError No se pudo cargar el documento de ayuda slug-que-no-existe.md

Validación AST
Expresiones parent.parent ejecutables: 0 []
11:from django.conf import settings
21:HELP_TEXTS_PATH = Path(settings.BASE_DIR) / "static" / "ayuda" / "help_texts"

.venv/bin/python manage.py check --settings=config.test_settings
System check identified no issues (0 silenced).

.venv/bin/python manage.py makemigrations --check --dry-run --settings=config.test_settings
No changes detected

.venv/bin/python manage.py test apps.accounts apps.certificates apps.company apps.dashboard apps.ergobot_ai apps.landing apps.presencial apps.quiz apps.training --settings=config.test_settings
----------------------------------------------------------------------
Ran 36 tests in 0.151s
OK
Destroying test database for alias 'default'...
Found 36 test(s).
System check identified no issues (0 silenced).

# Intentos de smoke
127.0.0.1:8021 -> Error: That port is already in use.
127.0.0.1:8022 -> servidor iniciado; consulta local sin respuesta, terminada.
.venv/bin/python manage.py runserver 127.0.0.1:8024 --noreload --settings=config.test_settings
System check identified no issues (0 silenced).
Starting development server at http://127.0.0.1:8024/
GET / -> 200
```

### Desvíos respecto del roadmap
El grep literal de `parent.parent` encuentra el término en el comentario que
el propio cambio agrega; la validación semántica por AST confirmó cero
expresiones ejecutables. La inexistencia de los 33 Markdown es el estado
previsto hasta 2.7. Operativamente, 8021 estaba ocupado y la consulta a 8022
quedó colgada; se repitió con timeout en 8024 y respondió 200.

### Notas para el commit siguiente
Copiar los estáticos byte a byte y repetir esta verificación hasta obtener 33.

## Commit 2.7 — Copiar estáticos y verificar artefactos (CF-3, CF-6)

| Campo | Valor |
|---|---|
| Fecha | 2026-08-03 00:43 |
| Repositorio | ergocapacitacion |
| Rama | `feature/ergonomia-886` |
| Hash | `aff71c6` |
| Fase | 2 |
| Estado | ✅ Completado |

### Qué se hizo
Se copiaron byte a byte los 44 estáticos sin colisiones: ayuda, widget,
vendor y lógica de planillas. Se validó B6 leyendo Markdown y CF-3 mediante la
tabla completa de artefactos, con siete aprobaciones conservadas. CF-6 volvió
a confirmar el SHA oficial.

### Archivos modificados
- `static/ayuda/` — 33 Markdown, CSS y JS del widget.
- `static/vendor/` — Bootstrap, iconos y librerías del widget.
- `static/js/planilla_logic.js` — lógica de planillas.
- `README.md` — inventario de estáticos y CF-3 registrado.
- `docs/ROADMAP_INTEGRACION_ERGONOMIA_886.md` — avance 2.7.
- `docs/BITACORA_INTEGRACION_886.md` — evidencia literal 2.7.

### Verificaciones ejecutadas

```text
=== 33 documentos de ayuda ===
identicos
33
=== ayuda completa ===
identica
=== vendor ===
identico
=== planilla_logic.js ===
identico

=== SHA PDF oficial CF-6 ===
bc0d0753943888779abd0936f6c4dc2e128766c7cf6370a4a2fb19073aad59f4  apps/ergonomia_886/exportaciones/official/templates_bin/res_srt_886_15-formulario.pdf

HELP_TEXTS_PATH : /Users/praguirre/ergocapacitacion/static/ayuda/help_texts
Existe          : True
Documentos .md  : 33 (esperado 33)
  home               339 caracteres  OK
  lmc               9051 caracteres  OK
  guia_general     20103 caracteres  OK

artefacto                                     data_version  approval     sha256
--------------------------------------------------------------------------------------------------------------------------------------------
lmc_tablas.json                               1.2.0         not_recorded 90e38e6733eeb94c07bdeee41950fa9c88b56922873de3c4db6c7a850355d30e
empuje_inicial.json                           1.0.0         not_recorded 8d0077856b9e62889a83fb1cf4332ed48a005c86b280c67b0fe6696e3ba5df4d
empuje_sostenida.json                         1.0.0         not_recorded 353be6b03afdc8bf1f31a3190a7ee890a1b850d72d28baea59a4e4f36ba660cc
traccion_inicial.json                         1.1.0         approved     8f62137cac5a28789b3d4416e9e0fff2dfac1fd2abb29ac55926f9ae0423d26d
traccion_sostenida.json                       1.0.0         not_recorded d32c4bc5315378d232909fdc47461e5b73e7f2131c1d5cf9eac67c35006996b7
transporte_limites.json                       1.1.0         approved     d2d3b8e5c535268e429b2befd9ba9477e469637ddc7483da62d72558cc301543
bipedestacion_limites.json                    1.1.0         approved     b7eb4b666b24758ae7855bb7d7cc12b12678834c2fb3016259c7e3fb578af527
repetitivos_ms_limites.json                   1.1.0         not_recorded 95d58128660bcd6d363cbc44e21768cc85e86da3e44bff46b2f4f40cfb7e7b00
posturas_forzadas_puntajes.json               1.0.0         not_recorded 0eed12472f8117c5d9fdb919314cccabf2ca64f3a67334a11c11215e9f25f796
vibracion_mano_brazo_limites.json             1.1.0         approved     01a93bdc8d4b0a7463ed8bbd2ec0f72dae08901b1969e0807d8e2fdad04812b5
vibracion_cuerpo_entero_limites.json          1.1.0         approved     4d045818cb2de8065153a328fead1c06c76e6b210270d6f141624a6430f8c963
confort_termico_umbrales.json                 1.1.0         approved     0e1a2568ccc86cf9509d6d2ca62967d6837bb0bbcb15b875cdd63f535d361a72
estres_contacto_criterios.json                1.1.0         approved     a51386d89aaf0d957b3fe986ce889907cf36935ebf19f49eee6bd729f6e6d0f4
Total artefactos: 13 (esperado 13)
Total approved  : 7 (esperado 7)

.venv/bin/python manage.py check --settings=config.test_settings
System check identified no issues (0 silenced).

.venv/bin/python manage.py makemigrations --check --dry-run --settings=config.test_settings
No changes detected

.venv/bin/python manage.py test apps.accounts apps.certificates apps.company apps.dashboard apps.ergobot_ai apps.landing apps.presencial apps.quiz apps.training --settings=config.test_settings
----------------------------------------------------------------------
Ran 36 tests in 0.151s
OK
Destroying test database for alias 'default'...
Found 36 test(s).
System check identified no issues (0 silenced).

.venv/bin/python manage.py runserver 127.0.0.1:8025 --noreload --settings=config.test_settings
System check identified no issues (0 silenced).
Starting development server at http://127.0.0.1:8025/
GET / -> 200
```

### Desvíos respecto del roadmap
La primera importación de `calculators.py` falló porque las apps aún no están
en `INSTALLED_APPS`, paso reservado a 2.8. Para no adelantar archivos, la
verificación normativa agregó las cuatro configuraciones únicamente en
memoria antes de `django.setup()`; así se cargaron los 13 artefactos reales.

`git diff --cached --check` señala espacios finales heredados en varios
Markdown y en `planilla_logic.js`. Se preservaron deliberadamente porque este
commit exige integridad byte a byte y todos los `diff -r`/`cmp` resultaron
idénticos; normalizarlos invalidaría esa evidencia.

### Notas para el commit siguiente
Registrar las cuatro apps y portar todos los settings previstos; recién desde
2.8 la suite trasplantada debe poder inicializar el registro de modelos.

## Commit 2.8 — Registrar apps y settings del módulo

| Campo | Valor |
|---|---|
| Fecha | 2026-08-03 00:47 |
| Repositorio | ergocapacitacion |
| Rama | `feature/ergonomia-886` |
| Hash | `9f2dee8` |
| Fase | 2 |
| Estado | ✅ Completado |

### Qué se hizo
Se registraron las cuatro apps en orden de dependencia, se agregaron los 14
settings con defaults y su plantilla versionada, y se eliminó el fallback de
modelo duplicado de Ergobot. CF-1 mantiene ambas apps de IA separadas y solo
comparte la decisión de configuración del modelo.

### Archivos modificados
- `config/settings.py` — apps y 14 settings del módulo.
- `apps/ergobot_ai/agents.py` — modelo leído exclusivamente desde settings.
- `.env.example` — variables documentadas sin tocar `.env` real.
- `README.md` — registro y CF-1 documentados.
- `docs/ROADMAP_INTEGRACION_ERGONOMIA_886.md` — avance y conteo real corregidos.
- `docs/BITACORA_INTEGRACION_886.md` — evidencia literal 2.8.

### Verificaciones ejecutadas

```text
.venv/bin/python manage.py check
System check identified no issues (0 silenced).

.venv/bin/python manage.py check --settings=config.test_settings
System check identified no issues (0 silenced).

.venv/bin/python manage.py makemigrations --check --dry-run --settings=config.test_settings
No changes detected

=== Apps del modulo ===
  label=planillas       name=apps.ergonomia_886.planillas
  label=evaluaciones    name=apps.ergonomia_886.evaluaciones
  label=exportaciones   name=apps.ergonomia_886.exportaciones
  label=help_ai         name=apps.ergonomia_886.help_ai

=== CF-1: las dos apps de IA coexisten ===
  apps.ergobot_ai              : True
  apps.ergonomia_886.help_ai   : True

=== Settings del modelo ===
  OPENAI_MODEL  : gpt-4.1-mini-2025-04-14
  CHAT_AI_MODEL : gpt-4.1-mini-2025-04-14
  Derivacion OK : True

=== Modelos registrados ===
  planillas       15 modelos
  evaluaciones    15 modelos
  exportaciones   2 modelos

=== 14 settings del modulo ===
  CHAT_AI_MODEL=gpt-4.1-mini-2025-04-14
  CHAT_AI_AGENT_CACHE_SIZE=64
  CHAT_AI_RATE_LIMIT=20
  CHAT_AI_RATE_WINDOW_SECONDS=60
  CHAT_AI_STREAM_TIMEOUT_SECONDS=120
  CHAT_AI_HEARTBEAT_SECONDS=10
  CHAT_AI_MAX_QUESTION_CHARS=2000
  CHAT_AI_MAX_THREAD_MESSAGES=20
  CHAT_AI_MAX_MESSAGE_CHARS=4000
  REPORT_AI_TIMEOUT_SECONDS=90
  REPORT_AI_RATE_LIMIT=10
  REPORT_AI_RATE_WINDOW_SECONDS=3600
  EXPORT_RATE_LIMIT=60
  EXPORT_RATE_WINDOW_SECONDS=300
  total=14

# Suite combinada en estado intermedio
.venv/bin/python manage.py test apps --settings=config.test_settings
Ran 140 tests in 0.521s
FAILED (failures=2, errors=90)
Found 196 test(s).
System check identified no issues (0 silenced).

# Suite preexistente aislada
.venv/bin/python manage.py test apps.accounts apps.certificates apps.company apps.dashboard apps.ergobot_ai apps.landing apps.presencial apps.quiz apps.training --settings=config.test_settings
----------------------------------------------------------------------
Ran 36 tests in 0.146s
OK
Destroying test database for alias 'default'...
Found 36 test(s).
System check identified no issues (0 silenced).

.venv/bin/python manage.py runserver 127.0.0.1:8026 --noreload --settings=config.test_settings
System check identified no issues (0 silenced).
You have 43 unapplied migration(s).
Starting development server at http://127.0.0.1:8026/
GET / -> 200
```

### Desvíos respecto del roadmap
El conteo esperado 14/16/2 era incorrecto. `planillas` registra 15 modelos
concretos; `evaluaciones` declara 16 clases de modelo pero
`BaseFactorEvaluation` es abstracta, por lo que registra 15; `exportaciones`
registra 2. El roadmap quedó corregido a 15/15/2.

La suite combinada ya descubre 196 casos, pero aún falla por namespaces no
montados (2.9), templates no adaptados (2.10–2.11) y factories del módulo que
no proporcionan el email obligatorio de `CustomUser`. No se relajó ninguna
prueba; las 36 preexistentes siguen verdes. El aviso de 43 migraciones es de
la base SQLite en memoria nueva del proceso de servidor.

### Notas para el commit siguiente
Montar el URLconf con namespaces planos; esto debe eliminar la mayoría de los
`NoReverseMatch` de la suite combinada.

## Commit 2.9 — URLconf del módulo y montaje

| Campo | Valor |
|---|---|
| Fecha | 2026-08-03 00:55 |
| Repositorio | ergocapacitacion |
| Rama | `feature/ergonomia-886` |
| Hash | `61a6dbb` |
| Fase | 2 |
| Estado | ✅ Completado |

### Qué se hizo
Se creó el URLconf contenedor y se montaron los cuatro namespaces planos bajo
`/evaluacion-ergonomica/`. CF-1 mantiene Ergobot bajo `/ai/`. La prueba
focalizada expuso expectativas del origen incompatibles con el prefijo nuevo;
DA-2.9 documenta y acota su adaptación indispensable.

### Archivos modificados
- `apps/ergonomia_886/urls.py` — URLconf contenedor sin namespace propio.
- `config/urls.py` — montaje público del módulo.
- `apps/ergonomia_886/help_ai/tests.py` — rutas/ASGI, imports diferidos y fixture adaptados conforme DA-2.9.
- `docs/INTEGRACION_MODULO_ERGONOMIA_886_PROPUESTA_TECNICA.md` — DA-2.9 registrada.
- `README.md` — prefijos y CF-1 documentados.
- `docs/ROADMAP_INTEGRACION_ERGONOMIA_886.md` — avance y DA-2.9.
- `docs/BITACORA_INTEGRACION_886.md` — mapa literal 2.9.

### Verificaciones ejecutadas

```text
.venv/bin/python manage.py check
System check identified no issues (0 silenced).
.venv/bin/python manage.py check --settings=config.test_settings
System check identified no issues (0 silenced).
.venv/bin/python manage.py makemigrations --check --dry-run --settings=config.test_settings
No changes detected

planillas:crear_evaluacion                 -> /evaluacion-ergonomica/protocolo/crear/
planillas:detalle_evaluacion               -> /evaluacion-ergonomica/protocolo/1/
planillas:planilla1                        -> /evaluacion-ergonomica/protocolo/1/planilla1/
planillas:planilla2a                       -> /evaluacion-ergonomica/protocolo/1/planilla2a/
planillas:planilla4                        -> /evaluacion-ergonomica/protocolo/1/planilla4/
evaluaciones:lmc_form_by_eval              -> /evaluacion-ergonomica/factores/1/lmc/
evaluaciones:wizard_resumen_by_eval        -> /evaluacion-ergonomica/factores/1/resumen/
evaluaciones:start_factor                  -> /evaluacion-ergonomica/factores/start/1/lmc/
exportaciones:panel                        -> /evaluacion-ergonomica/documentos/1/
exportaciones:protocolo_completo           -> /evaluacion-ergonomica/documentos/1/oficial/protocolo-completo.pdf
exportaciones:paquete_zip                  -> /evaluacion-ergonomica/documentos/1/paquete.zip
help_ai:help_guide                         -> /evaluacion-ergonomica/ayuda/guide/lmc/
help_ai:chat_ai                            -> /evaluacion-ergonomica/ayuda/chat/lmc/

=== CF-1: los dos asistentes en prefijos distintos ===
  ergobot_ai : /ai/ergobot/ergonomia/stream/
  help_ai    : /evaluacion-ergonomica/ayuda/chat/lmc/

# Respuestas anónimas
GET /evaluacion-ergonomica/                                    -> 404
GET /evaluacion-ergonomica/protocolo/crear/                    -> 302
GET /evaluacion-ergonomica/factores/1/lmc/                     -> 302
GET /evaluacion-ergonomica/documentos/1/                       -> 302
GET /evaluacion-ergonomica/ayuda/guide/lmc/                    -> 401

# Suite preexistente
Ran 36 tests in 0.145s
OK
Found 36 test(s).
System check identified no issues (0 silenced).

# Suite help_ai tras DA-2.9
Ran 22 tests in 0.213s
FAILED (failures=2, errors=1)
Found 22 test(s).
System check identified no issues (0 silenced).
Pendientes: widget/base (2.10-2.11), CDN y cabecera CSP (Fase 6).

.venv/bin/python manage.py runserver 127.0.0.1:8027 --noreload --settings=config.test_settings
System check identified no issues (0 silenced).
Starting development server at http://127.0.0.1:8027/
GET / -> 200
GET /evaluacion-ergonomica/protocolo/crear/ -> 302
```

### Desvíos respecto del roadmap
DA-2.9 resuelve una incompatibilidad lógica: mantener aserciones `/ai/...`
obligaba a violar CF-1. Se cambiaron solo las dos expectativas de prefijo, la
expectativa ASGI del proyecto, trece targets de `patch` como imports diferidos
y el email obligatorio del fixture. Ningún caso, cuota ni aserción funcional
adicional cambió.

La raíz del módulo devuelve 404 deliberadamente hasta implementar el listado
en 3.6. Las otras rutas anónimas están protegidas y ninguna devuelve 500.

### Notas para el commit siguiente
Extraer el cuerpo del offcanvas a `_help_widget_body.html`, sin mover el bloque
`help_slug` fuera de la cadena de herencia.

## Commit 2.10 — Plantilla base del módulo y adaptación de 10 templates

| Campo | Valor |
|---|---|
| Fecha | 2026-08-03 00:59 |
| Repositorio | ergocapacitacion |
| Rama | `feature/ergonomia-886` |
| Hash | `c6f5fdd` |
| Fase | 2 |
| Estado | ✅ Completado |

### Qué se hizo
Se implementó la variante inline recomendada de `base_886.html`: el bloque
`help_slug` vive en la cadena de `{% extends %}` y el include queda limitado al
cuerpo del offcanvas. Se adaptaron los nueve templates trasplantados presentes;
el décimo, `core/dashboard.html`, continúa diferido al commit 3.6 como prescribe
el propio roadmap. Los 13 formularios de factor heredan del único base adaptado.

### Archivos modificados
- `templates/ergonomia_886/base_886.html` — base intermedia inline del módulo.
- `apps/ergonomia_886/planillas/templates/planillas/*.html` — seis templates adaptados.
- `apps/ergonomia_886/evaluaciones/templates/evaluaciones/factor_form_base.html` — base de 13 factores adaptada.
- `apps/ergonomia_886/evaluaciones/templates/evaluaciones/wizard_resumen.html` — resumen adaptado.
- `apps/ergonomia_886/exportaciones/templates/exportaciones/panel_exportacion.html` — panel adaptado.
- `apps/ergonomia_886/help_ai/tests.py` — lectura del widget trasladada de `base.html` a `base_886.html`.
- `README.md` — integración visual y alcance 9+1 documentados.
- `docs/ROADMAP_INTEGRACION_ERGONOMIA_886.md` — avance y criterios marcados.
- `docs/BITACORA_INTEGRACION_886.md` — evidencia literal 2.10.

### Verificaciones ejecutadas

```text
# Estructura de herencia
rg -l "extends ...ergonomia_886/base_886.html" apps/ergonomia_886/*/templates | wc -l
       9
rg -n "block help_slug" templates/ergonomia_886 apps/ergonomia_886/*/templates | wc -l
      23
rg -n "extends ...base_dashboard.html" apps/ergonomia_886/*/templates
# sin salida

.venv/bin/python manage.py check --settings=config.test_settings
System check identified no issues (0 silenced).
.venv/bin/python manage.py makemigrations --check --dry-run --settings=config.test_settings
No changes detected
.venv/bin/python manage.py shell --settings=config.test_settings -c "...get_template('ergonomia_886/base_886.html')..."
Template base_886: compilacion OK

# Suite preexistente aislada por sus nueve labels
Ran 36 tests in 0.142s
OK
Found 36 test(s).
System check identified no issues (0 silenced).

# Suite help_ai focalizada, después de trasladar su lectura a base_886.html
Ran 22 tests in 0.238s
FAILED (failures=1, errors=1)
Found 22 test(s).
System check identified no issues (0 silenced).
ERROR: test_dynamic_responses_apply_restrictive_csp
KeyError: 'content-security-policy'
FAIL: test_templates_do_not_depend_on_cdn_or_inline_event_handlers
AssertionError: 'cdn.jsdelivr.net' unexpectedly found
Pendientes planificados: cabecera CSP y retiro global de CDN en Fase 6.

.venv/bin/python manage.py runserver 127.0.0.1:8028 --noreload --settings=config.test_settings
System check identified no issues (0 silenced).
Starting development server at http://127.0.0.1:8028/
GET / -> 200
GET /evaluacion-ergonomica/protocolo/crear/ -> 302
```

### Desvíos respecto del roadmap
El título habla de diez templates, pero la tabla del mismo commit difiere
explícitamente `core/dashboard.html` a 3.6; por eso este commit adapta los nueve
archivos realmente copiados y preserva el décimo para su reimplantación.

La prueba de seguridad todavía leía el widget en el `templates/base.html` del
origen. Se actualizó únicamente esa ruta para acompañar el traslado arquitectónico
a `templates/ergonomia_886/base_886.html`; sus aserciones funcionales no cambiaron.

La primera ejecución con settings reales fue bloqueada por el sandbox al acceder
a PostgreSQL. La repetición autorizada ejecutó los 22 tests y luego detectó una
sesión ajena reteniendo `test_ergocapacitacion` durante el teardown. Las
verificaciones deterministas finales se aislaron con `config.test_settings`; no
hubo cambios de código para ocultar la incidencia.

### Notas para el commit siguiente
Crear `_help_widget_body.html` y validar el render completo del offcanvas; en
2.10 el include se deja deliberadamente preparado para ese paso inmediato.

## Commit 2.11 — Extraer el cuerpo del widget de ayuda contextual

| Campo | Valor |
|---|---|
| Fecha | 2026-08-03 01:02 |
| Repositorio | ergocapacitacion |
| Rama | `feature/ergonomia-886` |
| Hash | `3316dbe` |
| Fase | 2 |
| Estado | ✅ Completado |

### Qué se hizo
Se trasladó el cuerpo del offcanvas del origen a
`templates/ergonomia_886/_help_widget_body.html`. El contenedor, el slug y las
URLs permanecen en `base_886.html`; el parcial conserva el token CSRF y los IDs
que consume `help_widget.js`. CF-1 permanece explícita en el encabezado.

### Archivos modificados
- `templates/ergonomia_886/_help_widget_body.html` — cuerpo del widget de ayuda.
- `README.md` — extracción, CSRF, IDs y CF-1 registrados.
- `docs/ROADMAP_INTEGRACION_ERGONOMIA_886.md` — avance y criterios marcados.
- `docs/BITACORA_INTEGRACION_886.md` — hash 2.10 y evidencia literal 2.11.

### Verificaciones ejecutadas

```text
grep -n "csrf_token" templates/ergonomia_886/_help_widget_body.html
44:        {% csrf_token %}

rg -n "help_ai:help_guide|help_ai:chat_ai" templates/ergonomia_886/
templates/ergonomia_886/base_886.html:22: data-guide-url-template="{% url 'help_ai:help_guide' slug='__slug__' %}"
templates/ergonomia_886/base_886.html:23: data-chat-url-template="{% url 'help_ai:chat_ai' slug='__slug__' %}

helpToggle -> OK
helpWidget -> OK
helpTabs -> OK
tabGuide -> OK
chat-form -> OK
chat-input -> OK
chat-messages -> OK
chat-submit-btn -> OK
ai-typing-indicator -> OK

.venv/bin/python manage.py check --settings=config.test_settings
System check identified no issues (0 silenced).
.venv/bin/python manage.py makemigrations --check --dry-run --settings=config.test_settings
No changes detected

# Render de una plantilla hija real, con RequestFactory
Render widget: slug=lmc, csrf_token e IDs -> OK

# Suite preexistente aislada por sus nueve labels
Ran 36 tests in 0.144s
OK
Found 36 test(s).
System check identified no issues (0 silenced).

# Suite help_ai focalizada
Ran 22 tests in 0.216s
FAILED (failures=1, errors=1)
Found 22 test(s).
System check identified no issues (0 silenced).
ERROR: test_dynamic_responses_apply_restrictive_csp
KeyError: 'content-security-policy'
FAIL: test_templates_do_not_depend_on_cdn_or_inline_event_handlers
AssertionError: 'cdn.jsdelivr.net' unexpectedly found
Pendientes planificados: cabecera CSP y retiro global de CDN en Fase 6.

.venv/bin/python manage.py runserver 127.0.0.1:8029 --noreload --settings=config.test_settings
System check identified no issues (0 silenced).
Starting development server at http://127.0.0.1:8029/
GET / -> 200
GET /evaluacion-ergonomica/protocolo/crear/ -> 302
```

### Desvíos respecto del roadmap
Ninguno. Se tomó el texto recomendado del roadmap, que además traduce el
`aria-label` de cierre y mantiene la separación contenedor/cuerpo definida en
2.10. Los dos fallos focalizados no pertenecen a este commit y su estado no
cambió respecto del cierre anterior.

### Notas para el commit siguiente
Implementar los checks de sistema del módulo y hacer que validen rutas
declarativas, CF-1, CF-3 y CF-6 sin ejecutar lógica de negocio.

## Commit 2.12 — `checks.py`: validación de las 48 rutas declarativas

| Campo | Valor |
|---|---|
| Fecha | 2026-08-03 01:07 |
| Repositorio | ergocapacitacion |
| Rama | `feature/ergonomia-886` |
| Hash | `30e01d4` |
| Fase | 2 |
| Estado | ✅ Completado |

### Qué se hizo
Se registraron cuatro checks Django desde `PlanillasConfig.ready()`: resolución
de las 48 rutas declarativas, integridad y aprobación de los 13 artefactos
normativos (CF-3), integridad del PDF oficial (CF-6) y separación por imports
entre `help_ai` y `ergobot_ai` (CF-1). DA-2.12 corrige dos defectos del ejemplo
sin relajar sus condiciones.

### Archivos modificados
- `apps/ergonomia_886/checks.py` — cuatro checks de arranque.
- `apps/ergonomia_886/planillas/apps.py` — registro en `ready()`.
- `docs/INTEGRACION_MODULO_ERGONOMIA_886_PROPUESTA_TECNICA.md` — DA-2.12.
- `README.md` — guardarraíles CF-1, CF-3 y CF-6 registrados.
- `docs/ROADMAP_INTEGRACION_ERGONOMIA_886.md` — avance y criterios marcados.
- `docs/BITACORA_INTEGRACION_886.md` — hash 2.11 y evidencia literal 2.12.

### Verificaciones ejecutadas

```text
.venv/bin/python manage.py check --settings=config.test_settings
System check identified no issues (0 silenced).
.venv/bin/python manage.py makemigrations --check --dry-run --settings=config.test_settings
No changes detected

check_rutas_declarativas: 0 issues
check_artefactos_normativos: 0 issues
check_plantilla_oficial: 0 issues
check_cf1_asistentes_separados: 0 issues

Rutas: 26 + 12 + 9 + 1 paquete = 48
Artefactos normativos unicos: 13
bc0d0753943888779abd0936f6c4dc2e128766c7cf6370a4a2fb19073aad59f4  apps/ergonomia_886/exportaciones/official/templates_bin/res_srt_886_15-formulario.pdf

# Prueba negativa: LMC_Eval sustituido temporalmente por NO_EXISTE
EXIT_CODE=1
SystemCheckError: System check identified some issues:

ERRORS:
?: (ergonomia_886.E001) Ruta declarativa no resoluble: 'apps.ergonomia_886.evaluaciones.models.NO_EXISTE'
    HINT: Declarada en catalog:lmc.model_path. Verificar que el módulo y el símbolo existan tras el trasplante a apps.ergonomia_886.

System check identified 1 issue (0 silenced).

# Restauración verificada
.venv/bin/python manage.py check --settings=config.test_settings
System check identified no issues (0 silenced).
git diff -- apps/ergonomia_886/evaluaciones/catalog.py
# sin salida

# Suite preexistente aislada por sus nueve labels
Ran 36 tests in 0.221s
OK
Found 36 test(s).
System check identified no issues (0 silenced).

.venv/bin/python manage.py runserver 127.0.0.1:8030 --noreload --settings=config.test_settings
System check identified no issues (0 silenced).
Starting development server at http://127.0.0.1:8030/
GET / -> 200
GET /evaluacion-ergonomica/protocolo/crear/ -> 302
```

### Desvíos respecto del roadmap
DA-2.12: el recolector literal propuesto sumaba 47 rutas y omitía el paquete de
datos declarado dos veces en `calculators.py`; se agregó como una ruta única y
el total comprobado es 48. El escaneo textual CF-1 marcaba el comentario que
documenta CF-1 en `help_ai/apps.py`; se reemplazó por AST para inspeccionar
imports estáticos y `import_string()` literales, que son el acoplamiento
prohibido. Comentarios y documentación no producen falsos positivos.

### Notas para el commit siguiente
Aplicar el protocolo de migraciones completo, ejecutar la suite combinada y
realizar la prueba de humo autenticada que cierra la Fase 2.

## Commit 2.13 — Aplicar migraciones y prueba de humo

| Campo | Valor |
|---|---|
| Fecha | 2026-08-03 01:18 |
| Repositorio | ergocapacitacion |
| Rama | `feature/ergonomia-886` |
| Hash | `89b47f5` |
| Fase | 2 |
| Estado | ✅ Completado |

### Qué se hizo
Se revisaron y aplicaron las diez migraciones del módulo siguiendo el protocolo
de seis pasos. La suite combinada quedó en 196/196. El humo autenticado usó un
profesional existente, creó y ejercitó una evaluación dentro de una transacción
y confirmó rollback total. Se verificaron las diez pantallas, CF-1, CF-5 y CF-6.

DA-2.13 resolvió la contradicción por la que dos pruebas exigían desde esta fase
el CSP calendarizado en Fase 6. Se portó el middleware bloqueante mínimo, se
sirvió Bootstrap desde vendor local, se agregaron nonces a los cinco scripts
inline y se reemplazaron los tres handlers HTML. La extracción y observación
siguen perteneciendo a Fase 6.

### Archivos modificados
- `config/middleware.py`, `config/settings.py` — CSP mínimo y registro.
- `templates/base_dashboard.html`, `templates/base_landing.html` — vendor local.
- cinco templates preexistentes — nonce en scripts inline y listeners sin handlers HTML.
- cinco templates del módulo — referencias `core:dashboard` adaptadas.
- tests de `planillas`, `evaluaciones` y `exportaciones` — email obligatorio,
  rutas anidadas, targets diferidos y semántica `get_username()` del destino.
- `docs/INTEGRACION_MODULO_ERGONOMIA_886_PROPUESTA_TECNICA.md` — DA-2.13.
- `README.md`, roadmap y bitácora — cierre documentado de Fase 2.

### Verificaciones ejecutadas

```text
.venv/bin/python manage.py makemigrations --check --dry-run
No changes detected

.venv/bin/python manage.py showmigrations planillas evaluaciones exportaciones
planillas
 [ ] 0001_initial
evaluaciones
 [ ] 0001_initial
 [ ] 0002_alter_empujeinicial_eval_altura_agarre_cm_and_more
 [ ] 0003_transporte_eval_en_plano_horizontal_and_more
 [ ] 0004_bipedestacion_eval_brazos_elevados_and_more
 [ ] 0005_vibracionmb_eval_ax_mps2_vibracionmb_eval_ay_mps2_and_more
 [ ] 0006_vibracionce_eval_calc_details_and_more
 [ ] 0007_transporte_frecuencias_maximas
exportaciones
 [ ] 0001_initial
 [ ] 0002_generatedreport

# Base creada desde cero y criterio de aceptación
.venv/bin/python manage.py test --settings=config.test_settings -v 1
Creating test database for alias 'default'...
Found 196 test(s).
System check identified no issues (0 silenced).
Ran 196 tests in 1.528s
OK
Destroying test database for alias 'default'...

# Desglose exigido por la compuerta
.venv/bin/python manage.py test apps.ergonomia_886 --settings=config.test_settings -v 1
Ran 160 tests in 1.495s
OK
Found 160 test(s).
System check identified no issues (0 silenced).

.venv/bin/python manage.py test apps.accounts apps.certificates apps.company apps.dashboard apps.ergobot_ai apps.landing apps.presencial apps.quiz apps.training --settings=config.test_settings -v 1
Ran 36 tests in 0.143s
OK
Found 36 test(s).
System check identified no issues (0 silenced).

.venv/bin/python manage.py migrate --noinput
Operations to perform:
  Apply all migrations: accounts, admin, auth, certificates, company, contenttypes, evaluaciones, exportaciones, planillas, presencial, quiz, sessions, training
Running migrations:
  Applying planillas.0001_initial... OK
  Applying evaluaciones.0001_initial... OK
  Applying evaluaciones.0002_alter_empujeinicial_eval_altura_agarre_cm_and_more... OK
  Applying evaluaciones.0003_transporte_eval_en_plano_horizontal_and_more... OK
  Applying evaluaciones.0004_bipedestacion_eval_brazos_elevados_and_more... OK
  Applying evaluaciones.0005_vibracionmb_eval_ax_mps2_vibracionmb_eval_ay_mps2_and_more... OK
  Applying evaluaciones.0006_vibracionce_eval_calc_details_and_more... OK
  Applying evaluaciones.0007_transporte_frecuencias_maximas... OK
  Applying exportaciones.0001_initial... OK
  Applying exportaciones.0002_generatedreport... OK

.venv/bin/python manage.py createcachetable
Cache table 'ergosolutions_cache' already exists.

.venv/bin/python manage.py showmigrations planillas evaluaciones exportaciones
planillas
 [X] 0001_initial
evaluaciones
 [X] 0001_initial
 [X] 0002_alter_empujeinicial_eval_altura_agarre_cm_and_more
 [X] 0003_transporte_eval_en_plano_horizontal_and_more
 [X] 0004_bipedestacion_eval_brazos_elevados_and_more
 [X] 0005_vibracionmb_eval_ax_mps2_vibracionmb_eval_ay_mps2_and_more
 [X] 0006_vibracionce_eval_calc_details_and_more
 [X] 0007_transporte_frecuencias_maximas
exportaciones
 [X] 0001_initial
 [X] 0002_generatedreport

Usuarios profesionales disponibles: 21
Superusuarios activos: 1
System check identified no issues (0 silenced).
```

### Prueba de humo autenticada

```text
1 Crear evaluación GET             200 OK
1 Crear evaluación POST            302 OK
  guardado transaccional id=1; rollback al finalizar
2 Detalle                          200 OK
3 Planilla 1                       200 OK
  widget help_slug=planilla1 OK
4 Planilla 2A                      200 OK
5 Inicio factor LMC                302 OK
5 Factor LMC GET                   200 OK
5 Factor LMC calcular              302 OK
  nivel calculado por motor=bajo
6 Wizard 13 factores               200 OK
7 Panel documentos                 200 OK
8 Protocolo oficial                200 OK
  PDF 12 páginas Carta; guardado en /private/tmp/ergonomia-886-smoke-2.13.pdf
9 Detalle técnico LMC              200 OK
10 Paquete ZIP                     200 OK
  ZIP LEEME.txt + 2 PDF(s)
CF-5 Planilla 2E en blanco         200 OK
  CF-5 sin operaciones de superposición (ni marcas NO)
CF-1 widget help_ai                200 OK
CF-1 Ergobot docente SSE           200 OK
  prefijos separados y ambos endpoints responden
CSP bloqueante presente en la respuesta dinámica
ROLLBACK OK: evaluación temporal no persistida

Evaluaciones temporales persistidas: 0
No changes detected
System check identified no issues (0 silenced).
```

### Verificación visual CF-6
El PDF generado tiene 12 páginas con MediaBox 612×792 (Carta). La numeración
del roadmap usa índices de página: el índice 5 es la página visible 6 (Planilla
2E) y el índice 8 es la visible 9 (Planilla 2H).

| Evidencia | Resultado visual |
|---|---|
| Índice 5 · Planilla 2E | Escala de Borg íntegra, legible, valores 0–10 y firmas visibles |
| Índice 8 · Planilla 2H | Curva de Fanger íntegra, ejes, zonas, fuente y leyenda visibles |
| Documento completo | 12 páginas Carta, abre sin advertencias |

SHA-256 del PDF oficial fuente:
`bc0d0753943888779abd0936f6c4dc2e128766c7cf6370a4a2fb19073aad59f4`.

### Desvíos respecto del roadmap
La primera suite limpia expuso 26 errores y un fallo: emails obligatorios,
targets diferidos todavía planos, cinco URLs `core:dashboard` y las dos pruebas
de CSP. Se corrigieron rutas/fixtures conservando casos y aserciones. DA-2.13
adelanta el mínimo CSP porque la compuerta de 196 pruebas era incumplible de
otro modo; la Fase 6 es declaradamente independiente.

La referencia “página 5/8” es un índice cero-based de los mapas normativos. La
inspección inicial de páginas visibles 5/8 mostró correctamente 2D/2G; se
repitió sobre las páginas visibles 6/9 y allí se aprobaron Borg/Fanger.

### Notas para el commit siguiente
Fase 2 cerrada. Iniciar 3.1 con la FK protegida a `CompanyProfile`, preservar
los campos históricos y generar/revisar íntegramente la migración 0002.

## Commit 3.1 — `Evaluacion.empresa` y alineación de longitudes

| Campo | Valor |
|---|---|
| Fecha | 2026-08-03 01:22 |
| Repositorio | ergocapacitacion |
| Rama | `feature/ergonomia-886` |
| Hash | `c737c49` |
| Fase | 3 |
| Estado | ✅ Completado |

### Qué se hizo
Se agregó `Evaluacion.empresa`, FK nullable con `PROTECT` a `CompanyProfile`, y
se definió `related_name` para empresa y profesional. Los campos de respaldo
histórico se conservaron y ampliaron a razón social 300, CUIT 20 y dirección
400. Se generó, leyó íntegramente y aplicó la migración aditiva 0002.

### Archivos modificados
- `apps/ergonomia_886/planillas/models.py` — relación y snapshots ampliados.
- `apps/ergonomia_886/planillas/migrations/0002_evaluacion_empresa.py` — migración aditiva.
- `README.md` — decisión documental y longitudes registradas.
- `docs/ROADMAP_INTEGRACION_ERGONOMIA_886.md` — avance y criterios marcados.
- `docs/BITACORA_INTEGRACION_886.md` — hash 2.13 y evidencia literal 3.1.

### Verificaciones ejecutadas

```text
.venv/bin/python manage.py makemigrations planillas --name evaluacion_empresa --settings=config.test_settings
Migrations for 'planillas':
  apps/ergonomia_886/planillas/migrations/0002_evaluacion_empresa.py
    + Add field empresa to evaluacion
    ~ Alter field cuit on evaluacion
    ~ Alter field direccion_establecimiento on evaluacion
    ~ Alter field razon_social on evaluacion
    ~ Alter field usuario on evaluacion

.venv/bin/python manage.py makemigrations --check --dry-run --settings=config.test_settings
No changes detected

.venv/bin/python manage.py test --settings=config.test_settings -v 1
Creating test database for alias 'default'...
Found 196 test(s).
System check identified no issues (0 silenced).
Ran 196 tests in 1.689s
OK
Destroying test database for alias 'default'...

.venv/bin/python manage.py migrate --noinput
Operations to perform:
  Apply all migrations: accounts, admin, auth, certificates, company, contenttypes, evaluaciones, exportaciones, planillas, presencial, quiz, sessions, training
Running migrations:
  Applying planillas.0002_evaluacion_empresa... OK

.venv/bin/python manage.py migrate --check
.venv/bin/python manage.py makemigrations --check --dry-run
No changes detected
.venv/bin/python manage.py check
System check identified no issues (0 silenced).

.venv/bin/python manage.py runserver 127.0.0.1:8031 --noreload --settings=config.test_settings
System check identified no issues (0 silenced).
Starting development server at http://127.0.0.1:8031/
GET / -> 200
GET /evaluacion-ergonomica/protocolo/crear/ -> 302
```

### Desvíos respecto del roadmap
Django generó la dependencia contra la hoja actual de `company`,
`0004_create_contact_request`, en vez de la mínima `0001_create_company_profile`
anticipada por el roadmap. Se conservó el grafo producido por el autodetector:
la migración sigue siendo aditiva y el modelo objetivo existe desde 0001.

### Notas para el commit siguiente
Ampliar `CLAVES_PROHIBIDAS` antes de incorporar relaciones con trabajadores,
manteniendo CF-4 y `trace_include_sensitive_data=False`.

---

## Commit 3.2 — Ampliar `CLAVES_PROHIBIDAS` (CF-4)

| Campo | Valor |
|---|---|
| Fecha | 2026-08-03 01:26 |
| Repositorio | ergocapacitacion |
| Rama | `feature/ergonomia-886` |
| Hash | `f7f7ee8` |
| Fase | 3 |
| Estado | ✅ Completado |

### Qué se hizo
Se amplió de forma aditiva `CLAVES_PROHIBIDAS` con la superficie de datos
personales que introduce la integración: trabajadores, usuarios, empresas,
contactos e identificadores. Los serializadores documentan que la relación
`Planilla1.trabajadores` nunca debe incorporarse a un payload dirigido al
modelo. Se agregó una única prueba que verifica la eliminación recursiva tanto
de claves como de valores personales, sin modificar las 16 pruebas existentes.

### Archivos modificados
- `apps/ergonomia_886/exportaciones/reports/llm.py` — ampliación aditiva del saneamiento CF-4.
- `apps/ergonomia_886/exportaciones/serializers.py` — regla explícita sobre `Planilla1.trabajadores`.
- `apps/ergonomia_886/exportaciones/tests/test_reports_llm.py` — única prueba de regresión nueva.
- `README.md` — registro profesional del cambio.
- `docs/ROADMAP_INTEGRACION_ERGONOMIA_886.md` — avance y criterios marcados.
- `docs/BITACORA_INTEGRACION_886.md` — evidencia literal del commit 3.2.

### Verificaciones ejecutadas

```text
.venv/bin/python manage.py test apps.ergonomia_886.exportaciones --settings=config.test_settings -v 2
Found 93 test(s).
System check identified no issues (0 silenced).
Ran 93 tests in 1.057s
OK

.venv/bin/python manage.py test --settings=config.test_settings
Creating test database for alias 'default'...
Found 197 test(s).
System check identified no issues (0 silenced).
Ran 197 tests in 1.586s
OK
Destroying test database for alias 'default'...

.venv/bin/python manage.py check --settings=config.test_settings
System check identified no issues (0 silenced).

.venv/bin/python manage.py makemigrations --check --dry-run --settings=config.test_settings
No changes detected

rg -n 'trace_include_sensitive_data' apps/ergonomia_886/exportaciones/reports/llm.py
111:                trace_include_sensitive_data=False,

git diff -- apps/ergonomia_886/exportaciones/tests/test_reports_llm.py
@@ -2,6 +2,7 @@
 +import json
@@ -41,6 +42,59 @@ class SanitizacionTests(TestCase):
 +    def test_cf4_la_superficie_nueva_de_datos_personales_sale_saneada(self):
 +        ...
# El diff sólo agrega el import requerido y el método nuevo; ninguna línea de
# las 16 pruebas originales fue modificada.

.venv/bin/python manage.py runserver 127.0.0.1:8032 --noreload --settings=config.test_settings
System check identified no issues (0 silenced).
Starting development server at http://127.0.0.1:8032/
GET / -> 200
GET /evaluacion-ergonomica/protocolo/crear/ -> 302
```

### Desvíos respecto del roadmap
Ninguno. El cambio se aplicó antes de introducir la relación con trabajadores,
conservó literalmente las doce claves originales y mantuvo
`trace_include_sensitive_data=False`.

### Notas para el commit siguiente
Implementar la propiedad mixta de evaluaciones sin ampliar el alcance de datos
visible para profesionales ni empresas.

---

## Commit 3.3 — Propiedad mixta por tipo de usuario

| Campo | Valor |
|---|---|
| Fecha | 2026-08-03 01:32 |
| Repositorio | ergocapacitacion |
| Rama | `feature/ergonomia-886` |
| Hash | `58249e8` |
| Fase | 3 |
| Estado | ✅ Completado |

### Qué se hizo
Se centralizó la propiedad de evaluaciones en `planillas/querysets.py`. Un
profesional activo ve y edita sólo lo que creó; una empresa ve todas las
evaluaciones asociadas a su propio perfil, pero no edita; trainees, empresas
sin perfil y anónimos obtienen un queryset vacío. La resolución de recursos
continúa mediante 404 para impedir enumeración. Las vistas de planillas,
factores y exportaciones consumen el mismo criterio.

Se agregaron cinco casos directos para D-9. Las factorías heredadas que
representaban profesionales fueron corregidas con `user_type="professional"`;
no se cambió ninguna aserción ni objetivo de prueba.

### Archivos modificados
- `apps/ergonomia_886/planillas/querysets.py` — autoridad central de visibilidad y edición.
- `apps/ergonomia_886/planillas/views.py` — seis resoluciones migradas al helper.
- `apps/ergonomia_886/evaluaciones/views.py` — propiedad indirecta y bridge migrados.
- `apps/ergonomia_886/exportaciones/views.py` — mixin propietario migrado.
- `apps/ergonomia_886/planillas/tests_querysets.py` — cinco pruebas directas de D-9.
- `apps/ergonomia_886/planillas/tests.py` — fixture declarado profesional.
- `apps/ergonomia_886/evaluaciones/tests.py` — fixture declarado profesional.
- `apps/ergonomia_886/exportaciones/tests/test_permissions.py` — fixtures declarados profesionales; casos y aserciones intactos.
- `apps/ergonomia_886/exportaciones/tests/test_reports_llm.py` — fixtures del endpoint declarados profesionales.
- `README.md` — modelo de propiedad registrado.
- `docs/ROADMAP_INTEGRACION_ERGONOMIA_886.md` — avance, criterios y H-N registrados.
- `docs/INTEGRACION_MODULO_ERGONOMIA_886_PROPUESTA_TECNICA.md` — hallazgo H-N.
- `docs/BITACORA_INTEGRACION_886.md` — hash 3.2 y evidencia literal 3.3.

### Verificaciones ejecutadas

```text
# Primera ejecución, antes de corregir los tipos de fixture:
.venv/bin/python manage.py test apps.ergonomia_886.exportaciones.tests.test_permissions --settings=config.test_settings -v 2
Found 21 test(s).
Ran 21 tests in 0.092s
FAILED (failures=46, errors=3)
# Causa: create_user() sin user_type crea trainees en ErgoSolutions; D-9 los
# excluyó correctamente.

.venv/bin/python manage.py test apps.ergonomia_886.planillas.tests_querysets apps.ergonomia_886.exportaciones.tests.test_permissions --settings=config.test_settings -v 1
Creating test database for alias 'default'...
Ran 26 tests in 0.728s
OK
Destroying test database for alias 'default'...
Found 26 test(s).
System check identified no issues (0 silenced).

.venv/bin/python manage.py test --settings=config.test_settings -v 1
Creating test database for alias 'default'...
Ran 202 tests in 1.554s
OK
Destroying test database for alias 'default'...
Found 202 test(s).
System check identified no issues (0 silenced).

.venv/bin/python manage.py check --settings=config.test_settings
System check identified no issues (0 silenced).

.venv/bin/python manage.py makemigrations --check --dry-run --settings=config.test_settings
No changes detected

rg -n 'usuario=request\.user|usuario=self\.request\.user|evaluacion__usuario=' apps/ergonomia_886/*/views.py
apps/ergonomia_886/exportaciones/views.py:286:                usuario=request.user,
# Es el argumento del autor de GeneratedReport, no un filtro de propiedad.
# No queda ninguna de esas expresiones en get_object_or_404/filter de vistas.

.venv/bin/python manage.py shell --settings=config.test_settings -c '<smoke con Client>'
51 objects imported automatically (use -v 2 for details).

GET / -> 200
GET /evaluacion-ergonomica/protocolo/crear/ -> 302
```

### Desvíos respecto del roadmap
**H-N:** las pruebas trasplantadas creaban usuarios con el default de
`CustomUserManager.create_user`, que en ErgoSolutions es `trainee`. El roadmap
suponía que esos fixtures eran profesionales y exigía que permanecieran
literalmente intactos, una combinación incompatible con D-9. Se corrigió sólo
el tipo explícito de los fixtures profesionales; casos y aserciones quedaron
intactos. Además se añadieron cinco pruebas que demuestran empresa,
profesional, trainee, anónimo y empresa sin perfil.

El grep literal del roadmap conserva un falso positivo: `usuario=request.user`
es el autor enviado a `get_or_create_report`, no un filtro de propiedad. Se
revisó en contexto y se mantuvo porque sostiene la auditoría del informe.

### Notas para el commit siguiente
Aplicar la defensa de autenticación y rol en todas las vistas, conservando la
propiedad D-9 y separando consulta empresarial de edición profesional.

---

## Commit 3.4 — Decoradores en todas las vistas del módulo

| Campo | Valor |
|---|---|
| Fecha | 2026-08-03 10:30 |
| Repositorio | ergocapacitacion |
| Rama | `feature/ergonomia-886` |
| Hash | `44dd342` |
| Fase | 3 |
| Estado | ✅ Completado |

### Qué se hizo
Se aplicó `login_required` como defensa exterior y `backoffice_required` como
control interior a las doce vistas funcionales de planillas. Las vistas de
factores, resumen, inicio y exportación ya heredaban `LoginRequiredMixin` y se
conservaron. La guía contextual ahora redirige anónimos antes de leer contenido.
Se agregó una regresión que recorre doce rutas del módulo contra HTTP 500.

### Archivos modificados
- `apps/ergonomia_886/planillas/views.py` — decoradores en las vistas funcionales.
- `apps/ergonomia_886/help_ai/views.py` — `login_required` en la guía.
- `apps/ergonomia_886/planillas/tests_permisos.py` — regresión N1 sobre doce rutas.
- `README.md` — defensa de acceso registrada.
- `docs/ROADMAP_INTEGRACION_ERGONOMIA_886.md` — avance y criterios marcados.
- `docs/INTEGRACION_MODULO_ERGONOMIA_886_PROPUESTA_TECNICA.md` — hallazgo H-O.
- `docs/BITACORA_INTEGRACION_886.md` — hash 3.3 y evidencia literal 3.4.

### Verificaciones ejecutadas

```text
.venv/bin/python manage.py test apps.ergonomia_886.planillas.tests_permisos --settings=config.test_settings -v 2
Found 1 test(s).
test_ninguna_ruta_del_modulo_devuelve_500_a_un_anonimo ... ok
Ran 1 test in 0.016s
OK
System check identified no issues (0 silenced).

.venv/bin/python manage.py test apps.ergonomia_886.help_ai apps.ergonomia_886.planillas.tests_permisos --settings=config.test_settings -v 1
Creating test database for alias 'default'...
Ran 23 tests in 0.214s
OK
Destroying test database for alias 'default'...
Found 23 test(s).
System check identified no issues (0 silenced).

.venv/bin/python manage.py test --settings=config.test_settings -v 1
Creating test database for alias 'default'...
Ran 203 tests in 1.660s
OK
Destroying test database for alias 'default'...
Found 203 test(s).
System check identified no issues (0 silenced).

.venv/bin/python manage.py check --settings=config.test_settings
System check identified no issues (0 silenced).
.venv/bin/python manage.py makemigrations --check --dry-run --settings=config.test_settings
No changes detected

.venv/bin/python manage.py shell --settings=config.test_settings -c '<smoke con Client>'
51 objects imported automatically (use -v 2 for details).

GET / -> 200
GET crear -> 302
GET guide -> 302
POST chat -> 401
```

### Desvíos respecto del roadmap
**H-O:** el roadmap proponía decorar también el chat async, pero el decorador
de rol existente es síncrono y la prueba vinculante exige conservar HTTP 401
para anónimos. Se mantuvo la validación autenticada propia del chat y no se
modificó ninguna de las 22 pruebas de `help_ai`. `guide_view` sí incorporó la
redirección previa. La referencia a una función independiente `review_factor`
tampoco aplica: la revisión real vive en `WizardResumenView.post`, ya protegida
por `LoginRequiredMixin`.

### Notas para el commit siguiente
Incorporar el selector de empresa y el poblado no destructivo exigido por CF-5.

---

## Commit 3.5 — Formulario de creación con selector de empresa (CF-5)

| Campo | Valor |
|---|---|
| Fecha | 2026-08-03 10:33 |
| Repositorio | ergocapacitacion |
| Rama | `feature/ergonomia-886` |
| Hash | `pendiente` |
| Fase | 3 |
| Estado | ✅ Completado |

### Qué se hizo
`EvaluacionForm` permite elegir una empresa activa o mantener una carga manual.
Al crear, los snapshots vacíos se proponen desde `CompanyProfile`; cualquier
valor escrito gana. Para un usuario empresa, el selector queda limitado y
deshabilitado sobre su propio perfil. La vista inyecta al usuario y delega la
asignación del responsable al formulario.

### Archivos modificados
- `apps/ergonomia_886/planillas/forms.py` — selector, validación y poblado CF-5.
- `apps/ergonomia_886/planillas/views.py` — formulario contextualizado con usuario.
- `apps/ergonomia_886/planillas/tests_forms.py` — tres regresiones de snapshots y alcance.
- `README.md` — comportamiento documental registrado.
- `docs/ROADMAP_INTEGRACION_ERGONOMIA_886.md` — avance y criterios marcados.
- `docs/INTEGRACION_MODULO_ERGONOMIA_886_PROPUESTA_TECNICA.md` — hallazgo H-P.
- `docs/BITACORA_INTEGRACION_886.md` — hash 3.4 y evidencia literal 3.5.

### Verificaciones ejecutadas

```text
.venv/bin/python manage.py test apps.ergonomia_886.planillas --settings=config.test_settings -v 2
Found 10 test(s).
test_cf5_el_poblado_no_sobrescribe_lo_que_el_profesional_tipeo ... ok
test_company_solo_puede_seleccionar_su_propia_empresa ... ok
test_el_poblado_no_resincroniza_al_editar ... ok
Ran 10 tests in 0.065s
OK
System check identified no issues (0 silenced).

.venv/bin/python manage.py test --settings=config.test_settings -v 1
Creating test database for alias 'default'...
Ran 206 tests in 1.571s
OK
Destroying test database for alias 'default'...
Found 206 test(s).
System check identified no issues (0 silenced).

.venv/bin/python manage.py check --settings=config.test_settings
System check identified no issues (0 silenced).
.venv/bin/python manage.py makemigrations --check --dry-run --settings=config.test_settings
No changes detected
```

### Desvíos respecto del roadmap
**H-P:** el ejemplo poblaba en `save()`, pero los snapshots `blank=False` hacen
que `is_valid()` rechace primero los vacíos. Se completan de forma no
destructiva en `clean()` antes de validar el modelo y se conserva `save()` como
segunda defensa. Sin empresa, los cuatro campos siguen siendo obligatorios.

### Notas para el commit siguiente
Reimplantar el listado completo con propiedad mixta, filtros, orden seguro y
paginación sin degradar la consulta original.
