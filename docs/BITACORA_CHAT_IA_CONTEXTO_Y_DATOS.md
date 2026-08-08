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
| Hash |  |
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
