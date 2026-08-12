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
| Hash | `177099b` |
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
| Hash | `4f34746` |
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
| Hash | `04a2430` |
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

---

## Commit 1.3 — Perfiles de composición del contexto

| Campo | Valor |
|---|---|
| Fecha | 2026-08-12 |
| Rama | feat/ayuda-contextual-capacitaciones |
| Hash | (se completa después del commit) |
| Fase | 1 |
| Estado | ✅ Completado |

### Qué se hizo

Se declaró qué documentos globales recibe cada pantalla (`profiles.py`), con la regla de
degradación que garantiza que un olvido cueste tokens y no calidad: un slug sin perfil recibe
el documento global **completo**, nunca menos contexto del que le corresponde.

### Archivos creados o modificados

- `apps/training/help_ai/profiles.py` — `NUCLEO`, `ANEXOS` (8 perfiles), `GLOBAL_COMPLETO`,
  `documentos_globales()` y `documentos_modulo()`.

### Verificaciones ejecutadas

Composición efectiva, verificada pantalla por pantalla:

```
slugs sin perfil declarado: []

home                       -> ('guia_capacitaciones_usuario', 'guia_capacitaciones_nucleo')
capacitaciones_menu        -> ('guia_capacitaciones_usuario', 'guia_capacitaciones_nucleo')
modalidad_selector         -> ('guia_capacitaciones_usuario', 'guia_capacitaciones_nucleo', 'anexo_modalidades')
online_links               -> ('guia_capacitaciones_usuario', 'guia_capacitaciones_nucleo', 'anexo_modalidades', 'anexo_online')
share_link                 -> ('guia_capacitaciones_usuario', 'guia_capacitaciones_nucleo', 'anexo_modalidades', 'anexo_online')
presencial_capacitacion    -> ('guia_capacitaciones_usuario', 'guia_capacitaciones_nucleo', 'anexo_modalidades', 'anexo_presencial')
presencial_quiz            -> ('guia_capacitaciones_usuario', 'guia_capacitaciones_nucleo', 'anexo_modalidades', 'anexo_presencial')
presencial_historial       -> ('guia_capacitaciones_usuario', 'guia_capacitaciones_nucleo', 'anexo_presencial')

degradación  : ('guia_capacitaciones_usuario', 'guia_capacitaciones_general')
modulo None  : ()
modulo vacio : ()
modulo raro  : ()
modulo real  : ('modulo_ergonomia',)
```

La tabla coincide exactamente con la estructura de control del Paso 1 del commit 1.3 del
roadmap.

```
$ .venv/bin/python manage.py check
System check identified no issues (0 silenced).

$ .venv/bin/python manage.py test --settings=config.test_settings
Ran 354 tests in 4.829s
OK

$ .venv/bin/python manage.py test apps.ergonomia_886.help_ai --settings=config.test_settings
Ran 52 tests in 0.386s
OK

$ .venv/bin/python manage.py makemigrations --check --dry-run
No changes detected
```

### Desvíos respecto del roadmap

Ninguno. El bloque se copió íntegro de §8.3.5 de la PROPUESTA.

### Notas para el commit siguiente

Con la Fase 1 cerrada, el contrato del slug tiene sus tres patas de código —catálogo, ficha y
perfil—. Falta la cuarta: el archivo `.md` de cada slug, que es toda la Fase 2. Hasta que
esos archivos existan, `documentos_globales()` devuelve nombres que aún no resuelven a
ningún archivo; es esperable, porque la lógica de composición no lee el disco.

---

## Commit 2.1 — Documentos globales del núcleo

| Campo | Valor |
|---|---|
| Fecha | 2026-08-12 |
| Rama | feat/ayuda-contextual-capacitaciones |
| Hash | (se completa después del commit) |
| Fase | 2 |
| Estado | ✅ Completado |

### Qué se hizo

Se escribieron los dos documentos que reciben **todas** las pantallas: la guía general del
área —qué es, los dos circuitos, el recorrido típico, qué queda registrado, qué NO hace el
área y el canal de feedback de la beta— y el glosario de conceptos operativos, con las reglas
exactas del quiz en cada modalidad (3 intentos y 8/10 en online; sin límite y sin certificado
en presencial).

Ambos van en `static/ayuda/capacitaciones/help_texts/`, el directorio propio del área (CV-3).
El corpus del módulo 886, en `static/ayuda/help_texts/`, no se tocó.

