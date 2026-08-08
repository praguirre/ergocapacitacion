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
| Hash |  |
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
