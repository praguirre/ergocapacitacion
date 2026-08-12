# Bitácora — Ayuda contextual del área de Capacitaciones

**Roadmap:** `docs/ROADMAP_AYUDA_CONTEXTUAL_CAPACITACIONES.md`
**Diseño:** `docs/AUDITORIA_Y_PROPUESTA_AYUDA_CONTEXTUAL_CAPACITACIONES_2026-08-12.md`
**Inicio:** 2026-08-12
**Ejecutor:** Asistente IA de desarrollo
**Titular:** Pablo R. Aguirre
**Rama:** `feat/ayuda-contextual-capacitaciones`

---

## Estado de partida verificado

| Medición | Resultado |
|---|---|
| Commit base | `4187b10` |
| Rama base | codex/beta-feedback |
| `manage.py check` | System check identified no issues (0 silenced). |
| Suite completa | Ran 354 tests — OK |
| Suite `help_ai` (886) | Ran 52 tests — OK |
| Migraciones pendientes | No changes detected |
| Árbol de trabajo | Con dos archivos sin trackear: los dos documentos de este trabajo |

Salida literal de las verificaciones:

```
$ git rev-parse --short HEAD
4187b10

$ git branch --show-current
codex/beta-feedback

$ git status --short
?? docs/AUDITORIA_Y_PROPUESTA_AYUDA_CONTEXTUAL_CAPACITACIONES_2026-08-12.md
?? docs/ROADMAP_AYUDA_CONTEXTUAL_CAPACITACIONES.md

$ .venv/bin/python manage.py check
System check identified no issues (0 silenced).

$ .venv/bin/python manage.py test --settings=config.test_settings
Ran 354 tests in 5.142s
OK

$ .venv/bin/python manage.py test apps.ergonomia_886.help_ai --settings=config.test_settings
Ran 52 tests in 0.395s
OK

$ .venv/bin/python manage.py makemigrations --check --dry-run
No changes detected
```

**Desvío respecto de §0.6 del roadmap:** `git status --short` no estaba vacío. Las dos
entradas sin trackear son el roadmap y la PROPUESTA de este mismo trabajo, entregados junto
con el encargo. No son cambios ajenos de código: viajan con la rama y se incorporan en el
commit 0.0. Todas las demás mediciones coinciden exactamente con la línea base declarada.

**Línea base adoptada:** 354 pruebas totales · 52 pruebas de `apps.ergonomia_886.help_ai` ·
0 migraciones pendientes.

---

## Registro de commits

<!-- Cada commit agrega su entrada acá, en orden cronológico -->

## Commit 0.0 — Crear rama de trabajo y bitácora

| Campo | Valor |
|---|---|
| Fecha | 2026-08-12 |
| Rama | feat/ayuda-contextual-capacitaciones |
| Hash | `c59fa8e` |
| Fase | 0 |
| Estado | ✅ Completado |

### Qué se hizo

Se reprodujo el estado de partida de §0.6 del roadmap sobre el commit `4187b10` de
`codex/beta-feedback`, se abrió la rama de trabajo `feat/ayuda-contextual-capacitaciones` y
se creó esta bitácora con la salida literal de las verificaciones. Se abrió además la
sección del trabajo en el `README.md`.

### Archivos creados o modificados

- `docs/BITACORA_AYUDA_CONTEXTUAL_CAPACITACIONES.md` — creado, con el estado de partida.
- `docs/ROADMAP_AYUDA_CONTEXTUAL_CAPACITACIONES.md` — incorporado al control de versiones;
  commit 0.0 marcado ✅ en la tabla de §0.9.
- `docs/AUDITORIA_Y_PROPUESTA_AYUDA_CONTEXTUAL_CAPACITACIONES_2026-08-12.md` — incorporado
  al control de versiones.
- `README.md` — se abrió la sección «Ayuda contextual del área de Capacitaciones».

### Verificaciones ejecutadas