### Archivos creados o modificados

- `static/ayuda/capacitaciones/help_texts/guia_capacitaciones_usuario.md` — 3.290 bytes.
- `static/ayuda/capacitaciones/help_texts/guia_capacitaciones_nucleo.md` — 2.447 bytes.

### Verificaciones ejecutadas

```
$ wc -c guia_capacitaciones_usuario.md guia_capacitaciones_nucleo.md
    3290 guia_capacitaciones_usuario.md
    2447 guia_capacitaciones_nucleo.md
    5737 total

$ tail -c 1 guia_capacitaciones_nucleo.md | xxd | tail -1
00000000: 0a                                       .

$ grep -nE '<patrones de CV-5>' *.md
✅ CV-5 OK

$ .venv/bin/python manage.py check
System check identified no issues (0 silenced).

$ .venv/bin/python manage.py test --settings=config.test_settings
Ran 354 tests in 4.634s
OK

$ .venv/bin/python manage.py test apps.ergonomia_886.help_ai --settings=config.test_settings
Ran 52 tests in 0.372s
OK

$ .venv/bin/python manage.py makemigrations --check --dry-run
No changes detected
```

`guia_capacitaciones_nucleo.md` termina en `0a`, el salto de línea que exige la concatenación
del commit 2.2: sin él, el título de `anexo_modalidades.md` quedaría pegado al último párrafo
del glosario.

**CV-5 verificada:** el corpus no contiene direcciones de correo, CUIT, ni referencias a
`custom_notes` o `company_name_custom`. Los documentos se escribieron asumiendo lectura
pública, porque `/static/` se sirve sin autenticación (H-11).

### Desvíos respecto del roadmap

Ninguno. Los dos documentos se copiaron íntegros de §8.4.1 y §8.4.2 de la PROPUESTA.

### Notas para el commit siguiente

El commit 2.2 **genera** `guia_capacitaciones_general.md` por concatenación; no se escribe a
mano. El orden es exactamente el de `PARTES_DEL_GLOBAL` en `catalog.py`: núcleo, modalidades,
online, presencial.

---

## Commit 2.2 — Anexos temáticos y documento maestro

| Campo | Valor |
|---|---|
| Fecha | 2026-08-12 |
| Rama | feat/ayuda-contextual-capacitaciones |
| Hash | (se completa después del commit) |
| Fase | 2 |
| Estado | ✅ Completado |

### Qué se hizo

Se escribieron los tres anexos temáticos que se suman al núcleo según la pantalla, y se
**generó** el documento maestro por concatenación literal de las cuatro partes, en el orden
declarado por `PARTES_DEL_GLOBAL`. El maestro no se escribe a mano: si maestro y partes
divergieran, el respaldo de degradación entregaría un texto distinto del que reciben las
pantallas con perfil, y la prueba de partición del commit 7.1 lo detectaría sin explicar por
qué.

### Archivos creados o modificados

- `static/ayuda/capacitaciones/help_texts/anexo_modalidades.md` — 1.428 bytes.
- `static/ayuda/capacitaciones/help_texts/anexo_online.md` — 1.687 bytes.
- `static/ayuda/capacitaciones/help_texts/anexo_presencial.md` — 1.644 bytes.
- `static/ayuda/capacitaciones/help_texts/guia_capacitaciones_general.md` — 7.206 bytes,
  **generado** por `cat`, no escrito a mano.

### Verificaciones ejecutadas

```
$ for f in anexo_modalidades anexo_online anexo_presencial; do tail -c 1 $f.md | xxd -p; done
anexo_modalidades: 0a
anexo_online: 0a
anexo_presencial: 0a

$ cat guia_capacitaciones_nucleo.md anexo_modalidades.md anexo_online.md anexo_presencial.md \
    > guia_capacitaciones_general.md

$ cat guia_capacitaciones_nucleo.md anexo_modalidades.md anexo_online.md anexo_presencial.md \
    | diff - guia_capacitaciones_general.md && echo "✅ PARTICIÓN OK"
✅ PARTICIÓN OK

$ grep -nE '<patrones de CV-5>' *.md
✅ CV-5 OK

$ wc -c *.md
    1428 anexo_modalidades.md
    1687 anexo_online.md
    1644 anexo_presencial.md
    7206 guia_capacitaciones_general.md
    2447 guia_capacitaciones_nucleo.md
    3290 guia_capacitaciones_usuario.md
   17702 total
```

