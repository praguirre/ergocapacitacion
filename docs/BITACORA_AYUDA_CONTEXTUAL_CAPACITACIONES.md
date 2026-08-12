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

---

## Commit 1.1 — Crear la app y registrarla con `label` propio

| Campo | Valor |
|---|---|
| Fecha | 2026-08-12 |
| Rama | feat/ayuda-contextual-capacitaciones |
| Hash | (se completa después del commit) |
| Fase | 1 |
| Estado | ⚠️ Completado con desvíos |

### Qué se hizo

Se creó el paquete de la app con su `AppConfig` y se la dio de alta en `LOCAL_APPS`,
inmediatamente después de `"apps.training"`. El `AppConfig` declara
`label = "capacitaciones_help_ai"` (CV-1), sin lo cual Django aborta el arranque con
`Application labels aren't unique, duplicates: help_ai`. Conforme al aviso del roadmap, el
método `ready()` se difiere al commit 4.4: `checks.py` todavía no existe y su import
produciría `ModuleNotFoundError` en el arranque.

### Archivos creados o modificados

- `apps/training/help_ai/__init__.py` — creado, vacío.
- `apps/training/help_ai/apps.py` — creado, con el `label` explícito y sin `ready()`.
- `config/settings.py` — alta de `"apps.training.help_ai"` en `LOCAL_APPS`.

### Verificaciones ejecutadas

```
$ .venv/bin/python manage.py check
System check identified no issues (0 silenced).

$ .venv/bin/python manage.py shell -c "…"
name  = apps.training.help_ai
label = capacitaciones_help_ai
verbose = Capacitaciones · Ayuda contextual
886 label = apps.ergonomia_886.help_ai

$ .venv/bin/python manage.py test --settings=config.test_settings
Ran 354 tests in 5.004s
OK

$ .venv/bin/python manage.py test apps.ergonomia_886.help_ai --settings=config.test_settings
Ran 52 tests in 0.405s
OK

$ .venv/bin/python manage.py makemigrations --check --dry-run
No changes detected
```

### Desvíos respecto del roadmap

**Hallazgo nuevo, no previsto por el roadmap ni por la PROPUESTA: existe una restricción
textual sobre `apps/training/`.**

Al copiar el docstring de `apps.py` tal como lo declara §8.3.2 de la PROPUESTA, la suite
completa pasó de 354 en verde a **354 con 1 fallo**:

```
FAIL: test_apps_training_no_importa_el_modulo_886
      (apps.ergonomia_886.evaluaciones.tests_sugerencias.SugerenciasCapacitacionTests)
AssertionError: 'apps.ergonomia_886' unexpectedly found in '…'
```

La prueba, preexistente y ajena a este trabajo, hace esto:

```python
training_dir = Path(settings.BASE_DIR) / "apps" / "training"
fuentes = "\n".join(
    path.read_text(encoding="utf-8")
    for path in training_dir.rglob("*.py")
    if "migrations" not in path.parts and not path.name.startswith("test")
)
self.assertNotIn("apps.ergonomia_886", fuentes)
```

Es un barrido **de texto plano**, no un análisis por AST: prohíbe la ruta punteada del
módulo 886 en cualquier archivo `.py` de `apps/training/`, **incluso dentro de un comentario
o de una cadena de documentación**. La PROPUESTA escribe esa ruta en los docstrings de
`apps.py`, `agents.py`, `limits.py` y `checks.py`, y además en la tupla `PROHIBIDOS` de
`checks.py`.

**Resolución adoptada (R-7 — gana la realidad).** No se toca la prueba del 886: R-11 sólo
autoriza una excepción, la del commit 5.1. Se adapta el código propio, que es lo que está
bajo nuestro control:

1. En comentarios y docstrings se nombra al módulo **en prosa** («el paquete de ayuda del
   módulo 886», «el asistente docente») en lugar de su ruta punteada.
