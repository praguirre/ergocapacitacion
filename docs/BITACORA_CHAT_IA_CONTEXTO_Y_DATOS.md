# Bitácora de ejecución — Chat IA: contexto de pantalla y acceso de lectura

**Roadmap:** `docs/ROADMAP_CHAT_IA_CONTEXTO_Y_DATOS.md`
**Diseño:** `docs/PROPUESTA_CHAT_IA_CONTEXTO_Y_DATOS.md`
**Inicio:** 2026-08-07
**Ejecutor:** Asistente IA de desarrollo
**Titular:** Pablo R. Aguirre
**Rama:** `feature/chat-ia-contexto`
**Commit de partida:** `ef6ef4e`

---

## Estado de partida verificado

| Comprobación | Resultado |
|---|---|
| `test apps` | `Ran 269 tests in 2.542s` — `OK` |
| `test apps.ergonomia_886` | `Ran 224 tests in 2.305s` — `OK` |
| `test apps.ergonomia_886.help_ai` | `Ran 28 tests in 0.226s` — `OK` |
| `makemigrations --check` | `No changes detected` |
| `check` | `System check identified no issues (0 silenced).` |

Los conteos y resultados coinciden con la línea base de §0.6. Los tiempos
varían respecto de la medición del 07/08/2026, como es esperable entre
ejecuciones.

### Medición de partida del prompt

| slug | instructions | global | específico | % específico |
|---|---:|---:|---:|---:|
| `home` | 28.273 | 27.241 | 339 | 1,2 % |
| `dashboard` | 28.471 | 27.241 | 532 | 1,9 % |
| `crear` | 28.381 | 27.241 | 446 | 1,6 % |
| `planilla1` | 34.845 | 27.241 | 6.906 | 19,8 % |
| `lmc` | 36.984 | 27.241 | 9.051 | 24,5 % |
| `vibracion_cuerpo_entero` | 39.479 | 27.241 | 11.526 | 29,2 % |

### Inventario de partida

| Elemento | Valor |
|---|---|
| Slugs de página en el catálogo | 31 |
| Plantillas con bloque `help_slug` | 23 |
| Documentos de ayuda en `static/ayuda/help_texts/` | 33 |
| Tamaño del contexto global | 27.241 caracteres |

---

## Registro de commits

## Commit A.0 — Crear rama de trabajo y bitácora de ejecución

| Campo | Valor |
|---|---|
| Fecha | 2026-08-07 21:40 |
| Rama | `feature/chat-ia-contexto` |
| Hash | `a5e6642` |
| Fase | A |
| Hallazgo / Condición | — |
| Estado | ✅ Completado |

### Qué se hizo
Se creó la rama de trabajo y la bitácora de trazabilidad. Se incorporaron al
índice documental la propuesta, el roadmap y esta bitácora, y se reprodujo la
línea base antes de iniciar cualquier cambio funcional.

### Archivos afectados
| Archivo | Acción | Qué cambió |
|---|---|---|
| `docs/BITACORA_CHAT_IA_CONTEXTO_Y_DATOS.md` | creado | Línea base y registro de ejecución. |
| `docs/README.md` | modificado | Alta de los tres documentos de la iniciativa. |
| `docs/ROADMAP_CHAT_IA_CONTEXTO_Y_DATOS.md` | creado | Plan de ejecución y tabla de control. |
| `docs/PROPUESTA_CHAT_IA_CONTEXTO_Y_DATOS.md` | creado | Diseño técnico auditado. |
| `docs/PROMPT_EJECUCION_ROADMAP_CHAT_IA.md` | creado | Contrato operativo de ejecución. |
| `README.md` | modificado | Registro del inicio de la iniciativa. |

### Decisiones de implementación
Ninguna. Los tiempos de la suite se registraron con sus valores reales; los
conteos y resultados coinciden con §0.6.

### Validación ejecutada

```text
$ .venv/bin/python manage.py test apps --settings=config.test_settings
Ran 269 tests in 2.322s
OK

$ .venv/bin/python manage.py test apps.ergonomia_886 --settings=config.test_settings
Ran 224 tests in 2.305s
OK

$ .venv/bin/python manage.py test apps.ergonomia_886.help_ai --settings=config.test_settings
Ran 28 tests in 0.226s
OK

$ .venv/bin/python manage.py makemigrations --check --dry-run --settings=config.test_settings
No changes detected

$ .venv/bin/python manage.py check --settings=config.test_settings
System check identified no issues (0 silenced).

$ git branch --show-current
feature/chat-ia-contexto

$ test -s docs/BITACORA_CHAT_IA_CONTEXTO_Y_DATOS.md
(sin salida; código de salida 0)
```

| Comprobación | Antes | Después |
|---|---|---|
| Tests totales | 269 | 269 |
| Tests de `help_ai` | 28 | 28 |
| Rama activa | `feature/ergonomia-886` | `feature/chat-ia-contexto` |

### Tests modificados y por qué
Ninguno.

### Impacto en despliegue
| Requisito | ¿Aplica? |
|---|---|
| `collectstatic` | No |
| Reinicio del servicio | No |
| Migración de base de datos | No |
| Variable de entorno nueva | No |

### Cómo se revierte
```bash
git switch feature/ergonomia-886
git branch -D feature/chat-ia-contexto
```
No se pierde código funcional: A.0 sólo agrega documentación.

### Desvíos respecto del roadmap
Ninguno.

### Notas para el commit siguiente
La ficha `menu_planillas` se creará en A.1 antes de ingresar al catálogo en A.3.

---

## Commit A.1 — Registro de páginas: `pages.py` y su cobertura

| Campo | Valor |
|---|---|
| Fecha | 2026-08-07 21:43 |
| Rama | `feature/chat-ia-contexto` |
| Hash | `b8059e2` |
| Fase | A |
| Hallazgo / Condición | H1 |
| Estado | ✅ Completado |

### Qué se hizo
Se creó el registro estático que traduce cada slug a título humano, ruta y
propósito. Las fichas de los 13 factores se derivan del catálogo canónico y la
cobertura falla cerrado ante slugs desconocidos o rutas concretas inventadas.

### Archivos afectados
| Archivo | Acción | Qué cambió |
|---|---|---|
| `apps/ergonomia_886/help_ai/pages.py` | creado | Registro de identidad de las 32 pantallas. |
| `apps/ergonomia_886/help_ai/tests.py` | modificado | Cuatro pruebas del contrato del registro. |
| `docs/BITACORA_CHAT_IA_CONTEXTO_Y_DATOS.md` | modificado | Entrada A.1 y hash de A.0. |
| `docs/ROADMAP_CHAT_IA_CONTEXTO_Y_DATOS.md` | modificado | A.1 marcado como completado. |
| `README.md` | modificado | Registro funcional de A.1. |

### Decisiones de implementación
Ninguna. `menu_planillas` queda deliberadamente como ficha sin slug hasta A.3.

### Validación ejecutada

```text
$ .venv/bin/python manage.py test apps --settings=config.test_settings
Ran 273 tests in 2.441s
OK

$ .venv/bin/python manage.py makemigrations --check --dry-run --settings=config.test_settings
No changes detected

$ .venv/bin/python manage.py check --settings=config.test_settings
System check identified no issues (0 silenced).

$ .venv/bin/python manage.py test apps.ergonomia_886.help_ai --settings=config.test_settings
Ran 32 tests in 0.218s
OK

$ DJANGO_SETTINGS_MODULE=config.test_settings .venv/bin/python -c "<resolver de rutas>"
listado  : /evaluacion-ergonomica/
crear    : /evaluacion-ergonomica/protocolo/crear/
detalle  : /evaluacion-ergonomica/protocolo/1/
planilla1: /evaluacion-ergonomica/protocolo/1/planilla1/
docs     : /evaluacion-ergonomica/documentos/1/

$ DJANGO_SETTINGS_MODULE=config.test_settings .venv/bin/python -c "<cobertura de fichas>"
fichas: 32 | catálogo: 31
sin ficha: ninguno
ficha sin slug: ['menu_planillas']
```

| Comprobación | Antes | Después |
|---|---|---|
| Tests totales | 269 | 273 |
| Tests de `help_ai` | 28 | 32 |
| Fichas / catálogo | 0 / 31 | 32 / 31 |

### Tests modificados y por qué
Ninguno existente. Se agregaron cuatro pruebas nuevas.

### Impacto en despliegue
| Requisito | ¿Aplica? |
|---|---|
| `collectstatic` | No |
| Reinicio del servicio | No |
| Migración de base de datos | No |
| Variable de entorno nueva | No |

### Cómo se revierte
```bash
git revert <hash de A.1>
```
Seguro: todavía ningún componente de runtime consume `pages.py`.

### Desvíos respecto del roadmap
Ninguno.

### Notas para el commit siguiente
La ficha `menu_planillas` es la única que aún no pertenece al catálogo; A.3
cerrará esa diferencia.

---

## Commit A.2 — Preámbulo v2.0: declarar la pantalla y acotar el descargo

| Campo | Valor |
|---|---|
| Fecha | 2026-08-07 21:47 |
| Rama | `feature/chat-ia-contexto` |
| Hash | `78e478b` |
| Fase | A |
| Hallazgo / Condición | H1 + H2 |
| Estado | ⚠️ Completado con desvíos |

### Qué se hizo
Se creó el preámbulo v2.0 y se cableó antes de toda la documentación del
agente. El prompt afirma título, ruta y propósito de la pantalla, mientras
acota explícitamente la falta de acceso a los datos cargados.

### Archivos afectados
| Archivo | Acción | Qué cambió |
|---|---|---|
| `apps/ergonomia_886/help_ai/preamble.py` | creado | Preámbulo v2.0 sin acceso a datos. |
| `apps/ergonomia_886/help_ai/agents.py` | modificado | Composición con ficha de pantalla y preámbulo. |
| `apps/ergonomia_886/help_ai/tests.py` | modificado | Tres pruebas nuevas y dos literales actualizados. |
| `docs/PROPUESTA_CHAT_IA_CONTEXTO_Y_DATOS.md` | modificado | Nota del desvío sintáctico encontrado al ejecutar. |
| `docs/BITACORA_CHAT_IA_CONTEXTO_Y_DATOS.md` | modificado | Entrada A.2 y hash de A.1. |
| `docs/ROADMAP_CHAT_IA_CONTEXTO_Y_DATOS.md` | modificado | A.2 marcado con desvío. |
| `README.md` | modificado | Registro funcional de A.2. |