Tamaño del contexto global efectivo por pantalla, ya resolviendo archivos reales:

```
home                     2 documentos,   5737 bytes
online_links             4 documentos,   8852 bytes
presencial_quiz          4 documentos,   8809 bytes
```

Entre 5,7 KB y 8,9 KB: dentro del rango razonable que declara el roadmap (5–12 KB) y
sensiblemente por debajo de los 27.241 caracteres del global completo del módulo 886.

```
$ .venv/bin/python manage.py check
System check identified no issues (0 silenced).

$ .venv/bin/python manage.py test --settings=config.test_settings
Ran 354 tests in 4.744s
OK

$ .venv/bin/python manage.py test apps.ergonomia_886.help_ai --settings=config.test_settings
Ran 52 tests in 0.381s
OK

$ .venv/bin/python manage.py makemigrations --check --dry-run
No changes detected
```

### Desvíos respecto del roadmap

Ninguno. Los tres anexos se copiaron íntegros de §8.4.3, §8.4.4 y §8.4.5 de la PROPUESTA.

### Notas para el commit siguiente

**Regla permanente:** cada vez que se edite una de las cuatro partes hay que regenerar
`guia_capacitaciones_general.md` con el mismo `cat`, en el mismo orden. Editar una parte sin
regenerar el maestro rompe la prueba de partición del commit 7.1.

---

## Commit 2.3 — Documentos específicos de las ocho pantallas

| Campo | Valor |
|---|---|
| Fecha | 2026-08-12 |
| Rama | feat/ayuda-contextual-capacitaciones |
| Hash | (se completa después del commit) |
| Fase | 2 |
| Estado | ✅ Completado |

### Qué se hizo

Se escribieron los ocho documentos de pantalla: el que se muestra en la pestaña **Guía** y el
que el prompt declara como «referencia principal». Antes de darlos por buenos se contrastaron
sus afirmaciones contra las plantillas reales del proyecto (R-7: gana la pantalla).

### Archivos creados o modificados

En `static/ayuda/capacitaciones/help_texts/`: `home.md`, `capacitaciones_menu.md`,
`modalidad_selector.md`, `online_links.md`, `share_link.md`, `presencial_capacitacion.md`,
`presencial_quiz.md` y `presencial_historial.md`.

### Verificaciones ejecutadas

Contraste de las etiquetas documentadas contra las plantillas reales:

```
Generar Link                                  templates/dashboard/online_links.html
Iniciar Presencial                            templates/dashboard/modalidad_selector.html
Gestionar Links                               templates/dashboard/modalidad_selector.html
Volver al menú de capacitaciones              templates/dashboard/modalidad_selector.html
No hay capacitaciones generales cargadas aún  templates/dashboard/capacitaciones_menu.html
No hay links generados                        templates/dashboard/online_links.html
Próximamente / Personalizada                  templates/dashboard/capacitaciones_menu.html
Finalizar Quiz                                templates/presencial/quiz.html
Repetir Quiz                                  templates/presencial/quiz.html
Generar Planilla de Asistencia                templates/presencial/quiz.html
Volver a la Capacitación                      templates/presencial/quiz.html
Todavía no realizaste capacitaciones presenciales  templates/presencial/historial.html
Anterior / Siguiente                          templates/presencial/quiz.html
```

Cobertura del catálogo y descubrimiento por `staticfiles`:

```
faltan: ninguno
vacíos: ninguno
archivos en el directorio: 14

OK  ayuda/capacitaciones/help_texts/home.md
OK  ayuda/capacitaciones/help_texts/capacitaciones_menu.md
OK  ayuda/capacitaciones/help_texts/modalidad_selector.md
OK  ayuda/capacitaciones/help_texts/online_links.md
OK  ayuda/capacitaciones/help_texts/share_link.md
OK  ayuda/capacitaciones/help_texts/presencial_capacitacion.md
OK  ayuda/capacitaciones/help_texts/presencial_quiz.md
OK  ayuda/capacitaciones/help_texts/presencial_historial.md

$ grep -nE '<patrones de CV-5>' *.md
✅ CV-5 OK

$ .venv/bin/python manage.py check
System check identified no issues (0 silenced).

$ .venv/bin/python manage.py test --settings=config.test_settings
Ran 354 tests in 4.763s
OK

$ .venv/bin/python manage.py test apps.ergonomia_886.help_ai --settings=config.test_settings
Ran 52 tests in 0.380s
OK

$ .venv/bin/python manage.py makemigrations --check --dry-run
No changes detected
```