```
$ git branch --show-current
feat/ayuda-contextual-capacitaciones

$ .venv/bin/python manage.py check
System check identified no issues (0 silenced).

$ .venv/bin/python manage.py test --settings=config.test_settings
Ran 354 tests in 5.142s
OK

$ .venv/bin/python manage.py test apps.ergonomia_886.help_ai --settings=config.test_settings
Ran 52 tests in 0.395s
OK

$ .venv/bin/python manage.py makemigrations --check --dry-run
No changes detected
```

### Desvíos respecto del roadmap

El árbol de trabajo no estaba limpio al empezar: los dos documentos del encargo estaban sin
trackear. Conforme al aviso del Paso 1 del commit 0.0, no se aborta: se registran y se
incorporan a la rama. Ningún otro desvío.

### Notas para el commit siguiente

El commit 1.1 debe escribir `apps.py` **sin** el método `ready()`; se agrega recién en el
commit 4.4, junto con `checks.py`. Incluirlo antes produce `ModuleNotFoundError` en el
arranque.

---

## Commit 0.1 — Crear la estructura de directorios

| Campo | Valor |
|---|---|
| Fecha | 2026-08-12 |
| Rama | feat/ayuda-contextual-capacitaciones |
| Hash | (se completa después del commit) |
| Fase | 0 |
| Estado | ⚠️ Completado con desvíos |

### Qué se hizo

Se crearon los tres directorios donde vivirán la app, las plantillas y el corpus, y se
confirmó que ninguno colisiona con estructuras existentes. Git no versiona directorios
vacíos, de modo que este commit lleva únicamente documentación: deja constancia del punto de
partida estructural.

### Archivos creados o modificados

- `apps/training/help_ai/` — directorio creado (vacío por ahora; se puebla en el commit 1.1).
- `templates/capacitaciones/` — directorio creado (se puebla en el commit 5.2).
- `static/ayuda/capacitaciones/help_texts/` — directorio creado (se puebla en la Fase 2).
- `docs/BITACORA_AYUDA_CONTEXTUAL_CAPACITACIONES.md` — entrada del commit 0.1.
- `docs/ROADMAP_AYUDA_CONTEXTUAL_CAPACITACIONES.md` — commit 0.1 marcado ✅.
- `README.md` — registro del cambio.

### Verificaciones ejecutadas

```
$ ls -1 apps/training/
__init__.py
__pycache__
admin.py
apps.py
attribution.py
content
fixtures
help_ai          ← nuevo
management
migrations
models.py
tests.py
urls.py
urls_public.py
views.py
views_public.py

$ ls -1 templates/
accounts
base.html
base_contextual_help.html
base_dashboard.html
base_landing.html
capacitaciones   ← nuevo
company
dashboard
ergonomia_886
feedback
includes
landing
presencial
quiz
training

$ ls -1 static/ayuda/
capacitaciones   ← nuevo
css
help_texts
js

$ ls -1 static/ayuda/help_texts/ | wc -l
50

$ .venv/bin/python manage.py check
System check identified no issues (0 silenced).

$ .venv/bin/python manage.py test --settings=config.test_settings
Ran 354 tests in 5.093s
OK

$ .venv/bin/python manage.py makemigrations --check --dry-run
No changes detected
```

### Desvíos respecto del roadmap

**Cantidad de documentos del corpus del 886.** §0.6 y la verificación del commit 0.1 dan por
sentado que `static/ayuda/help_texts/` contiene **51** documentos. El conteo real es **50**
archivos, todos `.md`. Es una diferencia en el dato declarado del estado de partida, no un
cambio producido por este trabajo: el directorio del 886 no fue tocado (CV-3). Conforme a
R-7 se registra y se adopta **50** como el número real a preservar en las verificaciones
posteriores.

### Notas para el commit siguiente

Sin novedad. El commit 1.1 crea `__init__.py` y `apps.py` (sin `ready()`) y da de alta la app
en `LOCAL_APPS`, inmediatamente después de `"apps.training"`.