### Decisiones de implementación
La concatenación propuesta `build_preamble(...) f"..."` no es sintaxis Python
válida. Se agregó el operador `+`, cambio mínimo indispensable. Además se
actualizaron dos aserciones literales del preámbulo anterior al texto v2.0.

### Preámbulo reemplazado íntegro

```text
Eres un asistente experto en la Resolución SRT 886/15 y en el uso de ErgoApp. Responde en español, con claridad, y usa Markdown cuando ayude a la legibilidad. No tienes acceso a los valores del formulario, resultados, observaciones ni datos de la evaluación que el usuario está viendo. Nunca afirmes haber visto esos datos ni inventes por qué obtuvo un nivel. Si la respuesta depende de ellos, indícale qué valores debe copiar en la consulta o qué campo debe revisar. No solicites nombres de trabajadores, CUIT ni otros datos personales innecesarios.
```

### Validación ejecutada

```text
$ .venv/bin/python manage.py test apps --settings=config.test_settings
Ran 276 tests in 2.499s
OK

$ .venv/bin/python manage.py makemigrations --check --dry-run --settings=config.test_settings
No changes detected

$ .venv/bin/python manage.py check --settings=config.test_settings
System check identified no issues (0 silenced).

$ .venv/bin/python manage.py test apps.ergonomia_886.help_ai --settings=config.test_settings
Ran 35 tests in 0.215s
OK

$ DJANGO_SETTINGS_MODULE=config.test_settings .venv/bin/python - <<'PY'
home           29558 chars  |  'está ahora mismo en': True  |  título: True
dashboard      29734 chars  |  'está ahora mismo en': True  |  título: True
crear          29618 chars  |  'está ahora mismo en': True  |  título: True
lmc            38238 chars  |  'está ahora mismo en': True  |  título: True
```

Prueba manual con respuesta del proveedor: recomendada pero no bloqueante en
A.2; se difiere a la aceptación integral de A.10.

| Comprobación | Antes | Después |
|---|---|---|
| Tests totales | 273 | 276 |
| Tests de `help_ai` | 32 | 35 |
| Prompt `home` | 28.273 | 29.558 (+1.285) |
| Prompt `dashboard` | 28.471 | 29.734 (+1.263) |
| Prompt `crear` | 28.381 | 29.618 (+1.237) |
| Prompt `lmc` | 36.984 | 38.238 (+1.254) |

### Tests modificados y por qué
`test_page_agent_receives_global_and_page_specific_context` conservó su
propósito, pero sus dos literales se actualizaron de «No tienes...»/«haber
visto» a «No tenés...»/«haber leído», porque A.2 reemplaza deliberadamente el
preámbulo y mantiene las mismas prohibiciones en rioplatense.

### Impacto en despliegue
| Requisito | ¿Aplica? |
|---|---|
| `collectstatic` | No |
| Reinicio del servicio | Sí — la caché de agentes es por proceso |
| Migración de base de datos | No |
| Variable de entorno nueva | No |

### Cómo se revierte
```bash
git revert <hash de A.2>
```
El bot volvería a negar su ubicación; `pages.py` quedaría sin consumidores.

### Desvíos respecto del roadmap
El diff literal carecía del operador de concatenación y produjo `SyntaxError`.
La realidad exigió agregar `+`. El roadmap afirmaba que el test existente no
cambiaría, pero dos aserciones comprobaban literalmente el texto sustituido.

### Notas para el commit siguiente
Ninguna.

---

## Commit A.3 — Separar el slug del detalle: `menu_planillas`

| Campo | Valor |
|---|---|
| Fecha | 2026-08-07 21:49 |
| Rama | `feature/chat-ia-contexto` |
| Hash | `29c02dd` |
| Fase | A |
| Hallazgo / Condición | H3 |
| Estado | ✅ Completado |

### Qué se hizo
El listado conserva `dashboard` y el detalle recibe `menu_planillas`. Se movió
el contenido existente a su slug correcto, se registró el slug nuevo y se
agregó una regresión que prohíbe que dos pantallas compartan slug.

### Archivos afectados
| Archivo | Acción | Qué cambió |
|---|---|---|
| `apps/ergonomia_886/help_ai/catalog.py` | modificado | Alta de `menu_planillas`. |
| `apps/ergonomia_886/planillas/templates/planillas/detalle_evaluacion.html` | modificado | Slug del detalle. |
| `static/ayuda/help_texts/menu_planillas.md` | creado | Contenido anterior de `dashboard.md`. |
| `static/ayuda/help_texts/dashboard.md` | modificado | Contenido anterior de `home.md`. |
| `apps/ergonomia_886/evaluaciones/tests_ui_dark.py` | modificado | Recorrido actualizado al slug deliberado. |
| `apps/ergonomia_886/help_ai/tests.py` | modificado | Test anti-colisión. |
| `docs/BITACORA_CHAT_IA_CONTEXTO_Y_DATOS.md` | modificado | Entrada A.3 y hash de A.2. |
| `docs/ROADMAP_CHAT_IA_CONTEXTO_Y_DATOS.md` | modificado | A.3 completado. |
| `README.md` | modificado | Registro funcional de A.3. |

### Decisiones de implementación
Ninguna.

### Mapeo antes → después
| Pantalla | Antes | Después | Documento servido |
|---|---|---|---|
| Listado | `dashboard` | `dashboard` | Contenido del listado |
| Detalle | `dashboard` | `menu_planillas` | Contenido del menú de planillas |
| Respaldo | `home` huérfano | `home` deliberado | Provisional hasta A.4 |

### Contenidos originales íntegros

`dashboard.md` original:

```markdown
# Guía del Menú de Planillas

Esta pantalla es el centro de comando de tu evaluación. Desde aquí puedes acceder a cada una de las planillas del protocolo 886/15.

- Las planillas marcadas como **"Pendiente"** o **"Completar"** requieren tu atención.
- Las planillas marcadas como **"Completa"** ya tienen datos guardados.

Sigue el orden lógico del protocolo: comienza con la **Planilla 1**, luego las **Planillas 2** correspondientes, seguido de la **Planilla 3** si hay riesgos, y finalmente la **Planilla 4** para el seguimiento.
```

`home.md` original:

```markdown
# Guía del Dashboard Principal

Bienvenido a ErgoApp. Desde esta pantalla puedes:

- **Crear Nueva Evaluación:** Inicia un nuevo protocolo para un establecimiento.
- **Ver/Editar:** Accede a una evaluación existente para completar o modificar las planillas.
- **Eliminar:** Borra permanentemente una evaluación y todos sus datos asociados.
```

### Validación ejecutada

```text
$ .venv/bin/python manage.py test apps --settings=config.test_settings
Ran 277 tests in 2.311s
OK

$ .venv/bin/python manage.py makemigrations --check --dry-run --settings=config.test_settings
No changes detected

$ .venv/bin/python manage.py check --settings=config.test_settings
System check identified no issues (0 silenced).

$ .venv/bin/python manage.py test apps.ergonomia_886.evaluaciones.tests_ui_dark --settings=config.test_settings
Ran 3 tests in 0.336s
OK

$ .venv/bin/python manage.py test apps.ergonomia_886.help_ai --settings=config.test_settings
Ran 36 tests in 0.229s
OK

$ DJANGO_SETTINGS_MODULE=config.test_settings .venv/bin/python -c "<igualdad catálogo/fichas>"
catálogo: 32 | fichas: 32
coinciden: True

$ for f in dashboard menu_planillas home; do ...; done
dashboard        # Guía del Dashboard Principal
menu_planillas   # Guía del Menú de Planillas
home             # Guía del Dashboard Principal
```

| Comprobación | Antes | Después |
|---|---|---|
| Tests totales | 276 | 277 |
| Tests de `help_ai` | 35 | 36 |
| Slugs | 31 | 32 |
| Pares de plantillas con slug repetido | 1 | 0 |

### Tests modificados y por qué
`tests_ui_dark.py` cambió la expectativa del detalle de `dashboard` a
`menu_planillas`: el comportamiento viejo codificaba la colisión que A.3
corrige deliberadamente. No se borró ninguna prueba.

### Impacto en despliegue
| Requisito | ¿Aplica? |
|---|---|
| `collectstatic` | Sí — obligatorio ida y vuelta |
| Reinicio del servicio | Sí — caché de agentes por proceso |
| Migración de base de datos | No |
| Variable de entorno nueva | No |

### Cómo se revierte
```bash
git revert <hash de A.3>
.venv/bin/python manage.py collectstatic --noinput
```
Vuelve la colisión. Si A.4 existe, se revierten A.4 y A.3 en ese orden.

### Desvíos respecto del roadmap
Ninguno.

### Notas para el commit siguiente
Los títulos provisionales `dashboard` y `home` son deliberadamente iguales;
A.4 reescribe los cuatro documentos.

---

## Commit A.4 — Reescribir y enriquecer los cuatro documentos cruzados

| Campo | Valor |
|---|---|
| Fecha | 2026-08-07 21:52 |
| Rama | `feature/chat-ia-contexto` |
| Hash | `d532c14` |
| Fase | A |
| Hallazgo / Condición | H3 + H4 |
| Estado | ✅ Completado |

### Qué se hizo
Se reescribieron las guías de listado, menú de planillas, creación y respaldo
general con el contenido obligatorio del roadmap. Las tres pantallas críticas
ya tienen señal específica suficiente y acciones, estados y pasos siguientes.

### Archivos afectados
| Archivo | Acción | Qué cambió |
|---|---|---|
| `static/ayuda/help_texts/dashboard.md` | modificado | Guía completa del listado. |
| `static/ayuda/help_texts/menu_planillas.md` | modificado | Guía completa del detalle. |
| `static/ayuda/help_texts/crear.md` | modificado | Empresas, snapshot CF-5 y errores. |
| `static/ayuda/help_texts/home.md` | modificado | Respaldo general e inofensivo. |
| `docs/BITACORA_CHAT_IA_CONTEXTO_Y_DATOS.md` | modificado | Entrada A.4 y hash de A.3. |
| `docs/ROADMAP_CHAT_IA_CONTEXTO_Y_DATOS.md` | modificado | A.4 completado. |
| `README.md` | modificado | Registro funcional de A.4. |