Los 14 archivos son los 6 globales más los 8 de pantalla; el decimoquinto,
`modulo_ergonomia.md`, llega en el commit 2.4.

### Desvíos respecto del roadmap

**Una diferencia menor entre el corpus y la pantalla, resuelta a favor de la ortografía.**
`templates/presencial/capacitacion.html:91` rotula el botón como «Iniciar Quiz de
**Evaluacion**», sin tilde. El corpus lo escribe con tilde, en `presencial_capacitacion.md` y
en `anexo_presencial.md`.

Se decidió **no** replicar el error ortográfico: la diferencia es de una tilde, no de
contenido, y ningún usuario deja de reconocer el botón por eso. La regla «gana la pantalla»
existe para que el corpus no describa elementos que no existen o que se llaman de otra
manera, y ése no es el caso. Queda anotado como defecto menor de interfaz, ajeno al alcance
de este roadmap: corregir la plantilla del área presencial no es parte de este trabajo.

Sin otros desvíos. Los ocho documentos se copiaron íntegros de §8.4.7 a §8.4.14 de la
PROPUESTA y todas sus demás afirmaciones se verificaron contra las plantillas reales.

### Notas para el commit siguiente

El commit 2.4 exige **verificación previa de CV-6**: confirmar que el módulo `ergonomia` no
es personalizado antes de escribirle una ficha pública.

---

## Commit 2.4 — Ficha del módulo `ergonomia`

| Campo | Valor |
|---|---|
| Fecha | 2026-08-12 |
| Rama | feat/ayuda-contextual-capacitaciones |
| Hash | (se completa después del commit) |
| Fase | 2 |
| Estado | ✅ Completado |

### Qué se hizo

Se escribió el anexo que describe la capacitación abierta, para que el asistente pueda decir
de qué trata el módulo sin leer la base de datos. Incluye la aclaración —importante— de que
**no** es la evaluación ergonómica del protocolo SRT 886/15, que vive en la sección
Evaluaciones y tiene su propia ayuda contextual.

Antes de escribirla se ejecutó la verificación previa obligatoria de CV-6.

### Archivos creados o modificados

- `static/ayuda/capacitaciones/help_texts/modulo_ergonomia.md` — creado.

### Verificaciones ejecutadas

Verificación previa de CV-6, **antes** de escribir la ficha:

```
slug         : ergonomia
título       : Ergonomía
activo       : True
personalizado: False

✅ APTO PARA FICHA PÚBLICA
```

Verificación posterior:

```
fichas declaradas: ['ergonomia']
documentos_modulo("ergonomia"): ('modulo_ergonomia',)
modulos personalizados en la base: ['personal-smoke']
CV-6: ✅ OK

$ ls -1 static/ayuda/capacitaciones/help_texts/*.md | wc -l
      15

$ grep -nE '<patrones de CV-5>' *.md
✅ CV-5 OK

$ .venv/bin/python manage.py check
System check identified no issues (0 silenced).

$ .venv/bin/python manage.py test --settings=config.test_settings
Ran 354 tests in 4.934s
OK

$ .venv/bin/python manage.py test apps.ergonomia_886.help_ai --settings=config.test_settings
Ran 52 tests in 0.364s
OK

$ .venv/bin/python manage.py makemigrations --check --dry-run
No changes detected
```

**Dato relevante sobre CV-6:** la base de desarrollo contiene efectivamente un módulo
personalizado, `personal-smoke`, y **no** tiene ficha. La verificación no es vacua: hay al
menos un módulo que la condición excluye, y queda excluido.

### Desvíos respecto del roadmap

Ninguno. La ficha se copió íntegra de §8.4.15 de la PROPUESTA. El corpus queda completo con
sus 15 documentos y la Fase 2 cerrada.

### Notas para el commit siguiente

Con el corpus completo, la Fase 3 ya puede leer archivos reales. `HELP_TEXTS_PATH` debe
anclarse a `settings.BASE_DIR` y **no** a la posición del archivo: la app está anidada bajo
`apps/training/`, de modo que un `parent.parent` apuntaría a un directorio inexistente y
`md()` lanzaría `HelpContentError` en cada llamada.

---

## Commit 3.1 — Carga versionada del contenido (`prompts.py`)