2. En `checks.py` (commit 4.4) la tupla `PROHIBIDOS` se construirá en tiempo de ejecución
   —anteponiendo el prefijo `apps.` a los nombres de paquete— de modo que la cadena
   prohibida no aparezca literal en el archivo. La semántica del chequeo no cambia.
3. `apps/training/help_ai/tests.py` queda **fuera** del barrido, porque el filtro excluye los
   archivos cuyo nombre empieza con `test`. La prueba de leases independientes del commit 7.3
   puede importar del módulo 886 sin conflicto.

La restricción es **más estricta** que CV-4, no contradictoria: CV-4 prohíbe los imports
reales, y esta prueba prohíbe además la mención literal. Cumplir las dos es posible y es lo
que se hace. La regla quedó documentada en el propio docstring de `apps.py` para que el
próximo que edite el paquete no la vuelva a pisar.

Tras la corrección: suite completa **354 en verde**, 886 **52 en verde**.

### Notas para el commit siguiente

**Vigente para todos los commits de código de esta app:** ningún archivo `.py` de
`apps/training/` que no sea de prueba puede contener la ruta punteada completa del módulo
886. Afecta en particular a `agents.py` (3.3), `limits.py` (4.1) y `checks.py` (4.4), cuyos
bloques en la PROPUESTA la incluyen en sus comentarios.

---

## Commit 1.2 — Catálogo de pantallas y fichas de pantalla

| Campo | Valor |
|---|---|
| Fecha | 2026-08-12 |
| Rama | feat/ayuda-contextual-capacitaciones |
| Hash | (se completa después del commit) |
| Fase | 1 |
| Estado | ✅ Completado |

### Qué se hizo

Se declaró el conjunto cerrado de slugs habilitados (`catalog.py`) y la ficha humana de cada
pantalla (`pages.py`): título, ruta y propósito. Son las dos primeras patas del contrato del
slug. El slug identifica una **pantalla**, no un módulo de capacitación (DA-7 / CV-6): por
eso el catálogo vive en el código y no en la base de datos.

### Archivos creados o modificados

- `apps/training/help_ai/catalog.py` — 2 slugs globales, 4 partes del maestro, 8 slugs de
  pantalla y el registro `MODULOS_CON_FICHA`, que sólo contiene `ergonomia`.
- `apps/training/help_ai/pages.py` — 8 fichas `PageInfo` y la función `page_info()`, que
  falla cerrado con `KeyError`.

### Verificaciones ejecutadas

```
$ .venv/bin/python manage.py shell -c "…"
slugs del catálogo : 8
fichas declaradas  : 8
sin ficha          : []
ficha sin slug     : []
OK: todas las fichas son válidas
OK: page_info falla cerrado
MODULOS_CON_FICHA  : ['ergonomia']

$ .venv/bin/python manage.py check
System check identified no issues (0 silenced).

$ .venv/bin/python manage.py test --settings=config.test_settings
Ran 354 tests in 4.789s
OK

$ .venv/bin/python manage.py test apps.ergonomia_886.help_ai --settings=config.test_settings
Ran 52 tests in 0.382s
OK

$ .venv/bin/python manage.py makemigrations --check --dry-run
No changes detected
```

Las rutas de las 8 fichas se verificaron contra la expresión `/\d+/`: ninguna contiene un
identificador numérico concreto. Los tramos variables se declaran como `<modulo>` y `<id>`,
para que el prompt no afirme un identificador que el modelo no conoce.

### Desvíos respecto del roadmap

Ninguno. Los dos bloques se copiaron íntegros de §8.3.3 y §8.3.4 de la PROPUESTA; ninguno
contiene la ruta punteada del módulo 886, de modo que la restricción registrada en el commit
1.1 no los afecta.

### Notas para el commit siguiente

`MODULOS_CON_FICHA` ya declara `ergonomia` desde este commit. El documento
`modulo_ergonomia.md` que respalda esa entrada llega recién en el commit 2.4; hasta entonces
`documentos_modulo("ergonomia")` devuelve un nombre de archivo que todavía no existe. No es
un problema: nada lo lee hasta la Fase 3.