### Decisiones de implementación
Ninguna fuera del contenido prescripto. Se usó español rioplatense coherente
con el preámbulo v2.0 y la configuración `es-ar`.

### Validación ejecutada

```text
$ .venv/bin/python manage.py test apps --settings=config.test_settings
Ran 277 tests in 2.294s
OK

$ .venv/bin/python manage.py makemigrations --check --dry-run --settings=config.test_settings
No changes detected

$ .venv/bin/python manage.py check --settings=config.test_settings
System check identified no issues (0 silenced).

$ for f in dashboard menu_planillas crear home; do ...; done
dashboard          3024 chars   # Guía de Evaluaciones Ergonómicas
menu_planillas     3144 chars   # Guía del Menú de Planillas
crear              3328 chars   # Guía para Crear una Evaluación
home               1900 chars   # Guía general del Módulo de Ergonomía SRT 886/15

$ DJANGO_SETTINGS_MODULE=config.test_settings .venv/bin/python -c "<carga de todos los slugs>"
Los 32 slugs cargan contexto sin error.
```

El humo de contenido se verificó cargando los 32 contextos con el constructor
real; la revisión visual de redacción por Pablo queda pendiente y no bloquea.

| Comprobación | Antes | Después |
|---|---|---|
| Tests totales | 277 | 277 |
| Tests de `help_ai` | 36 | 36 |
| `dashboard.md` | 339 | 3.024 |
| `menu_planillas.md` | 532 | 3.144 |
| `crear.md` | 446 | 3.328 |
| `home.md` | 339 | 1.900 |

### Tests modificados y por qué
Ninguno.

### Impacto en despliegue
| Requisito | ¿Aplica? |
|---|---|
| `collectstatic` | Sí — obligatorio ida y vuelta |
| Reinicio del servicio | Sí — cambian cuatro `help_version` |
| Migración de base de datos | No |
| Variable de entorno nueva | No |

Los usuarios que conserven una guía anterior abierta recibirán HTTP 409 con
«Recargá la guía» para `dashboard`, `menu_planillas`, `crear` y `home`; es el
comportamiento diseñado.

### Cómo se revierte
```bash
git revert <hash de A.4>
.venv/bin/python manage.py collectstatic --noinput
```
Los contenidos originales están transcriptos íntegramente en A.3.

### Desvíos respecto del roadmap
Ninguno.

### Notas para el commit siguiente
Redacción pendiente de revisión de Pablo. No bloquea el avance del roadmap.

---

## Commit A.5 — Respaldo del slug y guarda en la vista genérica

| Campo | Valor |
|---|---|
| Fecha | 2026-08-07 21:54 |
| Rama | `feature/chat-ia-contexto` |
| Hash | `48d081b` |
| Fase | A |
| Hallazgo / Condición | H5 |
| Estado | ⚠️ Completado con desvíos |

### Qué se hizo
La plantilla genérica de Planillas 2 usa `home` si el slug falta o está vacío.
La vista falla con `ImproperlyConfigured` cuando un llamador no declara slug,
y dos pruebas recorren las plantillas y ejercitan la guarda.

### Archivos afectados
| Archivo | Acción | Qué cambió |
|---|---|---|
| `apps/ergonomia_886/planillas/templates/planillas/planilla2_structured_form.html` | modificado | Filtro `default:"home"`. |
| `apps/ergonomia_886/planillas/views.py` | modificado | Guarda explícita antes de consultar datos. |
| `apps/ergonomia_886/help_ai/tests.py` | modificado | Contrato de bloques y guarda vacía. |
| `docs/BITACORA_CHAT_IA_CONTEXTO_Y_DATOS.md` | modificado | Entrada A.5 y hash de A.4. |
| `docs/ROADMAP_CHAT_IA_CONTEXTO_Y_DATOS.md` | modificado | A.5 marcado con desvío. |
| `README.md` | modificado | Registro funcional de A.5. |

### Decisiones de implementación
El test de la guarda usa un objeto request mínimo porque la excepción ocurre
antes de acceder al request o a la base. Esto prueba exactamente la frontera.

### Validación ejecutada

```text
$ DJANGO_SETTINGS_MODULE=config.test_settings .venv/bin/python -c "<filtro default>"
sin variable   actual: data-page-slug=""                nuevo: data-page-slug="home"
vacía          actual: data-page-slug=""                nuevo: data-page-slug="home"
presente       actual: data-page-slug="planilla2c"      nuevo: data-page-slug="planilla2c"

$ .venv/bin/python manage.py test apps --settings=config.test_settings
Ran 279 tests in 2.373s
OK

$ .venv/bin/python manage.py makemigrations --check --dry-run --settings=config.test_settings
No changes detected

$ .venv/bin/python manage.py check --settings=config.test_settings
System check identified no issues (0 silenced).

$ .venv/bin/python manage.py test apps.ergonomia_886.help_ai --settings=config.test_settings
Ran 38 tests in 0.243s
OK

$ .venv/bin/python manage.py test apps.ergonomia_886.planillas --settings=config.test_settings
Ran 43 tests in 0.229s
OK

$ DJANGO_SETTINGS_MODULE=config.test_settings .venv/bin/python - <<'PY'
ImproperlyConfigured: Planilla2C: la vista no declaró help_slug y el panel de ayuda contextual quedaría inutilizable en esa pantalla.

$ rg -n "'help_slug': help_slug" apps/ergonomia_886/planillas/views.py
313:        'help_slug': help_slug,
```

La línea de contexto quedó restaurada y presente.

| Comprobación | Antes | Después |
|---|---|---|
| Tests totales | 277 | 279 |
| Tests de `help_ai` | 36 | 38 |
| Slug faltante o vacío | `""` silencioso | respaldo `home` |

### Tests modificados y por qué
Ninguno existente. Se agregaron dos pruebas.

### Impacto en despliegue
| Requisito | ¿Aplica? |
|---|---|
| `collectstatic` | No |
| Reinicio del servicio | Sí |
| Migración de base de datos | No |
| Variable de entorno nueva | No |

### Cómo se revierte
```bash
git revert <hash de A.5>
```
El camino feliz no cambia; al revertir reaparece el modo de falla silencioso.

### Desvíos respecto del roadmap
La reproducción indicada de comentar sólo `'help_slug': help_slug` no puede
activar una guarda ubicada al inicio de la función: el parámetro sigue siendo
no vacío. Se reprodujo correctamente llamando la misma vista con `help_slug=''`
y se confirmó por `rg` que la línea de contexto quedó intacta.

### Notas para el commit siguiente
Ninguna.

---

## Commit A.6 — Defensa activa en el cliente: la falla deja de ser muda

| Campo | Valor |
|---|---|
| Fecha | 2026-08-07 22:01 |
| Rama | `feature/chat-ia-contexto` |
| Hash | `e2ed314` |
| Fase | A |
| Hallazgo / Condición | H5 |
| Estado | ✅ Completado |

### Qué se hizo
El widget informa visualmente cuando falta `data-page-slug` y registra dos
errores identificables según el origen: apertura del panel o envío al Chat IA.
D-P-4 se resolvió con mensaje + consola, sin telemetría.

### Archivos afectados
| Archivo | Acción | Qué cambió |
|---|---|---|
| `static/ayuda/js/help_widget.js` | modificado | Aviso visible y `console.error` ante slug ausente. |
| `docs/BITACORA_CHAT_IA_CONTEXTO_Y_DATOS.md` | modificado | Entrada A.6 y hash de A.5. |
| `docs/ROADMAP_CHAT_IA_CONTEXTO_Y_DATOS.md` | modificado | A.6 completado. |
| `README.md` | modificado | Registro funcional de A.6. |

### Decisiones de implementación
D-P-4: Opción A. No se agregó `sendBeacon` ni endpoint. El aviso ya permite
que el usuario reporte la pantalla y evita ampliar superficie, CSRF y límites.

### Validación ejecutada

```text
$ .venv/bin/python manage.py test apps --settings=config.test_settings
Ran 279 tests in 2.383s
OK

$ .venv/bin/python manage.py makemigrations --check --dry-run --settings=config.test_settings
No changes detected

$ .venv/bin/python manage.py check --settings=config.test_settings
System check identified no issues (0 silenced).

$ .venv/bin/python manage.py test apps.ergonomia_886.help_ai --settings=config.test_settings
Ran 38 tests in 0.237s
OK

$ grep -nE "onclick|onload|onerror|innerHTML...<script" static/ayuda/js/help_widget.js || echo "OK — sin handlers inline ni script inyectado"
OK — sin handlers inline ni script inyectado
```

Prueba funcional en navegador local con un arnés temporal eliminado antes del
cierre:

```text
Camino normal:
guía: # Guía normal
help_version: version-de-prueba
errores nuevos de consola: []

Slug vacío al abrir:
La ayuda contextual no está disponible en esta pantalla. Avisale al equipo técnico indicando en qué página estabas.

Slug vacío al enviar:
prueba
⚠️ La ayuda contextual no está disponible en esta pantalla.

Consola:
[ayuda-886] El panel de ayuda no recibió data-page-slug. Object
[ayuda-886] El panel de ayuda no recibió data-page-slug. Object
```

La recarga con slug normal volvió a cargar la guía y dejó la consola limpia.
El servidor local se detuvo y no quedó ningún archivo del arnés.

| Comprobación | Antes | Después |
|---|---|---|
| Tests totales | 279 | 279 |
| Tests de `help_ai` | 38 | 38 |
| Falla con slug vacío | silenciosa | aviso + error de consola |

### Tests modificados y por qué
Ninguno.

### Impacto en despliegue
| Requisito | ¿Aplica? |
|---|---|
| `collectstatic` | Sí — obligatorio ida y vuelta |
| Reinicio del servicio | No |
| Migración de base de datos | No |
| Variable de entorno nueva | No |

El archivo servido será `help_widget.<hash>.js`; sin `collectstatic` el
navegador conservaría la versión anterior.

### Cómo se revierte
```bash
git revert <hash de A.6>
.venv/bin/python manage.py collectstatic --noinput
```

### Desvíos respecto del roadmap
Ninguno.

### Notas para el commit siguiente
Ninguna.

---

## Commit A.7 — Partir `guia_general.md` en núcleo y anexos