| Campo | Valor |
|---|---|
| Fecha | 2026-08-12 |
| Rama | feat/ayuda-contextual-capacitaciones |
| Hash | (se completa después del commit) |
| Fase | 3 |
| Estado | ✅ Completado |

### Qué se hizo

Se implementó la lectura estricta de los Markdown y el cálculo del SHA-256 que sincroniza la
Guía con el Chat. El versionado no es un adorno: la Guía devuelve el hash en
`X-Help-Content-Version` y el Chat lo **exige** en el cuerpo del POST, respondiendo 409 si no
coincide. Es lo que garantiza que el usuario nunca esté leyendo una guía mientras el modelo
recibe otra.

### Archivos creados o modificados

- `apps/training/help_ai/prompts.py` — `HELP_TEXTS_PATH`, `VALID_HELP_NAME`,
  `HelpContentError`, `PageHelpContext` (con `guide_markdown`), `md()` y
  `page_help_context()`.

### Verificaciones ejecutadas

```
home                       v=40a7550fd8af… global=  5661 esp= 1357
capacitaciones_menu        v=5e5b3dc56edb… global=  5661 esp= 1462
modalidad_selector         v=6f2c34a82b2c… global=  7082 esp= 1387
online_links               v=2d6c1270d1ef… global=  8744 esp= 2050
share_link                 v=8ec30a5afb2d… global=  8744 esp= 1501
presencial_capacitacion    v=8b762273144d… global=  8700 esp= 1449
presencial_quiz            v=7453cc2ac3cb… global=  8700 esp= 1373
presencial_historial       v=d03abcb69e2c… global=  7279 esp= 1333
determinista: True | longitud: 64
modulo cambia version: True
guide_markdown crece : True
OK fail-closed: slug-que-no-existe
OK fail-closed: ../../../etc/passwd
OK fail-closed: MAYUSCULAS
CV-3 HELP_TEXTS_PATH: True /Users/praguirre/ergocapacitacion/static/ayuda/capacitaciones/help_texts
```

Los tres casos de fallo cerrado cubren las tres familias de riesgo: documento inexistente,
*path traversal* y nombre fuera del alfabeto permitido. En los tres, `md()` lanza
`HelpContentError` en vez de devolver texto vacío, que es lo que convierte una ausencia de
contenido en un 503 explícito y no en una respuesta degradada.

**CV-3 verificada:** `HELP_TEXTS_PATH` apunta al directorio propio anclado a
`settings.BASE_DIR`, no a la posición del archivo.

```
$ .venv/bin/python manage.py check
System check identified no issues (0 silenced).

$ .venv/bin/python manage.py test --settings=config.test_settings
Ran 354 tests in 5.229s
OK

$ .venv/bin/python manage.py test apps.ergonomia_886.help_ai --settings=config.test_settings
Ran 52 tests in 0.412s
OK

$ .venv/bin/python manage.py makemigrations --check --dry-run
No changes detected
```

### Desvíos respecto del roadmap

Ninguno. El bloque se copió íntegro de §8.5.1 de la PROPUESTA. Su única mención del módulo
886 estaba en un comentario que nombraba el directorio del corpus, no la ruta punteada del
paquete, de modo que la restricción del commit 1.1 no obligó a cambiar nada de fondo; aun así
se redactó en prosa para mantener la convención del paquete.

### Notas para el commit siguiente

En `preamble.py` **no se reordenan los bloques**. «DÓNDE ESTÁ EL USUARIO» va antes que «QUÉ
NO PODÉS VER» porque el módulo 886 verificó que el modelo generaliza el descargo de
privacidad hasta negar que sabe en qué pantalla está el usuario.

---

## Commit 3.2 — Preámbulo del sistema (`preamble.py`)

| Campo | Valor |
|---|---|
| Fecha | 2026-08-12 |
| Rama | feat/ayuda-contextual-capacitaciones |
| Hash | (se completa después del commit) |
| Fase | 3 |
| Estado | ✅ Completado |

### Qué se hizo

Se escribió el texto que define qué clase de asistente es: su rol, su ubicación afirmada, sus
límites de conocimiento y su estilo. Conserva la estructura ya depurada del módulo 886 y le
agrega el bloque propio del área, «QUÉ SOS Y QUÉ NO SOS», que fija la doble frontera: con
Ergobot docente —que responde sobre el contenido de la capacitación— y con la ayuda del
módulo de Evaluaciones.

El orden de los bloques no se alteró.

