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
| Hash | Se completa después del commit |
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