| Campo | Valor |
|---|---|
| Fecha | 2026-08-07 22:04 |
| Rama | `feature/chat-ia-contexto` |
| Hash | `5fa171c` |
| Fase | A |
| Hallazgo / Condición | H4 |
| Estado | ✅ Completado |

### Qué se hizo
Se partió mecánicamente el documento maestro en núcleo, cinco pasos y nueve
subguías del Paso 2. Dos pruebas garantizan que las 15 partes no están vacías
y reconstruyen `guia_general.md` carácter por carácter.

### Archivos afectados
| Archivo | Acción | Qué cambió |
|---|---|---|
| `static/ayuda/help_texts/guia_general_nucleo.md` | creado | Cabecera, introducción y diagrama. |
| `static/ayuda/help_texts/guia_general_paso1.md` | creado | Paso 1. |
| `static/ayuda/help_texts/guia_general_paso2.md` | creado | Cabecera del Paso 2. |
| `static/ayuda/help_texts/guia_general_paso2a.md` … `paso2i.md` | creados | Nueve subguías. |
| `static/ayuda/help_texts/guia_general_paso3.md` … `paso5.md` | creados | Pasos 3, 4 y 5. |
| `apps/ergonomia_886/help_ai/tests.py` | modificado | Reconstrucción e integridad. |
| `docs/BITACORA_CHAT_IA_CONTEXTO_Y_DATOS.md` | modificado | Entrada A.7 y hash de A.6. |
| `docs/ROADMAP_CHAT_IA_CONTEXTO_Y_DATOS.md` | modificado | A.7 completado. |
| `README.md` | modificado | Registro funcional de A.7. |

### Decisiones de implementación
La generación del parche fue mecánica a partir de los encabezados del maestro.
Se retiró el único salto final agregado por la herramienta de parcheo al último
anexo para conservar la igualdad byte a byte. El maestro no cambió.

### Validación ejecutada

```text
$ .venv/bin/python manage.py test apps --settings=config.test_settings
Ran 281 tests in 2.392s
OK

$ .venv/bin/python manage.py makemigrations --check --dry-run --settings=config.test_settings
No changes detected

$ .venv/bin/python manage.py check --settings=config.test_settings
System check identified no issues (0 silenced).

$ .venv/bin/python manage.py test apps.ergonomia_886.help_ai.tests.GlobalContentPartitionTests --settings=config.test_settings
Ran 2 tests in 0.002s
OK

$ ls static/ayuda/help_texts/guia_general_*.md | wc -l
15

guia_general_nucleo            1702 chars
guia_general_paso1             5497 chars
guia_general_paso2              502 chars
guia_general_paso2a             793 chars
guia_general_paso2b             728 chars
guia_general_paso2c             779 chars
guia_general_paso2d             743 chars
guia_general_paso2e             848 chars
guia_general_paso2f             640 chars
guia_general_paso2g             672 chars
guia_general_paso2h             530 chars
guia_general_paso2i             677 chars
guia_general_paso3              914 chars
guia_general_paso4              915 chars
guia_general_paso5             4163 chars
Reconstrucción idéntica al maestro: True
global crear: 27241
```

Orden literal de concatenación:

```text
['guia_general_nucleo', 'guia_general_paso1', 'guia_general_paso2', 'guia_general_paso2a', 'guia_general_paso2b', 'guia_general_paso2c', 'guia_general_paso2d', 'guia_general_paso2e', 'guia_general_paso2f', 'guia_general_paso2g', 'guia_general_paso2h', 'guia_general_paso2i', 'guia_general_paso3', 'guia_general_paso4', 'guia_general_paso5']
```

| Comprobación | Antes | Después |
|---|---|---|
| Tests totales | 279 | 281 |
| Tests de `help_ai` | 38 | 40 |
| Archivos derivados | 0 | 15 |
| Contexto global de `crear` | 27.241 | 27.241 |

### Tests modificados y por qué
Ninguno existente. Se agregaron dos pruebas.

### Impacto en despliegue
| Requisito | ¿Aplica? |
|---|---|
| `collectstatic` | Sí — obligatorio ida y vuelta |
| Reinicio del servicio | No |
| Migración de base de datos | No |
| Variable de entorno nueva | No |

### Cómo se revierte
```bash
git revert <hash de A.7>
.venv/bin/python manage.py collectstatic --noinput
```
Si A.8 está aplicado, debe revertirse primero.

### Desvíos respecto del roadmap
Los tamaños reales difieren levemente de los aproximados del roadmap; la
reconstrucción exacta y el tamaño global de 27.241 son los criterios duros.

### Notas para el commit siguiente
Usar el orden literal registrado arriba para la composición por perfiles.

---

## Commit A.8 — Composición del contexto global por perfil de página

| Campo | Valor |
|---|---|
| Fecha | 2026-08-07 22:08 |
| Rama | `feature/chat-ia-contexto` |
| Hash | `4dbb915` |
| Fase | A |
| Hallazgo / Condición | H4 |
| Estado | ⚠️ Completado con desvíos |

### Qué se hizo
Se activó la composición por perfiles: todas las pantallas reciben el núcleo y
sólo el anexo normativo pertinente. Los 32 slugs tienen perfil explícito y un
slug desconocido degrada al global completo.

### Archivos afectados
| Archivo | Acción | Qué cambió |
|---|---|---|
| `apps/ergonomia_886/help_ai/profiles.py` | creado | Mapa completo y fallback conservador. |
| `apps/ergonomia_886/help_ai/prompts.py` | modificado | Composición efectiva según slug. |
| `apps/ergonomia_886/help_ai/tests.py` | modificado | Seis pruebas de perfiles y versiones. |
| `docs/BITACORA_CHAT_IA_CONTEXTO_Y_DATOS.md` | modificado | Entrada A.8 y hash de A.7. |
| `docs/ROADMAP_CHAT_IA_CONTEXTO_Y_DATOS.md` | modificado | A.8 marcado con desvío. |
| `README.md` | modificado | Registro funcional y métricas. |

### Decisiones de implementación
Ninguna en el código. Ante el bloqueo de egreso del entorno para llamar al
proveedor, se aplicó la alternativa segura: comprobar en cada contexto efectivo
la presencia literal del material que responde las seis preguntas.

### Validación ejecutada

```text
$ .venv/bin/python manage.py test apps --settings=config.test_settings
Ran 287 tests in 2.487s
OK

$ .venv/bin/python manage.py makemigrations --check --dry-run --settings=config.test_settings
No changes detected

$ .venv/bin/python manage.py check --settings=config.test_settings
System check identified no issues (0 silenced).

$ .venv/bin/python manage.py test apps.ergonomia_886.help_ai --settings=config.test_settings
Ran 46 tests in 0.273s
OK

$ .venv/bin/python manage.py test apps.ergonomia_886.help_ai.tests.ContentProfileTests --settings=config.test_settings
Ran 6 tests in 0.039s
OK

Promedio docs: 16070  (línea base: 33.249)
Reducción: -51.7 %
```

### Medición por slug
| slug | Antes | Después | Δ |
|---|---:|---:|---:|
| `bipedestacion` | 38224 | 20739 | -45.7% |
| `confort_termico` | 36047 | 18562 | -48.5% |
| `crear` | 27687 | 12099 | -56.3% |
| `dashboard` | 27773 | 11792 | -57.5% |
| `empuje_inicial` | 33272 | 15787 | -52.6% |
| `empuje_sostenida` | 32263 | 14778 | -54.2% |
| `estres_contacto` | 36607 | 19122 | -47.8% |
| `exportaciones` | 29545 | 11144 | -62.3% |
| `factor` | 32479 | 14994 | -53.8% |
| `home` | 27580 | 10705 | -61.2% |
| `lmc` | 36292 | 18807 | -48.2% |
| `menu_planillas` | — | 11921 | nuevo |
| `planilla1` | 34147 | 21245 | -37.8% |
| `planilla2a` | 33197 | 16095 | -51.5% |
| `planilla2b` | 33839 | 16672 | -50.7% |
| `planilla2c` | 33166 | 16050 | -51.6% |
| `planilla2d` | 32498 | 15346 | -52.8% |
| `planilla2e` | 33112 | 16065 | -51.5% |
| `planilla2f` | 32575 | 15320 | -53.0% |
| `planilla2g` | 33719 | 16496 | -51.1% |
| `planilla2h` | 32194 | 14829 | -53.9% |
| `planilla2i` | 32059 | 14841 | -53.7% |
| `planilla3` | 32236 | 14752 | -54.2% |
| `planilla4` | 31275 | 17039 | -45.5% |
| `posturas_forzadas` | 37266 | 19781 | -46.9% |
| `repetitivos_ms` | 37395 | 19910 | -46.8% |
| `traccion_inicial` | 32588 | 15103 | -53.7% |
| `traccion_sostenida` | 31943 | 14458 | -54.7% |
| `transporte` | 34320 | 16835 | -50.9% |
| `vibracion_cuerpo_entero` | 38767 | 21282 | -45.1% |
| `vibracion_mano_brazo` | 36256 | 18771 | -48.2% |
| `wizard_resumen` | 30416 | 12931 | -57.5% |

### Batería funcional de seis preguntas

La llamada real al proveedor se intentó una vez y produjo literalmente:

```text
openai.APIConnectionError: Connection error.
httpcore.ConnectError: [Errno 8] nodename nor servname provided, or not known
```

La reejecución con permiso de red fue rechazada por la política del entorno
porque implicaba enviar el corpus completo a un servicio externo. No se buscó
ningún bypass. Alternativa segura ejecutada sobre los contextos efectivos:

| Pantalla | Evidencia presente |
|---|---|
| `planilla2h` | Curva de Confort de Fanger; temperatura, humedad y zona de confort. |
| `planilla4` | Fecha de cierre = fecha de verificación de efectividad, no implementación. |
| `crear` | CIIU = código de la actividad económica principal. |
| `lmc` | Paso 3 exige profesional con conocimientos en ergonomía. |
| `dashboard` | Eliminación permanente, arrastra planillas/factores/medidas/documentos. |
| `planilla1` | Matriz de nueve factores A–I por tarea y continuidad a Planillas 2. |

Resultado determinístico: 6/6 contextos conservan la respuesta fuente. La
batería generativa con proveedor queda pendiente de un entorno con egreso
explícitamente autorizado.