### Archivos creados o modificados

- `apps/training/help_ai/preamble.py` — `PREAMBLE_VERSION`, `NOMBRE_ASISTENTE` y
  `build_preamble()`.

### Verificaciones ejecutadas

```
OK  no ves lo que hay cargado
OK  Nunca afirmes haber leído
OK  está ahora mismo en
OK  nunca sobre la UBICACIÓN
OK  No pidas nombres de trabajadores
OK  derivá explícitamente a Ergobot

nombre del asistente: ErgoBot Capacitaciones
declara el título   : True
declara la ruta     : True
declara el propósito: True
orden correcto      : True
bloque de módulo    : True

$ .venv/bin/python manage.py check
System check identified no issues (0 silenced).

$ .venv/bin/python manage.py test --settings=config.test_settings
Ran 354 tests in 4.751s
OK

$ .venv/bin/python manage.py test apps.ergonomia_886.help_ai --settings=config.test_settings
Ran 52 tests in 0.380s
OK

$ .venv/bin/python manage.py makemigrations --check --dry-run
No changes detected
```

Preámbulo completo generado para la pantalla `online_links`:

```text
Sos ErgoBot Capacitaciones, el asistente de USO del área de Capacitaciones de ErgoSolutions.
Ayudás a profesionales de Higiene y Seguridad y a cuentas de empresa a manejar la aplicación:
elegir una capacitación, dictarla de forma presencial u online, generar y compartir links,
tomar el quiz, generar la planilla de asistencia y leer el historial. También podés explicar
la pantalla de feedback y cómo enviar errores o sugerencias.

### QUÉ SOS Y QUÉ NO SOS
No sos el asistente docente. En la pantalla de dictado presencial y en la pantalla del
trabajador hay otro chat, llamado **Ergobot**, que responde sobre el CONTENIDO de la
capacitación: qué es un factor de riesgo, cómo levantar una carga, qué dice el video. Si te
preguntan eso, respondé lo que sepas en una o dos frases y derivá explícitamente a Ergobot,
que tiene el material del módulo.
Tampoco sos el asistente del módulo de Evaluación Ergonómica SRT 886/15. Las planillas del
protocolo, los factores cuantitativos y los documentos oficiales viven en la sección
Evaluaciones, que tiene su propia ayuda contextual. Si la consulta es de ese ámbito, decilo y
orientá hacia Evaluaciones en lugar de improvisar.

### DÓNDE ESTÁ EL USUARIO
El usuario está ahora mismo en la pantalla «Links de la capacitación online» de
ErgoSolutions, cuya ruta es /dashboard/capacitaciones/<modulo>/links/. Esa pantalla sirve
para generación, copia y seguimiento de los links que se comparten con los trabajadores para
que realicen la capacitación por su cuenta.
Este dato te lo entrega la aplicación en cada consulta: es un hecho verificado, no una
suposición tuya. Si te preguntan en qué pantalla están, respondé con ese nombre y esa ruta,
directamente y sin pedir que te lo confirmen ni que te copien nada.
La sección «GUÍA ESPECÍFICA (online_links)» de este mensaje es la documentación de esa misma
pantalla: usala como la referencia principal para responder.
Cuando la ruta incluya un tramo <modulo> o <id>, no lo completes con un valor inventado:
sólo conocés los que esta instrucción declara.

### QUÉ NO PODÉS VER
Sabés en qué pantalla está el usuario, pero no ves lo que hay cargado en ella. No tenés
acceso a los links generados ni a sus etiquetas, ni a los contadores de accesos, ni a las
direcciones de correo a las que se compartió una capacitación, ni a los resultados del quiz,
ni a los nombres de los trabajadores, ni a los certificados emitidos, ni al historial de
sesiones.
Nunca afirmes haber leído esos datos ni inventes cifras. Tampoco recibís, abrís ni leés
archivos adjuntos. Si la respuesta depende de un valor concreto, pedile al usuario que lo
copie en el mensaje o indicale qué parte de la pantalla mirar.
No sabés qué capacitaciones personalizadas existen ni para qué empresas fueron creadas. Si te
preguntan por una capacitación que no figura en tu documentación, explicá el mecanismo —las
personalizadas sólo las ven los profesionales asignados— sin afirmar que existe o que no
existe.
Esta limitación es sobre los DATOS, nunca sobre la UBICACIÓN. No la uses para decir que no
sabés en qué pantalla está el usuario: eso sí lo sabés, está declarado arriba.

### CÓMO RESPONDER
Escribí en español rioplatense, claro y directo. Usá Markdown cuando mejore la lectura.
Preferí pasos numerados cuando expliques un flujo.
No pidas nombres de trabajadores, CUIT, CUIL, DNI, contraseñas, datos de salud ni otros datos
personales que no necesites para responder.
Si la pregunta excede el área de Capacitaciones y no trata sobre el canal de feedback de la
aplicación, decilo con franqueza en vez de improvisar.
```

