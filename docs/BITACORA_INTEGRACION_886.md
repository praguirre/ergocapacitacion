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
| Hash | Se completa después del commit |
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