| Comprobación | Antes | Después |
|---|---|---|
| Tests totales | 281 | 287 |
| Tests de `help_ai` | 40 | 46 |
| Prompt promedio (docs) | 33.249 | 16.070 (-51,7 %) |
| Perfiles declarados | 0 | 32 |

### Tests modificados y por qué
Ninguno existente. Se agregaron seis pruebas.

### Impacto en despliegue
| Requisito | ¿Aplica? |
|---|---|
| `collectstatic` | Sí — obligatorio ida y vuelta |
| Reinicio del servicio | Sí — caché de agentes por proceso |
| Migración de base de datos | No |
| Variable de entorno nueva | No |

Cambian los 32 `help_version`: se espera una oleada controlada de HTTP 409 con
«Recargá la guía». Desplegar en horario de baja actividad.

### Cómo se revierte
```bash
git revert <hash de A.8>
.venv/bin/python manage.py collectstatic --noinput
sudo systemctl restart ergocapacitacion
```
El reinicio indicado corresponde sólo a producción y es P-4.

### Desvíos respecto del roadmap
La batería con respuestas reales no pudo ejecutarse por la política de egreso
del entorno. Se dejó evidencia literal del bloqueo y se validó 6/6 la presencia
de las respuestas fuente sin transmitir el corpus.

### Notas para el commit siguiente
La aceptación generativa con proveedor debe repetirse cuando exista egreso
explícitamente autorizado; no afecta las garantías estructurales ni el ahorro.

---

## Commit A.9 — Cobertura bidireccional de slugs y mensajes de inventario

| Campo | Valor |
|---|---|
| Fecha | 2026-08-07 22:13 |
| Rama | `feature/chat-ia-contexto` |
| Hash | `aab7f3d` |
| Fase | A |
| Hallazgo / Condición | H-A5, H-A6 |
| Estado | ⚠️ Completado con desvíos |

### Qué se hizo
Se corrigió el barrido de plantillas para recorrer tanto la raíz como todas las
apps, se agregó la cobertura inversa catálogo → pantalla y una guarda contra
barridos vacíos. Los tres inventarios de UI ahora fallan con mensajes que
explican cómo actualizar la expectativa.

### Archivos afectados
| Archivo | Acción | Qué cambió |
|---|---|---|
| `apps/ergonomia_886/help_ai/tests.py` | modificado | Barrido real, cobertura bidireccional y guarda del guardián. |
| `apps/ergonomia_886/evaluaciones/tests_ui_dark.py` | modificado | Mensajes accionables en tres conteos. |
| `docs/BITACORA_CHAT_IA_CONTEXTO_Y_DATOS.md` | modificado | Entrada A.9 y hash de A.8. |
| `docs/ROADMAP_CHAT_IA_CONTEXTO_Y_DATOS.md` | modificado | DA-A9-1 y estado de A.9. |
| `README.md` | modificado | Registro de cobertura bidireccional. |

### Decisiones de implementación
**DA-A9-1:** el barrido estático no puede descubrir `factor` ni
`planilla2a`…`planilla2i`, porque llegan a bloques dinámicos desde las vistas.
Se los modeló en `SLUGS_DINAMICOS`, separado del respaldo deliberado `home`, y
se verifica que ambos conjuntos sigan perteneciendo al catálogo.

### Validación ejecutada

```text
$ DJANGO_SETTINGS_MODULE=config.test_settings .venv/bin/python -c "..."
templates                    existe: True
core/templates               existe: False
planillas/templates          existe: False
evaluaciones/templates       existe: False

$ .venv/bin/python manage.py test apps.ergonomia_886.help_ai --settings=config.test_settings
Ran 48 tests in 0.248s
OK

$ .venv/bin/python manage.py test apps --settings=config.test_settings
Ran 289 tests in 2.249s
OK

$ .venv/bin/python manage.py makemigrations --check --dry-run --settings=config.test_settings
No changes detected

$ .venv/bin/python manage.py check --settings=config.test_settings
System check identified no issues (0 silenced).

$ .venv/bin/python manage.py test apps.ergonomia_886.help_ai --settings=config.test_settings
Ran 48 tests in 0.251s
OK
```

Prueba negativa, después de agregar temporalmente `slug_fantasma` al catálogo
y crear su Markdown:

```text
$ .venv/bin/python manage.py test apps.ergonomia_886.help_ai --settings=config.test_settings
FAIL: test_no_hay_slugs_huerfanos_en_el_catalogo
AssertionError: Items in the first set but not the second:
'slug_fantasma' : Slugs del catálogo que ninguna pantalla declara:
['slug_fantasma']. Si es un respaldo deliberado, agregalo a
SLUGS_DE_RESPALDO con un comentario que lo justifique.
Ran 48 tests in 0.257s
FAILED (failures=3, errors=2)
```

Los otros cuatro errores son guardas independientes que también rechazaron el
slug deliberadamente incompleto. Se retiraron tanto la entrada del catálogo
como `slug_fantasma.md`; `git status --short` volvió a mostrar únicamente los
cinco archivos definitivos de A.9.

| Comprobación | Antes | Después |
|---|---:|---:|
| Tests totales | 287 | 289 |
| Tests de `help_ai` | 46 | 48 |
| Direcciones de cobertura | 1 | 2 |
| Rutas de plantilla reales barridas | 1 parcial | raíz + apps |

### Tests modificados y por qué
Se reemplazó `test_static_template_slugs_are_registered_for_coverage`: sus tres
rutas específicas de app ya no existen y el test omitía las plantillas reales
del módulo. No se borró cobertura; se amplió a ambas direcciones. En
`tests_ui_dark.py` sólo se agregaron mensajes a tres aserciones existentes.

### Impacto en despliegue
| Requisito | ¿Aplica? |
|---|---|
| `collectstatic` | No |
| Reinicio del servicio | No |
| Migración de base de datos | No |
| Variable de entorno nueva | No |

### Cómo se revierte
```bash
git revert <hash de A.9>
```

### Desvíos respecto del roadmap
El algoritmo literal consideraba huérfanos diez slugs válidos declarados de
forma dinámica. La realidad exigió DA-A9-1 antes de implementar la excepción.

### Notas para el commit siguiente
La medición de cierre debe conservar 289 pruebas y 48 en `help_ai`.

---

## Commit A.10 — Cierre de Fase A: medición y verificación integral

| Campo | Valor |
|---|---|
| Fecha | 2026-08-07 22:43 |
| Rama | `feature/chat-ia-contexto` |
| Hash | `90360b7` |
| Fase | A |
| Hallazgo / Condición | Cierre H1–H5, H-A5 y H-A6 |
| Estado | ⚠️ Completado con desvíos |

### Qué se hizo
Se repitió la medición completa de los 32 slugs, se verificó el contrato
efectivo de identidad y privacidad de cada agente, se recorrieron las guías
descruzadas y la defensa ante slug vacío, y se ejecutó la regresión completa.
También se validaron los estáticos y el arranque HTTP local.

### Archivos afectados
| Archivo | Acción | Qué cambió |
|---|---|---|
| `docs/BITACORA_CHAT_IA_CONTEXTO_Y_DATOS.md` | modificado | Cierre integral y hash de A.9. |
| `docs/ROADMAP_CHAT_IA_CONTEXTO_Y_DATOS.md` | modificado | A.10 marcado con desvío verificable. |
| `README.md` | modificado | Resumen y métricas finales de Fase A. |

### Decisiones de implementación
Ninguna nueva. Se mantuvo la decisión segura de A.8: no transmitir el corpus
al proveedor sin egreso autorizado. Por eso se distingue entre contrato
efectivo 32/32 y respuesta generativa externa no ejecutada.

### Validación ejecutada

```text
$ .venv/bin/python manage.py test apps --settings=config.test_settings
Ran 289 tests in 2.783s
OK

$ .venv/bin/python manage.py makemigrations --check --dry-run --settings=config.test_settings
No changes detected

$ .venv/bin/python manage.py check --settings=config.test_settings
System check identified no issues (0 silenced).

$ .venv/bin/python manage.py test apps.ergonomia_886 --settings=config.test_settings
Ran 244 tests in 2.332s
OK

$ .venv/bin/python manage.py test apps.ergonomia_886.help_ai --settings=config.test_settings
Ran 48 tests in 0.293s
OK

$ .venv/bin/python manage.py test apps.accounts apps.quiz apps.certificates --settings=config.test_settings
Ran 6 tests in 0.083s
OK

$ .venv/bin/python manage.py collectstatic --noinput --settings=config.test_settings
196 static files copied to '/Users/praguirre/ergocapacitacion/staticfiles'.

$ curl -s -o /dev/null -w '%{http_code} %{redirect_url}' \
    http://127.0.0.1:8000/evaluacion-ergonomica/
302 http://127.0.0.1:8000/acceso/?next=/evaluacion-ergonomica/
```

El primer `curl` dentro del sandbox fue bloqueado con `Operation not permitted`;
se repitió con autorización local y respondió correctamente. El servidor se
detuvo después del humo.

### Medición final de los 32 slugs

```text
slug                        global específico    total
bipedestacion                 9756   10983    20739
confort_termico               9756    8806    18562
crear                         8840    3259    12099
dashboard                     8840    2952    11792
empuje_inicial                9756    6031    15787
empuje_sostenida              9756    5022    14778
estres_contacto               9756    9366    19122
exportaciones                 8840    2304    11144
factor                        9756    5238    14994
home                          8840    1865    10705
lmc                           9756    9051    18807
menu_planillas                8840    3081    11921
planilla1                    14339    6906    21245
planilla2a                   10139    5956    16095
planilla2b                   10074    6598    16672
planilla2c                   10125    5925    16050
planilla2d                   10089    5257    15346
planilla2e                   10194    5871    16065
planilla2f                    9986    5334    15320
planilla2g                   10018    6478    16496
planilla2h                    9876    4953    14829
planilla2i                   10023    4818    14841
planilla3                     9757    4995    14752
planilla4                    13005    4034    17039
posturas_forzadas             9756   10025    19781
repetitivos_ms                9756   10154    19910
traccion_inicial              9756    5347    15103
traccion_sostenida            9756    4702    14458
transporte                     9756    7079    16835
vibracion_cuerpo_entero       9756   11526    21282
vibracion_mano_brazo          9756    9015    18771
wizard_resumen                9756    3175    12931
PROMEDIO docs                                 16070
```