*(El texto real es de líneas largas sin cortar; acá se reprodujo con saltos para que sea
legible en la bitácora. El contenido es literal.)*

### Desvíos respecto del roadmap

Ninguno. El bloque se copió íntegro de §8.5.2 de la PROPUESTA.

Nota sobre la numeración de bloques: el docstring del archivo enumera cuatro bloques (QUIÉN
SOS, DÓNDE ESTÁ, QUÉ NO PODÉS VER, CÓMO RESPONDER) mientras que el texto emitido tiene cinco,
porque «QUÉ SOS Y QUÉ NO SOS» se intercala en segundo lugar. La discrepancia viene de la
PROPUESTA y se conservó tal cual: es una imprecisión del comentario, no del texto, y el orden
efectivo es el que exige §3.2 del roadmap, con «DÓNDE ESTÁ EL USUARIO» antes que «QUÉ NO
PODÉS VER». Verificado por índice de posición en la cadena.

### Notas para el commit siguiente

La clave del `lru_cache` de `agents.py` incluye `content_version`: es lo que hace que editar
un `.md` invalide el agente automáticamente, sin reiniciar el proceso. No simplificar la
firma.

---

## Commit 3.3 — Ensamblado del agente (`agents.py`)

| Campo | Valor |
|---|---|
| Fecha | 2026-08-12 |
| Rama | feat/ayuda-contextual-capacitaciones |
| Hash | (se completa después del commit) |
| Fase | 3 |
| Estado | ✅ Completado |

### Qué se hizo

Se unieron preámbulo, versión, contexto general, ficha de módulo y guía específica en las
instrucciones del `Agent` del SDK. El agente se cachea por la clave
`(slug, content_version, modulo)`, de modo que editar un `.md` lo invalida solo, sin
reiniciar el proceso.

### Archivos creados o modificados

- `apps/training/help_ai/agents.py` — `page_agent()` con `lru_cache`.

### Verificaciones ejecutadas

Ensamblado de los 8 slugs, con `Agent` parcheado: **no se hizo ninguna llamada real a
OpenAI**.

```
OK  home                        10695 caracteres
OK  capacitaciones_menu         10832 caracteres
OK  modalidad_selector          12165 caracteres
OK  online_links                14515 caracteres
OK  share_link                  13950 caracteres
OK  presencial_capacitacion     13877 caracteres
OK  presencial_quiz             13756 caracteres
OK  presencial_historial        12344 caracteres
con ficha de módulo : True
sin ficha de módulo : True
modelo              : gpt-5.6-luna == gpt-5.6-luna
tools vacio         : True
OK fail-closed ante versión desactualizada
OK rechaza un slug ajeno al catálogo
```

El `OK` de cada slug verifica cuatro cosas a la vez: que las instrucciones contienen
`### CONTEXTO GENERAL`, que contienen `### GUÍA ESPECÍFICA (<slug>)`, que declaran la versión
vigente y que incluyen el documento específico completo.

Dos comprobaciones de fallo cerrado:

- una versión desactualizada produce `HelpContentError`, no un agente con contenido viejo;
- un slug del catálogo del módulo 886 (`planilla1`) produce `ValueError`: el catálogo es
  cerrado y no se cruza con el del otro sistema.

**CV-4 verificada** sobre toda la app:

```
$ grep -rn "ergonomia_886\|ergobot_ai" apps/training/help_ai/*.py
sin coincidencias
```

```
$ .venv/bin/python manage.py check
System check identified no issues (0 silenced).

$ .venv/bin/python manage.py test --settings=config.test_settings
Ran 354 tests in 4.786s
OK

$ .venv/bin/python manage.py test apps.ergonomia_886.help_ai --settings=config.test_settings
Ran 52 tests in 0.381s
OK

$ .venv/bin/python manage.py makemigrations --check --dry-run
No changes detected
```