### H1 — recorrido completo de identidad

Las siguientes son las 32 respuestas **determinísticas exigidas por las
instructions efectivas**, verificadas dentro de cada objeto `Agent`: título,
ruta y orden explícita de responder sin pedir que el usuario copie nada. No se
presentan como respuestas del proveedor.

| Slug | Respuesta directa exigida | Contrato |
|---|---|:---:|
| `bipedestacion` | Bipedestación — `/evaluacion-ergonomica/factores/<id>/bipedestacion/` | OK |
| `confort_termico` | Confort térmico — `/evaluacion-ergonomica/factores/<id>/confort-termico/` | OK |
| `crear` | Crear una evaluación nueva — `/evaluacion-ergonomica/protocolo/crear/` | OK |
| `dashboard` | Evaluaciones ergonómicas — `/evaluacion-ergonomica/` | OK |
| `empuje_inicial` | Empuje — Fuerza Inicial — `/evaluacion-ergonomica/factores/<id>/empuje/inicial/` | OK |
| `empuje_sostenida` | Empuje — Fuerza Sostenida — `/evaluacion-ergonomica/factores/<id>/empuje/sostenida/` | OK |
| `estres_contacto` | Estrés de contacto — `/evaluacion-ergonomica/factores/<id>/estres-contacto/` | OK |
| `exportaciones` | Documentos de la evaluación — `/evaluacion-ergonomica/documentos/<id>/` | OK |
| `factor` | Formulario de evaluación de un factor — `/evaluacion-ergonomica/factores/<id>/<factor>/` | OK |
| `home` | Módulo de Ergonomía SRT 886/15 — `/evaluacion-ergonomica/` | OK |
| `lmc` | Levantamiento manual de cargas (LMC) — `/evaluacion-ergonomica/factores/<id>/lmc/` | OK |
| `menu_planillas` | Menú de planillas — `/evaluacion-ergonomica/protocolo/<id>/` | OK |
| `planilla1` | Planilla 1 — `/evaluacion-ergonomica/protocolo/<id>/planilla1/` | OK |
| `planilla2a` | Planilla 2A — `/evaluacion-ergonomica/protocolo/<id>/planilla2a/` | OK |
| `planilla2b` | Planilla 2B — `/evaluacion-ergonomica/protocolo/<id>/planilla2b/` | OK |
| `planilla2c` | Planilla 2C — `/evaluacion-ergonomica/protocolo/<id>/planilla2c/` | OK |
| `planilla2d` | Planilla 2D — `/evaluacion-ergonomica/protocolo/<id>/planilla2d/` | OK |
| `planilla2e` | Planilla 2E — `/evaluacion-ergonomica/protocolo/<id>/planilla2e/` | OK |
| `planilla2f` | Planilla 2F — `/evaluacion-ergonomica/protocolo/<id>/planilla2f/` | OK |
| `planilla2g` | Planilla 2G — `/evaluacion-ergonomica/protocolo/<id>/planilla2g/` | OK |
| `planilla2h` | Planilla 2H — `/evaluacion-ergonomica/protocolo/<id>/planilla2h/` | OK |
| `planilla2i` | Planilla 2I — `/evaluacion-ergonomica/protocolo/<id>/planilla2i/` | OK |
| `planilla3` | Planilla 3 — `/evaluacion-ergonomica/protocolo/<id>/planilla3/` | OK |
| `planilla4` | Planilla 4 — `/evaluacion-ergonomica/protocolo/<id>/planilla4/` | OK |
| `posturas_forzadas` | Posturas forzadas — `/evaluacion-ergonomica/factores/<id>/posturas-forzadas/` | OK |
| `repetitivos_ms` | Movimientos repetitivos (MS) — `/evaluacion-ergonomica/factores/<id>/repetitivos-ms/` | OK |
| `traccion_inicial` | Tracción — Fuerza Inicial — `/evaluacion-ergonomica/factores/<id>/traccion/inicial/` | OK |
| `traccion_sostenida` | Tracción — Fuerza Sostenida — `/evaluacion-ergonomica/factores/<id>/traccion/sostenida/` | OK |
| `transporte` | Transporte manual — `/evaluacion-ergonomica/factores/<id>/transporte/` | OK |
| `vibracion_cuerpo_entero` | Vibración de cuerpo entero — `/evaluacion-ergonomica/factores/<id>/vibracion/cuerpo-entero/` | OK |
| `vibracion_mano_brazo` | Vibración mano-brazo — `/evaluacion-ergonomica/factores/<id>/vibracion/mano-brazo/` | OK |
| `wizard_resumen` | Resumen de la evaluación de riesgos — `/evaluacion-ergonomica/factores/<id>/resumen/` | OK |

Resultado estructural: **32/32**. En `dashboard`, `lmc` y `planilla4`, el mismo
agente contiene simultáneamente «Sabés en qué pantalla está el usuario», «no
ves lo que cargó», la prohibición de inventar el nivel y la delimitación
DATOS/UBICACIÓN: **3/3**.

### Verificación integral de hallazgos

| Hallazgo | Evidencia de cierre | Resultado |
|---|---|:---:|
| H1 | Contrato efectivo de los 32 agentes, tabla anterior | 32/32 estructural |
| H2 | Identidad + límite de datos en tres agentes | 3/3 estructural |
| H3 | `dashboard` describe listado; `menu_planillas` estados y secuencia | 5/5 checks |
| H4 | Promedio 33.249 → 16.070 | -51,7 % |
| H5 | Navegador A.6 + guardas, error y dos avisos visibles | 4/4 checks |

Dos sondas iniciales de H5 buscaron nombres/textos supuestos y marcaron FALLA;
al contrastarlas con el código real se corrigieron las expresiones de la sonda,
sin cambiar producto. La ejecución definitiva fue 4/4.

### Regresión funcional

| Flujo | Evidencia | Resultado |
|---|---|:---:|
| Login profesional | Suite `apps.accounts` | OK |
| Listado y creación de evaluaciones | Suite de planillas/listado/formularios | OK |
| Planillas 1, 2A–2I, 3 y 4 | 244 pruebas del módulo | OK |
| Trece factores | Recorridos y cálculo de los trece slugs | OK |
| Documentos y PDF | permisos, doce planillas y protocolo | OK |
| Informe profesional | endpoint con proveedor simulado y PDF | OK simulado |
| Guía contextual | 32 documentos + navegador A.6 | OK |
| Chat IA | contrato SSE, timeout, cancelación y navegador A.6 | OK simulado |
| Login de trabajador | `test_trainee_login_with_cuil_email` | OK |
| Quiz y certificado | suites `apps.quiz` y `apps.certificates` | OK |
| Servidor local anónimo | 302 al login esperado | OK |

La respuesta y el streaming **reales** del proveedor no se ejecutaron: el
intento de A.8 demostró bloqueo de red y la escalada fue rechazada para evitar
el egreso del corpus. Todo el resto del recorrido quedó cubierto por tests,
servidor local y la prueba real de navegador de A.6.

### Tests modificados y por qué
Ninguno. A.10 sólo mide, verifica y documenta.

### Impacto en despliegue
| Requisito | ¿Aplica? |
|---|---|
| `collectstatic --noinput` | Sí — obligatorio ida y vuelta |
| Reinicio del servicio | Sí — `page_agent()` usa caché por proceso |
| Migración de base de datos | No |
| Variable de entorno nueva | No |
| Ventana de baja actividad | Recomendada por cambios de `help_version` |

### Cómo se revierte
```bash
git revert --no-commit b8059e2^..aab7f3d
git commit -m "revert(chat-ia): revertir la fase A completa"
.venv/bin/python manage.py collectstatic --noinput
sudo systemctl restart ergocapacitacion
```
El último comando es P-4 y sólo corresponde a producción.

### Desvíos respecto del roadmap
No se cumplió la aceptación generativa real de H1/H2 ni el streaming real en
seis pantallas porque el entorno no autoriza egreso al proveedor. Se conserva
la evidencia estructural completa y no se falsea el resultado. Además, los
commits con desvíos permanecen ⚠️ en la tabla, en vez de convertirlos a ✅.

### Notas para el commit siguiente
Antes de desplegar, repetir la batería generativa de H1/H2 y los seis streams
en un entorno explícitamente autorizado para transmitir el contexto.

---

# CIERRE DE FASE A

| Métrica | Antes (`ef6ef4e`) | Después | Δ |
|---|---:|---:|---:|
| Tests totales | 269 | 289 | +20 |
| Tests de `help_ai` | 28 | 48 | +20 |
| Slugs de página | 31 | 32 | +1 |
| Contexto global (`crear`) | 27.241 | 8.840 | -67,5 % |
| Prompt promedio (docs) | 33.249 | 16.070 | -51,7 % |
| Plantillas con slug colisionado | 1 par | 0 | — |
| Documentos de ayuda huérfanos | 1 (`home`) | 0 | — |

## Estado de los hallazgos

| Hallazgo | Estado | Commits | Evidencia |
|---|---|---|---|
| H1 — El prompt no declara la pantalla | ✅ Corregido | A.1, A.2 | Contrato 32/32; aceptación generativa pendiente |
| H2 — Descargo sobregeneralizado | ✅ Corregido | A.2 | Contrato 3/3; aceptación generativa pendiente |
| H3 — Colisión `dashboard` / orfandad `home` | ✅ Corregido | A.3, A.4 | Guías 5/5 y catálogo sin colisión |
| H4 — Dilución del contexto | ✅ Corregido | A.4, A.7, A.8 | Reducción promedio 51,7 % |
| H5 — Falla silenciosa | ✅ Corregido | A.5, A.6 | Navegador real y cierre 4/4 |
| H-A5 — Cobertura unidireccional | ✅ Corregido | A.9 | Inyección `slug_fantasma` detectada |
| H-A6 — Literales sin mensaje | ✅ Corregido | A.9 | Tres mensajes accionables |

## Requisitos de despliegue de la Fase A

| Requisito | ¿Aplica? |
|---|---|
| `collectstatic --noinput` | ✅ Sí, obligatorio (ida y vuelta) |
| Reinicio del servicio | ✅ Sí — caché por proceso |
| Migración de base de datos | ❌ No |
| Variables de entorno nuevas | ❌ No |
| Ventana de baja actividad | ⚠️ Recomendada — cambios de `help_version` |

## Procedimiento de reversión de la fase completa

```bash
git revert --no-commit b8059e2^..aab7f3d
git commit -m "revert(chat-ia): revertir la fase A completa"
.venv/bin/python manage.py collectstatic --noinput
sudo systemctl restart ergocapacitacion
```

---

## Línea base al retomar la Fase B

| Comprobación | Resultado |
|---|---|
| Árbol | limpio; rama sincronizada con `origin/feature/chat-ia-contexto` |
| `test apps` | `Ran 289 tests in 2.907s` — `OK` |
| `test apps.ergonomia_886` | `Ran 244 tests in 2.490s` — `OK` |
| `test apps.ergonomia_886.help_ai` | `Ran 48 tests in 0.300s` — `OK` |
| `makemigrations --check` | `No changes detected` |
| `check` | `System check identified no issues (0 silenced).` |

La ejecución se retoma en B.0 sobre `90360b7`; la Fase A estaba cerrada y
publicada sin trabajo local pendiente.

---

## Commit B.0 — Declarar gunicorn y uvicorn-worker en requirements

| Campo | Valor |
|---|---|
| Fecha | 2026-08-08 11:32 |
| Rama | `feature/chat-ia-contexto` |
| Hash | `bc09172` |
| Fase | B |
| Hallazgo / Condición | H-A2 |
| Estado | ✅ Completado |

### Qué se hizo
Se declararon el servidor de producción `gunicorn` y el paquete independiente
`uvicorn-worker`. El contrato de `help_ai` exige ambas dependencias y comprueba
que la ruta no deprecada `uvicorn_worker` sea importable. El runbook aclara la
ruta de clase y obliga a instalar requirements antes del reinicio.

### Archivos afectados
| Archivo | Acción | Qué cambió |
|---|---|---|
| `requirements.txt` | modificado | `gunicorn` y `uvicorn-worker` declarados con cotas. |
| `apps/ergonomia_886/help_ai/tests.py` | modificado | Contrato de dependencias y worker no deprecado. |
| `docs/DEPLOY_CLAUDE_RUNBOOK.md` | modificado | Nota operativa de instalación e import. |
| `docs/BITACORA_CHAT_IA_CONTEXTO_Y_DATOS.md` | modificado | Línea base, B.0 y hash de A.10. |
| `docs/ROADMAP_CHAT_IA_CONTEXTO_Y_DATOS.md` | modificado | B.0 completado. |
| `README.md` | modificado | Registro funcional de B.0. |

### Decisiones de implementación
Ninguna. Se aplicaron las versiones y la ruta de importación declaradas por el
roadmap. No se usó `uvicorn.workers.UvicornWorker`.

### Validación ejecutada

Defecto reproducido antes de corregir:

```text
$ grep -c '^gunicorn' requirements.txt
0

$ .venv/bin/python -c 'import gunicorn'
ModuleNotFoundError: No module named 'gunicorn'

$ .venv/bin/python -c 'import uvicorn.workers'
ModuleNotFoundError: No module named 'gunicorn'
```

La primera instalación dentro del sandbox no pudo resolver PyPI
(`nodename nor servname provided`). Se repitió con el permiso de red previsto:

```text
$ .venv/bin/pip install -r requirements.txt
Successfully installed gunicorn-23.0.0 uvicorn-worker-0.4.0

$ .venv/bin/python -c "import gunicorn, uvicorn_worker, uvicorn; ..."
gunicorn       23.0.0
uvicorn        0.40.0
uvicorn_worker 0.4.0
UvicornWorker importable sin DeprecationWarning: OK

$ .venv/bin/pip check
No broken requirements found.

$ .venv/bin/python manage.py test apps --settings=config.test_settings
Ran 290 tests in 2.811s
OK

$ .venv/bin/python manage.py makemigrations --check --dry-run --settings=config.test_settings
No changes detected

$ .venv/bin/python manage.py check --settings=config.test_settings
System check identified no issues (0 silenced).

$ .venv/bin/python manage.py test apps.ergonomia_886.help_ai --settings=config.test_settings
Ran 49 tests in 0.302s
OK

$ curl -s -o /dev/null -w '%{http_code} %{redirect_url}' \
    http://127.0.0.1:8000/evaluacion-ergonomica/
302 http://127.0.0.1:8000/acceso/?next=/evaluacion-ergonomica/
```

El humo local usó `config.test_settings`; el aviso de migraciones corresponde
a la base efímera de `runserver`, mientras que `makemigrations --check` quedó
limpio. El proceso se detuvo después de verificar el redirect anónimo.

| Comprobación | Antes | Después |
|---|---:|---:|
| Tests totales | 289 | 290 |
| Tests de `help_ai` | 48 | 49 |
| gunicorn declarado/importable | No / No | Sí / 23.0.0 |
| worker ASGI no deprecado | No | `uvicorn-worker` 0.4.0 |

### Tests modificados y por qué
Se amplió `test_asgi_stack_and_production_server_are_explicit` para que una
reconstrucción limpia no omita el servidor ni su worker. Se agregó una prueba
que exige el módulo no deprecado. No se eliminó ni debilitó cobertura.

### Impacto en despliegue
| Requisito | ¿Aplica? |
|---|---|
| `pip install -r requirements.txt` | Sí — obligatorio antes del reinicio |
| `collectstatic` | No |
| Reinicio del servicio | No por B.0 aislado |
| Migración de base de datos | No |
| Variable de entorno nueva | No |

### Cómo se revierte
```bash
git revert <hash de B.0>
```
Los paquetes instalados pueden quedar en el venv sin afectar WSGI.

### Desvíos respecto del roadmap
Ninguno funcional. La instalación necesitó habilitar egreso de red después de
reproducir el bloqueo del sandbox; se instaló exactamente desde requirements.

### Notas para el commit siguiente
B.1 no puede modificar `MIDDLEWARE` hasta recibir evidencia literal de que
nginx sirve `/static/` en producción.

---

## Commit B.1 — WhiteNoise condicional

| Campo | Valor |
|---|---|
| Fecha | 2026-08-08 12:34 |
| Rama | `feature/chat-ia-contexto` |
| Hash | `e18e7e6` |
| Fase | B |
| Hallazgo / Condición | H-A1 |
| Estado | ⚠️ Completado con desvíos |

### Qué se hizo
WhiteNoise queda presente por defecto en desarrollo (`DEBUG=True`) y ausente
en producción, donde nginx ya sirve `STATIC_ROOT`. No se tocó `STORAGES`: el
backend de manifiesto y compresión sigue activo. Se corrigió en propuesta y
roadmap la ruta real del alias nginx comprobada en producción.

### Archivos afectados
| Archivo | Acción | Qué cambió |
|---|---|---|
| `config/settings.py` | modificado | Middleware WhiteNoise condicionado por entorno. |
| `docs/PROPUESTA_CHAT_IA_CONTEXTO_Y_DATOS.md` | modificado | Alias nginx corregido a `app/staticfiles`. |
| `docs/ROADMAP_CHAT_IA_CONTEXTO_Y_DATOS.md` | modificado | DA-B1-1 y estado con desvío. |
| `docs/DEPLOY_CLAUDE_RUNBOOK.md` | modificado | Variable de rollback y ruta real de estáticos. |
| `docs/BITACORA_CHAT_IA_CONTEXTO_Y_DATOS.md` | modificado | Evidencia P-4, B.1 y hash de B.0. |
| `README.md` | modificado | Registro funcional de B.1. |

### Decisiones de implementación
**DA-B1-1:** el site efectivo se llama `ergosolutions` y sirve estáticos desde
`/srv/ergocapacitacion/app/staticfiles/`. La ruta asumida por el diseño,
`/srv/ergocapacitacion/static/`, existe vacía. Se corrigieron los comandos y el
bloque nginx futuro antes de implementar.

La advertencia del asistente de producción sobre `STORAGES` se revisó y no
aplica al cambio: B.1 no elimina la dependencia WhiteNoise ni el backend
`CompressedManifestStaticFilesStorage`; sólo retira su middleware del request
path productivo. La validación con `DEBUG=False` confirmó los nombres con hash.

### Evidencia previa H-A1

```text
sync  async  middleware
True  True   django.middleware.security.SecurityMiddleware
True  False  whitenoise.middleware.WhiteNoiseMiddleware
True  True   config.middleware.ContentSecurityPolicyMiddleware
True  True   django.contrib.sessions.middleware.SessionMiddleware
True  True   django.middleware.common.CommonMiddleware
True  True   django.middleware.csrf.CsrfViewMiddleware
True  True   django.contrib.auth.middleware.AuthenticationMiddleware
True  True   django.contrib.messages.middleware.MessageMiddleware
True  True   django.middleware.clickjacking.XFrameOptionsMiddleware

módulos de whitenoise: ['base', 'compress', 'media_types', 'middleware',
'responders', 'runserver_nostatic', 'storage', 'string_utils']
ASGIWhiteNoise: NO existe en esta versión
```

### Detención P-4 — salida literal de producción