### Desvíos respecto del roadmap

Ninguno de fondo. El bloque se copió íntegro de §8.5.3 de la PROPUESTA, con una única
adaptación de redacción: el docstring nombra al paquete de ayuda del módulo 886 y al
asistente docente en prosa, en lugar de con sus rutas punteadas, por la restricción
registrada en el commit 1.1.

**Observación sobre el modelo.** `settings.CHAT_AI_MODEL` vale `gpt-5.6-luna` en este
entorno, mientras que §2.3 de la PROPUESTA documentaba `gpt-4.1-mini-2025-04-14` como valor
auditado. No es un desvío de este trabajo: el agente lee el modelo de la configuración y no
lo fija, de modo que hereda lo que el proyecto tenga definido. Se registra por trazabilidad.

### Notas para el commit siguiente

Fase 3 cerrada: el sistema ya puede construir el agente, aunque todavía no hay ninguna URL
que lo exponga. La Fase 4 empieza por `limits.py`, cuyo punto crítico es
`KEY_PREFIX = "help-capa"`: reutilizar el prefijo del módulo 886 haría que consultar una
ayuda bloqueara la otra.

---

## Commit 4.1 — Límites de uso con prefijo propio

| Campo | Valor |
|---|---|
| Fecha | 2026-08-12 |
| Rama | feat/ayuda-contextual-capacitaciones |
| Hash | (se completa después del commit) |
| Fase | 4 |
| Estado | ✅ Completado |

### Qué se hizo

Se implementó la protección del endpoint del chat: un lease de concurrencia que impide dos
streams simultáneos del mismo usuario, y una cuota por ventana temporal. Es una copia
deliberada de la mecánica probada del módulo 886 —no un import, por CF-1 bis— con **prefijo
de clave propio**, `help-capa`.

### Archivos creados o modificados

- `apps/training/help_ai/limits.py` — `KEY_PREFIX`, `ChatLimitExceeded`, `ChatLease`,
  `acquire_chat_lease()` y `release_chat_lease()`.

### Verificaciones ejecutadas

Ejecutado con `--settings=config.test_settings` para que el cache sea `LocMemCache` y la
prueba no toque el `DatabaseCache` de desarrollo.

```
prefijo propio: help-capa
OK bloquea el segundo stream | retry_after = 2
OK los leases del 886 y de capacitaciones son independientes
OK cuota aplicada tras 20 consultas | retry_after = 47
OK release libera: True
```

La segunda línea es la que justifica el commit: con el lease del módulo 886 tomado por el
usuario 1, el lease de Capacitaciones para ese mismo usuario **se concede**. Si se hubiera
reutilizado el prefijo `help-ai:`, un profesional que estuviera consultando la ayuda de
Evaluaciones recibiría «ya existe una consulta en curso» al abrir la ayuda de Capacitaciones.

```
$ .venv/bin/python manage.py check
System check identified no issues (0 silenced).

$ .venv/bin/python manage.py test --settings=config.test_settings
Ran 354 tests in 4.708s
OK

$ .venv/bin/python manage.py test apps.ergonomia_886.help_ai --settings=config.test_settings
Ran 52 tests in 0.382s
OK

$ .venv/bin/python manage.py makemigrations --check --dry-run
No changes detected
```

### Efecto secundario declarado y aceptado

Con prefijos separados, un usuario que use **ambos** asistentes en simultáneo puede alcanzar
`2 × CHAT_AI_RATE_LIMIT` consultas por ventana: 40 por minuto con el valor por defecto, en
lugar de 20. Se acepta para la beta, como decide el roadmap. La variante de cuota unificada
—lease propio, bucket de cuota compartido— está documentada en §8.12.2 de la PROPUESTA y
puede adoptarse sin tocar nada más que este archivo, ajustando además la prueba de leases
independientes.

### Desvíos respecto del roadmap

Ninguno de fondo. El bloque se copió íntegro de §8.6.1 de la PROPUESTA, con la misma
adaptación de redacción del commit 3.3: el docstring nombra al módulo 886 en prosa.

### Notas para el commit siguiente

El commit 4.2 es el archivo más largo del roadmap (≈380 líneas) y se copia íntegro de
§8.6.2, sin simplificar. En particular: el `while` con `asyncio.wait`, el bloque `finally`
que libera el lease siempre, el respaldo `message_output_created`, `to_wire_thread()` y la
cabecera `X-Accel-Buffering: no`.