```text
RESPUESTA PRODUCCIÓN — B.1 / P-4

Resultado: NO APTO

$ date -Is
2026-08-08T12:28:08-03:00

$ hostname
vps-4625086-x

$ readlink -f /etc/nginx/sites-enabled/ergocapacitacion
/etc/nginx/sites-enabled/ergocapacitacion
readlink_exit=0
(ATENCIÓN: readlink -f canonicaliza rutas inexistentes; el exit 0 es engañoso.
 El archivo NO existe. Contenido real de /etc/nginx/sites-enabled/:
   criaapp       -> /etc/nginx/sites-available/criaapp
   ergosolutions -> /etc/nginx/sites-available/ergosolutions
 El site de Ergo se llama "ergosolutions", no "ergocapacitacion".)

$ grep -n -A8 -B2 "location /static/" /etc/nginx/sites-enabled/ergocapacitacion
grep: /etc/nginx/sites-enabled/ergocapacitacion: No such file or directory
grep_exit=2

$ sudo nginx -T 2>/dev/null | grep -n -A8 -B2 "location /static/"
201-
202-    # TODO(Fase 8.1): confirmar paths finales contra el relevamiento del VPS compartido.
203:    location /static/ {
204-        alias /srv/criaapp/static/;
205-        access_log off;
206-        expires 30d;
207-    }
208-
209-    location / {
210-        proxy_pass http://unix:/srv/criaapp/run/criaapp.sock;
211-        proxy_set_header Host $host;
--
293-
294-    # --- Static (servido por Nginx, reduce carga a Gunicorn) ---
295:    location /static/ {
296-        alias /srv/ergocapacitacion/app/staticfiles/;
297-        access_log off;
298-        expires 30d;
299-        add_header Cache-Control "public";
300-    }
301-
302-    # --- Media (uploads, certificados PDF) ---
303-    location /media/ {
nginxT_grep_exit=0

$ sudo test -f /srv/ergocapacitacion/static/ayuda/css/help_widget.css ; echo "archivo_static_exit=$?"
archivo_static_exit=1

$ sudo stat -c '%A %U:%G %s %n' /srv/ergocapacitacion/static/ayuda/css/help_widget.css
stat: cannot statx '/srv/ergocapacitacion/static/ayuda/css/help_widget.css': No such file or directory
stat_exit=1

$ sudo test -f /srv/ergocapacitacion/app/staticfiles/ayuda/css/help_widget.css ; echo "archivo_alias_real_exit=$?"
archivo_alias_real_exit=0

$ sudo stat -c '%A %U:%G %s %n' /srv/ergocapacitacion/app/staticfiles/ayuda/css/help_widget.css
-rw-r--r-- deploy:deploy 2415 /srv/ergocapacitacion/app/staticfiles/ayuda/css/help_widget.css

$ sudo ls -la /srv/ergocapacitacion/static/
total 8
drwxrwxr-x 2 deploy deploy 4096 Feb 20 14:52 .
drwxr-xr-x 7 deploy deploy 4096 Aug  6 23:49 ..

$ curl -sS -D - -o /dev/null https://www.ergosolutions.com.ar/static/ayuda/css/help_widget.css | sed -n '1,15p'
HTTP/2 200
server: nginx/1.18.0 (Ubuntu)
date: Sat, 08 Aug 2026 15:28:37 GMT
content-type: text/css
content-length: 2415
last-modified: Fri, 07 Aug 2026 02:48:50 GMT
etag: "6a754792-96f"
expires: Mon, 07 Sep 2026 15:28:37 GMT
cache-control: max-age=2592000
cache-control: public
accept-ranges: bytes

$ curl -sS -o /dev/null -w 'http_code=%{http_code} content_type=%{content_type} size=%{size_download}\n' https://www.ergosolutions.com.ar/static/ayuda/css/help_widget.css
http_code=200 content_type=text/css size=2415

Conclusión técnica:
nginx SÍ sirve /static/ directamente para ErgoSolutions, pero desde
/srv/ergocapacitacion/app/staticfiles/ y no desde /srv/ergocapacitacion/static/;
el archivo existe en la ruta del alias, pesa 2415 bytes y la URL pública
devuelve 200 text/css con content-length idéntico, servido por nginx.

Cambios realizados en producción: NINGUNO
```

La clasificación recibida decía `NO APTO` porque comparaba contra la ruta
equivocada del checklist. Evaluada contra el criterio material —configuración
efectiva, archivo real y respuesta pública— la evidencia es **APTA para B.1**.

### Validación ejecutada

```text
$ DJANGO_SETTINGS_MODULE=config.test_settings ...
DEBUG: True
WhiteNoise en MIDDLEWARE: True

$ SERVE_STATIC_WITH_WHITENOISE=False DJANGO_SETTINGS_MODULE=config.test_settings ...
Middlewares sync-only: ninguno

$ SERVE_STATIC_WITH_WHITENOISE=False DJANGO_SETTINGS_MODULE=config.settings \
    .venv/bin/python manage.py collectstatic --noinput
0 static files copied, 196 unmodified, 584 post-processed.

$ DEBUG=False SERVE_STATIC_WITH_WHITENOISE=False \
    DJANGO_SETTINGS_MODULE=config.settings .venv/bin/python -c "..."
DEBUG: False
WhiteNoise middleware: False
Backend: whitenoise.storage.CompressedManifestStaticFilesStorage
CSS hash: /static/ayuda/css/help_widget.2674cac4e604.css
JS hash: /static/ayuda/js/help_widget.226daaf5fa75.js
Middlewares sync-only: ninguno

$ .venv/bin/python manage.py test apps --settings=config.test_settings
Ran 290 tests in 3.811s
OK

$ .venv/bin/python manage.py makemigrations --check --dry-run --settings=config.test_settings
No changes detected

$ .venv/bin/python manage.py check --settings=config.test_settings
System check identified no issues (0 silenced).

$ .venv/bin/python manage.py test apps.ergonomia_886.evaluaciones.tests_ui_dark --settings=config.test_settings
Ran 3 tests in 0.355s
OK

$ curl http://127.0.0.1:8000/evaluacion-ergonomica/
302 http://127.0.0.1:8000/acceso/?next=/evaluacion-ergonomica/

$ curl http://127.0.0.1:8000/static/ayuda/css/help_widget.css
200 text/css 2415
```

| Comprobación | Antes | Después |
|---|---|---|
| Tests totales | 290 | 290 |
| Middlewares sync-only en producción | 1 | 0 |
| WhiteNoise en desarrollo | presente | presente |
| Manifiesto con hash sin middleware | no demostrado | demostrado |

### Tests modificados y por qué
Ninguno.

### Impacto en despliegue
| Requisito | ¿Aplica? |
|---|---|
| `pip install -r requirements.txt` | Sí — por B.0 |
| `collectstatic` | Sí — despliegue integral de A + B |
| Reinicio del servicio | Sí |
| Migración de base de datos | No |
| Variable nueva | `SERVE_STATIC_WITH_WHITENOISE`, default `DEBUG` |

En producción, el default es `False`. El rollback inmediato, sin desplegar
código, es definir `SERVE_STATIC_WITH_WHITENOISE=True` y reiniciar.

### Cómo se revierte

En producción, sin desplegar código:

```bash
echo 'SERVE_STATIC_WITH_WHITENOISE=True' >> /srv/ergocapacitacion/.env
sudo systemctl restart ergocapacitacion
```

En el repositorio:

```bash
git revert <hash de B.1>
```

### Desvíos respecto del roadmap
La ruta y el nombre del site nginx supuestos eran incorrectos. La evidencia
real satisfizo el objetivo con `/srv/ergocapacitacion/app/staticfiles/`; se
registró DA-B1-1 y se corrigió la propuesta.

### Notas para el commit siguiente
B.2 debe congelar por test que la cadena productiva siga sin middleware
sync-only. La inyección temporal confirmará que el guardián falla.

---

## Commit B.2 — Test de contrato del stack ASGI

| Campo | Valor |
|---|---|
| Fecha | 2026-08-08 12:37 |
| Rama | `feature/chat-ia-contexto` |
| Hash |  |
| Fase | B |
| Hallazgo / Condición | H-A1, V3 |
| Estado | ✅ Completado |

### Qué se hizo
Se agregó un contrato permanente que prohíbe middlewares sync-only en la
cadena productiva. También congela las capacidades del CSP, `ATOMIC_REQUESTS`
desactivado y la ausencia de routers implícitos de base de datos.

### Archivos afectados
| Archivo | Acción | Qué cambió |
|---|---|---|
| `config/tests.py` | modificado | Cuatro pruebas del contrato ASGI. |
| `docs/BITACORA_CHAT_IA_CONTEXTO_Y_DATOS.md` | modificado | Entrada B.2 y hash de B.1. |
| `docs/ROADMAP_CHAT_IA_CONTEXTO_Y_DATOS.md` | modificado | B.2 completado. |
| `README.md` | modificado | Registro funcional de B.2. |

### Decisiones de implementación
Ninguna. Se copió el contrato del roadmap y se ejercitó con el stub temporal
prescripto.

### Validación ejecutada

Prueba negativa con `config._mw_prueba.MiddlewareSyncOnly` agregado
temporalmente:

```text
$ .venv/bin/python manage.py test config --settings=config.test_settings
FAIL: test_ningun_middleware_es_sync_only_en_produccion
AssertionError: Lists differ: ['config._mw_prueba.MiddlewareSyncOnly'] != []
Middlewares sync-only en la cadena de producción:
['config._mw_prueba.MiddlewareSyncOnly']. Cada uno obliga a Django a adaptar
con async_to_sync todo lo que tiene por debajo, y anula el beneficio de ASGI
para el SSE.
Ran 7 tests in 0.001s
FAILED (failures=1)
```

Después se retiraron la entrada y `config/_mw_prueba.py`. `git status --short`
mostró únicamente `config/tests.py` antes de documentar.

```text
$ .venv/bin/python manage.py test config --settings=config.test_settings
Ran 7 tests in 0.001s
OK

$ .venv/bin/python manage.py test apps --settings=config.test_settings
Ran 290 tests in 3.741s
OK

$ .venv/bin/python manage.py makemigrations --check --dry-run --settings=config.test_settings
No changes detected

$ .venv/bin/python manage.py check --settings=config.test_settings
System check identified no issues (0 silenced).

$ DEBUG=False SERVE_STATIC_WITH_WHITENOISE=False ...
Middlewares sync-only: ninguno

$ curl http://127.0.0.1:8000/evaluacion-ergonomica/
302 http://127.0.0.1:8000/acceso/?next=/evaluacion-ergonomica/
```

| Comprobación | Antes | Después |
|---|---:|---:|
| Tests de `apps` | 290 | 290 |
| Tests de `config` | 3 | 7 |
| Contrato automático de cadena async | No | Sí |

### Tests modificados y por qué
Ninguno existente. Se agregaron cuatro pruebas.

### Impacto en despliegue
| Requisito | ¿Aplica? |
|---|---|
| `collectstatic` | No |
| Reinicio del servicio | No |
| Migración de base de datos | No |
| Variable de entorno nueva | No |

### Cómo se revierte
```bash
git revert <hash de B.2>
```
Sólo retira guardas; no cambia runtime.

### Desvíos respecto del roadmap
Ninguno.

### Notas para el commit siguiente
B.3 requiere decisión D-P-7, upgrade de VPS y evidencia literal de siete
verificaciones productivas antes de poder documentarse o commitearse.

---
