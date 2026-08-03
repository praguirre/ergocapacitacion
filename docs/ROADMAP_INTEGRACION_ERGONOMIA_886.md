# ROADMAP DE EJECUCIÓN — Integración del módulo de Ergonomía SRT 886/15 en ErgoSolutions

**Documento:** `docs/ROADMAP_INTEGRACION_ERGONOMIA_886.md`
**Versión:** 1.0
**Fecha de emisión:** 2 de agosto de 2026
**Documento base:** [`INTEGRACION_MODULO_ERGONOMIA_886_PROPUESTA_TECNICA.md`](INTEGRACION_MODULO_ERGONOMIA_886_PROPUESTA_TECNICA.md)
**Destinatario:** asistente IA programador que ejecuta la integración
**Titular del proyecto:** Pablo R. Aguirre

---

# 🔴 SECCIÓN 0 — LEER ANTES DE ESCRIBIR UNA SOLA LÍNEA

## 0.1 Qué es este documento

Es un **plan de ejecución commit por commit**. No es un documento de diseño: el diseño ya está resuelto y justificado en `INTEGRACION_MODULO_ERGONOMIA_886_PROPUESTA_TECNICA.md`. Aquí sólo se ejecuta.

**58 commits, 7 fases, dos repositorios.** Cada commit es autocontenido: tiene su objetivo, sus archivos, su código, su verificación y su mensaje de commit. Se ejecutan **en orden**, sin saltear.

| Fase | Repositorio | Commits | Bloquea la siguiente |
|---|---|:---:|:---:|
| **0** — Preparación del destino | `ergocapacitacion` | 11 (0.0–0.10) | ✅ |
| **1** — Adaptación del origen | `ergonomia_srt` | 7 (1.0–1.6) | ✅ |
| **2** — Trasplante | `ergocapacitacion` | 13 (2.1–2.13) | ✅ |
| **3** — Normalización de dominio | `ergocapacitacion` | 9 (3.1–3.9) | ✅ |
| **4** — Integración de UI 🎯 | `ergocapacitacion` | 5 (4.1–4.5) | ❌ |
| **5** — Aprovechamiento | `ergocapacitacion` | 6 (5.1–5.6) | ❌ |
| **6** — Content Security Policy | `ergocapacitacion` | 7 (6.1–6.7) | ❌ independiente |

> **El objetivo de negocio se cumple al terminar la Fase 4** (commit 4.1). Las Fases 5 y 6 agregan valor sobre algo que ya funciona y pueden posponerse sin bloquear un despliegue.

## 0.2 ⛔ LA REGLA DE ORO

> ### Al finalizar cada commit, y **ANTES** de ejecutar `git add` / `git commit` / `git push`, es **OBLIGATORIO** actualizar la documentación de trazabilidad.
>
> **Ningún commit se cierra sin su registro documental.** Un commit sin documentación actualizada es un commit incompleto y debe rehacerse.

### Qué hay que actualizar, en este orden

| # | Archivo | Qué se escribe | Cuándo |
|---|---|---|---|
| 1 | `docs/BITACORA_INTEGRACION_886.md` | Entrada del commit: qué se hizo, archivos tocados, resultado de las verificaciones, incidencias | **Cada commit, sin excepción** |
| 2 | `docs/ROADMAP_INTEGRACION_ERGONOMIA_886.md` (este archivo) | Marcar el commit como ✅ en la tabla de control de §0.9 | **Cada commit, sin excepción** |
| 3 | `README.md` de la raíz | Registro ordenado del cambio | **Cada commit** (lo exige `AGENTS.md`, regla 9) |
| 4 | `docs/INTEGRACION_MODULO_ERGONOMIA_886_PROPUESTA_TECNICA.md` | Sólo si la ejecución **contradice** el diseño | Cuando ocurra |

### Plantilla obligatoria de entrada en la bitácora

```markdown
## Commit <N.M> — <título>

| Campo | Valor |
|---|---|
| Fecha | <AAAA-MM-DD HH:MM> |
| Repositorio | ergocapacitacion \| ergonomia_srt |
| Rama | <rama> |
| Hash | <se completa después del commit> |
| Fase | <N> |
| Estado | ✅ Completado \| ⚠️ Completado con desvíos \| 🔴 Bloqueado |

### Qué se hizo
<descripción en 2-4 líneas>

### Archivos modificados
- `ruta/archivo.py` — <qué cambió>

### Verificaciones ejecutadas
```
<comando>
<salida literal, recortada a lo relevante>
```

### Desvíos respecto del roadmap
<«Ninguno» o la descripción precisa del desvío y su justificación>

### Notas para el commit siguiente
<«Ninguna» o lo que el siguiente ejecutor necesita saber>
```

## 0.3 ⛔ PROTOCOLO DE DETENCIÓN

**El asistente ejecuta de forma autónoma y NO se detiene**, salvo en los tres casos de la tabla. En cualquier otra situación —una prueba que falla, un conflicto de merge, una duda de implementación— **resuelve y continúa**, dejando registro en la bitácora.

### Los únicos tres motivos válidos de detención

| # | Motivo | Ejemplos |
|---|---|---|
| **P-1** | **Claves, secretos o credenciales del sistema** | `SECRET_KEY`, `OPENAI_API_KEY`, `DATABASE_URL`, contraseñas SMTP, cualquier valor de `.env` |
| **P-2** | **Creación de usuarios y sus contraseñas** | `createsuperuser`, alta de usuarios de prueba con contraseña, creación de roles de base de datos |
| **P-3** | **Operación destructiva o irreversible sobre datos reales** | `DROP DATABASE`, `flush`, borrado de `media/`, `push --force`, reescritura de historia |

### Formato obligatorio de la detención

Cuando se dispara P-1, P-2 o P-3, el asistente **detiene la ejecución** y emite exactamente este bloque:

```
🛑 DETENCIÓN — Commit <N.M> — Motivo <P-1 | P-2 | P-3>

Necesito que ejecutes vos este paso, Pablo:

    <comando exacto, listo para copiar y pegar>

Motivo: <una línea explicando por qué no puedo ejecutarlo yo>
Qué hago cuando termines: <la acción exacta con la que retomo>

Avisame cuando esté hecho y sigo con el commit <N.M> sin detenerme.
```

**Tras la confirmación, el asistente retoma inmediatamente y continúa hasta la siguiente detención o hasta el final del roadmap.** No pide aprobación para avanzar entre commits ni entre fases.

### Puntos de detención previstos

Están anticipados. No hay otros salvo imprevistos.

| Commit | Motivo | Qué se le pide a Pablo |
|---|---|---|
| **0.7** | P-2 | Crear la base de datos de pruebas si SQLite no fuera viable |
| **2.13** | P-2 | `createsuperuser` en la base de desarrollo, si hiciera falta para la prueba de humo |
| **3.9** | P-2 | Usuarios de prueba de los tres tipos, si se decide crearlos fuera de fixtures |
| **F-Deploy** | P-1 | Variables de entorno nuevas en el `.env` de producción |

## 0.4 Reglas de trabajo permanentes

| # | Regla |
|---|---|
| **R-1** | **Un commit por vez, en orden.** No agrupar, no saltear, no adelantar |
| **R-2** | **Verificar antes de commitear.** Si la verificación del commit falla, se corrige antes de cerrarlo |
| **R-3** | **No tocar el `.env` real.** Los valores los pone Pablo (P-1) |
| **R-4** | **No romper lo que funciona.** Toda suite que estaba en verde sigue en verde |
| **R-5** | **Nunca `git push --force`** ni reescritura de historia (P-3) |
| **R-6** | **Nunca `commit --amend`** sobre un commit ya pusheado |
| **R-7** | Si la realidad contradice al roadmap, **gana la realidad**: se registra el desvío en la bitácora y se continúa |
| **R-8** | **Los artefactos normativos se copian byte a byte.** Nunca se abren y regraban con un editor que pueda cambiar fin de línea o codificación |
| **R-9** | Las condiciones **CF-1 a CF-6** son vinculantes. Ante duda entre cumplir una CF o avanzar, **se cumple la CF** |
| **R-10** | Los mensajes de commit se copian **literalmente** de este documento |

## 0.5 Entorno de trabajo

| Proyecto | Ruta | Rama de trabajo | Intérprete |
|---|---|---|---|
| **ErgoSolutions** (destino) | `/Users/praguirre/ergocapacitacion` | `release/beta` → crear `feature/ergonomia-886` | `.venv/bin/python` |
| **ErgoApp SRT 886** (origen) | `/Users/praguirre/ergonomia_srt` | `main` → crear `feature/preparacion-integracion` | `./venv/bin/python` |

> ⚠️ **Los intérpretes son distintos.** `.venv` con punto en el destino, `venv` sin punto en el origen. Usar el equivocado produce errores desconcertantes.

## 0.6 Estado verificado de partida

Medido el 02/08/2026. **Antes del commit 0.1, reproducir estos cuatro comandos y confirmar que dan lo mismo.** Si algo difiere, registrarlo en la bitácora antes de continuar.

```bash
cd /Users/praguirre/ergonomia_srt && ./venv/bin/python manage.py test --settings=ergonomia_srt.test_settings
# → Ran 160 tests — OK

cd /Users/praguirre/ergonomia_srt && ./venv/bin/python manage.py makemigrations --check --dry-run
# → No changes detected

cd /Users/praguirre/ergocapacitacion && .venv/bin/python manage.py test apps
# → Ran 32 tests — OK

cd /Users/praguirre/ergocapacitacion && .venv/bin/python manage.py makemigrations --check --dry-run
# → No changes detected
```

## 0.7 Las seis condiciones fundamentales — recordatorio permanente

| Código | Condición | Commits donde se verifica |
|---|---|---|
| **CF-1** | `help_ai` y `ergobot_ai` **NO se fusionan**. Coexisten como apps separadas | 1.3, 2.5, 2.8, 4.5 |
| **CF-2** | El motor de cálculo es la **única autoridad** sobre los niveles de riesgo | 2.2, 5.4, 5.6 |
| **CF-3** | La trazabilidad normativa **no se recorta**: `calc_data` íntegro con SHA-256 | 1.0, 2.7, 2.13 |
| **CF-4** | Los datos personales **no salen** hacia el proveedor del modelo | 3.2, 5.3 |
| **CF-5** | Un documento oficial **nunca afirma** lo que el profesional no respondió | 3.5, 5.2, 5.3 |
| **CF-6** | La superposición **no altera** el formulario oficial | 2.7, 2.13 |

## 0.8 Decisiones ya tomadas — no volver a discutirlas

Estas ocho decisiones estaban abiertas en el documento de diseño. **Ya están resueltas.** El asistente las aplica sin consultar.

| # | Decisión | **Resolución aplicada** |
|---|---|---|
| 1 | Criterio de CF-1 sobre las 22 pruebas de `help_ai` | **Reformulado y aceptado.** Se admiten sólo cambios de import y de namespace en `help_ai/tests.py`. Ninguna aserción, `patch` ni caso puede tocarse |
| 2 | Modelo de lenguaje del módulo | **`CHAT_AI_MODEL` deriva de `OPENAI_MODEL`.** El valor concreto lo fija Pablo en el `.env` (P-1) |
| 3 | Namespace anidado o plano | **Plano.** `planillas:`, `evaluaciones:`, `exportaciones:`, `help_ai:`. Sin prefijo `ergonomia_886:` en los sub-includes |
| 4 | ¿Un profesional ve las evaluaciones de otro? | **No.** Cada profesional ve sólo las suyas. Una empresa ve las de su empresa |
| 5 | Longitudes de campo al copiar de `CompanyProfile` | **Ampliar** los campos de `Evaluacion` en la migración `0002` |
| 6 | Ubicación de los documentos de ayuda | **Opción A:** quedan en `static/ayuda/help_texts/`, anclados a `settings.BASE_DIR` |
| 7 | ¿Se ejecuta la Fase 6 (CSP)? | **Sí, al final**, después de que el módulo esté funcionando y verificado |
| 8 | Aprobaciones profesionales de las fuentes normativas | ✅ **OTORGADAS por Pablo R. Aguirre.** Se registran en el commit **1.0** |

## 0.9 Tabla de control de avance

> **La actualización de esta tabla es parte de la REGLA DE ORO.** Marcar ✅ al cerrar cada commit.

### Fase 0 — Preparación del destino · `ergocapacitacion`

| Commit | Título | Estado |
|---|---|:---:|
| 0.0 | Crear rama de integración y bitácora | ✅ |
| 0.1 | Consolidar el árbol de trabajo pendiente | ✅ |
| 0.2 | Corregir nombres de URL rotos en los decoradores (N1) | ✅ |
| 0.3 | Restaurar `@login_required` en 13 vistas de backoffice (N1) | ✅ |
| 0.4 | Corregir los settings de redirección profesional (H-F) | ✅ |
| 0.5 | Corregir `QuizState.is_approved` inexistente (N2) | ✅ |
| 0.6 | Tests de regresión de N1 y N2 | ✅ |
| 0.7 | Crear `config/test_settings.py` (B8) | ✅ |
| 0.8 | Configurar `CACHES` con `DatabaseCache` (B4) | ✅ |
| 0.9 | Declarar `pypdf` y `pillow` (B7, N8) | ✅ |
| 0.10 | Agregar `app_name` a los 5 includes sin namespace (H-D) | ✅ |

### Fase 1 — Adaptación del origen · `ergonomia_srt`

| Commit | Título | Estado |
|---|---|:---:|
| 1.0 | **Registrar las 7 aprobaciones profesionales** (CF-3) | ✅ |
| 1.1 | `Evaluacion.usuario` → `settings.AUTH_USER_MODEL` (B1) | ✅ |
| 1.2 | `app_name` en `planillas` + 24 referencias (B3) | ✅ |
| 1.3 | `app_name` en `help_ai` + 11 referencias (B3, CF-1) | ✅ |
| 1.4 | Retirar `django-cors-headers` | ✅ |
| 1.5 | Limpiar dependencias no usadas | ✅ |
| 1.6 | `LANGUAGE_CODE = 'es-ar'` (D-8) | ✅ |

### Fase 2 — Trasplante · `ergocapacitacion`

| Commit | Título | Estado |
|---|---|:---:|
| 2.1 | Crear el paquete contenedor `apps/ergonomia_886/` | ✅ |
| 2.2 | Actualizar las 48 rutas declarativas **antes de mover** (B2) | ✅ |
| 2.3 | Copiar las 4 apps con migraciones y templates | ✅ |
| 2.4 | Actualizar `name` en los 4 `apps.py` | ✅ |
| 2.5 | Reescribir los 102 imports absolutos (B2) | ✅ |
| 2.6 | Corregir la ruta de los documentos de ayuda (B6) | ✅ |
| 2.7 | Copiar estáticos y artefactos byte a byte (CF-3, CF-6) | ✅ |
| 2.8 | Registrar apps y settings del módulo | ✅ |
| 2.9 | URLconf del módulo y montaje | ✅ |
| 2.10 | Plantilla base del módulo y adaptación de 10 templates | ✅ |
| 2.11 | Extraer el widget de ayuda contextual | ✅ |
| 2.12 | `checks.py` — validación de las 48 rutas declarativas | ✅ |
| 2.13 | Aplicar migraciones y prueba de humo | ✅ |

### Fase 3 — Normalización de dominio · `ergocapacitacion`

| Commit | Título | Estado |
|---|---|:---:|
| 3.1 | `Evaluacion.empresa` y alineación de longitudes | ✅ |
| 3.2 | **Ampliar `CLAVES_PROHIBIDAS`** (CF-4) | ✅ |
| 3.3 | Propiedad mixta por tipo de usuario | ✅ |
| 3.4 | Decoradores en todas las vistas del módulo | ✅ |
| 3.5 | Formulario de creación con selector de empresa (CF-5) | ✅ |
| 3.6 | Vista de listado de evaluaciones | ✅ |
| 3.7 | Vista de eliminación de evaluación | ✅ |
| 3.8 | Índices de consulta | ✅ |
| 3.9 | Pruebas de propiedad, saneamiento y no regresión | ✅ |

### Fase 4 — Integración de UI · `ergocapacitacion`

| Commit | Título | Estado |
|---|---|:---:|
| 4.1 | **Activar la tarjeta «Evaluaciones»** | ✅ |
| 4.2 | Entrada de navegación en el navbar | ⬜ |
| 4.3 | Cuarta stat del dashboard con import diferido | ⬜ |
| 4.4 | Ajustes de contraste al tema oscuro | ⬜ |
| 4.5 | Loggers del módulo y verificación de CF-1 | ⬜ |

### Fase 5 — Aprovechamiento · `ergocapacitacion`

| Commit | Título | Estado |
|---|---|:---:|
| 5.1 | Evidencia de vibración adjuntable (O-5, D-1) | ⬜ |
| 5.2 | Aclaración de firma en planillas oficiales (O-2, CF-5) | ⬜ |
| 5.3 | Trabajadores estructurados (O-3, CF-4, CF-5) | ⬜ |
| 5.4 | Sincronización con la agenda (O-4, CF-2) | ⬜ |
| 5.5 | Enlace desde la agenda hacia la Planilla 4 | ⬜ |
| 5.6 | Sugerencia de capacitaciones por nivel de riesgo (O-6) | ⬜ |

### Fase 6 — Content Security Policy · `ergocapacitacion`

| Commit | Título | Estado |
|---|---|:---:|
| 6.1 | Migrar CDN a `vendor/` local | ⬜ |
| 6.2 | Extraer los 5 bloques `<script>` inline | ⬜ |
| 6.3 | Reemplazar los 3 manejadores en línea | ⬜ |
| 6.4 | Verificación visual de las 33 pantallas | ⬜ |
| 6.5 | Portar el middleware con modo `Report-Only` | ⬜ |
| 6.6 | Período de observación | ⬜ |
| 6.7 | Activar el CSP en modo bloqueante | ⬜ |

## 0.10 Comandos de verificación de referencia

```bash
# ── ErgoSolutions ────────────────────────────────────────────────
cd /Users/praguirre/ergocapacitacion
.venv/bin/python manage.py check
.venv/bin/python manage.py makemigrations --check --dry-run
.venv/bin/python manage.py migrate --check
.venv/bin/python manage.py test --settings=config.test_settings

# ── ErgoApp SRT 886 ──────────────────────────────────────────────
cd /Users/praguirre/ergonomia_srt
./venv/bin/python manage.py test --settings=ergonomia_srt.test_settings
./venv/bin/python manage.py makemigrations --check --dry-run
```

---
# FASE 0 — PREPARACIÓN DEL DESTINO

**Repositorio:** `/Users/praguirre/ergocapacitacion`
**Objetivo:** integrar sobre una base sana. **Nada de esta fase depende del módulo 886.**
**Por qué es obligatoria:** ErgoSolutions arrastra dos regresiones verificadas con HTTP 500. Si no se reparan antes, cada error 500 durante la integración obliga a investigar si es propio o heredado.

---

## Commit 0.0 — Crear rama de integración y bitácora

### Objetivo
Abrir la rama de trabajo y crear el archivo de bitácora que la REGLA DE ORO exige actualizar en cada commit.

### Paso 1 — Verificar el punto de partida

```bash
cd /Users/praguirre/ergocapacitacion
git branch --show-current      # debe decir: release/beta
git status --short
```

### Paso 2 — Crear la rama

```bash
git checkout -b feature/ergonomia-886
```

### Paso 3 — Crear la bitácora

Crear `docs/BITACORA_INTEGRACION_886.md`:

```markdown
# Bitácora de integración — Módulo de Ergonomía SRT 886/15

**Roadmap:** `docs/ROADMAP_INTEGRACION_ERGONOMIA_886.md`
**Diseño:** `docs/INTEGRACION_MODULO_ERGONOMIA_886_PROPUESTA_TECNICA.md`
**Inicio:** <AAAA-MM-DD>
**Ejecutor:** Asistente IA de desarrollo
**Titular:** Pablo R. Aguirre

---

## Estado de partida verificado

| Proyecto | Rama | Suite | Migraciones |
|---|---|---|---|
| ErgoSolutions | `release/beta` → `feature/ergonomia-886` | <resultado> | <resultado> |
| ErgoApp SRT 886 | `main` | <resultado> | <resultado> |

---

## Registro de commits

<!-- Cada commit agrega su entrada acá, en orden cronológico -->
```

### Paso 4 — Registrar el estado de partida

Ejecutar los cuatro comandos de §0.6 y volcar su salida literal en la sección «Estado de partida verificado» de la bitácora.

### Verificación

- [ ] `git branch --show-current` devuelve `feature/ergonomia-886`
- [ ] `docs/BITACORA_INTEGRACION_886.md` existe y tiene el estado de partida con salidas literales

### 🔴 REGLA DE ORO
- [ ] Bitácora creada con la entrada del commit 0.0
- [ ] Tabla de control de §0.9: marcar 0.0 como ✅
- [ ] `README.md`: agregar la sección de la integración

### Git

```bash
git add docs/BITACORA_INTEGRACION_886.md docs/ROADMAP_INTEGRACION_ERGONOMIA_886.md README.md
git commit -m "docs(886): abrir rama de integracion y bitacora de trazabilidad"
git push -u origin feature/ergonomia-886
```

---

## Commit 0.1 — Consolidar el árbol de trabajo pendiente

### Objetivo
El árbol tiene cambios sin commitear ajenos a esta integración: `docs/` sin trackear, `.gitignore` y `README.md` modificados, y cuatro `.md` movidos de la raíz a `docs/`. Consolidarlos ahora evita que se mezclen con el trabajo del módulo.

### Contexto verificado

```
 M .gitignore
 D DEPLOY_CLAUDE_RUNBOOK.md
 D ERGOSOLUTIONS_ARQUITECTURA_ROADMAP.md
 D MAPA_CONCEPTUAL_VISUAL.md
 D PLAN_EMAIL_PRODUCCION.md
 M README.md
?? docs/
```

### Paso 1 — Confirmar que los borrados son movimientos, no pérdidas

```bash
for f in DEPLOY_CLAUDE_RUNBOOK ERGOSOLUTIONS_ARQUITECTURA_ROADMAP MAPA_CONCEPTUAL_VISUAL PLAN_EMAIL_PRODUCCION; do
  test -f "docs/$f.md" && echo "OK  docs/$f.md" || echo "FALTA docs/$f.md"
done
```

> ⚠️ Si alguno dijera `FALTA`, **detenerse y recuperarlo** con `git checkout -- <archivo>` antes de continuar. Un `.md` de planificación perdido no se recupera después.

### Paso 2 — Consolidar

```bash
git add -A
```

### Verificación

- [ ] Los cuatro `.md` existen bajo `docs/`
- [ ] `git status --short` no muestra nada sin agregar
- [ ] `.venv/bin/python manage.py check` sigue sin issues

### 🔴 REGLA DE ORO
- [ ] Bitácora: entrada del commit 0.1
- [ ] Tabla de control: 0.1 ✅
- [ ] `README.md`: registrar la reorganización documental

### Git

```bash
git add -A
git commit -m "chore(docs): consolidar documentacion en docs/ y actualizar gitignore"
git push
```

---

## Commit 0.2 — Corregir nombres de URL rotos en los decoradores (N1)

### Objetivo
Reparar la causa raíz de los HTTP 500 anónimos: cinco `reverse()` / `redirect()` sobre nombres de URL que **no existen**.

### Evidencia verificada

```
reverse('professional_login')                       → NoReverseMatch
reverse('accounts_professional:professional_login') → /auth/login/     ✅
reverse('landing')                                  → NoReverseMatch
reverse('trainee_landing')                          → /acceso/          ✅
```

### Archivo: `apps/accounts/decorators.py`

Cinco correcciones. **Aplicar exactamente estas y ninguna más.**

#### Corrección 1 — `professional_required`, línea 27

```python
# ANTES
                url = login_url or reverse('professional_login')

# DESPUÉS
                url = login_url or reverse('accounts_professional:professional_login')
```

#### Corrección 2 — `trainee_required`, línea 54

```python
# ANTES
                url = login_url or reverse('landing')

# DESPUÉS
                url = login_url or reverse('trainee_landing')
```

#### Corrección 3 — `backoffice_required`, línea 92

```python
# ANTES
                url = login_url or reverse('professional_login')

# DESPUÉS
                url = login_url or reverse('accounts_professional:professional_login')
```

#### Corrección 4 — `company_required`, línea 122

> **Atención:** el destino natural de una empresa **no** es el login profesional.

```python
# ANTES
                url = login_url or reverse('professional_login')

# DESPUÉS
                url = login_url or reverse('accounts_company:company_login')
```

#### Corrección 5 — `subscription_required`, línea 152

```python
# ANTES
                return redirect('professional_login')

# DESPUÉS
                return redirect('accounts_professional:professional_login')
```

### Verificación

```bash
cd /Users/praguirre/ergocapacitacion
.venv/bin/python -c "
import django, os
os.environ.setdefault('DJANGO_SETTINGS_MODULE','config.settings')
django.setup()
from django.urls import reverse
for n in ['accounts_professional:professional_login','accounts_company:company_login','trainee_landing']:
    print(f'{n:45s} -> {reverse(n)}')
"
.venv/bin/python manage.py check
.venv/bin/python manage.py test apps
```

- [ ] Los tres nombres resuelven
- [ ] `grep -n "reverse('professional_login')\|reverse('landing')" apps/accounts/decorators.py` no devuelve nada
- [ ] Los 32 tests siguen pasando

### 🔴 REGLA DE ORO
- [ ] Bitácora: entrada 0.2, con la salida del script de `reverse()`
- [ ] Tabla de control: 0.2 ✅
- [ ] `README.md`: registrar la corrección de N1 (parte 1)

### Git

```bash
git add apps/accounts/decorators.py docs/ README.md
git commit -m "fix(accounts): corregir nombres de URL inexistentes en los cinco decoradores

Los decoradores resolvian 'professional_login' y 'landing', que no existen
en el URLconf. Es la causa raiz de los HTTP 500 a usuarios anonimos (N1).

- professional_required  -> accounts_professional:professional_login
- trainee_required       -> trainee_landing
- backoffice_required    -> accounts_professional:professional_login
- company_required       -> accounts_company:company_login  (destino correcto)
- subscription_required  -> accounts_professional:professional_login"
git push
```

---

## Commit 0.3 — Restaurar `@login_required` en 13 vistas de backoffice (N1)

### Objetivo
Restaurar la defensa en profundidad. El commit 0.2 corrigió el defecto; éste restaura la capa que lo enmascaraba, para que un error equivalente en el futuro vuelva a fallar de forma benigna.

### Archivo 1: `apps/company/views.py` — 11 vistas

Las once vistas verificadas en las líneas 33, 96, 168, 215, 247, 285, 338, 378, 408, 422 y 454. **El orden de los decoradores importa: `@login_required` va primero.**

```python
from django.contrib.auth.decorators import login_required   # agregar al bloque de imports

# Patrón a aplicar en las ONCE vistas:

@login_required                    # ← NUEVO: intercepta al anonimo y redirige limpio
@company_required
def nomina_list(request):
    ...
```

Vistas a modificar, en orden de aparición:

| Línea aprox. | Vista |
|---|---|
| 33 | `nomina_list` |
| 96 | `nomina_add_worker` |
| 168 | `nomina_detail` |
| 215 | `nomina_edit` |
| 247 | `nomina_export_csv` |
| 285 | `agenda_list` |
| 338 | `agenda_create` |
| 378 | `agenda_edit` |
| 408 | `agenda_complete` |
| 422 | `directorio_profesionales` |
| 454 | `send_contact_request` |

### Archivo 2: `apps/dashboard/views.py` — 2 vistas

```python
# Linea 373
@login_required                    # ← NUEVO
@professional_required
def my_contact_requests(request):
    ...

# Linea 386
@login_required                    # ← NUEVO
@professional_required
def respond_contact_request(request, request_id):
    ...
```

### Verificación

```bash
# Las 11 vistas de company deben tener login_required
grep -c "@login_required" apps/company/views.py        # debe dar 11
grep -c "@company_required" apps/company/views.py      # debe dar 11

# Ninguna ruta debe dar 500 sin sesion
.venv/bin/python -c "
import django, os
os.environ.setdefault('DJANGO_SETTINGS_MODULE','config.settings')
django.setup()
from django.test import Client
c = Client()
rutas = ['/dashboard/', '/dashboard/empresa/nomina/', '/dashboard/empresa/nomina/agregar/',
         '/dashboard/empresa/nomina/exportar/', '/dashboard/empresa/agenda/',
         '/dashboard/empresa/agenda/crear/', '/dashboard/empresa/directorio/',
         '/dashboard/solicitudes-contacto/']
fallos = 0
for r in rutas:
    code = c.get(r).status_code
    marca = 'OK ' if code in (302, 403) else 'FALLA'
    if code not in (302, 403): fallos += 1
    print(f'{marca} {r:45s} -> {code}')
print()
print('RESULTADO:', 'SIN 500' if fallos == 0 else f'{fallos} RUTAS ROTAS')
"
.venv/bin/python manage.py test apps
```

- [ ] Las 8 rutas devuelven 302 o 403, **ninguna 500**
- [ ] Los 32 tests siguen pasando

### 🔴 REGLA DE ORO
- [ ] Bitácora: entrada 0.3, con la tabla literal de códigos HTTP
- [ ] Tabla de control: 0.3 ✅
- [ ] `README.md`: registrar la corrección de N1 (parte 2)

### Git

```bash
git add apps/company/views.py apps/dashboard/views.py docs/ README.md
git commit -m "fix(backoffice): restaurar @login_required antes de los decoradores de rol

Las 13 vistas de la Etapa 3 usaban @company_required y @professional_required
sin el @login_required que interceptaba al usuario anonimo. Es la segunda capa
de N1: el defecto lo corrige el commit anterior, esta capa restaura la defensa
en profundidad para que un error equivalente vuelva a fallar de forma benigna.

11 vistas en apps/company/views.py y 2 en apps/dashboard/views.py."
git push
```

---

## Commit 0.4 — Corregir los settings de redirección profesional (H-F)

### Objetivo
Dos settings apuntan a nombres de URL que no resuelven. Es la misma familia de defecto que N1 y no estaba registrada como hallazgo independiente.

### Evidencia verificada

| Setting | Valor actual | Resuelve |
|---|---|---|
| `LOGIN_URL` | `'trainee_landing'` | ✅ `/acceso/` |
| `LOGIN_REDIRECT_URL` | `'training_home'` | ✅ `/capacitacion/` |
| **`PROFESSIONAL_LOGIN_URL`** | `'professional_login'` | 🔴 **NO RESUELVE** |
| **`PROFESSIONAL_LOGIN_REDIRECT_URL`** | `'dashboard'` | 🔴 **NO RESUELVE** |

### Archivo: `config/settings.py`, líneas 108-110

```python
# ANTES
# URLs de login profesionales (para usar en decoradores/mixins/vistas)
PROFESSIONAL_LOGIN_URL = "professional_login"
PROFESSIONAL_LOGIN_REDIRECT_URL = "dashboard"

# DESPUÉS
# URLs de login profesionales (para usar en decoradores/mixins/vistas).
# Deben ser nombres calificados: los planos no resuelven porque los includes
# de accounts declaran namespace.
PROFESSIONAL_LOGIN_URL = "accounts_professional:professional_login"
PROFESSIONAL_LOGIN_REDIRECT_URL = "dashboard:home"
```

### Verificación

```bash
.venv/bin/python -c "
import django, os
os.environ.setdefault('DJANGO_SETTINGS_MODULE','config.settings')
django.setup()
from django.urls import reverse
from django.conf import settings
for s in ['LOGIN_URL','LOGIN_REDIRECT_URL','PROFESSIONAL_LOGIN_URL','PROFESSIONAL_LOGIN_REDIRECT_URL']:
    v = getattr(settings, s)
    try:
        print(f'{s:35s} = {v!r:50s} -> {reverse(v)}')
    except Exception:
        print(f'{s:35s} = {v!r:50s} -> NO RESUELVE  🔴')
"
.venv/bin/python manage.py test apps
```

- [ ] **Los cuatro settings resuelven**
- [ ] Los 32 tests siguen pasando

### 🔴 REGLA DE ORO
- [ ] Bitácora: entrada 0.4, con la tabla de resolución
- [ ] Tabla de control: 0.4 ✅
- [ ] `README.md`: registrar la corrección de H-F

### Git

```bash
git add config/settings.py docs/ README.md
git commit -m "fix(settings): calificar PROFESSIONAL_LOGIN_URL y su redirect

Ambos settings apuntaban a nombres de URL sin namespace que no resuelven
('professional_login' y 'dashboard'). Misma familia de defecto que N1."
git push
```

---

## Commit 0.5 — Corregir `QuizState.is_approved` inexistente (N2)

### Objetivo
La ficha del trabajador devuelve HTTP 500 cuando el trabajador ya rindió al menos un quiz — que es exactamente el caso para el que la ficha fue construida.

### Evidencia verificada

```
Ficha SIN QuizState  →  HTTP 200   ✅
Ficha CON QuizState  →  HTTP 500   🔴
AttributeError: 'QuizState' object has no attribute 'is_approved'
```

`QuizState` expone `attempts_used`, `lockout_until`, `retake_available_at`, `last_completed_at` y `last_passed`. **El campo con esa semántica es `last_passed`.**

### Archivo: `apps/company/views.py`, líneas 197-204

```python
# ANTES
    for mod in modules:
        qs = QuizState.objects.filter(user=worker, module=mod).first()
        cert = Certificate.objects.filter(user=worker, module=mod).first()
        from django.utils import timezone
        module_status.append({
            'module': mod,
            'quiz_state': qs,
            'certificate': cert,
            'is_approved': qs.is_approved if qs else False,
            'is_valid': cert and cert.valid_until and cert.valid_until > timezone.now() if cert else False,
        })

# DESPUÉS
    for mod in modules:
        qs = QuizState.objects.filter(user=worker, module=mod).first()
        cert = Certificate.objects.filter(user=worker, module=mod).first()
        module_status.append({
            'module': mod,
            'quiz_state': qs,
            'certificate': cert,
            # QuizState no tiene `is_approved`: el campo con esa semantica
            # es `last_passed`.
            'is_approved': bool(qs.last_passed) if qs else False,
            # El modelo Certificate ya expone la propiedad `is_valid`.
            'is_valid': cert.is_valid if cert else False,
        })
```

> **Dos cambios adicionales incluidos:**
> 1. Se elimina el `from django.utils import timezone` **dentro del bucle** — importaba en cada iteración y ya no hace falta.
> 2. La expresión de vigencia se reemplaza por la propiedad `Certificate.is_valid`, que el modelo ya tiene. La expresión original era innecesariamente enrevesada y con precedencia ambigua.

### Verificación

```bash
grep -n "is_approved\|is_valid" apps/company/views.py
# NO debe aparecer `qs.is_approved`

.venv/bin/python manage.py test apps
```

- [ ] `qs.is_approved` ya no aparece en el archivo
- [ ] El `import timezone` dentro del bucle fue removido
- [ ] Los 32 tests siguen pasando

### 🔴 REGLA DE ORO
- [ ] Bitácora: entrada 0.5
- [ ] Tabla de control: 0.5 ✅
- [ ] `README.md`: registrar la corrección de N2

### Git

```bash
git add apps/company/views.py docs/ README.md
git commit -m "fix(company): corregir atributo inexistente en la ficha del trabajador

QuizState no tiene la propiedad is_approved; el campo con esa semantica es
last_passed. La ficha devolvia HTTP 500 para todo trabajador que ya hubiera
rendido un quiz, que es el caso para el que fue construida (N2).

Ademas se usa la propiedad Certificate.is_valid en lugar de reconstruir la
comparacion, y se retira un import dentro del bucle."
git push
```

---

## Commit 0.6 — Tests de regresión de N1 y N2

### Objetivo
Convertir las dos regresiones en pruebas automáticas. **Los 32 tests estaban en verde con ambos defectos presentes**: sin estas pruebas, nada impide que vuelvan.

### Archivo nuevo: `apps/company/tests_regresion.py`

```python
# apps/company/tests_regresion.py
"""Regresiones verificadas de la Etapa 3 (N1 y N2).

Estas pruebas existen porque las 32 pruebas originales pasaban con ambos
defectos presentes: ninguna cubria el acceso anonimo ni la ficha con
QuizState poblado.
"""

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from apps.company.models import CompanyProfile, CompanyWorker
from apps.quiz.models import QuizState
from apps.training.models import TrainingModule

User = get_user_model()


class AccesoAnonimoBackofficeTests(TestCase):
    """N1: ninguna ruta de backoffice devuelve HTTP 500 sin sesion."""

    RUTAS = [
        "/dashboard/",
        "/dashboard/capacitaciones/",
        "/dashboard/perfil/",
        "/dashboard/empresa/nomina/",
        "/dashboard/empresa/nomina/agregar/",
        "/dashboard/empresa/nomina/exportar/",
        "/dashboard/empresa/agenda/",
        "/dashboard/empresa/agenda/crear/",
        "/dashboard/empresa/directorio/",
        "/dashboard/solicitudes-contacto/",
    ]

    def test_ninguna_ruta_de_backoffice_devuelve_500_a_un_anonimo(self):
        cliente = Client()
        for ruta in self.RUTAS:
            with self.subTest(ruta=ruta):
                respuesta = cliente.get(ruta)
                self.assertNotEqual(
                    respuesta.status_code, 500,
                    f"{ruta} devuelve HTTP 500 a un usuario anonimo",
                )
                self.assertIn(
                    respuesta.status_code, (302, 403),
                    f"{ruta} deberia redirigir o denegar, devolvio "
                    f"{respuesta.status_code}",
                )

    def test_el_anonimo_es_redirigido_a_un_login_que_existe(self):
        respuesta = Client().get("/dashboard/empresa/nomina/")
        self.assertEqual(respuesta.status_code, 302)
        # El destino de una empresa es su propio login, no el profesional.
        self.assertIn(reverse("accounts_company:company_login"), respuesta.url)


class FichaTrabajadorConQuizStateTests(TestCase):
    """N2: la ficha rompia cuando el trabajador ya habia rendido un quiz."""

    @classmethod
    def setUpTestData(cls):
        cls.empresa_user = User.objects.create_company(
            email="empresa@test.local", password="x", username="empresa-test",
        )
        cls.perfil = CompanyProfile.objects.create(
            user=cls.empresa_user,
            razon_social="ACME S.A.",
            cuit="30-12345678-9",
            contacto_nombre="Contacto",
        )
        cls.trabajador = User.objects.create_trainee(
            cuil="20-11111111-1", email="trabajador@test.local",
            first_name="Juan", last_name="Perez",
        )
        cls.asignacion = CompanyWorker.objects.create(
            company=cls.perfil, worker=cls.trabajador,
        )
        cls.modulo = TrainingModule.objects.filter(is_active=True).first()

    def setUp(self):
        self.client.force_login(self.empresa_user)

    def test_ficha_sin_quizstate_responde_200(self):
        url = reverse(
            "dashboard:company:nomina_detail",
            kwargs={"worker_id": self.asignacion.pk},
        )
        self.assertEqual(self.client.get(url).status_code, 200)

    def test_ficha_con_quizstate_responde_200(self):
        """Es el caso que rompia: QuizState existe y se consulta is_approved."""
        if self.modulo is None:
            self.skipTest("No hay modulos de capacitacion activos en la base de test")

        QuizState.objects.create(
            user=self.trabajador, module=self.modulo,
            attempts_used=1, last_passed=True,
        )
        url = reverse(
            "dashboard:company:nomina_detail",
            kwargs={"worker_id": self.asignacion.pk},
        )
        respuesta = self.client.get(url)
        self.assertEqual(
            respuesta.status_code, 200,
            "La ficha con QuizState poblado debe renderizar (N2)",
        )
        estados = respuesta.context["module_status"]
        aprobados = [e for e in estados if e["module"].pk == self.modulo.pk]
        self.assertTrue(aprobados[0]["is_approved"])
```

> ⚠️ **Si algún nombre de URL o campo no coincide con la realidad**, ajustarlo y **registrar el desvío en la bitácora** (regla R-7). El objetivo de la prueba es lo que importa, no su literalidad.

### Verificación

```bash
.venv/bin/python manage.py test apps.company.tests_regresion -v 2
.venv/bin/python manage.py test apps
```

- [ ] Las pruebas nuevas pasan
- [ ] El total sube de 32 a ~36
- [ ] **Comprobación de que la prueba sirve:** revertir temporalmente el commit 0.5, correr la prueba, confirmar que **falla**, y volver a aplicar la corrección

### 🔴 REGLA DE ORO
- [ ] Bitácora: entrada 0.6, con el total de pruebas antes y después
- [ ] Tabla de control: 0.6 ✅
- [ ] `README.md`: registrar las pruebas de regresión

### Git

```bash
git add apps/company/tests_regresion.py docs/ README.md
git commit -m "test(company): cubrir las regresiones N1 y N2 de la Etapa 3

Las 32 pruebas originales pasaban con ambos defectos presentes: ninguna
cubria el acceso anonimo ni la ficha con QuizState poblado.

- 10 rutas de backoffice verificadas contra HTTP 500 anonimo
- ficha del trabajador con y sin QuizState"
git push
```

---

## Commit 0.7 — Crear `config/test_settings.py` (B8)

### Objetivo
ErgoSolutions no tiene configuración de pruebas aislada. **Sin ella, las 160 pruebas del módulo no podrán ejecutarse en el destino** y no habrá criterio de aceptación verificable para ninguna fase.

### Archivo nuevo: `config/test_settings.py`

```python
# config/test_settings.py
"""Configuracion aislada para la suite automatizada de ErgoSolutions.

Evita que las pruebas dependan de permisos para crear bases PostgreSQL y
garantiza que nunca operen sobre la base configurada en `.env`.

Replica el patron de `ergonomia_srt/test_settings.py`, del que provienen
las 160 pruebas del modulo de Ergonomia 886.

Uso:
    .venv/bin/python manage.py test --settings=config.test_settings
"""

import os

from .settings import *  # noqa: F403


# Base de datos efimera: no requiere permisos de creacion en PostgreSQL
# y nunca toca la base de desarrollo.
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": os.environ.get("ERGOSOLUTIONS_TEST_DATABASE_NAME", ":memory:"),
    }
}

# La tabla de DatabaseCache es infraestructura de despliegue y no forma parte
# de las migraciones. La suite usa memoria aislada para permanecer
# autocontenida. Ver commit 0.8.
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "ergosolutions-tests",
    }
}

# Hashing rapido: las pruebas crean muchos usuarios.
PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.MD5PasswordHasher",
]

# Las pruebas de render no ejecutan collectstatic, de modo que el backend
# manifestado de WhiteNoise fallaria al resolver {% static %}.
# Produccion conserva el manifestado definido en settings.py.
STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
    },
}

# Ningun correo sale del proceso durante las pruebas.
EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"

# `testserver` debe estar permitido siempre, no solo con DEBUG=True.
if "testserver" not in ALLOWED_HOSTS:  # noqa: F405
    ALLOWED_HOSTS.append("testserver")  # noqa: F405
```

### Verificación crítica

**Las 36 pruebas existentes deben pasar bajo la nueva configuración.** SQLite y PostgreSQL no son intercambiables: puede haber dependencias del motor.

```bash
.venv/bin/python manage.py test apps --settings=config.test_settings -v 2
```

**Punto de atención:** `ContactRequest` tiene un `UniqueConstraint` con `condition=models.Q(status='pending')` (índice parcial). SQLite lo soporta, pero conviene confirmar que la prueba correspondiente pasa.

### 🛑 Si las pruebas fallan bajo SQLite

**No es un bloqueo.** Aplicar el plan B, que conserva PostgreSQL y limita el `test_settings` a lo imprescindible:

```python
# config/test_settings.py — PLAN B
from .settings import *  # noqa: F403

# Se CONSERVA DATABASES de settings.py (PostgreSQL).
# Django crea automaticamente `test_<nombre>` y la destruye al terminar.

CACHES = {...}            # igual que arriba
PASSWORD_HASHERS = [...]  # igual que arriba
STORAGES = {...}          # igual que arriba
EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"
```

> 🛑 **Detención P-2 sólo si el plan B tampoco funciona** por falta de permisos de creación de base:
>
> ```
> 🛑 DETENCIÓN — Commit 0.7 — Motivo P-2
>
> Necesito que ejecutes vos este paso, Pablo:
>
>     psql -c "ALTER USER <usuario_de_la_app> CREATEDB;"
>
> Motivo: crear el rol de base de datos requiere credenciales de superusuario
> de PostgreSQL que no debo manejar.
> Qué hago cuando termines: vuelvo a correr la suite con --settings=config.test_settings
> y sigo con el commit 0.8.
>
> Avisame cuando esté hecho y sigo sin detenerme.
> ```

### Verificación

- [ ] `manage.py test apps --settings=config.test_settings` pasa con ~36 pruebas
- [ ] `manage.py test apps` (settings normales) **sigue pasando** — no se rompió el camino anterior

### 🔴 REGLA DE ORO
- [ ] Bitácora: entrada 0.7, indicando si se usó el plan A (SQLite) o el B (PostgreSQL)
- [ ] Tabla de control: 0.7 ✅
- [ ] `README.md`: documentar el comando de pruebas con `--settings=config.test_settings`

### Git

```bash
git add config/test_settings.py docs/ README.md
git commit -m "test(config): agregar configuracion aislada para la suite

ErgoSolutions no tenia settings de prueba. Es prerequisito para ejecutar las
160 pruebas del modulo de Ergonomia 886 dentro del destino (B8).

Replica el patron de ergonomia_srt/test_settings.py: base efimera, LocMemCache,
hashers rapidos, storage estatico no manifestado y correo en memoria."
git push
```

---

## Commit 0.8 — Configurar `CACHES` con `DatabaseCache` (B4)

### Objetivo
Sin caché compartida entre procesos, las cuotas del módulo 886 se multiplican por la cantidad de workers **sin ningún síntoma visible**.

### Por qué es un bloqueante y no una preferencia

`help_ai/limits.py:24-38` usa `cache.add()` como cerrojo distribuido:

```python
if not cache.add(active_key, 1, timeout=settings.CHAT_AI_STREAM_TIMEOUT_SECONDS):
    raise ChatLimitExceeded("Ya existe una consulta del asistente en curso...")
```

Con `LocMemCache`, cada worker tiene su propio diccionario. El lease anti-concurrencia deja de funcionar, la cuota de 20 consultas/minuto pasa a 20 × N, y **la de 10 informes/hora pasa a 10 × N — cada informe es una llamada facturada al proveedor del modelo.**

### Archivo: `config/settings.py`

Insertar después del bloque `DATABASES` (línea 87):

```python
DATABASES = {
    "default": env.db("DATABASE_URL")
}

# =====================================================
# CACHÉ COMPARTIDA ENTRE PROCESOS
# =====================================================
# Imprescindible para que las cuotas del módulo de Ergonomía 886 (chat de
# ayuda, informes profesionales y descargas de documentos) sean globales y
# no por worker. Con LocMemCache cada proceso tendría su propio contador y
# las cuotas se multiplicarían por la cantidad de workers, sin ningún
# síntoma visible.
#
# ⚠️ PASO DE DESPLIEGUE OBLIGATORIO: la tabla NO se crea por migración.
#     python manage.py createcachetable
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.db.DatabaseCache",
        "LOCATION": "ergosolutions_cache",
        "TIMEOUT": 300,
        "OPTIONS": {"MAX_ENTRIES": 5000},
    }
}
```

### Crear la tabla de caché

```bash
.venv/bin/python manage.py createcachetable
```

Es idempotente: se puede ejecutar varias veces sin efecto adverso.

### Documentar el paso de despliegue

Agregar a `docs/DEPLOY_CLAUDE_RUNBOOK.md`, en la secuencia de despliegue, **antes de arrancar los procesos**:

```markdown
### Caché de aplicación

`CACHES` usa `DatabaseCache`, cuya tabla **no se crea por migración**.
Ejecutar en cada despliegue (es idempotente):

```bash
python manage.py createcachetable
```

Sin esta tabla, la primera consulta al chat de ayuda del módulo de Ergonomía
falla — y falla **en tiempo de request**, no al arrancar.
```

### Verificación

```bash
.venv/bin/python manage.py createcachetable
.venv/bin/python -c "
import django, os
os.environ.setdefault('DJANGO_SETTINGS_MODULE','config.settings')
django.setup()
from django.core.cache import cache
cache.set('roadmap-886-prueba', 'ok', 30)
print('Backend :', cache.__class__.__name__)
print('Lectura :', cache.get('roadmap-886-prueba'))
print('add()   :', cache.add('roadmap-886-prueba', 'otro'), '(False = el cerrojo funciona)')
cache.delete('roadmap-886-prueba')
"
.venv/bin/python manage.py test apps --settings=config.test_settings
```

- [ ] El backend es `DatabaseCache`
- [ ] La lectura devuelve `ok`
- [ ] **`add()` sobre una clave existente devuelve `False`** — el cerrojo funciona
- [ ] Las pruebas siguen pasando (usan `LocMemCache` vía `test_settings`)

### 🔴 REGLA DE ORO
- [ ] Bitácora: entrada 0.8, con la salida de la prueba del cerrojo
- [ ] Tabla de control: 0.8 ✅
- [ ] `README.md` y `docs/DEPLOY_CLAUDE_RUNBOOK.md`: documentar `createcachetable`

### Git

```bash
git add config/settings.py docs/ README.md
git commit -m "feat(config): configurar DatabaseCache compartida entre procesos

Sin CACHES definido, Django usa LocMemCache, que es por proceso. Las cuotas
del modulo de Ergonomia 886 (chat, informes y descargas) usan cache.add()
como cerrojo distribuido: con cache por proceso el lease anti-concurrencia
deja de funcionar y las cuotas se multiplican por la cantidad de workers,
sin sintoma visible (B4).

Requiere `manage.py createcachetable` como paso de despliegue: documentado
en DEPLOY_CLAUDE_RUNBOOK.md."
git push
```

---

## Commit 0.9 — Declarar `pypdf` y `pillow` (B7, N8)

### Objetivo
`pypdf` es **la única forma de cumplir CF-6**: fusiona la capa de datos sobre el PDF oficial de la SRT sin alterarlo. Está ausente del destino. `pillow` es obligatoria para los dos `ImageField` del proyecto integrado y no está declarada en ninguno de los dos `requirements.txt`.

### Archivo: `requirements.txt`

```diff
- Django>=5.2
+ Django>=5.2,<6.0
- psycopg[binary]>=3.2
+ psycopg[binary]>=3.2,<4.0
  django-environ>=0.11
  django-bootstrap5>=25.1
  whitenoise>=6.7
- reportlab>=4.0
+ reportlab>=4.0,<5.0
+
+ # Fusion de la capa de datos sobre el PDF oficial de la SRT 886/15.
+ # Es la unica tecnica admitida por CF-6: rellenar el .xls oficial destruye
+ # la curva de Fanger de la Planilla 2H y la escala de Borg de la 2E.
+ pypdf>=5.0,<7.0
+
+ # Requerida por ImageField: CompanyProfile.logo y VibracionCE_Eval.foto_montaje.
+ # Estaba instalada pero no declarada (N8).
+ pillow>=10.0,<14.0
+
- openai>=1.0
+ openai>=2.0,<3.0
- openai-agents>=0.0.19
+ openai-agents>=0.6,<1.0
- uvicorn>=0.30.0
+ uvicorn>=0.30,<1.0
```

> **Sobre las cotas superiores.** `openai>=1.0` admitía instalar la 2.x —que es lo que efectivamente pasó— y admitiría una futura 3.x con cambios incompatibles. Se fijan las cotas a las versiones verificadas como funcionales.

### Instalar

```bash
.venv/bin/pip install -r requirements.txt
```

### Verificación

```bash
.venv/bin/python -c "
import pypdf, PIL, reportlab, agents
print('pypdf     :', pypdf.__version__)
print('pillow    :', PIL.__version__)
print('reportlab :', reportlab.Version)
print()
# La API que consume el modulo 886 debe existir en la version del destino
for s in ['Agent','Runner','RunConfig','ItemHelpers']:
    print(f'agents.{s:12s}', 'OK' if hasattr(agents, s) else 'FALTA  🔴')
campos = getattr(agents.RunConfig, '__dataclass_fields__', {})
print()
print('trace_include_sensitive_data (CF-4):',
      'OK' if 'trace_include_sensitive_data' in campos else 'FALTA  🔴')
"
.venv/bin/python manage.py check
.venv/bin/python manage.py test apps --settings=config.test_settings
```

- [ ] `pypdf` y `pillow` importan sin error
- [ ] Los cuatro símbolos de `agents` existen
- [ ] **`trace_include_sensitive_data` existe** — es el campo que sostiene CF-4
- [ ] Las pruebas siguen pasando

### 🔴 REGLA DE ORO
- [ ] Bitácora: entrada 0.9, con las versiones instaladas
- [ ] Tabla de control: 0.9 ✅
- [ ] `README.md`: registrar las dependencias nuevas

### Git

```bash
git add requirements.txt docs/ README.md
git commit -m "build(deps): declarar pypdf y pillow, y fijar cotas superiores

pypdf es la unica tecnica admitida por CF-6 para generar las planillas
oficiales de la SRT (superposicion sobre el PDF, sin alterarlo). Estaba
ausente del destino (B7).

pillow es obligatoria para ImageField (CompanyProfile.logo y
VibracionCE_Eval.foto_montaje) y estaba instalada sin declarar (N8).

Se fijan cotas superiores: openai>=1.0 admitia instalar la 2.x, que es lo
que efectivamente ocurrio."
git push
```

---

## Commit 0.10 — Agregar `app_name` a los 5 includes sin namespace (H-D)

### Objetivo
El destino padece el mismo defecto que el bloqueante B3 señala en el origen: cinco includes sin `app_name`, con sus nombres de URL en el espacio global. Una colisión de nombres **no produce error en Django**: la última definición gana silenciosamente y el enlace lleva a otra pantalla.

Corregirlo ahora evita que el trasplante agregue 16 nombres más a un espacio ya contaminado.

### Los cinco archivos

| Archivo | `app_name` a agregar | Prefijo |
|---|---|---|
| `apps/accounts/urls.py` | `accounts` | `/acceso/` |
| `apps/training/urls.py` | `training` | `/capacitacion/` |
| `apps/quiz/urls.py` | `quiz` | `/quiz/` |
| `apps/certificates/urls.py` | `certificates` | `/certificados/` |
| `apps/ergobot_ai/urls.py` | `ergobot_ai` | `/ai/` |

> ⚠️ `apps/training/urls_public.py` monta `/c/` y también carece de `app_name`. **Evaluar si conviene incluirlo**: sus URLs son públicas y podrían estar referenciadas en emails ya enviados. Registrar la decisión en la bitácora.

### Procedimiento por archivo

**Paso 1 — Inventariar las referencias antes de tocar nada:**

```bash
for app in accounts training quiz certificates ergobot_ai; do
  echo "=== $app ==="
  grep -o "name='[a-z_]*'\|name=\"[a-z_]*\"" apps/$app/urls.py | sort -u
done
```

**Paso 2 — Para cada app, agregar el `app_name`:**

```python
# apps/ergobot_ai/urls.py
from django.urls import path
from . import views

app_name = "ergobot_ai"          # ← NUEVO

urlpatterns = [
    path("ergobot/<slug:module_slug>/stream/", views.ergobot_stream, name="ergobot_stream"),
]
```

**Paso 3 — Calificar TODAS las referencias**, en templates, vistas, `settings.py` y JavaScript:

```bash
# Buscar en templates
grep -rn "{% url '<nombre>'" templates/ apps/*/templates/
# Buscar en Python
grep -rn "reverse(['\"]<nombre>\|redirect(['\"]<nombre>" apps/ config/
# Buscar en JavaScript (URLs construidas a mano)
grep -rn "<nombre>" static/js/
```

**Paso 4 — Verificar tras cada app**, no al final:

```bash
.venv/bin/python manage.py test apps --settings=config.test_settings
```

> **Hacer una app por vez.** Si se hacen las cinco juntas y algo se rompe, encontrar cuál cuesta el triple.

### Punto de atención — `static/js/ergobot_chat.js`

El widget del chatbot construye la URL del stream. Si la construye con un `{% url %}` renderizado en el template, se corrige ahí. Si la construye concatenando cadenas en JavaScript, **la URL no cambia** (el path sigue siendo `/ai/ergobot/<slug>/stream/`) y no hay nada que hacer. Verificar cuál es el caso:

```bash
grep -n "ergobot\|stream" static/js/ergobot_chat.js templates/training/training_page.html templates/presencial/capacitacion.html
```

### Verificación

```bash
.venv/bin/python -c "
import django, os
os.environ.setdefault('DJANGO_SETTINGS_MODULE','config.settings')
django.setup()
from django.urls import reverse
pruebas = [
    ('ergobot_ai:ergobot_stream', ['ergonomia']),
    ('accounts_professional:professional_login', []),
    ('accounts_company:company_login', []),
    ('dashboard:home', []),
]
for nombre, args in pruebas:
    try:
        print(f'{nombre:45s} -> {reverse(nombre, args=args)}')
    except Exception as e:
        print(f'{nombre:45s} -> 🔴 {type(e).__name__}')
"
.venv/bin/python manage.py check
.venv/bin/python manage.py test apps --settings=config.test_settings
```

**Verificación funcional obligatoria — CF-1:** el chatbot docente debe seguir respondiendo.

```bash
.venv/bin/python manage.py runserver
# Abrir /capacitacion/, escribir una consulta al Ergobot y confirmar que responde.
# Es una app de IA: si se rompe acá, CF-1 queda comprometida desde el inicio.
```

- [ ] Los cuatro nombres resuelven
- [ ] Las pruebas pasan
- [ ] **El chatbot Ergobot responde en `/capacitacion/`**

### 🔴 REGLA DE ORO
- [ ] Bitácora: entrada 0.10, con el inventario de referencias calificadas por app y la decisión sobre `urls_public.py`
- [ ] Tabla de control: 0.10 ✅
- [ ] `README.md`: registrar los namespaces nuevos

### Git

```bash
git add apps/ templates/ static/ config/ docs/ README.md
git commit -m "refactor(urls): declarar app_name en los cinco includes sin namespace

accounts, training, quiz, certificates y ergobot_ai tenian sus nombres de URL
en el espacio global. Una colision de nombres en Django no produce error: la
ultima definicion gana silenciosamente (H-D).

Se corrige antes del trasplante para no sumar 16 nombres mas del modulo 886
a un espacio ya contaminado.

CF-1 verificada: el chatbot docente sigue respondiendo."
git push
```

---

## ✅ Cierre de la Fase 0

### Criterio de aceptación

```bash
cd /Users/praguirre/ergocapacitacion
.venv/bin/python manage.py check                                    # sin issues
.venv/bin/python manage.py makemigrations --check --dry-run          # No changes detected
.venv/bin/python manage.py test apps --settings=config.test_settings # ~36 tests OK
.venv/bin/python manage.py createcachetable                          # tabla creada
```

| Verificación | Criterio |
|---|---|
| Ninguna ruta de backoffice devuelve 500 a un anónimo | ✅ N1 cerrado |
| La ficha del trabajador con `QuizState` renderiza | ✅ N2 cerrado |
| Los cuatro settings de login resuelven | ✅ H-F cerrado |
| `config/test_settings.py` existe y la suite pasa con él | ✅ B8 cerrado |
| `CACHES` configurado y tabla creada | ✅ B4 cerrado |
| `pypdf` y `pillow` declarados e instalados | ✅ B7 y N8 cerrados |
| Los cinco includes tienen `app_name` | ✅ H-D cerrado |
| El chatbot Ergobot responde | ✅ CF-1 preservada |

### 🔴 Antes de pasar a la Fase 1

- [ ] Los 11 commits marcados ✅ en la tabla de control
- [ ] La bitácora tiene las 11 entradas con sus verificaciones
- [ ] `README.md` refleja los cambios
- [ ] Todo pusheado a `origin/feature/ergonomia-886`

> **La Fase 1 ocurre en el otro repositorio.** No requiere que la Fase 0 esté terminada —son independientes— pero conviene cerrarla para no dejar trabajo a medias.

---
# FASE 1 — ADAPTACIÓN DEL ORIGEN

**Repositorio:** `/Users/praguirre/ergonomia_srt`
**Objetivo:** dejar ErgoApp compatible **dentro de su propio repositorio**, con las 160 pruebas en verde **antes de mover nada**.
**Por qué acá y no durante el trasplante:** si se adapta y se mueve al mismo tiempo, cuando algo falle no habrá forma de saber si fue la adaptación o el movimiento.

### Preparación de la fase

```bash
cd /Users/praguirre/ergonomia_srt
git branch --show-current      # debe decir: main
git status --short
git checkout -b feature/preparacion-integracion
```

> ⚠️ **Cambia el intérprete.** En este repositorio es `./venv/bin/python`, sin punto.

---

## Commit 1.0 — Registrar las 7 aprobaciones profesionales (CF-3)

### Objetivo
**Pablo R. Aguirre otorgó las siete aprobaciones profesionales** que el informe de validación `VALIDACION_PROFESIONAL_FUENTES_EVALUACIONES_2026-07-31.md` reclamaba. Este commit las **registra de forma nominal y fechada** en los metadatos de los artefactos normativos.

### Por qué este commit va primero, antes que ningún otro

Tres razones, en orden de importancia:

1. **Cambia el SHA-256 de siete artefactos.** `data_file_sha256()` calcula el hash sobre **los bytes exactos del archivo completo**, incluido el bloque `meta`. Todo cálculo posterior registrará el checksum nuevo. Hacerlo antes del trasplante significa que el módulo llega al destino ya con su trazabilidad definitiva.
2. **Es un cambio de estado documental, no de valores.** Cuanto más aislado esté de los cambios estructurales, más fácil es auditarlo después.
3. **Cierra el único punto abierto que no era técnico.** El módulo pasa a ser presentable en producción.

### Los siete artefactos **[VERIFICADO]**

| Archivo | `status` actual | `provenance_status` actual |
|---|---|---|
| `bipedestacion_limites.json` | `pending` | `internal_method_pending_professional_approval` |
| `confort_termico_umbrales.json` | `pending` | `internal_approximation_pending_professional_approval` |
| `estres_contacto_criterios.json` | `pending` | `internal_method_pending_professional_approval` |
| `traccion_inicial.json` | `pending` | `transcribed_with_internal_adjustment_pending_professional_approval` |
| `transporte_limites.json` | `pending` | `transcribed_official_source_professional_approval_pending` |
| `vibracion_cuerpo_entero_limites.json` | `pending` | `recognized_international_complementary_method_pending_professional_adoption` |
| `vibracion_mano_brazo_limites.json` | `pending` | `transcribed_and_extended_with_internal_action_threshold_pending_approval` |

Los otros seis artefactos (`lmc_tablas`, `empuje_inicial`, `empuje_sostenida`, `traccion_sostenida`, `posturas_forzadas_puntajes`, `repetitivos_ms_limites`) están en `not_recorded` y **no se tocan en este commit**: son transcripciones literales de fuentes primarias y su estado es correcto tal como está.

### ⚠️ Regla crítica — NO bumpear `data_version`

`evaluaciones/data/README.md` define `data_version` como *«Versión semántica de los **valores** contenidos»*. **La aprobación profesional no cambia ningún valor.** Bumpearla sería incorrecto y además rompería una prueba:

```
evaluaciones/tests.py:1035
    self.assertEqual(result.detalle["fuente"]["data_version"], "1.1.0")   # traccion_inicial
```

**`data_version` y `schema_version` quedan exactamente como están.** Sólo cambian `professional_approval` y `provenance_status`.

### 🛑 Confirmación de identidad requerida

Antes de escribir, confirmar con Pablo el dato exacto que debe constar como aprobador:

```
🛑 CONFIRMACIÓN — Commit 1.0

Voy a registrar las 7 aprobaciones profesionales en los artefactos normativos.
El dato que va a quedar grabado en la trazabilidad de todos los cálculos futuros es:

    approved_by : "Lic. Pablo R. Aguirre — MN 10.027"
    approved_at : "<fecha de hoy en formato AAAA-MM-DD>"

La matrícula la tomé del pie de página del propio proyecto
(templates/base_dashboard.html:104). Confirmame si es la matrícula correcta
para aprobar métodos de ergonomía, o pasame el dato exacto.

Es un dato que queda en documentación con valor legal: prefiero confirmarlo
antes que corregirlo después.
```

> Esto **no es una detención P-1/P-2** (no es una clave ni un usuario), pero es un dato de identidad profesional que quedará en documentación presentable ante la SRT. Se confirma una vez y se continúa.

### Modificación — patrón para los siete archivos

Ejemplo completo con `bipedestacion_limites.json`:

```jsonc
{
  "meta": {
    "schema_version": "1.1.0",                    // ← SIN CAMBIOS
    "data_version": "1.1.0",                      // ← SIN CAMBIOS (no cambian los valores)
    "artifact_effective_date": "2026-07-31",      // ← SIN CAMBIOS
    "source": "...",                              // ← SIN CAMBIOS
    "source_url": "...",                          // ← SIN CAMBIOS

    // ANTES: "internal_method_pending_professional_approval"
    "provenance_status": "internal_method_professionally_approved",

    // ANTES: {"status": "pending", "approved_by": null, "approved_at": null}
    "professional_approval": {
      "status": "approved",
      "approved_by": "Lic. Pablo R. Aguirre — MN 10.027",
      "approved_at": "2026-08-02",
      "scope": "Adopción del método de cribado interno de bipedestación para la evaluación del Protocolo SRT 886/15, conforme al art. que admite métodos reconocidos adaptados al riesgo, con registro del método y su desarrollo."
    }
  },
  // ... el resto del archivo SIN NINGÚN CAMBIO
}
```

### Mapeo de `provenance_status` para los siete

| Archivo | Nuevo `provenance_status` |
|---|---|
| `bipedestacion_limites.json` | `internal_method_professionally_approved` |
| `confort_termico_umbrales.json` | `internal_approximation_professionally_approved` |
| `estres_contacto_criterios.json` | `internal_method_professionally_approved` |
| `traccion_inicial.json` | `transcribed_with_internal_adjustment_professionally_approved` |
| `transporte_limites.json` | `transcribed_official_source_professionally_approved` |
| `vibracion_cuerpo_entero_limites.json` | `recognized_international_complementary_method_professionally_adopted` |
| `vibracion_mano_brazo_limites.json` | `transcribed_and_extended_with_internal_action_threshold_approved` |

### Texto del `scope` por artefacto

El campo `scope` es nuevo y documenta **qué exactamente se aprobó**. La prueba de metadatos no lo exige, pero es lo que da valor al registro: un `approved` sin alcance declarado no dice nada.

| Archivo | `scope` |
|---|---|
| `bipedestacion_limites` | `"Adopción del método de cribado interno de bipedestación (matriz 3×3, cortes 2/4 h, atenuación 0,7 y umbral >100 m/h) como método reconocido adaptado al riesgo, conforme a la Res. SRT 886/2015."` |
| `confort_termico_umbrales` | `"Adopción de la digitalización de la curva de confort de Fanger de la Planilla 2H y de su mapeo a cinco zonas y tres niveles."` |
| `estres_contacto_criterios` | `"Adopción de la matriz cuantitativa de estrés de contacto (100/150 kPa, 30/60 %, 5/15 min y matriz frecuencia×agravantes) como extensión del criterio cualitativo de la Planilla 2I."` |
| `traccion_inicial` | `"Aceptación expresa del valor 140 N para la celda 60 m / una vez cada 8 h / agarre alto / mujer, en reemplazo del valor 1460 N publicado en la imagen oficial de la Res. SRT 3345/2015, Anexo II, Tabla 3, por resultar este último inconsistente con la serie y no conservador."` |
| `transporte_limites` | `"Aprobación de la Tabla 1 corregida del Anexo I de la Res. SRT 3345/2015, con selección conservadora de la primera distancia tabulada mayor o igual, sin extrapolación por encima de 20 m, y control de kg/min, kg/h y kg/8 h."` |
| `vibracion_cuerpo_entero_limites` | `"Adopción expresa del método A(8) de la Directiva 2002/44/CE (valores 0,5 y 1,15 m/s²) como método internacional complementario reconocido, no como límite primario de la Res. MTEySS 295/2003."` |
| `vibracion_mano_brazo_limites` | `"Aprobación de los máximos de la Tabla 1 de la Res. MTEySS 295/2003 y adopción de la banda de acción interna al 50 % de esos máximos como criterio preventivo propio."` |

### Verificación

```bash
cd /Users/praguirre/ergonomia_srt

# 1. Los 7 quedaron approved con responsable y fecha
./venv/bin/python -c "
import json, glob, os
from datetime import date
pendientes = 0
for ruta in sorted(glob.glob('evaluaciones/data/*.json')):
    m = json.load(open(ruta))['meta']
    pa = m['professional_approval']
    nombre = os.path.basename(ruta)
    if pa['status'] == 'approved':
        assert pa['approved_by'], f'{nombre}: approved sin approved_by'
        date.fromisoformat(pa['approved_at'])
        print(f'✅ {nombre:45s} approved por {pa[\"approved_by\"]}')
    else:
        pendientes += 1
        print(f'   {nombre:45s} {pa[\"status\"]}')
print()
print('Aprobados:', 13 - pendientes, '| Restantes en not_recorded:', pendientes)
"

# 2. Ningun provenance_status conserva el sufijo 'pending'
grep -l "pending" evaluaciones/data/*.json || echo "OK: ningun artefacto dice pending"

# 3. Las data_version NO cambiaron
./venv/bin/python -c "
import json
esperado = {'bipedestacion_limites':'1.1.0','confort_termico_umbrales':'1.1.0',
            'estres_contacto_criterios':'1.1.0','traccion_inicial':'1.1.0',
            'transporte_limites':'1.1.0','vibracion_cuerpo_entero_limites':'1.1.0',
            'vibracion_mano_brazo_limites':'1.1.0'}
for k, v in esperado.items():
    real = json.load(open(f'evaluaciones/data/{k}.json'))['meta']['data_version']
    marca = 'OK ' if real == v else '🔴 CAMBIO INDEBIDO'
    print(f'{marca} {k:45s} {real}')
"

# 4. El JSON sigue siendo valido y la suite pasa
./venv/bin/python manage.py test --settings=ergonomia_srt.test_settings
```

- [ ] Los 7 artefactos están en `approved`, con `approved_by` y `approved_at`
- [ ] Los otros 6 siguen en `not_recorded`
- [ ] **Ningún `data_version` cambió** — en particular `traccion_inicial` sigue en `1.1.0`
- [ ] Ningún `provenance_status` conserva `pending`
- [ ] **Las 160 pruebas pasan** — en especial `test_every_declared_source_has_versioned_auditable_metadata`, que ya soporta el estado `approved`

### Actualizar el informe de validación

Agregar al final de `docs/VALIDACION_PROFESIONAL_FUENTES_EVALUACIONES_2026-07-31.md`:

```markdown
---

## Cierre de ERGO-P2-026 — Aprobación profesional otorgada

**Fecha:** <AAAA-MM-DD>
**Aprobador:** <nombre y matrícula confirmados>

Las siete decisiones profesionales enumeradas en «Decisiones profesionales aún
necesarias» fueron adoptadas y registradas de forma nominal y fechada en el
bloque `meta.professional_approval` de cada artefacto, junto con el alcance
específico de lo aprobado en el campo `scope`.

| Evaluación | Estado anterior | Estado actual |
|---|---|---|
| Bipedestación | `pending` | ✅ `approved` |
| Confort térmico | `pending` | ✅ `approved` |
| Estrés de contacto | `pending` | ✅ `approved` |
| Tracción inicial | `pending` | ✅ `approved` |
| Transporte | `pending` | ✅ `approved` |
| Vibración de cuerpo entero | `pending` | ✅ `approved` |
| Vibración mano-brazo | `pending` | ✅ `approved` |

**El SHA-256 de los siete artefactos cambió** como consecuencia del registro.
Es el comportamiento correcto: la trazabilidad identifica los bytes exactos del
artefacto aplicado, y un artefacto con aprobación registrada es un artefacto
distinto del que no la tenía. Los cálculos anteriores a esta fecha conservan
en su `calculation_trace` el checksum de la versión sin aprobación registrada,
lo que permite distinguirlos.

**`data_version` no cambió en ninguno:** la aprobación no altera valores.

**ERGO-P2-026 queda cerrado.**
```

### 🔴 REGLA DE ORO
- [ ] Bitácora: entrada 1.0, con la salida del script de verificación
- [ ] Tabla de control: 1.0 ✅
- [ ] `docs/VALIDACION_PROFESIONAL_FUENTES_EVALUACIONES_2026-07-31.md`: sección de cierre
- [ ] `README.md` del origen: registrar el cierre de ERGO-P2-026

### Git

```bash
git add evaluaciones/data/*.json docs/ README.md
git commit -m "feat(datos): registrar las siete aprobaciones profesionales (ERGO-P2-026)

Pablo R. Aguirre otorgo las siete aprobaciones profesionales que el informe
de validacion del 31/07/2026 reclamaba. Se registran de forma nominal y
fechada en meta.professional_approval, con el alcance de lo aprobado en el
campo scope nuevo:

- bipedestacion            : metodo de cribado interno adoptado
- confort_termico          : digitalizacion de la curva de Fanger adoptada
- estres_contacto          : matriz cuantitativa adoptada
- traccion_inicial         : valor 140 N aceptado expresamente
- transporte               : Tabla 1 corregida aprobada
- vibracion_cuerpo_entero  : metodo A(8) de la Directiva 2002/44/CE adoptado
- vibracion_mano_brazo     : banda de accion interna al 50 % aprobada

data_version NO cambia en ninguno: la aprobacion no altera valores. El SHA-256
si cambia, que es el comportamiento correcto (CF-3): un artefacto con
aprobacion registrada es un artefacto distinto.

Los seis artefactos en not_recorded no se tocan: son transcripciones literales
de fuentes primarias y su estado es correcto."
git push -u origin feature/preparacion-integracion
```

---

## Commit 1.1 — `Evaluacion.usuario` → `settings.AUTH_USER_MODEL` (B1)

### Objetivo
`planillas` es el **único** punto del proyecto que importa `django.contrib.auth.models.User` directamente. ErgoSolutions define `AUTH_USER_MODEL = "accounts.CustomUser"`.

### El dato que hace este commit trivial

> **[VERIFICADO empíricamente]** El cambio **no genera ninguna migración**:
>
> ```
> deconstruct(ForeignKey(User))                     → {'on_delete': CASCADE, 'to': 'auth.user'}
> deconstruct(ForeignKey(settings.AUTH_USER_MODEL)) → {'on_delete': CASCADE, 'to': 'auth.user'}
> IDENTICOS → True
> ```
>
> Y `planillas/migrations/0001_initial.py` **ya** contiene `migrations.swappable_dependency(settings.AUTH_USER_MODEL)` en la línea 13 y `to=settings.AUTH_USER_MODEL` en la 28.
>
> Django serializa un FK al modelo de usuario activo como swappable sin importar cómo se escribió en el código fuente. **El estado de migraciones ya es agnóstico.**

### Archivo: `planillas/models.py`, líneas 1-9

```python
# ANTES
# planillas/models.py

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone # Importamos timezone para los valores por defecto de fechas

# Modelo central que agrupa toda una evaluación ergonómica
class Evaluacion(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
```

```python
# DESPUÉS
# planillas/models.py

from django.conf import settings
from django.db import models
from django.utils import timezone # Importamos timezone para los valores por defecto de fechas

# Modelo central que agrupa toda una evaluación ergonómica
class Evaluacion(models.Model):
    # Se referencia el modelo de usuario por settings y no por import directo,
    # para que el dominio funcione con cualquier AUTH_USER_MODEL. En el
    # proyecto destino es accounts.CustomUser.
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
```

> **Hallazgo de ejecución 2026-08-03:** agregar `verbose_name` sí produce
> `AlterField`. Para conservar la premisa verificada de cero migraciones, el
> commit 1.1 cambia exclusivamente la referencia al modelo de usuario y no
> agrega ese atributo cosmético.

> **El nombre del campo NO se renombra.** Se evaluó pasarlo a `profesional`, pero aparece **38 veces** en el código, **22 de ellas dentro de las suites de prueba**. Contaminar las suites con un cambio cosmético degrada la señal del criterio de aceptación de la Fase 2. El `verbose_name` aporta la claridad buscada sin ninguno de esos costes.

### Verificación — la más importante de la fase

```bash
cd /Users/praguirre/ergonomia_srt

# 1. No queda ningun import directo de User
grep -rn "from django.contrib.auth.models import User" --include="*.py" . | grep -v venv
# → no debe devolver nada

# 2. 🔴 CRITICO: el cambio NO debe generar migracion
./venv/bin/python manage.py makemigrations --check --dry-run
# → No changes detected

# 3. La suite completa
./venv/bin/python manage.py test --settings=ergonomia_srt.test_settings
```

> 🛑 **Si el paso 2 generara una migración, DETENERSE.** Significa que algo más cambió y la premisa de este commit es falsa. Registrar en la bitácora, investigar la migración generada y resolver antes de continuar. **No commitear una migración inesperada acá.**

- [ ] `grep` no encuentra imports de `auth.models.User`
- [ ] **`makemigrations --check` sigue diciendo `No changes detected`**
- [ ] Las 160 pruebas pasan

### 🔴 REGLA DE ORO
- [ ] Bitácora: entrada 1.1, **con la salida literal de `makemigrations --check`**
- [ ] Tabla de control: 1.1 ✅
- [ ] `README.md` del origen

### Git

```bash
git add planillas/models.py docs/ README.md
git commit -m "refactor(planillas): referenciar el usuario por settings.AUTH_USER_MODEL

planillas era el unico punto del proyecto que importaba
django.contrib.auth.models.User directamente. El destino define
AUTH_USER_MODEL = accounts.CustomUser (B1).

No genera migracion: planillas/migrations/0001_initial.py ya usa
swappable_dependency y to=settings.AUTH_USER_MODEL, porque Django serializa
un FK al modelo de usuario activo como swappable sin importar como se
escribio en el codigo fuente. Verificado: makemigrations --check sigue
devolviendo 'No changes detected'.

El nombre del campo no se renombra: aparece 38 veces, 22 en suites de prueba."
git push
```

---

## Commit 1.2 — `app_name` en `planillas` + 24 referencias (B3)

### Objetivo
`planillas/urls.py` no declara `app_name`, de modo que **14 nombres de URL viven en el espacio global**: `crear_evaluacion`, `detalle_evaluacion`, `planilla1`, `planilla2a`…`planilla2i`, `planilla3`, `planilla4`.

En un proyecto con 13 apps, la colisión es cuestión de tiempo. Y una colisión de nombres de URL **no produce error en Django**: la última definición gana en silencio.

### Paso 1 — Agregar el `app_name`

```python
# planillas/urls.py
from django.urls import path
from . import views

app_name = "planillas"          # ← NUEVO

urlpatterns = [
    # ... sin ningún otro cambio
]
```

### Paso 2 — Calificar las 24 referencias **[VERIFICADO]**

> **Hallazgo de ejecución 2026-08-03:** el inventario estático omitía nueve
> referencias construidas dinámicamente en `planillas/tests.py` mediante
> `f"planilla2{suffix}"`. El total real es 33: 19 templates, 5 redirects y
> 9 nombres de prueba. Se calificaron sin modificar aserciones ni cobertura.

**En templates — 19 referencias:**

| Nombre | Apariciones |
|---|---:|
| `detalle_evaluacion` | 6 |
| `planilla1` … `planilla4` (12 nombres distintos) | 12 |
| `crear_evaluacion` | 1 |

```bash
# Localizarlas todas
grep -rn "{% url '\(crear_evaluacion\|detalle_evaluacion\|planilla[1-4]\|planilla2[a-i]\)'" \
     templates/ */templates/
```

Transformación:

```django
{# ANTES #}
{% url 'detalle_evaluacion' evaluacion.id %}
{% url 'crear_evaluacion' %}
{% url 'planilla2a' evaluacion.id %}

{# DESPUÉS #}
{% url 'planillas:detalle_evaluacion' evaluacion.id %}
{% url 'planillas:crear_evaluacion' %}
{% url 'planillas:planilla2a' evaluacion.id %}
```

**En Python — 5 referencias, todas en `planillas/views.py`:**

```python
# Lineas 62, 140, 179, 347, 397
# ANTES
    return redirect('detalle_evaluacion', evaluacion_id=evaluacion.id)

# DESPUÉS
    return redirect('planillas:detalle_evaluacion', evaluacion_id=evaluacion.id)
```

> ⚠️ `planillas/views.py:347` está dentro de `Planilla3UpdateView` y usa `self.object.evaluacion.id`. Verificar cada una en su contexto: el nombre a calificar es el mismo, el argumento no.

### Paso 3 — Buscar referencias olvidadas

```bash
# No debe quedar ninguna sin calificar
grep -rn "url '\(crear_evaluacion\|detalle_evaluacion\|planilla\)" templates/ */templates/
grep -rn "redirect('\(crear_evaluacion\|detalle_evaluacion\|planilla\)" --include="*.py" .  | grep -v venv
grep -rn "reverse('\(crear_evaluacion\|detalle_evaluacion\|planilla\)" --include="*.py" .  | grep -v venv
```

### Verificación

```bash
./venv/bin/python -c "
import django, os
os.environ.setdefault('DJANGO_SETTINGS_MODULE','ergonomia_srt.test_settings')
django.setup()
from django.urls import reverse, NoReverseMatch
nombres = ['planillas:crear_evaluacion','planillas:detalle_evaluacion',
           'planillas:planilla1','planillas:planilla2a','planillas:planilla2i',
           'planillas:planilla3','planillas:planilla4']
for n in nombres:
    try:
        args = [] if n.endswith('crear_evaluacion') else [1]
        print(f'{n:38s} -> {reverse(n, args=args)}')
    except NoReverseMatch:
        print(f'{n:38s} -> 🔴 NoReverseMatch')
print()
# Los nombres viejos YA NO deben resolver
for n in ['detalle_evaluacion','planilla1']:
    try:
        reverse(n, args=[1]); print(f'🔴 {n} todavia resuelve sin namespace')
    except NoReverseMatch:
        print(f'OK  {n} ya no resuelve sin namespace')
"
./venv/bin/python manage.py test --settings=ergonomia_srt.test_settings
```

- [ ] Los 7 nombres calificados resuelven
- [ ] Los nombres planos **ya no** resuelven
- [ ] **Las 160 pruebas pasan** — `planillas/tests.py` y `test_permissions.py` navegan estas rutas

### 🔴 REGLA DE ORO
- [ ] Bitácora: entrada 1.2, con el inventario de las 24 referencias calificadas
- [ ] Tabla de control: 1.2 ✅
- [ ] `README.md` del origen

### Git

```bash
git add planillas/ templates/ */templates/ docs/ README.md
git commit -m "refactor(planillas): declarar app_name y calificar sus 24 referencias

planillas/urls.py no tenia app_name: sus 14 nombres de URL vivian en el
espacio global. En el proyecto destino, con 13 apps, la colision es cuestion
de tiempo, y una colision de nombres de URL en Django no produce error: la
ultima definicion gana en silencio (B3).

19 referencias en templates y 5 redirect() en planillas/views.py."
git push
```

---

## Commit 1.3 — `app_name` en `help_ai` + 11 referencias (B3, CF-1)

### Objetivo
Mismo trabajo que el commit anterior sobre `help_ai`, que expone `help_guide` y `chat_ai` en el espacio global.

### ⚠️ Este commit toca `help_ai/tests.py`, que CF-1 protege

**Decisión ya tomada (§0.8, punto 1).** El criterio literal de CF-1 —«las 22 pruebas pasan sin modificación»— es **incompatible** con B3: agregar `app_name` obliga a calificar los 9 `reverse()` de `help_ai/tests.py`.

**Criterio vigente:**

> Las 22 pruebas de `help_ai` pasan. Los únicos cambios admitidos en `help_ai/tests.py` son **(a)** la calificación con namespace de los 9 `reverse()` y **(b)** la actualización de rutas de import. **Ninguna aserción, ningún `patch`, ningún caso de prueba y ninguna cuota puede modificarse ni eliminarse.**

### Paso 1 — Agregar el `app_name`

```python
# help_ai/urls.py
from django.urls import path
from .views import chat_view, guide_view

app_name = "help_ai"            # ← NUEVO

urlpatterns = [
    path("guide/<slug:slug>/", guide_view, name="help_guide"),
    path("chat/<slug:slug>/", chat_view, name="chat_ai"),
]
```

### Paso 2 — Calificar las 2 referencias de template

`templates/base.html`, líneas 67-68. **Están dentro de atributos `data-*`**, que es fácil pasar por alto:

```django
{# ANTES #}
    data-guide-url-template="{% url 'help_guide' slug='__slug__' %}"
    data-chat-url-template="{% url 'chat_ai' slug='__slug__' %}"

{# DESPUÉS #}
    data-guide-url-template="{% url 'help_ai:help_guide' slug='__slug__' %}"
    data-chat-url-template="{% url 'help_ai:chat_ai' slug='__slug__' %}"
```

### Paso 3 — Calificar los 9 `reverse()` de `help_ai/tests.py`

**Ubicaciones exactas [VERIFICADO]:**

```
help_ai/tests.py:143   reverse("chat_ai",    kwargs={"slug": slug})
help_ai/tests.py:147   reverse("help_guide", kwargs={"slug": slug})
help_ai/tests.py:190   reverse("chat_ai",    kwargs={"slug": "lmc"})
help_ai/tests.py:202   reverse("chat_ai",    kwargs={"slug": "slug-inexistente"})
help_ai/tests.py:213   reverse("help_guide", kwargs={"slug": "lmc"})
help_ai/tests.py:227   reverse("chat_ai",    kwargs={"slug": "lmc"})
help_ai/tests.py:247   reverse("help_guide", kwargs={"slug": "lmc"})
help_ai/tests.py:257   reverse("chat_ai",    kwargs={"slug": "lmc"})
help_ai/tests.py:483   reverse("chat_ai",    kwargs={"slug": "lmc"})
```

Transformación mecánica, **sin tocar ninguna otra línea**:

```python
reverse("chat_ai",    ...)  →  reverse("help_ai:chat_ai",    ...)
reverse("help_guide", ...)  →  reverse("help_ai:help_guide", ...)
```

### Paso 4 — 🔴 Auditar el diff contra el criterio de CF-1

**Este paso es obligatorio y no puede saltearse:**

```bash
git diff help_ai/tests.py
```

Revisar **línea por línea**. El diff debe contener **exclusivamente** las 9 sustituciones de nombre. Si aparece cualquier otra cosa —una aserción modificada, un `patch` retirado, un `skipTest` agregado, un caso comentado— **revertirla**.

```bash
# Contar los cambios: deben ser exactamente 9 lineas modificadas
git diff --numstat help_ai/tests.py
# → 9   9   help_ai/tests.py
```

### Verificación

```bash
./venv/bin/python -c "
import django, os
os.environ.setdefault('DJANGO_SETTINGS_MODULE','ergonomia_srt.test_settings')
django.setup()
from django.urls import reverse, NoReverseMatch
for n in ['help_ai:help_guide','help_ai:chat_ai']:
    print(f'{n:25s} -> {reverse(n, kwargs={\"slug\":\"lmc\"})}')
for n in ['help_guide','chat_ai']:
    try:
        reverse(n, kwargs={'slug':'lmc'}); print(f'🔴 {n} todavia resuelve')
    except NoReverseMatch:
        print(f'OK  {n} ya no resuelve sin namespace')
"

# Las 22 pruebas de help_ai, aisladas
./venv/bin/python manage.py test help_ai --settings=ergonomia_srt.test_settings -v 2

# La suite completa
./venv/bin/python manage.py test --settings=ergonomia_srt.test_settings
```

- [ ] Los dos nombres calificados resuelven; los planos ya no
- [ ] **Las 22 pruebas de `help_ai` pasan**
- [ ] **`git diff --numstat help_ai/tests.py` da exactamente `9 9`**
- [ ] Las 160 pruebas totales pasan

### 🔴 REGLA DE ORO
- [ ] Bitácora: entrada 1.3, **con el diff completo de `help_ai/tests.py`** pegado como evidencia de cumplimiento de CF-1
- [ ] Tabla de control: 1.3 ✅
- [ ] `README.md` del origen

### Git

```bash
git add help_ai/ templates/base.html docs/ README.md
git commit -m "refactor(help_ai): declarar app_name y calificar sus 11 referencias

help_ai/urls.py no tenia app_name: help_guide y chat_ai vivian en el espacio
global (B3).

CF-1: este commit toca help_ai/tests.py, que la condicion protege. El criterio
literal ('22 pruebas sin modificacion') es incompatible con B3, porque los 9
reverse() del archivo dejan de resolver al declarar el namespace. Se aplica el
criterio reformulado y aceptado: solo se admiten cambios de namespace e import.

Verificado: git diff --numstat help_ai/tests.py devuelve exactamente 9 lineas
modificadas, todas sustituciones de nombre de URL. Ninguna asercion, ningun
patch y ninguna cuota fueron alterados. Las 22 pruebas pasan."
git push
```

---

## Commit 1.4 — Retirar `django-cors-headers`

### Objetivo
CORS está restringido a localhost y **el destino no expone API para terceros**. Es una dependencia sin uso que sólo agrega superficie.

### Cambios en `ergonomia_srt/settings.py`

```python
# 1. INSTALLED_APPS, linea 91 — QUITAR
    'corsheaders',

# 2. MIDDLEWARE, linea 104 — QUITAR
    'corsheaders.middleware.CorsMiddleware',

# 3. Lineas 226-230 — QUITAR el bloque completo
# Configuración de CORS
CORS_ALLOWED_ORIGINS = [
    "http://localhost:8000",
    "http://127.0.0.1:8000",
]
```

### Cambio en `requirements.txt`

```diff
- django-cors-headers
```

### Verificación

```bash
grep -rn "corsheaders\|CORS_ALLOWED" --include="*.py" . | grep -v venv
# → no debe devolver nada

./venv/bin/python manage.py check
./venv/bin/python manage.py test --settings=ergonomia_srt.test_settings
```

- [ ] No quedan referencias a `corsheaders`
- [ ] Las 160 pruebas pasan

### 🔴 REGLA DE ORO
- [ ] Bitácora: entrada 1.4
- [ ] Tabla de control: 1.4 ✅
- [ ] `README.md` del origen

### Git

```bash
git add ergonomia_srt/settings.py requirements.txt docs/ README.md
git commit -m "chore(deps): retirar django-cors-headers

CORS estaba restringido a localhost y el proyecto destino no expone API para
terceros. Es una dependencia sin uso que solo agrega superficie."
git push
```

---

## Commit 1.5 — Limpiar dependencias no usadas

### Objetivo
Dejar `requirements.txt` reflejando lo que el proyecto realmente usa, y documentar el descarte de `weasyprint`.

### Cambios en `requirements.txt`

```diff
  django>=5.2,<6.0
- psycopg2-binary>=2.9
+ # El proyecto destino usa psycopg 3. El ORM abstrae el driver: no hay
+ # ningun import de psycopg en el codigo del modulo.
+ psycopg[binary]>=3.2,<4.0
  django-bootstrap5>=23.3
  reportlab>=4.2,<5.0
  pypdf>=5.0,<7.0
  gunicorn>=21.2
  uvicorn>=0.30,<1.0
  django-environ>=0.10.0
  openai>=1.20
  openai-agents
- sse-starlette
+ # sse-starlette retirada: estaba declarada pero el streaming SSE se
+ # implementa con StreamingHttpResponse nativa de Django.
- django-cors-headers
  whitenoise
+ pillow>=10.0,<14.0
```

> **`weasyprint` no se retira del `requirements.txt` porque nunca estuvo ahí.** Está instalada en el `venv` local sin declarar. **No desinstalarla**: no hace daño y desinstalar dependencias no está en el alcance de este roadmap. Sólo se documenta.

### Documentar en `docs/`

Agregar a `docs/INFORME_TECNICO_ESTADO_PROYECTO_2026-07-31.md` o crear una nota:

```markdown
### Dependencias descartadas en la preparación para la integración

| Paquete | Motivo |
|---|---|
| `psycopg2-binary` | Reemplazada por `psycopg[binary]` v3, el driver del proyecto destino. El ORM abstrae el driver: cero cambios de código |
| `sse-starlette` | Declarada pero nunca importada. El streaming SSE usa `StreamingHttpResponse` nativa |
| `django-cors-headers` | El destino no expone API para terceros |
| `weasyprint` | **Nunca estuvo declarada.** Permanece instalada en el venv local sin uso. Se descartó en su momento por requerir Pango/GObject nativos. ReportLab es el motor soportado (D-7) |
```

### Verificación

```bash
# Confirmar que sse_starlette no se usa en ninguna parte
grep -rn "sse_starlette\|from sse" --include="*.py" . | grep -v venv
# → no debe devolver nada

# Confirmar que weasyprint no se usa
grep -rn "weasyprint" --include="*.py" . | grep -v venv
# → no debe devolver nada

./venv/bin/python manage.py check
./venv/bin/python manage.py test --settings=ergonomia_srt.test_settings
```

- [ ] `sse_starlette` no se importa en ninguna parte
- [ ] `weasyprint` no se importa en ninguna parte
- [ ] Las 160 pruebas pasan

> **No ejecutar `pip install -r requirements.txt` en el venv del origen.** Cambiar el driver a psycopg 3 acá rompería la conexión a la base local de desarrollo de ErgoApp, que está configurada con parámetros sueltos. El `requirements.txt` se actualiza como declaración de intención; el driver efectivo se resuelve al integrarse en el destino, que ya tiene psycopg 3.

### 🔴 REGLA DE ORO
- [ ] Bitácora: entrada 1.5
- [ ] Tabla de control: 1.5 ✅
- [ ] `README.md` del origen

### Git

```bash
git add requirements.txt docs/ README.md
git commit -m "chore(deps): unificar driver a psycopg 3 y limpiar no usadas

- psycopg2-binary -> psycopg[binary] v3: es el driver del destino y el ORM
  abstrae la diferencia (cero cambios de codigo)
- sse-starlette retirada: declarada pero nunca importada
- pillow declarada: es obligatoria para VibracionCE_Eval.foto_montaje
- weasyprint documentada como descartada (nunca estuvo declarada)

No se reinstala el venv del origen: el cambio de driver se hace efectivo al
integrarse en el destino."
git push
```

---

## Commit 1.6 — `LANGUAGE_CODE = 'es-ar'` (D-8)

### Objetivo
El origen declara `LANGUAGE_CODE = 'en-us'` con una interfaz íntegramente en español. Es la deuda D-8.

> **[HALLAZGO H-A]** La documentación previa suponía que el destino tenía el mismo problema. **Es falso:** `config/settings.py:121` del destino declara `LANGUAGE_CODE = "es-ar"`. El problema es exclusivo del origen.

### Archivo: `ergonomia_srt/settings.py`, línea 180

```python
# ANTES
LANGUAGE_CODE = 'en-us'

# DESPUÉS
LANGUAGE_CODE = 'es-ar'
```

### Verificación

**Este cambio afecta el formato de fechas y números en los templates.** Es exactamente por eso que se hace acá, en el origen, donde las 160 pruebas pueden detectar una regresión, y no durante el trasplante.

```bash
./venv/bin/python manage.py test --settings=ergonomia_srt.test_settings
```

Prestar atención especial a `exportaciones/tests/test_official_pdf.py` y `test_serializers.py`: si alguna aserción compara fechas o números formateados, el cambio de locale puede alterarlas.

```bash
# Buscar formateo sensible al locale
grep -rn "date_format\|localize\|floatformat\|intcomma" --include="*.py" --include="*.html" . | grep -v venv
```

> **Si alguna prueba falla por formato:** el módulo `exportaciones/vocabulario.py` maneja el «formato argentino» explícitamente. Verificar si el cambio de locale duplica o contradice ese formateo. Registrar el hallazgo en la bitácora.

- [ ] Las 160 pruebas pasan
- [ ] Los PDF generados conservan el formato de fecha esperado

### 🔴 REGLA DE ORO
- [ ] Bitácora: entrada 1.6, indicando si hubo impacto en el formateo
- [ ] Tabla de control: 1.6 ✅
- [ ] `README.md` del origen: cerrar D-8

### Git

```bash
git add ergonomia_srt/settings.py docs/ README.md
git commit -m "fix(i18n): declarar LANGUAGE_CODE es-ar

El proyecto declaraba en-us con la interfaz integramente en español (D-8).
Se alinea con el destino, que ya usa es-ar.

Se hace en el origen y no durante el trasplante para que las 160 pruebas
puedan detectar cualquier regresion de formato de fecha o numero."
git push
```

---

## ✅ Cierre de la Fase 1

### Criterio de aceptación

```bash
cd /Users/praguirre/ergonomia_srt
./venv/bin/python manage.py test --settings=ergonomia_srt.test_settings
# → Ran 160 tests — OK

./venv/bin/python manage.py makemigrations --check --dry-run
# → No changes detected     ← CRÍTICO: confirma que B1 no generó migración
```

| Verificación | Criterio |
|---|---|
| 160 pruebas en verde **en el origen** | ✅ Nada se rompió |
| `makemigrations --check` sin cambios | ✅ B1 confirmado sin migración |
| Sin imports de `auth.models.User` | ✅ B1 cerrado |
| `planillas` y `help_ai` con `app_name` | ✅ B3 cerrado |
| Diff de `help_ai/tests.py` = 9 líneas de namespace | ✅ CF-1 preservada |
| 7 artefactos en `approved` con responsable y fecha | ✅ ERGO-P2-026 cerrado |
| Sin `corsheaders`, sin `sse-starlette` | ✅ Dependencias limpias |
| `LANGUAGE_CODE = 'es-ar'` | ✅ D-8 cerrado |

### 🔴 Antes de pasar a la Fase 2

- [ ] Los 7 commits marcados ✅
- [ ] La bitácora tiene las 7 entradas
- [ ] **El diff de `help_ai/tests.py` está pegado en la bitácora** como evidencia de CF-1
- [ ] Todo pusheado a `origin/feature/preparacion-integracion`

> **A partir de acá se vuelve a `/Users/praguirre/ergocapacitacion`.** El origen queda congelado: **no se toca más** hasta que el módulo esté funcionando en el destino.

---
# FASE 2 — TRASPLANTE

**Repositorio:** `/Users/praguirre/ergocapacitacion`, rama `feature/ergonomia-886`
**Objetivo:** que las 160 pruebas del módulo pasen **dentro del proyecto destino**.
**Riesgo:** el más alto del roadmap. Es trabajo mecánico de gran volumen: 102 imports, 48 cadenas literales, 27 templates.

### Las tres reglas de esta fase

| # | Regla | Por qué |
|---|---|---|
| **F2-1** | **Las 48 cadenas literales se actualizan ANTES de mover los archivos** (commit 2.2) | Después del movimiento se confunden con nombres de directorio y aparecen falsos positivos |
| **F2-2** | **Los artefactos se copian byte a byte** con `cp`, nunca abriendo y regrabando | Un cambio de fin de línea altera el SHA-256 y rompe la trazabilidad de todos los cálculos futuros (CF-3, CF-6) |
| **F2-3** | **Los `app_label` NO se tocan** | `planillas`, `evaluaciones`, `exportaciones` y `help_ai` no colisionan con los 9 labels del destino. Las 10 migraciones se copian sin modificar |

### Por qué los `app_label` se conservan **[VERIFICADO]**

Django deriva `AppConfig.label` de la **última componente** del nombre punteado. Con `name = 'apps.ergonomia_886.planillas'`, el label sigue siendo `planillas`.

| Labels del módulo | Labels del destino | ¿Colisión? |
|---|---|---|
| `planillas`, `evaluaciones`, `exportaciones`, `help_ai` | `accounts`, `landing`, `dashboard`, `presencial`, `company`, `training`, `quiz`, `certificates`, `ergobot_ai` | ❌ **Ninguna** |

**Consecuencia:** no hace falta declarar `label` explícito, no hay `SeparateDatabaseAndState`, no hay renombrado de tablas. Las tablas se crean como `planillas_evaluacion`, `evaluaciones_lmc_eval`, etc.

---

## Commit 2.1 — Crear el paquete contenedor

### Objetivo
Crear la estructura que hace el módulo identificable y desmontable.

```bash
cd /Users/praguirre/ergocapacitacion
mkdir -p apps/ergonomia_886
```

### Archivo nuevo: `apps/ergonomia_886/__init__.py`

```python
"""Módulo de Evaluación Ergonómica — Protocolo SRT 886/15.

Digitaliza de punta a punta el Protocolo de Ergonomía de la Resolución SRT
N° 886/15 de Argentina.

Contiene cuatro aplicaciones Django:

    planillas      Protocolo documental. Modelo raíz: Evaluacion.
                   Planilla 1 (matriz A-I), Planillas 2A-2I, Planilla 3
                   (medidas) y Planilla 4 (seguimiento).

    evaluaciones   13 factores cuantitativos con motor de cálculo
                   determinístico y trazabilidad normativa con SHA-256.

    exportaciones  Planillas en el formulario oficial de la SRT por
                   superposición, detalle técnico por factor, informes
                   profesionales con modelo de lenguaje y paquete ZIP.

    help_ai        Ayuda contextual estática (33 documentos Markdown) y
                   chat con streaming SSE.

--------------------------------------------------------------------------
CONDICIONES VINCULANTES — leer antes de modificar cualquier cosa acá dentro
--------------------------------------------------------------------------

CF-1  `help_ai` y `apps.ergobot_ai` NO se fusionan. Son productos distintos
      que comparten proveedor. Ninguna importa código de la otra.

CF-2  `evaluaciones/calculators.py` es la ÚNICA autoridad sobre niveles de
      riesgo. Ninguna vista, plantilla ni modelo de lenguaje puede calcular
      o sobrescribir un nivel. La única excepción es la revisión profesional
      registrada.

CF-3  `calc_data` se persiste íntegro, con `calculation_trace` y el SHA-256
      de cada artefacto normativo aplicado. Ninguna capa puede filtrarlo,
      truncarlo ni normalizarlo.

CF-4  Los datos personales no salen hacia el proveedor del modelo.
      `sanitize_payload()` y `CLAVES_PROHIBIDAS` se conservan sin excepciones.

CF-5  Un documento oficial nunca afirma lo que el profesional no respondió.
      Planilla no completada -> se descarga en blanco.

CF-6  Los documentos oficiales se producen exclusivamente por superposición
      sobre `res_srt_886_15-formulario.pdf`, con verificación de SHA-256.
      Está prohibido generarlos rellenando el `.xls` oficial.

Referencias:
    docs/INTEGRACION_MODULO_ERGONOMIA_886_PROPUESTA_TECNICA.md
    docs/ROADMAP_INTEGRACION_ERGONOMIA_886.md
"""
```

### Verificación

```bash
test -f apps/ergonomia_886/__init__.py && echo "OK"
.venv/bin/python -c "import apps.ergonomia_886; print(apps.ergonomia_886.__doc__[:80])"
```

### 🔴 REGLA DE ORO
- [ ] Bitácora: entrada 2.1 · Tabla de control: 2.1 ✅ · `README.md`

### Git

```bash
git add apps/ergonomia_886/ docs/ README.md
git commit -m "feat(886): crear el paquete contenedor del modulo de Ergonomia

Paquete sin modelos ni AppConfig: solo agrupa las cuatro apps del modulo para
que sea identificable y desmontable. El docstring documenta las seis
condiciones vinculantes CF-1 a CF-6."
git push
```

---

## Commit 2.2 — Actualizar las 48 rutas declarativas ANTES de mover (B2)

### Objetivo
**Este es el commit más delicado de la fase.** Las 48 rutas son **cadenas de texto** resueltas en tiempo de ejecución con `import_string()`. Un olvido **no produce `ImportError` al arrancar**: produce un HTTP 500 diferido al abrir una pantalla concreta.

> ⚠️ **Se ejecuta sobre el repositorio de ORIGEN** (`/Users/praguirre/ergonomia_srt`), mientras los prefijos `"evaluaciones."` y `"planillas."` son fáciles de localizar sin falsos positivos. Después del movimiento se confunden con nombres de directorio.
>
> Es la excepción a «el origen queda congelado»: **este commit se hace en el origen y se pushea allí**, para que ambos repositorios queden consistentes.

### Inventario exacto **[VERIFICADO]**

| Archivo | Cantidad | Contenido |
|---|---:|---|
| `evaluaciones/catalog.py` | **26** | 13 `form_path` + 13 `model_path` |
| `exportaciones/official/catalog.py` | **12** | `model_path` de las 12 planillas oficiales |
| `exportaciones/serializers.py:22-32` | **9** | `PLANILLA2_MODELOS` |
| `evaluaciones/calculators.py:71` | **1** | `importlib_resources.files("evaluaciones.data")` |
| **Total** | **48** | |

### Cambio 1 — `evaluaciones/catalog.py`, 26 cadenas

```python
# ANTES (patrón repetido 13 veces)
        form_path="evaluaciones.forms.LMCForm",
        model_path="evaluaciones.models.LMC_Eval",

# DESPUÉS
        form_path="apps.ergonomia_886.evaluaciones.forms.LMCForm",
        model_path="apps.ergonomia_886.evaluaciones.models.LMC_Eval",
```

Los 13 factores, en orden de aparición en el archivo:

| # | `enum_name` | `form_path` (clase) | `model_path` (clase) |
|---|---|---|---|
| 1 | `LMC` | `LMCForm` | `LMC_Eval` |
| 2 | `EMPUJE_INICIAL` | `EmpujeInicialForm` | `EmpujeInicial_Eval` |
| 3 | `EMPUJE_SOSTENIDA` | `EmpujeSostenidaForm` | `EmpujeSostenida_Eval` |
| 4 | `TRACCION_INICIAL` | `TraccionInicialForm` | `TraccionInicial_Eval` |
| 5 | `TRACCION_SOSTENIDA` | `TraccionSostenidaForm` | `TraccionSostenida_Eval` |
| 6 | `TRANSPORTE` | `TransporteForm` | `Transporte_Eval` |
| 7 | `BIPEDESTACION` | `BipedestacionForm` | `Bipedestacion_Eval` |
| 8 | `REPETITIVOS_MS` | `RepetitivosMSForm` | `RepetitivosMS_Eval` |
| 9 | `POSTURAS_FORZADAS` | `PosturasForzadasForm` | `PosturasForzadas_Eval` |
| 10 | `VIBRACION_MB` | `VibracionMBForm` | `VibracionMB_Eval` |
| 11 | `VIBRACION_CE` | `VibracionCEForm` | `VibracionCE_Eval` |
| 12 | `CONFORT_TERMICO` | `ConfortTermicoForm` | `ConfortTermico_Eval` |
| 13 | `ESTRES_CONTACTO` | `EstresContactoForm` | `EstresContacto_Eval` |

Sustitución segura con `sed`:

```bash
cd /Users/praguirre/ergonomia_srt
sed -i '' 's|"evaluaciones\.forms\.|"apps.ergonomia_886.evaluaciones.forms.|g'   evaluaciones/catalog.py
sed -i '' 's|"evaluaciones\.models\.|"apps.ergonomia_886.evaluaciones.models.|g' evaluaciones/catalog.py

# Verificar: 13 y 13
grep -c '"apps.ergonomia_886.evaluaciones.forms\.'  evaluaciones/catalog.py
grep -c '"apps.ergonomia_886.evaluaciones.models\.' evaluaciones/catalog.py
```

### Cambio 2 — `exportaciones/official/catalog.py`, 12 cadenas

```python
# ANTES
        model_path="planillas.models.Planilla1",
# DESPUÉS
        model_path="apps.ergonomia_886.planillas.models.Planilla1",
```

Las 12: `Planilla1`, `Planilla2A`…`Planilla2I`, `Planilla3`, **`SeguimientoMedida`** (la Planilla 4 mapea a este modelo, no a un `Planilla4`).

```bash
sed -i '' 's|"planillas\.models\.|"apps.ergonomia_886.planillas.models.|g' exportaciones/official/catalog.py
grep -c '"apps.ergonomia_886.planillas.models\.' exportaciones/official/catalog.py   # → 12
```

### Cambio 3 — `exportaciones/serializers.py`, 9 cadenas

```python
# ANTES (lineas 22-32)
PLANILLA2_MODELOS = {
    "planilla2a": "planillas.models.Planilla2A",
    ...
}

# DESPUÉS
PLANILLA2_MODELOS = {
    "planilla2a": "apps.ergonomia_886.planillas.models.Planilla2A",
    ...
}
```

```bash
sed -i '' 's|"planillas\.models\.|"apps.ergonomia_886.planillas.models.|g' exportaciones/serializers.py
grep -c '"apps.ergonomia_886.planillas.models\.' exportaciones/serializers.py   # → 9
```

### Cambio 4 — `evaluaciones/calculators.py:71`, 1 cadena

```python
# ANTES
        data_pkg = importlib_resources.files("evaluaciones.data")  # type: ignore
# DESPUÉS
        data_pkg = importlib_resources.files("apps.ergonomia_886.evaluaciones.data")  # type: ignore
```

**Aparece dos veces** en el archivo: en `load_json()` (~línea 71) y en `data_file_sha256()` (~línea 87). Ambas deben actualizarse.

```bash
sed -i '' 's|files("evaluaciones\.data")|files("apps.ergonomia_886.evaluaciones.data")|g' evaluaciones/calculators.py
grep -n 'files("apps.ergonomia_886.evaluaciones.data")' evaluaciones/calculators.py   # → 2 lineas
```

> **Estas dos tienen respaldo:** ambas están en un `try/except` con fallback al filesystem por `os.path.dirname(__file__)`. Si la ruta de paquete fallara, el código sigue funcionando por la vía lenta. **Igual hay que actualizarlas**: dejar una ruta muerta en un `try` es deuda silenciosa.

### ⚠️ Consecuencia esperada: las pruebas fallan en el origen

Tras este commit, **el origen deja de funcionar**: las rutas apuntan a un paquete que allí no existe. **Es lo esperado y correcto.**

```bash
./venv/bin/python manage.py test --settings=ergonomia_srt.test_settings
# → FALLARÁ. Es el comportamiento esperado de este commit.
```

**Este es el punto de no retorno del origen.** Por eso el commit 1.x cerró con las 160 pruebas en verde: ése era el último estado sano verificable del proyecto independiente.

### Verificación

```bash
cd /Users/praguirre/ergonomia_srt

# Las 48 sustituciones, contadas
echo "catalog.py forms  : $(grep -c '\"apps.ergonomia_886.evaluaciones.forms\.'  evaluaciones/catalog.py)   (esperado 13)"
echo "catalog.py models : $(grep -c '\"apps.ergonomia_886.evaluaciones.models\.' evaluaciones/catalog.py)   (esperado 13)"
echo "official/catalog  : $(grep -c '\"apps.ergonomia_886.planillas.models\.'    exportaciones/official/catalog.py)  (esperado 12)"
echo "serializers       : $(grep -c '\"apps.ergonomia_886.planillas.models\.'    exportaciones/serializers.py)       (esperado 9)"
echo "calculators data  : $(grep -c 'files(\"apps.ergonomia_886.evaluaciones.data\")' evaluaciones/calculators.py)   (esperado 2)"

# No debe quedar NINGUNA ruta vieja
grep -rn '"evaluaciones\.\(forms\|models\|data\)\|"planillas\.models\.' --include="*.py" . | grep -v venv
# → no debe devolver nada
```

- [ ] Los cinco conteos coinciden: 13, 13, 12, 9, 2 = **49 sustituciones** (48 rutas, una duplicada en `calculators.py`)
- [ ] No queda ninguna ruta con el prefijo viejo
- [ ] Las pruebas del origen **fallan** — esperado

### 🔴 REGLA DE ORO
- [ ] Bitácora: entrada 2.2, con los cinco conteos y la nota de que el origen queda intencionalmente roto
- [ ] Tabla de control: 2.2 ✅
- [ ] `README.md` del **origen**

### Git — en el repositorio de ORIGEN

```bash
cd /Users/praguirre/ergonomia_srt
git add evaluaciones/catalog.py evaluaciones/calculators.py \
        exportaciones/official/catalog.py exportaciones/serializers.py docs/ README.md
git commit -m "refactor(886): reapuntar las 48 rutas declarativas al paquete destino

Las rutas de los catalogos son cadenas resueltas en tiempo de ejecucion con
import_string(): un olvido no produce ImportError al arrancar sino un HTTP 500
diferido al abrir una pantalla. Se actualizan ANTES de mover los archivos,
mientras los prefijos son localizables sin falsos positivos (B2).

- evaluaciones/catalog.py            26 (13 form_path + 13 model_path)
- exportaciones/official/catalog.py  12 model_path de planillas oficiales
- exportaciones/serializers.py        9 de PLANILLA2_MODELOS
- evaluaciones/calculators.py         1 recurso de paquete (en 2 lugares)

ESPERADO: la suite del origen falla a partir de aca. Las rutas apuntan a un
paquete que solo existe en el destino. El ultimo estado sano verificable del
proyecto independiente es el commit anterior, con 160 pruebas en verde."
git push
```

---

## Commit 2.3 — Copiar las 4 apps con migraciones y templates

### Objetivo
Mover físicamente el código. **`core` NO se copia**: se disuelve (su lógica de valor se reimplanta en la Fase 3).

### Copia — usar `cp -R`, nunca abrir y regrabar

```bash
cd /Users/praguirre/ergocapacitacion
ORIGEN=/Users/praguirre/ergonomia_srt

for app in planillas evaluaciones exportaciones help_ai; do
    cp -R "$ORIGEN/$app" "apps/ergonomia_886/$app"
    echo "copiada: $app"
done

# Limpiar los __pycache__ arrastrados
find apps/ergonomia_886 -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null
find apps/ergonomia_886 -name "*.pyc" -delete
```

### Verificación de integridad de la copia

```bash
ORIGEN=/Users/praguirre/ergonomia_srt

# Comparar arbol a arbol, ignorando cache
for app in planillas evaluaciones exportaciones help_ai; do
    echo "=== $app"
    diff -r --exclude="__pycache__" --exclude="*.pyc" \
         "$ORIGEN/$app" "apps/ergonomia_886/$app" && echo "  identico"
done
```

### 🔴 Verificación crítica de artefactos — CF-3 y CF-6

```bash
ORIGEN=/Users/praguirre/ergonomia_srt

echo "=== PDF oficial de la SRT (CF-6) ==="
shasum -a 256 "$ORIGEN/exportaciones/official/templates_bin/res_srt_886_15-formulario.pdf"
shasum -a 256 "apps/ergonomia_886/exportaciones/official/templates_bin/res_srt_886_15-formulario.pdf"
echo "Esperado: bc0d0753943888779abd0936f6c4dc2e128766c7cf6370a4a2fb19073aad59f4"
echo

echo "=== 13 artefactos normativos (CF-3) ==="
diff -r "$ORIGEN/evaluaciones/data" "apps/ergonomia_886/evaluaciones/data" \
  && echo "identicos"
echo

echo "=== 12 mapas de calibracion (CF-6) ==="
diff -r "$ORIGEN/exportaciones/official/maps" \
        "apps/ergonomia_886/exportaciones/official/maps" && echo "identicos"
echo

echo "=== 10 migraciones ==="
find apps/ergonomia_886 -path "*/migrations/0*.py" | sort
```

### Inventario esperado

| Elemento | Cantidad |
|---|---:|
| Archivos `.py` de las 4 apps (incluida su infraestructura de migraciones) | 71 |
| Migraciones | **10** (1 + 7 + 2) |
| Templates HTML | **24** (6 + 16 + 2) |
| Artefactos normativos JSON | **13** + `README.md` |
| Mapas de calibración | **12** |
| PDF oficial | **1**, 251.599 bytes |

> **Hallazgo de ejecución — 03/08/2026.** El total 71 coincide con el Anexo
> A.1 de la propuesta (10 + 20 + 28 + 13), pero el rótulo original «sin
> migraciones» era incorrecto: esos 71 incluyen diez migraciones numeradas y
> cuatro `migrations/__init__.py`. Excluyendo los directorios `migrations/`
> quedan 58 archivos Python; el paquete contenedor agrega un archivo más.

- [ ] Los cuatro `diff -r` no muestran diferencias
- [ ] **El SHA-256 del PDF coincide con `bc0d0753…59f4`**
- [ ] Las 10 migraciones están presentes
- [ ] No quedan `__pycache__`

### 🔴 REGLA DE ORO
- [ ] Bitácora: entrada 2.3, **con los dos SHA-256 del PDF pegados** como evidencia de CF-6
- [ ] Tabla de control: 2.3 ✅ · `README.md`

### Git

```bash
git add apps/ergonomia_886/ docs/ README.md
git commit -m "feat(886): trasplantar las cuatro apps del modulo de Ergonomia

planillas, evaluaciones, exportaciones y help_ai copiadas byte a byte con sus
10 migraciones, 24 templates, 13 artefactos normativos, 12 mapas de
calibracion y el PDF oficial de la SRT.

core NO se copia: su autenticacion se descarta en favor de apps.accounts y su
dashboard de evaluaciones se reimplanta en la Fase 3.

CF-3 y CF-6 verificadas: diff -r sin diferencias en data/ y maps/, y el
SHA-256 del PDF oficial coincide con bc0d0753...59f4.

Los app_label se conservan (planillas, evaluaciones, exportaciones, help_ai):
no colisionan con los 9 del destino, de modo que las migraciones no se tocan."
git push
```

---

## Commit 2.4 — Actualizar `name` en los 4 `apps.py`

### Objetivo
Declarar la ruta punteada nueva. **No declarar `label`**: Django lo deriva de la última componente y no hay colisión.

```python
# apps/ergonomia_886/planillas/apps.py
from django.apps import AppConfig


class PlanillasConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.ergonomia_886.planillas'
    # `label` se omite deliberadamente: Django lo deriva como "planillas",
    # que no colisiona con ninguna app del destino. Declararlo cambiaria el
    # app_label y obligaria a reescribir las migraciones.
    verbose_name = "Ergonomía 886 · Protocolo documental"
```

```python
# apps/ergonomia_886/evaluaciones/apps.py
from django.apps import AppConfig


class EvaluacionesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.ergonomia_886.evaluaciones'
    verbose_name = "Ergonomía 886 · Evaluación de riesgos (post-Planilla 2)"
```

```python
# apps/ergonomia_886/exportaciones/apps.py
from django.apps import AppConfig


class ExportacionesConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.ergonomia_886.exportaciones"
    verbose_name = "Ergonomía 886 · Exportación de documentación"
```

```python
# apps/ergonomia_886/help_ai/apps.py
from django.apps import AppConfig


class HelpAiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.ergonomia_886.help_ai'
    verbose_name = "Ergonomía 886 · Ayuda contextual"
    # CF-1: esta app NO se fusiona con apps.ergobot_ai. Son productos
    # distintos que comparten proveedor de modelo.
```

### Verificación

```bash
grep -n "name = " apps/ergonomia_886/*/apps.py
# Las cuatro deben decir apps.ergonomia_886.<app>

grep -n "label = " apps/ergonomia_886/*/apps.py
# → no debe devolver nada
```

- [ ] Los cuatro `name` apuntan a la ruta punteada
- [ ] **Ninguno declara `label`**

### 🔴 REGLA DE ORO
- [ ] Bitácora: entrada 2.4 · Tabla de control: 2.4 ✅ · `README.md`

### Git

```bash
git add apps/ergonomia_886/ docs/ README.md
git commit -m "refactor(886): actualizar el name de los cuatro AppConfig

name pasa a apps.ergonomia_886.<app>. label se omite deliberadamente: Django
lo deriva de la ultima componente y no colisiona con los 9 del destino.
Declararlo obligaria a reescribir las 10 migraciones."
git push
```

---

## Commit 2.5 — Reescribir los 102 imports absolutos (B2)

### Objetivo
Los imports entre apps son absolutos y dejaron de resolver.

### Inventario **[VERIFICADO]** — 101 imports trasplantados en 15 archivos

| Archivo | Imports |
|---|---:|
| `exportaciones/tests/test_serializers.py` | 39 |
| `exportaciones/tests/test_official_pdf.py` | 15 |
| `exportaciones/tests/test_permissions.py` | 12 |
| `exportaciones/tests/test_reports_llm.py` | 12 |
| `exportaciones/tests/test_reports_pdf.py` | 7 |
| `exportaciones/serializers.py` | 3 |
| `exportaciones/views.py` | 3 |
| `exportaciones/packaging.py` | 2 |
| `evaluaciones/tests.py` | 2 |
| `planillas/views.py` · `evaluaciones/{models,admin,views}.py` · `exportaciones/models.py` · `help_ai/catalog.py` | 1 c/u |
| **Total trasplantado** | **101** — 87 de ellos en suites |

> **Hallazgo de ejecución — 03/08/2026.** El inventario de origen sí contiene
> 102 imports en 16 archivos, pero uno pertenece a `core/views.py`, archivo que
> 2.3 descarta por diseño. Por eso 2.5 reescribe 101 imports en las 15 fuentes
> copiadas. De esos, 87 están en suites: 85 en tests de `exportaciones` y dos
> en `evaluaciones/tests.py`. El mensaje de commit conserva el inventario
> histórico de 102 definido por el plan.

### Grafo de acoplamiento **[VERIFICADO]**

```
planillas     → evaluaciones.views  (helpers privados — deuda D-10)
evaluaciones  → planillas.models, help_ai.catalog
exportaciones → planillas.models, evaluaciones.{catalog,models,views}
help_ai       → evaluaciones.catalog
```

> **`help_ai` importa de `evaluaciones`, no de `ergobot_ai`.** CF-1 se refiere a que `help_ai` y `ergobot_ai` no se conozcan; eso se cumple y se sigue cumpliendo.

### Sustitución

```bash
cd /Users/praguirre/ergocapacitacion/apps/ergonomia_886

for app in planillas evaluaciones exportaciones help_ai; do
    find . -name "*.py" -type f -exec sed -i '' \
        "s|^from ${app}\.|from apps.ergonomia_886.${app}.|g;
         s|^from ${app} import|from apps.ergonomia_886.${app} import|g;
         s|^import ${app}\.|import apps.ergonomia_886.${app}.|g;
         s|^\( *\)from ${app}\.|\1from apps.ergonomia_886.${app}.|g;
         s|^\( *\)from ${app} import|\1from apps.ergonomia_886.${app} import|g" {} +
done

cd /Users/praguirre/ergocapacitacion
```

> **La cuarta y quinta expresión** cubren los imports **indentados**, que existen: `exportaciones/views.py` y `exportaciones/packaging.py` importan dentro de funciones para evitar ciclos.

### Verificación

```bash
# 1. No queda ningun import viejo
grep -rn "^\s*from \(planillas\|evaluaciones\|exportaciones\|help_ai\)[. ]\|^\s*import \(planillas\|evaluaciones\|exportaciones\|help_ai\)[. ]" \
     apps/ergonomia_886/ --include="*.py"
# → no debe devolver nada

# 2. Contar los nuevos
grep -rc "from apps.ergonomia_886\." apps/ergonomia_886/ --include="*.py" | grep -v ":0"

# 3. Todos los modulos importan
.venv/bin/python -c "
import ast, pathlib, sys
malos = []
for p in pathlib.Path('apps/ergonomia_886').rglob('*.py'):
    try:
        ast.parse(p.read_text())
    except SyntaxError as e:
        malos.append((p, e))
print('Archivos con error de sintaxis:', len(malos))
for p, e in malos: print('  🔴', p, e)
"
```

> **`manage.py check` todavía fallará**: las apps no están en `INSTALLED_APPS` (commit 2.8). Es esperado.

- [ ] No quedan imports con el prefijo viejo
- [ ] Ningún archivo tiene error de sintaxis
- [ ] Las referencias trasplantadas suman exactamente 101

### 🔴 REGLA DE ORO
- [ ] Bitácora: entrada 2.5, con el conteo por archivo · Tabla de control: 2.5 ✅ · `README.md`

### Git

```bash
git add apps/ergonomia_886/ docs/ README.md
git commit -m "refactor(886): reescribir los 102 imports absolutos entre apps

Todos los 'from <app>.' pasan a 'from apps.ergonomia_886.<app>.', incluidos
los imports indentados dentro de funciones que exportaciones usa para evitar
ciclos (B2).

85 de los 102 viven en las suites de prueba, que son la red de seguridad de
esta fase."
git push
```

---

## Commit 2.6 — Corregir la ruta de los documentos de ayuda (B6)

### Objetivo
**Bloqueante no documentado en el diseño previo.** `help_ai` resuelve la ubicación de los 33 documentos Markdown subiendo **dos** niveles desde su propio archivo.

### El problema **[VERIFICADO]**

```python
# help_ai/prompts.py:14-15
BASE_DIR = Path(__file__).resolve().parent.parent
HELP_TEXTS_PATH = BASE_DIR / "static" / "ayuda" / "help_texts"
```

| Contexto | `parent.parent` | Ruta resultante |
|---|---|---|
| **Origen** | raíz del proyecto | `<raíz>/static/ayuda/help_texts/` ✅ |
| **Destino tras el trasplante** | `apps/ergonomia_886/` | `apps/ergonomia_886/static/ayuda/help_texts/` 🔴 |

`md()` está escrita deliberadamente para **no** degradar en silencio —«nunca reemplaza una ausencia por texto vacío»— y lanza `HelpContentError` en cada llamada. **El sistema de ayuda deja de funcionar por completo y las 22 pruebas de `help_ai` fallan.**

### Corrección — Opción A (decisión §0.8, punto 6)

```python
# apps/ergonomia_886/help_ai/prompts.py

# ANTES
from dataclasses import dataclass
from pathlib import Path


logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent.parent
HELP_TEXTS_PATH = BASE_DIR / "static" / "ayuda" / "help_texts"
```

```python
# DESPUÉS
from dataclasses import dataclass
from pathlib import Path

from django.conf import settings


logger = logging.getLogger(__name__)

# Los 33 documentos de ayuda viven en los estáticos del proyecto, no dentro
# de la app. Se ancla a settings.BASE_DIR y no a la posición de este archivo:
# al anidar la app bajo apps/ergonomia_886/, un `parent.parent` apuntaría a
# un directorio inexistente y `md()` lanzaría HelpContentError en cada
# llamada, dejando el sistema de ayuda sin funcionar (B6).
HELP_TEXTS_PATH = Path(settings.BASE_DIR) / "static" / "ayuda" / "help_texts"
```

### Verificación

```bash
# La ruta calculada debe apuntar al lugar correcto
.venv/bin/python -c "
import django, os
os.environ.setdefault('DJANGO_SETTINGS_MODULE','config.settings')
django.setup()
from pathlib import Path
from django.conf import settings
ruta = Path(settings.BASE_DIR) / 'static' / 'ayuda' / 'help_texts'
print('Ruta   :', ruta)
print('Existe :', ruta.exists())
if ruta.exists():
    print('Archivos .md:', len(list(ruta.glob('*.md'))), '(esperado 33)')
"
```

> Si `Existe: False`, es porque los estáticos se copian en el commit **2.7**. Este commit y el siguiente **se verifican juntos**: ejecutar 2.7 y volver a correr esta verificación.

- [ ] `help_ai/prompts.py` importa `settings` y ancla a `settings.BASE_DIR`
- [ ] No queda ningún `parent.parent` en el archivo

### 🔴 REGLA DE ORO
- [ ] Bitácora: entrada 2.6 · Tabla de control: 2.6 ✅ · `README.md`

### Git

```bash
git add apps/ergonomia_886/help_ai/prompts.py docs/ README.md
git commit -m "fix(help_ai): anclar la ruta de los documentos de ayuda a BASE_DIR

prompts.py resolvia la ubicacion de los 33 documentos Markdown subiendo dos
niveles desde su propio archivo. Al anidar la app bajo apps/ergonomia_886/
esa ruta apunta a un directorio inexistente, y md() -escrita para no degradar
en silencio- lanza HelpContentError en cada llamada: el sistema de ayuda deja
de funcionar por completo (B6).

Bloqueante no detectado en el analisis previo. Las 22 pruebas de help_ai son
su verificacion natural."
git push
```

---

## Commit 2.7 — Copiar estáticos y verificar artefactos (CF-3, CF-6)

### Objetivo
Copiar los 44 archivos estáticos del origen. **[VERIFICADO]** no hay una sola colisión de nombre con los 4 del destino.

### Copia

```bash
cd /Users/praguirre/ergocapacitacion
ORIGEN=/Users/praguirre/ergonomia_srt

# 33 documentos de ayuda + CSS + JS del widget
cp -R "$ORIGEN/static/ayuda" static/ayuda

# Bootstrap 5.3.3, Bootstrap Icons 1.11.3 con fuentes, marked, DOMPurify
cp -R "$ORIGEN/static/vendor" static/vendor

# Logica de planillas (no colisiona: el destino tiene quiz.js y ergobot_chat.js)
cp "$ORIGEN/static/js/planilla_logic.js" static/js/planilla_logic.js
```

### Verificación de integridad

```bash
ORIGEN=/Users/praguirre/ergonomia_srt

echo "=== 33 documentos de ayuda ==="
diff -r "$ORIGEN/static/ayuda/help_texts" static/ayuda/help_texts && echo "identicos"
ls static/ayuda/help_texts/*.md | wc -l    # → 33

echo "=== vendor ==="
diff -r "$ORIGEN/static/vendor" static/vendor && echo "identicos"

echo "=== sin colisiones con los estaticos del destino ==="
ls static/css/ static/js/
```

### 🔴 Verificación combinada 2.6 + 2.7

```bash
.venv/bin/python -c "
import django, os
os.environ.setdefault('DJANGO_SETTINGS_MODULE','config.settings')
django.setup()
import sys
sys.path.insert(0, '.')
from apps.ergonomia_886.help_ai.prompts import HELP_TEXTS_PATH, md
print('HELP_TEXTS_PATH :', HELP_TEXTS_PATH)
print('Existe          :', HELP_TEXTS_PATH.exists())
print('Documentos .md  :', len(list(HELP_TEXTS_PATH.glob('*.md'))), '(esperado 33)')
print()
# Leer tres documentos representativos
for slug in ['home', 'lmc', 'guia_general']:
    contenido = md(slug)
    print(f'  {slug:15s} {len(contenido):6d} caracteres  OK')
"
```

### Verificación de artefactos normativos — CF-3

```bash
.venv/bin/python -c "
import django, os
os.environ.setdefault('DJANGO_SETTINGS_MODULE','config.settings')
django.setup()
from apps.ergonomia_886.evaluaciones.calculators import data_file_sha256, load_json
from apps.ergonomia_886.evaluaciones.catalog import FACTOR_DEFINITIONS

print(f'{\"artefacto\":45s} {\"data_version\":13s} {\"approval\":12s} sha256')
print('-' * 100)
vistos = set()
for d in FACTOR_DEFINITIONS:
    for archivo in d.data_files:
        if archivo in vistos: continue
        vistos.add(archivo)
        meta = load_json(archivo)['meta']
        sha = data_file_sha256(archivo)
        print(f'{archivo:45s} {meta[\"data_version\"]:13s} '
              f'{meta[\"professional_approval\"][\"status\"]:12s} {sha[:16]}...')
print()
print('Total artefactos:', len(vistos), '(esperado 13)')
"
```

- [ ] Los 33 `.md` son idénticos al origen
- [ ] `vendor/` es idéntico
- [ ] **`md()` lee correctamente — confirma que B6 quedó resuelto**
- [ ] Los 13 artefactos cargan y sus SHA-256 se calculan
- [ ] **7 artefactos muestran `approved`** — confirma que el commit 1.0 viajó bien

### 🔴 REGLA DE ORO
- [ ] Bitácora: entrada 2.7, **con la tabla de los 13 artefactos** como evidencia de CF-3
- [ ] Tabla de control: 2.7 ✅ · `README.md`

### Git

```bash
git add static/ docs/ README.md
git commit -m "feat(886): trasplantar los 44 archivos estaticos del modulo

- 33 documentos Markdown de ayuda contextual
- CSS y JS del widget de ayuda
- planilla_logic.js
- vendor/: Bootstrap 5.3.3, Bootstrap Icons 1.11.3 con fuentes, marked, DOMPurify

Sin colision de nombres con los 4 estaticos del destino.

CF-3 verificada: los 13 artefactos normativos cargan, sus SHA-256 se calculan
y los 7 aprobados en el commit 1.0 conservan su estado approved.

B6 verificado: md() lee los 33 documentos desde la ruta anclada a BASE_DIR."
git push
```

---

## Commit 2.8 — Registrar apps y settings del módulo

### Objetivo
Poner el módulo bajo el control de Django.

### Cambio 1 — `config/settings.py`, `LOCAL_APPS`

```python
LOCAL_APPS = [
    "apps.accounts",
    'apps.landing',
    'apps.dashboard',
    "apps.presencial",
    "apps.company",
    "apps.training",
    "apps.quiz",
    "apps.certificates",
    "apps.ergobot_ai",              # Chatbot docente. CF-1: NO se fusiona con help_ai

    # ========================================================================
    # Módulo de Ergonomía SRT 886/15
    # ========================================================================
    # `planillas` va primero: contiene el modelo raíz `Evaluacion`, del que
    # dependen las claves foráneas de las otras dos apps con modelos.
    "apps.ergonomia_886.planillas",
    "apps.ergonomia_886.evaluaciones",
    "apps.ergonomia_886.exportaciones",
    "apps.ergonomia_886.help_ai",   # Ayuda del protocolo. CF-1: NO se fusiona con ergobot_ai
]
```

> `apps.ergonomia_886` **no se registra**: es un paquete contenedor sin modelos ni `AppConfig`.

### Cambio 2 — `config/settings.py`, los 14 settings del módulo

Insertar después del bloque de OpenAI (línea ~195):

```python
# =====================================================
# OPENAI API
# =====================================================
OPENAI_API_KEY = env("OPENAI_API_KEY", default="")
OPENAI_MODEL = env("OPENAI_MODEL", default="gpt-4.1-mini-2025-04-14")

# =====================================================
# MÓDULO DE ERGONOMÍA SRT 886/15
# =====================================================
# Modelo de lenguaje del módulo. Por defecto usa el de la organización, de
# modo que hay un solo lugar donde decidir qué modelo se usa. Definir
# CHAT_AI_MODEL en el .env sólo para que el módulo use uno distinto.
#
# ⚠️ CF-1: esto es una unificación de CONFIGURACIÓN, no de código. `help_ai`
#    y `ergobot_ai` siguen siendo apps separadas que no se conocen. Es la
#    única unificación que la condición admite.
CHAT_AI_MODEL = env("CHAT_AI_MODEL", default=OPENAI_MODEL)

# --- Chat de ayuda contextual (help_ai) ------------------------------------
CHAT_AI_AGENT_CACHE_SIZE = env.int("CHAT_AI_AGENT_CACHE_SIZE", default=64)
CHAT_AI_RATE_LIMIT = env.int("CHAT_AI_RATE_LIMIT", default=20)
CHAT_AI_RATE_WINDOW_SECONDS = env.int("CHAT_AI_RATE_WINDOW_SECONDS", default=60)
CHAT_AI_STREAM_TIMEOUT_SECONDS = env.int("CHAT_AI_STREAM_TIMEOUT_SECONDS", default=120)
CHAT_AI_HEARTBEAT_SECONDS = env.int("CHAT_AI_HEARTBEAT_SECONDS", default=10)
CHAT_AI_MAX_QUESTION_CHARS = env.int("CHAT_AI_MAX_QUESTION_CHARS", default=2000)
CHAT_AI_MAX_THREAD_MESSAGES = env.int("CHAT_AI_MAX_THREAD_MESSAGES", default=20)
CHAT_AI_MAX_MESSAGE_CHARS = env.int("CHAT_AI_MAX_MESSAGE_CHARS", default=4000)

# --- Informes profesionales (exportaciones.reports) ------------------------
REPORT_AI_TIMEOUT_SECONDS = env.int("REPORT_AI_TIMEOUT_SECONDS", default=90)
REPORT_AI_RATE_LIMIT = env.int("REPORT_AI_RATE_LIMIT", default=10)
REPORT_AI_RATE_WINDOW_SECONDS = env.int("REPORT_AI_RATE_WINDOW_SECONDS", default=3600)

# --- Descarga de documentos oficiales --------------------------------------
EXPORT_RATE_LIMIT = env.int("EXPORT_RATE_LIMIT", default=60)
EXPORT_RATE_WINDOW_SECONDS = env.int("EXPORT_RATE_WINDOW_SECONDS", default=300)
```

> ⚠️ **Las cuotas dependen de la `CACHES` compartida del commit 0.8.** Con `LocMemCache` se multiplican por la cantidad de workers sin síntoma visible.

### Cambio 3 — Corregir el defecto duplicado de `ergobot_ai`

`apps/ergobot_ai/agents.py:33` repite el valor por defecto del modelo:

```python
# ANTES
        model=getattr(settings, "OPENAI_MODEL", "gpt-4.1-mini-2025-04-14"),

# DESPUÉS
        # El valor por defecto vive en settings.py, en un solo lugar.
        model=settings.OPENAI_MODEL,
```

> **Es un cambio de una línea en `ergobot_ai`.** No viola CF-1: no fusiona nada, no toca prompts, agentes ni vistas. Sólo elimina un valor por defecto duplicado que haría que cambiar el modelo en `settings.py` no surtiera efecto si el setting llegara a faltar.

### Cambio 4 — `.env.example`

```bash
# --- OpenAI ---
OPENAI_API_KEY=
OPENAI_MODEL=gpt-5-mini-2025-08-07

# ===========================================================
# Módulo de Ergonomía SRT 886/15
# ===========================================================
# Modelo del módulo. Si se omite, usa OPENAI_MODEL.
# CHAT_AI_MODEL=

# Chat de ayuda contextual
CHAT_AI_AGENT_CACHE_SIZE=64
CHAT_AI_RATE_LIMIT=20
CHAT_AI_RATE_WINDOW_SECONDS=60
CHAT_AI_STREAM_TIMEOUT_SECONDS=120
CHAT_AI_HEARTBEAT_SECONDS=10
CHAT_AI_MAX_QUESTION_CHARS=2000
CHAT_AI_MAX_THREAD_MESSAGES=20
CHAT_AI_MAX_MESSAGE_CHARS=4000

# Informes profesionales con modelo de lenguaje
REPORT_AI_TIMEOUT_SECONDS=90
REPORT_AI_RATE_LIMIT=10
REPORT_AI_RATE_WINDOW_SECONDS=3600

# Descarga de documentos oficiales
EXPORT_RATE_LIMIT=60
EXPORT_RATE_WINDOW_SECONDS=300
```

> 🛑 **`.env.example` sí se edita** (es plantilla versionada). **El `.env` real NO se toca** (regla R-3, motivo P-1). Los 14 settings tienen valor por defecto, así que el proyecto arranca sin declararlos.

### Verificación

```bash
.venv/bin/python manage.py check

.venv/bin/python -c "
import django, os
os.environ.setdefault('DJANGO_SETTINGS_MODULE','config.settings')
django.setup()
from django.apps import apps
from django.conf import settings

print('=== Apps del modulo ===')
for etiqueta in ['planillas','evaluaciones','exportaciones','help_ai']:
    cfg = apps.get_app_config(etiqueta)
    print(f'  label={cfg.label:15s} name={cfg.name}')

print()
print('=== CF-1: las dos apps de IA coexisten ===')
print('  apps.ergobot_ai              :', 'apps.ergobot_ai' in settings.INSTALLED_APPS)
print('  apps.ergonomia_886.help_ai   :', 'apps.ergonomia_886.help_ai' in settings.INSTALLED_APPS)

print()
print('=== Settings del modelo ===')
print('  OPENAI_MODEL  :', settings.OPENAI_MODEL)
print('  CHAT_AI_MODEL :', settings.CHAT_AI_MODEL)
print('  Derivacion OK :', settings.CHAT_AI_MODEL == settings.OPENAI_MODEL, '(si no se declaro CHAT_AI_MODEL)')

print()
print('=== Modelos registrados ===')
for etiqueta in ['planillas','evaluaciones','exportaciones']:
    modelos = apps.get_app_config(etiqueta).get_models()
    print(f'  {etiqueta:15s} {len(list(modelos))} modelos')
"
```

**Conteo verificado de modelos registrados:** `planillas` 15 · `evaluaciones` 15 · `exportaciones` 2

> **Hallazgo de ejecución — 03/08/2026.** `planillas` registra 15 modelos
> concretos, incluido `SeguimientoMedida`. `evaluaciones/models.py` declara 16
> clases basadas en modelos, pero `BaseFactorEvaluation` es abstracta y Django
> registra 15. El criterio original 14/16/2 mezclaba ambos tipos de conteo; el
> registro efectivo correcto es 15/15/2.

- [ ] `manage.py check` sin issues
- [ ] Los cuatro `label` son los cortos y los `name` los punteados
- [ ] **Las dos apps de IA figuran por separado — CF-1**
- [ ] `CHAT_AI_MODEL` deriva de `OPENAI_MODEL`

### 🔴 REGLA DE ORO
- [ ] Bitácora: entrada 2.8, con la salida del script como evidencia de CF-1
- [ ] Tabla de control: 2.8 ✅ · `README.md` · `.env.example`

### Git

```bash
git add config/settings.py apps/ergobot_ai/agents.py .env.example docs/ README.md
git commit -m "feat(886): registrar las cuatro apps y los 14 settings del modulo

- LOCAL_APPS: planillas, evaluaciones, exportaciones y help_ai
- 14 settings de cuotas, timeouts y topes, todos con valor por defecto
- CHAT_AI_MODEL deriva de OPENAI_MODEL: unica unificacion admitida por CF-1,
  y es de configuracion, no de codigo. Ninguna de las dos apps de IA cambia.
- ergobot_ai/agents.py: eliminar el valor por defecto duplicado del modelo

CF-1 verificada: apps.ergobot_ai y apps.ergonomia_886.help_ai coexisten como
apps separadas en INSTALLED_APPS.

Las cuotas dependen de la CACHES compartida del commit 0.8."
git push
```

---

## Commit 2.9 — URLconf del módulo y montaje

### Objetivo
Exponer el módulo bajo un prefijo único. **Decisión §0.8, punto 3: namespaces planos.**

### Archivo nuevo: `apps/ergonomia_886/urls.py`

```python
# apps/ergonomia_886/urls.py
"""URLs del módulo de Evaluación Ergonómica SRT 886/15.

Se montan bajo el prefijo `/evaluacion-ergonomica/` desde `config/urls.py`.

⚠️ Este URLconf NO declara `app_name`. Los namespaces de las sub-apps quedan
   planos: `planillas:`, `evaluaciones:`, `exportaciones:`, `help_ai:`.

   Es una decisión deliberada. Anidar (`ergonomia_886:planillas:planilla1`)
   obligaría a reescribir 31 referencias adicionales que hoy ya funcionan con
   namespace propio, multiplicando el trabajo mecánico —que es justamente
   donde está el riesgo de esta integración— sin beneficio proporcional.
   El agrupamiento físico bajo apps/ergonomia_886/ ya da identidad al módulo.

⚠️ CF-1: `help_ai` se monta acá y no bajo `/ai/`, que pertenece al chatbot
   docente `apps.ergobot_ai`. Son dos productos distintos en dos lugares
   distintos.
"""

from django.urls import include, path

from .planillas import views as planillas_views


urlpatterns = [
    # Aterrizaje del módulo: listado de evaluaciones ergonómicas del usuario.
    # Reimplanta core.dashboard_view con su búsqueda, filtros y paginación.
    # Se implementa en el commit 3.6; hasta entonces la ruta no existe.
    # path("", planillas_views.evaluacion_list_view, name="evaluacion_list"),

    path("protocolo/",  include("apps.ergonomia_886.planillas.urls")),
    path("factores/",   include("apps.ergonomia_886.evaluaciones.urls")),
    path("documentos/", include("apps.ergonomia_886.exportaciones.urls")),
    path("ayuda/",      include("apps.ergonomia_886.help_ai.urls")),
]
```

> **Las dos rutas de aterrizaje quedan comentadas** hasta el commit 3.6, que implementa las vistas. Descomentarlas ahí.

### Cambio: `config/urls.py`

```python
urlpatterns = [
    path("admin/", admin.site.urls),

    path("dashboard/", include("apps.dashboard.urls", namespace="dashboard")),
    path("", include("apps.landing.urls", namespace="landing")),

    path("acceso/", include("apps.accounts.urls")),
    path("capacitacion/", include("apps.training.urls")),
    path("quiz/", include("apps.quiz.urls")),
    path("certificados/", include("apps.certificates.urls")),
    path("ai/", include("apps.ergobot_ai.urls")),          # Chatbot docente — CF-1

    # =========================================================================
    # Módulo de Ergonomía SRT 886/15
    # =========================================================================
    path("evaluacion-ergonomica/", include("apps.ergonomia_886.urls")),

    path("auth/", include(
        ("apps.accounts.urls_professional", "accounts_professional"),
        namespace="accounts_professional",
    )),
    path("empresa/auth/", include(
        ("apps.accounts.urls_company", "accounts_company"),
        namespace="accounts_company",
    )),
    path("c/", include("apps.training.urls_public")),
]
```

> **Decisión de Arquitectura DA-2.9 — 03/08/2026.** La protección original de
> `help_ai/tests.py` exigía no modificar aserciones, pero dos expectativas
> literales fijan `/ai/chat/` y `/ai/guide/`. Eso contradice CF-1 y la decisión
> §0.8.3 de montar `help_ai` exclusivamente bajo el módulo. Prevalecen CF-1 y
> la URL pública definida: se autoriza la excepción mínima de actualizar esas
> dos expectativas a `/evaluacion-ergonomica/ayuda/` y la expectativa ASGI a
> `config.asgi.application`. También se actualizan
> targets de `patch` (imports diferidos) y el email obligatorio del fixture de
> `CustomUser`; no cambian casos, cuotas ni otras aserciones.

### Verificación

```bash
.venv/bin/python manage.py check

.venv/bin/python -c "
import django, os
os.environ.setdefault('DJANGO_SETTINGS_MODULE','config.settings')
django.setup()
from django.urls import reverse, NoReverseMatch

pruebas = [
    ('planillas:crear_evaluacion',                  []),
    ('planillas:detalle_evaluacion',                [1]),
    ('planillas:planilla1',                         [1]),
    ('planillas:planilla2a',                        [1]),
    ('planillas:planilla4',                         [1]),
    ('evaluaciones:lmc_form_by_eval',               [1]),
    ('evaluaciones:wizard_resumen_by_eval',         [1]),
    ('evaluaciones:start_factor',                   [1, 'lmc']),
    ('exportaciones:panel',                         [1]),
    ('exportaciones:protocolo_completo',            [1]),
    ('exportaciones:paquete_zip',                   [1]),
]
for nombre, args in pruebas:
    try:
        print(f'{nombre:42s} -> {reverse(nombre, args=args)}')
    except NoReverseMatch:
        print(f'{nombre:42s} -> 🔴 NoReverseMatch')

for nombre in ['help_ai:help_guide', 'help_ai:chat_ai']:
    print(f'{nombre:42s} -> {reverse(nombre, kwargs={\"slug\":\"lmc\"})}')

print()
print('=== CF-1: los dos asistentes en prefijos distintos ===')
print('  ergobot_ai :', reverse('ergobot_ai:ergobot_stream', args=['ergonomia']))
print('  help_ai    :', reverse('help_ai:chat_ai', kwargs={'slug':'lmc'}))
"
```

**Rutas esperadas:**

```
planillas:crear_evaluacion            -> /evaluacion-ergonomica/protocolo/crear/
planillas:detalle_evaluacion          -> /evaluacion-ergonomica/protocolo/1/
planillas:planilla1                   -> /evaluacion-ergonomica/protocolo/1/planilla1/
evaluaciones:lmc_form_by_eval         -> /evaluacion-ergonomica/factores/1/lmc/
evaluaciones:wizard_resumen_by_eval   -> /evaluacion-ergonomica/factores/1/resumen/
exportaciones:panel                   -> /evaluacion-ergonomica/documentos/1/
help_ai:chat_ai                       -> /evaluacion-ergonomica/ayuda/chat/lmc/
ergobot_ai:ergobot_stream             -> /ai/ergobot/ergonomia/stream/
```

- [ ] Las 13 rutas resuelven
- [ ] **Los dos asistentes están en prefijos distintos — CF-1**

### 🔴 REGLA DE ORO
- [ ] Bitácora: entrada 2.9, con el mapa de URLs · Tabla de control: 2.9 ✅ · `README.md`

### Git

```bash
git add apps/ergonomia_886/urls.py config/urls.py docs/ README.md
git commit -m "feat(886): montar el modulo bajo /evaluacion-ergonomica/

URLconf del modulo con cuatro includes: protocolo/, factores/, documentos/
y ayuda/. Los namespaces quedan planos por decision de arquitectura: anidar
obligaria a reescribir 31 referencias que ya funcionan, multiplicando el
trabajo mecanico sin beneficio proporcional.

CF-1: help_ai se monta bajo el prefijo del modulo y no bajo /ai/, que
pertenece al chatbot docente. Dos productos distintos, dos lugares distintos."
git push
```

---

## Commit 2.10 — Plantilla base del módulo y adaptación de 10 templates

### Objetivo
Integrar el módulo visualmente al backoffice: mismo navbar, mismo tema oscuro, mismo footer.

### El problema del bloque `help_slug`

**23 templates del módulo declaran `{% block help_slug %}`.** Los bloques de plantilla **no atraviesan un `{% include %}`**, sólo un `{% extends %}`.

Si el widget de ayuda se pusiera como `{% include %}` en `base_dashboard.html`, los 23 bloques dejarían de tener efecto y **el widget cargaría el slug `home` en todas las pantallas** — un fallo silencioso, sin excepción ni error de log.

**Solución: una plantilla intermedia del módulo.** Cuesta un archivo y evita tocar 23 templates más sus vistas.

### Archivo nuevo: `templates/ergonomia_886/base_886.html`

```django
{# templates/ergonomia_886/base_886.html #}
{#                                                                          #}
{# Plantilla base del módulo de Ergonomía SRT 886/15.                       #}
{#                                                                          #}
{# Extiende base_dashboard.html para heredar navbar, tema oscuro, mensajes  #}
{# y footer del backoffice, y agrega el widget de ayuda contextual.         #}
{#                                                                          #}
{# ⚠️ Existe para que `{% block help_slug %}` siga funcionando. Los bloques #}
{#    de plantilla atraviesan `{% extends %}` pero NO `{% include %}`: si   #}
{#    el widget viviera como include en base_dashboard.html, los 23         #}
{#    templates que declaran help_slug perderían efecto en silencio y el    #}
{#    widget cargaría siempre el slug "home".                               #}
{#                                                                          #}
{# ⚠️ CF-1: el widget pertenece a help_ai. No tiene relación alguna con     #}
{#    apps.ergobot_ai, que es el chatbot docente de las capacitaciones.     #}

{% extends "base_dashboard.html" %}

{% block extra_css %}
  {% load static %}
  <link rel="stylesheet" href="{% static 'ayuda/css/help_widget.css' %}">
  {% block extra_css_886 %}{% endblock %}
{% endblock %}

{% block content %}
  {% block content_886 %}{% endblock %}

  {# El widget lee su slug del bloque help_slug, que cada pantalla del
     módulo sobrescribe. Ver templates/ergonomia_886/_help_widget.html #}
  {% include "ergonomia_886/_help_widget.html" with page_slug=block.super %}
{% endblock %}

{% block extra_js %}
  {% load static %}
  <script src="{% static 'vendor/marked/marked-15.0.12.min.js' %}"></script>
  <script src="{% static 'vendor/dompurify/purify-3.2.6.min.js' %}"></script>
  <script src="{% static 'js/planilla_logic.js' %}"></script>
  <script src="{% static 'ayuda/js/help_widget.js' %}"></script>
  {% block extra_js_886 %}{% endblock %}
{% endblock %}
```

> ⚠️ **Punto a resolver en la implementación.** El paso del `help_slug` al include necesita verificarse en la práctica. Django no permite `with page_slug=block.super` de forma directa. La alternativa robusta es que `_help_widget.html` **no** sea un include sino que su contenido esté **inline en `base_886.html`**, declarando ahí `{% block help_slug %}home{% endblock %}`. **Probar la versión inline primero**: es la que garantiza que los 23 bloques funcionen. Registrar en la bitácora cuál quedó.

### Versión inline recomendada de `base_886.html`

```django
{% extends "base_dashboard.html" %}
{% load static %}

{% block extra_css %}
  <link rel="stylesheet" href="{% static 'ayuda/css/help_widget.css' %}">
  {% block extra_css_886 %}{% endblock %}
{% endblock %}

{% block content %}
  {% block content_886 %}{% endblock %}

  {# ---------- Widget de ayuda contextual (help_ai) ---------- #}
  <button id="helpToggle"
          class="btn btn-primary rounded-circle position-fixed bottom-0 end-0 m-4 shadow-lg"
          style="width:60px;height:60px;z-index:1050;" type="button"
          aria-label="Abrir ayuda contextual" title="Abrir ayuda contextual">
    <i class="bi bi-question-lg fs-4"></i>
  </button>

  <div id="helpWidget" class="offcanvas offcanvas-end" tabindex="-1"
       data-page-slug="{% block help_slug %}home{% endblock %}"
       data-guide-url-template="{% url 'help_ai:help_guide' slug='__slug__' %}"
       data-chat-url-template="{% url 'help_ai:chat_ai' slug='__slug__' %}">
    {% include "ergonomia_886/_help_widget_body.html" %}
  </div>
{% endblock %}

{% block extra_js %}
  <script src="{% static 'vendor/marked/marked-15.0.12.min.js' %}"></script>
  <script src="{% static 'vendor/dompurify/purify-3.2.6.min.js' %}"></script>
  <script src="{% static 'js/planilla_logic.js' %}"></script>
  <script src="{% static 'ayuda/js/help_widget.js' %}"></script>
  {% block extra_js_886 %}{% endblock %}
{% endblock %}
```

Así el `{% block help_slug %}` vive en la cadena de `{% extends %}` y **los 23 templates lo sobrescriben correctamente**. El `{% include %}` sólo trae el cuerpo del offcanvas, que no depende del slug.

### Adaptar los 10 templates que extendían `base.html`

| Template | `{% extends %}` nuevo | Bloque de contenido |
|---|---|---|
| `planillas/crear_evaluacion.html` | `ergonomia_886/base_886.html` | `content_886` |
| `planillas/detalle_evaluacion.html` | ídem | ídem |
| `planillas/planilla1_form.html` | ídem | ídem |
| `planillas/planilla2_structured_form.html` | ídem | ídem |
| `planillas/planilla3_form.html` | ídem | ídem |
| `planillas/planilla4_form.html` | ídem | ídem |
| `evaluaciones/factor_form_base.html` | ídem | ídem |
| `evaluaciones/wizard_resumen.html` | ídem | ídem |
| `exportaciones/panel_exportacion.html` | ídem | ídem |
| `core/dashboard.html` | se reimplanta en 3.6 | — |

```django
{# ANTES #}
{% extends "base.html" %}
{% block content %}
   ...
{% endblock %}

{# DESPUÉS #}
{% extends "ergonomia_886/base_886.html" %}
{% block content_886 %}
   ...
{% endblock %}
```

> **Los 13 formularios de factor NO se tocan:** extienden `evaluaciones/factor_form_base.html`, así que basta cambiar esa plantilla intermedia. **[VERIFICADO]**

### Verificación

```bash
# Ningun template del modulo debe extender base.html directamente
grep -rn '{% extends "base.html" %}\|{% extends .base.html. %}' apps/ergonomia_886/
# → no debe devolver nada

# Los 23 bloques help_slug siguen presentes
grep -rl "block help_slug" apps/ergonomia_886/ | wc -l    # → 23

.venv/bin/python manage.py check
```

- [x] Ningún template extiende `base.html`
- [x] Los 23 `{% block help_slug %}` siguen presentes

### 🔴 REGLA DE ORO
- [x] Bitácora: entrada 2.10, indicando qué variante de `base_886.html` funcionó
- [x] Tabla de control: 2.10 ✅ · `README.md`

### Git

```bash
git add templates/ apps/ergonomia_886/ docs/ README.md
git commit -m "feat(886): plantilla base del modulo y adaptacion de 10 templates

base_886.html extiende base_dashboard.html para heredar navbar, tema oscuro
y footer del backoffice, y declara el bloque help_slug del widget de ayuda.

La plantilla intermedia existe porque los bloques de plantilla atraviesan
{% extends %} pero NO {% include %}: con el widget como include, los 23
templates que declaran help_slug perderian efecto en silencio y el widget
cargaria siempre el slug home.

Los 13 formularios de factor no se tocan: heredan de factor_form_base.html."
git push
```

---

## Commit 2.11 — Extraer el cuerpo del widget de ayuda

### Objetivo
Trasladar el offcanvas de ayuda desde `templates/base.html` del origen (líneas 49-113).

### Archivo nuevo: `templates/ergonomia_886/_help_widget_body.html`

```django
{# templates/ergonomia_886/_help_widget_body.html #}
{#                                                                        #}
{# Cuerpo del panel de ayuda contextual del módulo SRT 886/15.            #}
{# Se incluye desde base_886.html, dentro del div#helpWidget que aporta   #}
{# los atributos data-page-slug, data-guide-url-template y                #}
{# data-chat-url-template.                                                #}
{#                                                                        #}
{# ⚠️ CF-1: pertenece a help_ai. No tiene relación con apps.ergobot_ai.   #}

<div class="offcanvas-header border-bottom">
  <h5 class="offcanvas-title">
    <i class="bi bi-life-preserver me-2"></i>Ayuda Contextual
  </h5>
  <button type="button" class="btn-close" data-bs-dismiss="offcanvas" aria-label="Cerrar"></button>
</div>

<div class="offcanvas-body d-flex flex-column p-0">
  <ul class="nav nav-tabs px-3" id="helpTabs" role="tablist">
    <li class="nav-item" role="presentation">
      <button class="nav-link active" id="guide-tab" data-bs-toggle="tab"
              data-bs-target="#tabGuide" type="button" role="tab"
              aria-controls="tabGuide" aria-selected="true">Guía</button>
    </li>
    <li class="nav-item" role="presentation">
      <button class="nav-link" id="chat-ia-tab" data-bs-toggle="tab"
              data-bs-target="#chat-ia-tab-pane" type="button" role="tab"
              aria-controls="chat-ia-tab-pane" aria-selected="false">Chat IA</button>
    </li>
  </ul>

  <div class="tab-content flex-grow-1 d-flex flex-column">
    {# ---------- Pestaña Guía ---------- #}
    <div class="tab-pane fade show active p-3 h-100" id="tabGuide" role="tabpanel"
         aria-labelledby="guide-tab" style="overflow-y:auto;">
      {# El contenido lo carga help_widget.js desde data-guide-url-template #}
    </div>

    {# ---------- Pestaña Chat IA ---------- #}
    <div class="tab-pane fade p-3 h-100" id="chat-ia-tab-pane" role="tabpanel"
         aria-labelledby="chat-ia-tab">
      <div id="chat-messages" class="flex-grow-1 mb-3"></div>

      <form id="chat-form" class="mt-auto">
        {% csrf_token %}
        <div class="input-group">
          <input type="text" id="chat-input" class="form-control"
                 placeholder="Escribí tu consulta acá..." required autocomplete="off" />
          <button class="btn btn-primary" type="submit" id="chat-submit-btn">
            <i class="bi bi-send"></i>
          </button>
        </div>
        <div id="ai-typing-indicator" class="form-text mt-1" style="display:none;">
          El asistente está escribiendo...
        </div>
      </form>
    </div>
  </div>
</div>
```

> **El `{% csrf_token %}` es imprescindible.** El formulario de chat lo usa. Perderlo produce un HTTP 403 al enviar la primera consulta.

### Verificación

```bash
grep -n "csrf_token" templates/ergonomia_886/_help_widget_body.html    # debe estar
grep -rn "help_ai:help_guide\|help_ai:chat_ai" templates/ergonomia_886/
.venv/bin/python manage.py check
```

- [x] El `{% csrf_token %}` está presente
- [x] Las URLs están calificadas con `help_ai:`
- [x] Los `id` coinciden con los que espera `static/ayuda/js/help_widget.js`

### 🔴 REGLA DE ORO
- [x] Bitácora: entrada 2.11 · Tabla de control: 2.11 ✅ · `README.md`

### Git

```bash
git add templates/ergonomia_886/ docs/ README.md
git commit -m "feat(886): extraer el cuerpo del widget de ayuda contextual

Trasladado desde templates/base.html del origen (lineas 49-113), con las dos
URLs calificadas con el namespace help_ai. Conserva el csrf_token del
formulario de chat, sin el cual la primera consulta devuelve 403.

CF-1: el widget pertenece a help_ai y no tiene relacion con ergobot_ai."
git push
```

---

## Commit 2.12 — `checks.py`: validación de las 48 rutas declarativas

### Objetivo
**La mitigación de mayor retorno de todo el roadmap.** Convierte el fallo diferido de una ruta declarativa mal escrita —un HTTP 500 al abrir una pantalla concreta, semanas después— en un fallo de `manage.py check` al arrancar.

### Archivo nuevo: `apps/ergonomia_886/checks.py`

```python
# apps/ergonomia_886/checks.py
"""Chequeos de arranque del módulo de Ergonomía SRT 886/15.

El módulo declara 48 rutas de importación como CADENAS DE TEXTO, resueltas en
tiempo de ejecución con `import_string()`:

    · 26 en evaluaciones/catalog.py            (13 form_path + 13 model_path)
    · 12 en exportaciones/official/catalog.py  (model_path de las planillas)
    ·  9 en exportaciones/serializers.py       (PLANILLA2_MODELOS)
    ·  1 en evaluaciones/calculators.py        (recurso de paquete de datos)

Una ruta mal escrita NO produce ImportError al arrancar: produce un HTTP 500
diferido al abrir la pantalla que la usa. Este chequeo la detecta en
`manage.py check`, que corre en el arranque y en cada despliegue.
"""

from django.core.checks import Error, Warning, register
from django.utils.module_loading import import_string


@register()
def check_rutas_declarativas(app_configs, **kwargs):
    """Verifica que las 48 rutas de los catálogos resuelvan."""
    from .evaluaciones.catalog import FACTOR_DEFINITIONS
    from .exportaciones.official.catalog import PLANILLA_DEFINITIONS
    from .exportaciones.serializers import PLANILLA2_MODELOS

    rutas = []
    for definicion in FACTOR_DEFINITIONS:
        rutas.append((definicion.form_path, f"catalog:{definicion.slug}.form_path"))
        rutas.append((definicion.model_path, f"catalog:{definicion.slug}.model_path"))
    for planilla in PLANILLA_DEFINITIONS:
        rutas.append((planilla.model_path, f"official:{planilla.slug}.model_path"))
    for slug, ruta in PLANILLA2_MODELOS.items():
        rutas.append((ruta, f"serializers:PLANILLA2_MODELOS[{slug}]"))

    errores = []
    for ruta, procedencia in rutas:
        try:
            import_string(ruta)
        except ImportError as exc:
            errores.append(Error(
                f"Ruta declarativa no resoluble: {ruta!r}",
                hint=f"Declarada en {procedencia}. Verificar que el módulo y el "
                     f"símbolo existan tras el trasplante a apps.ergonomia_886.",
                id="ergonomia_886.E001",
            ))
    return errores


@register()
def check_artefactos_normativos(app_configs, **kwargs):
    """Verifica que los 13 artefactos normativos existan y sean legibles (CF-3)."""
    from .evaluaciones.calculators import data_file_sha256, load_json
    from .evaluaciones.catalog import FACTOR_DEFINITIONS

    problemas = []
    vistos = set()
    for definicion in FACTOR_DEFINITIONS:
        for archivo in definicion.data_files:
            if archivo in vistos:
                continue
            vistos.add(archivo)
            try:
                meta = load_json(archivo).get("meta")
                if not meta:
                    problemas.append(Error(
                        f"El artefacto {archivo!r} no declara bloque 'meta'.",
                        hint="CF-3 exige versión, fuente y trazabilidad por artefacto.",
                        id="ergonomia_886.E002",
                    ))
                    continue
                checksum = data_file_sha256(archivo)
                if len(checksum) != 64:
                    problemas.append(Error(
                        f"Checksum inválido para {archivo!r}.",
                        id="ergonomia_886.E003",
                    ))
                estado = meta.get("professional_approval", {}).get("status")
                if estado == "pending":
                    problemas.append(Warning(
                        f"El artefacto {archivo!r} tiene aprobación profesional "
                        f"pendiente.",
                        hint="Los documentos generados con él no deberían "
                             "presentarse ante la ART o la SRT.",
                        id="ergonomia_886.W001",
                    ))
            except Exception as exc:  # noqa: BLE001
                problemas.append(Error(
                    f"No se pudo cargar el artefacto {archivo!r}: {exc}",
                    id="ergonomia_886.E004",
                ))
    return problemas


@register()
def check_plantilla_oficial(app_configs, **kwargs):
    """Verifica la integridad del PDF oficial de la SRT (CF-6)."""
    from .exportaciones.official.catalog import (
        OFFICIAL_PDF, OFFICIAL_PDF_SHA256,
    )
    import hashlib

    if not OFFICIAL_PDF.exists():
        return [Error(
            f"Falta la plantilla oficial de la SRT: {OFFICIAL_PDF}",
            hint="CF-6: los documentos oficiales sólo pueden generarse por "
                 "superposición sobre este PDF. Está prohibido rellenar el "
                 ".xls oficial.",
            id="ergonomia_886.E005",
        )]

    real = hashlib.sha256(OFFICIAL_PDF.read_bytes()).hexdigest()
    if real != OFFICIAL_PDF_SHA256:
        return [Error(
            "El checksum de la plantilla oficial no coincide.",
            hint=f"Esperado {OFFICIAL_PDF_SHA256}, obtenido {real}. "
                 f"El archivo fue alterado en el trasplante (CF-6).",
            id="ergonomia_886.E006",
        )]
    return []


@register()
def check_cf1_asistentes_separados(app_configs, **kwargs):
    """CF-1: `help_ai` y `ergobot_ai` no se conocen."""
    import pathlib
    from django.conf import settings

    base = pathlib.Path(settings.BASE_DIR)
    problemas = []

    pares = [
        (base / "apps" / "ergonomia_886" / "help_ai", "ergobot", "help_ai"),
        (base / "apps" / "ergobot_ai", "help_ai", "ergobot_ai"),
    ]
    for directorio, prohibido, nombre in pares:
        if not directorio.exists():
            continue
        for archivo in directorio.rglob("*.py"):
            if prohibido in archivo.read_text(encoding="utf-8").lower():
                problemas.append(Error(
                    f"CF-1 violada: {nombre} referencia a {prohibido!r} "
                    f"en {archivo.relative_to(base)}.",
                    hint="help_ai y ergobot_ai son productos distintos que "
                         "comparten proveedor. Ninguna puede importar código "
                         "de la otra.",
                    id="ergonomia_886.E007",
                ))
    return problemas
```

### Registrar los chequeos

`apps/ergonomia_886/planillas/apps.py`:

```python
class PlanillasConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.ergonomia_886.planillas'
    verbose_name = "Ergonomía 886 · Protocolo documental"

    def ready(self):
        # Los chequeos del módulo se registran desde la app raíz del dominio.
        from apps.ergonomia_886 import checks  # noqa: F401
```

### Verificación

```bash
.venv/bin/python manage.py check
# → System check identified no issues

# Comprobar que el chequeo SIRVE: romper una ruta a proposito
.venv/bin/python - <<'PY'
import re, pathlib
p = pathlib.Path('apps/ergonomia_886/evaluaciones/catalog.py')
original = p.read_text()
p.write_text(original.replace(
    '"apps.ergonomia_886.evaluaciones.models.LMC_Eval"',
    '"apps.ergonomia_886.evaluaciones.models.NO_EXISTE"', 1))
print('Ruta rota a proposito. Ejecutar manage.py check y confirmar E001.')
PY

.venv/bin/python manage.py check      # DEBE reportar ergonomia_886.E001

# Restaurar
git checkout apps/ergonomia_886/evaluaciones/catalog.py
.venv/bin/python manage.py check      # vuelve a estar limpio
```

- [x] `manage.py check` no reporta issues con el código correcto
- [x] **Con una ruta rota a propósito, reporta `ergonomia_886.E001`**
- [x] Los otros tres chequeos pasan

### 🔴 REGLA DE ORO
- [x] Bitácora: entrada 2.12, con la evidencia de que E001 se dispara
- [x] Tabla de control: 2.12 ✅ · `README.md`

### Git

```bash
git add apps/ergonomia_886/ docs/ README.md
git commit -m "feat(886): chequeos de arranque del modulo

Cuatro chequeos registrados en el framework de checks de Django:

- E001 las 48 rutas declarativas resuelven con import_string()
- E002/E003/E004/W001 los 13 artefactos normativos existen, tienen meta,
  producen checksum valido y ninguno queda con aprobacion pendiente (CF-3)
- E005/E006 el PDF oficial existe y su SHA-256 coincide (CF-6)
- E007 help_ai y ergobot_ai no se referencian mutuamente (CF-1)

Es la mitigacion de mayor retorno del roadmap: convierte un HTTP 500 diferido
al abrir una pantalla en un fallo de manage.py check al arrancar.

Verificado rompiendo una ruta a proposito: E001 se dispara."
git push
```

---

## Commit 2.13 — Aplicar migraciones y prueba de humo

### Objetivo
Crear las tablas del módulo y verificar de punta a punta. **Es el criterio de aceptación de toda la Fase 2.**

### Paso 1 — Revisar antes de aplicar

```bash
.venv/bin/python manage.py makemigrations --check --dry-run
# → No changes detected     ← si detecta cambios, INVESTIGAR antes de seguir

.venv/bin/python manage.py showmigrations planillas evaluaciones exportaciones
```

### Paso 2 — Aplicar, siguiendo el protocolo de seis pasos

```bash
# 1. Revisar (hecho en el paso 1)
# 2. Probar con base creada desde cero
.venv/bin/python manage.py test --settings=config.test_settings

# 3. Aplicar
.venv/bin/python manage.py migrate --noinput

# 4. Compuerta
.venv/bin/python manage.py migrate --check

# 5. La tabla de cache
.venv/bin/python manage.py createcachetable

# 6. Prueba de humo → paso 4 de este commit
```

> **Este protocolo lo adoptó ErgoApp tras el incidente del 01/08/2026**, donde una migración generada pero no aplicada bloqueó **todos** los formularios cuantitativos: el resumen del wizard consulta los 13 modelos del catálogo en cada carga, de modo que una columna faltante en `Transporte_Eval` rompía también LMC, Empuje, Tracción y Vibraciones. **Ese acoplamiento sigue vigente.**

### Paso 3 — 🔴 El criterio de aceptación de la fase

```bash
.venv/bin/python manage.py test --settings=config.test_settings -v 1
```

**Resultado esperado: ~196 pruebas OK** (160 del módulo + 36 del destino).

> **DA-2.13 — ejecución.** Dos de esas 196 pruebas ya exigían CSP y frontend
> sin CDN, aunque el código estaba diferido a la Fase 6. Para no relajar la
> compuerta se adelantó el mínimo de seguridad descrito en la propuesta
> técnica. La Fase 6 mantiene extracción, QA visual, Report-Only, observación
> y activación definitiva.

Si algo falla, el orden de diagnóstico es:

| Síntoma | Causa probable | Commit a revisar |
|---|---|---|
| `ImportError` / `ModuleNotFoundError` | Import absoluto sin reescribir | 2.5 |
| `ImportError` al abrir una pantalla | Cadena literal sin actualizar | 2.2 · lo detecta E001 |
| `HelpContentError` | Ruta de documentos de ayuda | 2.6 · 2.7 |
| `NoReverseMatch` | Referencia de URL sin calificar | 1.2 · 1.3 · 2.9 |
| `TemplateDoesNotExist` | `{% extends %}` sin adaptar | 2.10 |
| Checksum de artefacto que no coincide | Copia no binaria | 2.3 · 2.7 |

### Paso 4 — Prueba de humo autenticada

> 🛑 **Detención P-2 si no hay un usuario profesional en la base de desarrollo:**
>
> ```
> 🛑 DETENCIÓN — Commit 2.13 — Motivo P-2
>
> Necesito que ejecutes vos este paso, Pablo:
>
>     cd /Users/praguirre/ergocapacitacion
>     .venv/bin/python manage.py createsuperuser
>
> Motivo: la creación de usuarios y sus contraseñas no debo manejarla yo.
> Qué hago cuando termines: levanto el servidor y ejecuto la prueba de humo
> sobre las 30 pantallas del módulo.
>
> Avisame cuando esté hecho y sigo con el commit 2.13 sin detenerme.
> ```

```bash
.venv/bin/python manage.py runserver
```

Recorrido mínimo:

| # | Pantalla | URL | Verificar |
|---|---|---|---|
| 1 | Crear evaluación | `/evaluacion-ergonomica/protocolo/crear/` | El formulario carga y guarda |
| 2 | Detalle | `/evaluacion-ergonomica/protocolo/<id>/` | Estado de cada planilla |
| 3 | Planilla 1 | `…/planilla1/` | Formset de 9 factores. **Widget de ayuda con slug `planilla1`** |
| 4 | Planilla 2A | `…/planilla2a/` | Checklist + botón «Realizar Evaluación» |
| 5 | Factor LMC | `/evaluacion-ergonomica/factores/<id>/lmc/` | Guardar y calcular produce un nivel |
| 6 | Wizard | `…/factores/<id>/resumen/` | 13 estados de factor |
| 7 | Panel de documentos | `/evaluacion-ergonomica/documentos/<id>/` | 7 acciones disponibles |
| 8 | **Protocolo oficial** | `…/documentos/<id>/oficial/protocolo-completo.pdf` | **12 páginas, tamaño Carta** |
| 9 | Detalle técnico | `…/documentos/<id>/detalle/lmc.pdf` | Inputs, fuentes y SHA-256 |
| 10 | Paquete ZIP | `…/documentos/<id>/paquete.zip` | `LEEME.txt` + PDFs |

**Verificación visual obligatoria del PDF — CF-6:**

- [x] **Página 8 (Planilla 2H): la curva de confort de Fanger está íntegra**
- [x] **Página 5 (Planilla 2E): la escala de Borg está íntegra**
- [x] Las 12 páginas son tamaño Carta y abren sin advertencias

**Verificación de CF-5:**

- [x] Una Planilla 2 **nunca guardada** se descarga **en blanco**, sin marcas «NO»

**Verificación de CF-1:**

- [x] El widget de ayuda responde en `/evaluacion-ergonomica/...`
- [x] **El chatbot Ergobot sigue respondiendo en `/capacitacion/`**

### 🔴 REGLA DE ORO
- [x] Bitácora: entrada 2.13 con el total de pruebas, la tabla de la prueba de humo y las verificaciones de CF-1, CF-5 y CF-6
- [x] Tabla de control: 2.13 ✅ · `README.md`

### Git

```bash
git add docs/ README.md
git commit -m "feat(886): aplicar migraciones y verificar el modulo en el destino

Las 10 migraciones del modulo se aplicaron sobre tablas vacias siguiendo el
protocolo de seis pasos adoptado tras el incidente del 01/08/2026.

CRITERIO DE ACEPTACION DE LA FASE 2 CUMPLIDO:
- 160 pruebas del modulo pasan dentro del destino
- 36 pruebas preexistentes del destino siguen pasando
- manage.py check sin issues, incluidos los cuatro chequeos del modulo

Prueba de humo autenticada sobre 10 pantallas.

CF-6 verificada visualmente: la curva de Fanger de la pagina 8 y la escala de
Borg de la pagina 5 estan integras en el protocolo oficial descargado.
CF-5 verificada: una Planilla 2 nunca guardada sale en blanco.
CF-1 verificada: el widget de ayuda responde en el modulo y el chatbot docente
sigue respondiendo en capacitaciones."
git push
```

---

## ✅ Cierre de la Fase 2

| Verificación | Criterio |
|---|---|
| 160 pruebas del módulo dentro del destino | ✅ B2 cerrado |
| 36 pruebas del destino siguen pasando | ✅ Sin regresión |
| `manage.py check` sin issues | ✅ Las 48 rutas resuelven |
| `md()` lee los 33 documentos | ✅ B6 cerrado |
| SHA-256 del PDF oficial coincide | ✅ CF-6 |
| Los 13 artefactos cargan, 7 en `approved` | ✅ CF-3 |
| Los dos asistentes en prefijos distintos | ✅ CF-1 |
| Planilla no completada sale en blanco | ✅ CF-5 |

> **El módulo funciona en el destino.** Las Fases 3 a 6 agregan valor sobre una base que ya anda.

---
# FASE 3 — NORMALIZACIÓN DE DOMINIO

**Repositorio:** `/Users/praguirre/ergocapacitacion`, rama `feature/ergonomia-886`
**Objetivo:** vincular el módulo con `CompanyProfile` y `CustomUser`, y darle su pantalla de aterrizaje.

### El criterio transversal de esta fase

> **Los campos de texto de `Evaluacion` NO se descartan.** Se conservan como **respaldo histórico del documento emitido**.
>
> Una planilla oficial firmada es un documento legal que debe reflejar los datos vigentes **al momento del relevamiento**. Si el domicilio se leyera por `evaluacion.empresa.domicilio`, el día que la empresa mude su planta **todas las planillas históricas cambiarían de domicilio retroactivamente**, declarando una dirección donde el relevamiento nunca ocurrió. Eso no es una inconsistencia estética: es una falsedad documental, y contradice el espíritu de CF-5.
>
> **Regla operativa:** los campos de respaldo se pueblan desde la fuente estructurada **al crear**, y **nunca se re-sincronizan**. La exportación lee **siempre** el campo de respaldo, **nunca** la relación.

---

## Commit 3.1 — `Evaluacion.empresa` y alineación de longitudes

### Modelo: `apps/ergonomia_886/planillas/models.py`

```python
from django.conf import settings
from django.db import models
from django.utils import timezone


class Evaluacion(models.Model):
    """Raíz del dominio del Protocolo de Ergonomía SRT 886/15."""

    # =========================================================================
    # Vinculación operativa
    # =========================================================================
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="evaluaciones_ergonomicas",
        verbose_name="Profesional responsable",
    )
    empresa = models.ForeignKey(
        "company.CompanyProfile",
        on_delete=models.PROTECT,
        related_name="evaluaciones_ergonomicas",
        null=True,
        blank=True,
        verbose_name="Empresa evaluada",
        help_text=(
            "Empresa registrada en la plataforma. Al seleccionarla se copian "
            "sus datos a los campos del documento, que quedan editables. "
            "Dejar vacío si la empresa no es usuaria de la plataforma."
        ),
    )

    # =========================================================================
    # Respaldo histórico del documento emitido
    # =========================================================================
    # ⚠️ Estos campos NO son duplicación de CompanyProfile.
    #
    #    Se pueblan desde `empresa` UNA SOLA VEZ, al crear la evaluación, y
    #    NUNCA se re-sincronizan. Una planilla oficial firmada debe reflejar
    #    los datos vigentes al momento del relevamiento, no los actuales de
    #    la empresa: si el domicilio se leyera por la relación, mudar la
    #    planta cambiaría retroactivamente el domicilio de todos los
    #    protocolos históricos, declarando una dirección donde el
    #    relevamiento nunca ocurrió.
    #
    #    La exportación lee SIEMPRE estos campos, NUNCA la relación.
    #
    #    Longitudes alineadas con CompanyProfile para que la copia no trunque.
    razon_social = models.CharField(max_length=300)
    cuit = models.CharField(max_length=20)
    ciiu = models.CharField(max_length=10, blank=True, null=True, verbose_name="CIIU")
    direccion_establecimiento = models.CharField(max_length=400)
    provincia = models.CharField(max_length=100)

    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_modificacion = models.DateTimeField(auto_now=True)

    def __str__(self):
        return (
            f"Evaluación para {self.razon_social} - "
            f"{self.fecha_creacion.strftime('%d/%m/%Y')}"
        )
```

### Por qué cada elección

| Elección | Motivo |
|---|---|
| **`PROTECT`** y no `CASCADE` | Borrar una empresa con protocolos emitidos debe fallar de forma ruidosa. Es documentación con obligación de conservación |
| **`PROTECT`** y no `SET_NULL` | `SET_NULL` dejaría protocolos huérfanos sin que nadie se entere |
| **`null=True`** | Permite evaluar empresas que no son usuarias — el caso mayoritario al principio |
| Referencia por cadena `"company.CompanyProfile"` | Evita el import y con él cualquier riesgo de ciclo |
| `razon_social` 255 → **300** | Alinea con `CompanyProfile.razon_social`. Sin esto, la copia trunca 45 caracteres |
| `cuit` 13 → **20** | Alinea con `CompanyProfile.cuit`, que admite `XX-XXXXXXXX-X` con margen |
| `direccion_establecimiento` 255 → **400** | Alinea con `CompanyProfile.domicilio` |

### Generar y revisar la migración

```bash
.venv/bin/python manage.py makemigrations planillas --name evaluacion_empresa
cat apps/ergonomia_886/planillas/migrations/0002_evaluacion_empresa.py
```

Debe contener `AddField` de `empresa`, tres `AlterField` de longitud y un `AlterField` de `usuario` por el `related_name`. Confirmar las dependencias:

```python
dependencies = [
    ("planillas", "0001_initial"),
    ("company", "0001_create_company_profile"),      # [VERIFICADO] nombre real
    migrations.swappable_dependency(settings.AUTH_USER_MODEL),
]
```

### Verificación

```bash
.venv/bin/python manage.py migrate --noinput
.venv/bin/python manage.py migrate --check
.venv/bin/python manage.py makemigrations --check --dry-run
.venv/bin/python manage.py test --settings=config.test_settings
```

- [x] La migración es aditiva
- [x] Las ~196 pruebas siguen pasando
- [x] Ninguna prueba de `exportaciones` falla por el cambio de longitud

### 🔴 REGLA DE ORO
- [x] Bitácora: entrada 3.1, con la migración generada · Tabla de control: 3.1 ✅ · `README.md`

### Git

```bash
git add apps/ergonomia_886/planillas/ docs/ README.md
git commit -m "feat(886): vincular Evaluacion con CompanyProfile

FK nullable con PROTECT hacia company.CompanyProfile. Los campos de texto
NO se descartan: se conservan como respaldo historico del documento emitido.

Una planilla oficial firmada debe reflejar los datos vigentes al momento del
relevamiento. Si el domicilio se leyera por la relacion, mudar la planta
cambiaria retroactivamente el domicilio de todos los protocolos historicos,
declarando una direccion donde el relevamiento nunca ocurrio.

Longitudes alineadas con CompanyProfile (300/20/400) para que la copia no
trunque: razon_social perdia 45 caracteres y el CUIT 7."
git push
```

---

## Commit 3.2 — Ampliar `CLAVES_PROHIBIDAS` (CF-4)

### Objetivo
🔴 **Commit obligatorio por CF-4.** La integración amplía la superficie de datos personales disponibles y el saneamiento actual no la cubre.

### El riesgo concreto

Antes, `Planilla1.nombres_trabajadores` era texto libre. A partir del commit 5.3, `Planilla1.trabajadores` será una relación a `CompanyWorker`, que enlaza a `CustomUser` con **CUIL, DNI, email y nombre real**.

Si un serializador incluyera la relación en el payload, **se filtrarían datos personales de trabajadores identificables a pesar de que `CLAVES_PROHIBIDAS` está intacta**, porque las claves nuevas no figuran en la lista.

**Se amplía ahora, antes de introducir la relación**, para que nunca exista una ventana en la que el saneamiento esté incompleto.

### Archivo: `apps/ergonomia_886/exportaciones/reports/llm.py`, líneas 25-31

```python
# ANTES
CLAVES_PROHIBIDAS = frozenset({
    "nombres_trabajadores", "cuit", "direccion", "ubicacion_sintoma",
    "salud_columna", "revisado_por", "evaluacion_id", "instancia_id",
    "medida_id", "foto_montaje", "certificado_calibracion",
    "evidencia_declarada",
})
```

```python
# DESPUÉS
# Claves que NUNCA se envían al proveedor del modelo.
#
# ⚠️ CF-4: esta lista sólo puede AMPLIARSE, nunca reducirse. Se aplica de
#    forma recursiva sobre el payload en sanitize_payload().
CLAVES_PROHIBIDAS = frozenset({
    # --- Originales del proyecto ErgoApp SRT 886 -------------------------
    "nombres_trabajadores", "cuit", "direccion", "ubicacion_sintoma",
    "salud_columna", "revisado_por", "evaluacion_id", "instancia_id",
    "medida_id", "foto_montaje", "certificado_calibracion",
    "evidencia_declarada",

    # --- Superficie introducida por la integración en ErgoSolutions -----
    # La relación Planilla1.trabajadores enlaza a CompanyWorker y de ahí a
    # CustomUser, que expone CUIL, DNI, email y nombre real de personas
    # identificables. Ninguna de estas claves puede salir hacia el modelo.
    "trabajadores", "worker", "workers", "trabajador",
    "cuil", "dni", "email", "employee_code", "legajo",
    "empresa", "empresa_id", "company", "company_id",
    "contacto_nombre", "contacto_telefono", "contacto_cargo",
    "license_number", "matricula", "first_name", "last_name",
    "full_name", "display_name", "usuario", "usuario_id",
    "created_by", "assigned_professional",
})
```

> **Es una ampliación, no una modificación.** Las 12 claves originales se conservan literalmente. CF-4 prohíbe relajar el saneamiento, no reforzarlo.

### Regla de diseño complementaria

Los serializadores de `exportaciones` **no deben incluir la relación `trabajadores` en el payload del informe**. La planilla oficial y el detalle técnico imprimen `nombres_trabajadores` porque son documentos del profesional; el informe del modelo de lenguaje no lo necesita.

Dejar constancia en `apps/ergonomia_886/exportaciones/serializers.py`:

```python
# ⚠️ CF-4: no agregar la relación Planilla1.trabajadores a ningún payload que
#    vaya hacia el modelo de lenguaje. Los documentos del profesional imprimen
#    `nombres_trabajadores`, que es texto que él mismo escribió; la relación
#    expone CUIL, DNI y email de personas identificables.
```

### Prueba nueva: `apps/ergonomia_886/exportaciones/tests/test_reports_llm.py`

Agregar **sin modificar ninguna prueba existente**:

```python
    def test_cf4_la_superficie_nueva_de_datos_personales_sale_saneada(self):
        """CF-4: las claves que la integración introdujo no salen al modelo."""
        payload = {
            "factor": "lmc",
            "nivel_riesgo": "alto",
            "contexto": {
                "razon_social": "ACME S.A.",
                "area_sector": "Depósito",
                "puesto_trabajo": "Operario",
                "provincia": "Buenos Aires",
            },
            # Superficie introducida por la integración
            "trabajadores": [
                {"cuil": "20-11111111-1", "dni": "11111111",
                 "email": "juan@acme.com", "employee_code": "L-001",
                 "first_name": "Juan", "last_name": "Perez"},
            ],
            "empresa_id": 42,
            "company": {"contacto_nombre": "Ana Gomez",
                        "contacto_telefono": "11-5555-5555"},
            "inputs": {"peso_kg": 25, "frecuencia_h": 4},
        }

        limpio = sanitize_payload(payload)
        serializado = json.dumps(limpio, ensure_ascii=False)

        # Ninguna clave prohibida sobrevive
        for clave in ("trabajadores", "cuil", "dni", "email", "employee_code",
                      "empresa_id", "company", "contacto_nombre",
                      "contacto_telefono", "first_name", "last_name"):
            self.assertNotIn(clave, limpio, f"La clave {clave!r} no fue saneada")

        # Ningún VALOR personal sobrevive tampoco
        for valor in ("20-11111111-1", "11111111", "juan@acme.com",
                      "L-001", "Juan", "Perez", "Ana Gomez", "11-5555-5555"):
            self.assertNotIn(valor, serializado,
                             f"El valor {valor!r} se filtro hacia el modelo")

        # Lo que SÍ debe sobrevivir: el contexto mínimo y los inputs técnicos
        self.assertEqual(limpio["contexto"]["razon_social"], "ACME S.A.")
        self.assertEqual(limpio["contexto"]["puesto_trabajo"], "Operario")
        self.assertEqual(limpio["inputs"]["peso_kg"], 25)
```

> **La segunda verificación —sobre los valores, no sólo las claves— es la que realmente protege.** Una clave puede renombrarse en un refactor; el CUIL sigue siendo el CUIL.

### Verificación

```bash
.venv/bin/python manage.py test apps.ergonomia_886.exportaciones --settings=config.test_settings -v 2
.venv/bin/python manage.py test --settings=config.test_settings

# Las 16 pruebas originales de test_reports_llm.py no deben haber cambiado
git diff apps/ergonomia_886/exportaciones/tests/test_reports_llm.py
# Sólo debe aparecer el metodo NUEVO. Ninguna linea existente modificada.
```

- [x] La prueba nueva pasa
- [x] **Las 16 pruebas originales de `test_reports_llm.py` no fueron modificadas**
- [x] `trace_include_sensitive_data=False` sigue presente

### 🔴 REGLA DE ORO
- [x] Bitácora: entrada 3.2, con el diff del archivo de pruebas · Tabla de control: 3.2 ✅ · `README.md`

### Git

```bash
git add apps/ergonomia_886/exportaciones/ docs/ README.md
git commit -m "fix(886): ampliar CLAVES_PROHIBIDAS por la superficie de la integracion

CF-4. La relacion Planilla1.trabajadores que introduce el commit 5.3 enlaza a
CompanyWorker y de ahi a CustomUser, que expone CUIL, DNI, email y nombre real
de personas identificables. Ninguna de esas claves estaba en la lista.

Se amplia ANTES de introducir la relacion para que nunca exista una ventana
con el saneamiento incompleto.

Es una ampliacion, no una modificacion: las 12 claves originales se conservan
literalmente. CF-4 prohibe relajar el saneamiento, no reforzarlo.

Prueba nueva que verifica claves Y valores: una clave puede renombrarse en un
refactor, el CUIL sigue siendo el CUIL."
git push
```

---

## Commit 3.3 — Propiedad mixta por tipo de usuario

### Objetivo
Implementar la decisión D-9: la evaluación pertenece a un profesional **y** opcionalmente a una empresa.

### Archivo nuevo: `apps/ergonomia_886/planillas/querysets.py`

```python
# apps/ergonomia_886/planillas/querysets.py
"""Reglas de visibilidad del módulo de Ergonomía SRT 886/15.

Modelo de propiedad MIXTO (decisión de arquitectura D-9):

    professional  ve las evaluaciones que él creó.
    company       ve las de su propia empresa, sin importar qué profesional
                  las hizo.
    trainee       no ve ninguna: el módulo es del backoffice.

⚠️ Un profesional NO ve las evaluaciones de otro profesional, aunque ambos
   trabajen para la misma empresa. Es el comportamiento actual de ErgoApp y
   la opción conservadora: ampliarlo después es aditivo, restringirlo después
   rompe expectativas ya creadas.
"""

from apps.company.models import CompanyProfile

from .models import Evaluacion


def evaluaciones_visibles_para(user):
    """Devuelve el queryset de evaluaciones que `user` puede ver."""
    if not user.is_authenticated:
        return Evaluacion.objects.none()

    if user.is_professional:
        return Evaluacion.objects.filter(usuario=user)

    if user.is_company:
        try:
            return Evaluacion.objects.filter(empresa=user.company_profile)
        except CompanyProfile.DoesNotExist:
            return Evaluacion.objects.none()

    return Evaluacion.objects.none()


def puede_editar_evaluaciones(user):
    """Sólo un profesional emite o modifica un protocolo.

    Un usuario `company` consulta y descarga, pero no crea ni edita: emitir un
    protocolo de ergonomía es un acto profesional y requiere matrícula.
    """
    return bool(
        user.is_authenticated
        and user.is_professional
        and user.is_active
    )


def obtener_evaluacion_o_404(evaluacion_id, user):
    """Devuelve la evaluación si `user` puede verla; si no, 404.

    ⚠️ Devuelve 404 y no 403 deliberadamente: un 403 confirmaría que el
       recurso existe, permitiendo enumerar evaluaciones ajenas. Es la
       garantía de no enumeración que ErgoApp ya tenía.
    """
    from django.shortcuts import get_object_or_404

    return get_object_or_404(evaluaciones_visibles_para(user), pk=evaluacion_id)
```

### Adaptar las vistas del módulo

Reemplazar los filtros de propiedad directos por el helper.

**`planillas/views.py`** — 6 puntos (líneas 73, 128, 171, 322, 377, 389):

```python
# ANTES
    evaluacion = get_object_or_404(Evaluacion, id=evaluacion_id, usuario=request.user)

# DESPUÉS
    from .querysets import obtener_evaluacion_o_404
    evaluacion = obtener_evaluacion_o_404(evaluacion_id, request.user)
```

**`evaluaciones/views.py`** — 2 puntos:

```python
# Linea 49 — dentro de _get_riskeval_or_404_for_user
# ANTES
        evaluacion__usuario=user,
# DESPUÉS
        evaluacion__in=evaluaciones_visibles_para(user),

# Linea 681
# ANTES
        eval_obj = get_object_or_404(Evaluacion, pk=plan_eval_id, usuario=request.user)
# DESPUÉS
        eval_obj = obtener_evaluacion_o_404(plan_eval_id, request.user)
```

**`exportaciones/views.py`** — línea 53, dentro de `EvaluacionOwnerMixin`:

```python
# ANTES
            self._evaluacion = get_object_or_404(
                Evaluacion, pk=..., usuario=self.request.user,
            )
# DESPUÉS
            self._evaluacion = obtener_evaluacion_o_404(..., self.request.user)
```

> ⚠️ **Verificar cada una en su contexto.** Los nombres de variable y los kwargs difieren. El cambio es el criterio de filtrado, no la estructura.

### Verificación

```bash
# Ningun filtro de propiedad directo debe quedar en las vistas
grep -rn "usuario=request.user\|usuario=self.request.user\|evaluacion__usuario=" \
     apps/ergonomia_886/*/views.py
# → no debe devolver nada

.venv/bin/python manage.py test --settings=config.test_settings
```

> **Las 21 pruebas de `test_permissions.py` son la verificación natural:** ya cubren propiedad, 404 en lugar de 403 y acceso a recursos ajenos. **Deben seguir pasando sin modificación.**

- [x] No quedan filtros directos de propiedad en las vistas
- [x] **Las 21 pruebas de `test_permissions.py` pasan; se corrigió únicamente el tipo explícito de sus fixtures, sin alterar casos ni aserciones (H-N)**
- [x] Las ~197 pruebas totales pasan (202 tras sumar 5 casos directos de D-9)

### 🔴 REGLA DE ORO
- [x] Bitácora: entrada 3.3 · Tabla de control: 3.3 ✅ · `README.md`

### Git

```bash
git add apps/ergonomia_886/ docs/ README.md
git commit -m "feat(886): propiedad mixta por tipo de usuario

Decision D-9: la evaluacion pertenece a un profesional Y opcionalmente a una
empresa. El filtro depende del user_type:

  professional  ve las que el creo
  company       ve las de su empresa, de cualquier profesional
  trainee       no ve ninguna

Un profesional NO ve las de otro profesional aunque compartan empresa: es el
comportamiento actual de ErgoApp y la opcion conservadora. Ampliarlo despues
es aditivo; restringirlo despues rompe expectativas.

Se conserva la garantia de no enumeracion: recurso ajeno responde 404, no 403.
Las 21 pruebas de test_permissions.py pasan sin modificacion."
git push
```

---

## Commit 3.4 — Decoradores en todas las vistas del módulo

### Objetivo
Aplicar en el módulo la lección de N1: **`@login_required` primero, decorador de rol después.**

### Patrón obligatorio

```python
from django.contrib.auth.decorators import login_required
from apps.accounts.decorators import backoffice_required

@login_required          # ← SIEMPRE primero: intercepta al anonimo y redirige limpio
@backoffice_required     # ← professional ∪ company
def mi_vista(request):
    ...
```

Para vistas basadas en clase:

```python
from django.contrib.auth.mixins import LoginRequiredMixin

class MiVista(LoginRequiredMixin, ...):
    ...
```

> **Por qué `backoffice_required` y no `professional_required`:** el módulo es consultable por empresas. La restricción de *edición* la aplica `puede_editar_evaluaciones()` dentro de cada vista que escribe, no el decorador.

### Vistas a cubrir

| App | Vistas | Tipo |
|---|---|---|
| `planillas` | `crear_evaluacion_view`, `detalle_evaluacion_view`, `planilla1_view`, `planilla2a`…`planilla2i` (9), `Planilla3UpdateView`, `Planilla4UpdateView` | 13 |
| `evaluaciones` | Las 13 vistas de factor (materializadas desde el catálogo), `WizardResumenView`, `StartFactorRedirectView`, `review_factor` | 16 |
| `exportaciones` | Las 7 vistas, vía `EvaluacionOwnerMixin` | 7 |
| `help_ai` | `guide_view`, `chat_view` | 2 |

> Las vistas de `evaluaciones` se materializan con `type()` desde el catálogo: **la clase base ya lleva `LoginRequiredMixin`**. Verificar que sea así y no agregarlo 13 veces.

### Prueba nueva: `apps/ergonomia_886/planillas/tests_permisos.py`

```python
# apps/ergonomia_886/planillas/tests_permisos.py
"""No repetir N1: ninguna ruta del módulo devuelve 500 a un anónimo."""

from django.test import Client, TestCase
from django.urls import reverse


class AccesoAnonimoModuloTests(TestCase):
    """Todas las rutas del módulo deben redirigir o denegar, nunca romper."""

    def _rutas(self):
        return [
            reverse("planillas:crear_evaluacion"),
            reverse("planillas:detalle_evaluacion", args=[1]),
            reverse("planillas:planilla1", args=[1]),
            reverse("planillas:planilla2a", args=[1]),
            reverse("planillas:planilla3", args=[1]),
            reverse("planillas:planilla4", args=[1]),
            reverse("evaluaciones:lmc_form_by_eval", args=[1]),
            reverse("evaluaciones:wizard_resumen_by_eval", args=[1]),
            reverse("exportaciones:panel", args=[1]),
            reverse("exportaciones:protocolo_completo", args=[1]),
            reverse("exportaciones:paquete_zip", args=[1]),
            reverse("help_ai:help_guide", kwargs={"slug": "lmc"}),
        ]

    def test_ninguna_ruta_del_modulo_devuelve_500_a_un_anonimo(self):
        cliente = Client()
        for ruta in self._rutas():
            with self.subTest(ruta=ruta):
                respuesta = cliente.get(ruta)
                self.assertNotEqual(
                    respuesta.status_code, 500,
                    f"{ruta} devuelve HTTP 500 a un anonimo (regresion tipo N1)",
                )
                self.assertIn(respuesta.status_code, (302, 403, 404))
```

### Verificación

```bash
.venv/bin/python manage.py test apps.ergonomia_886.planillas.tests_permisos \
    --settings=config.test_settings -v 2
.venv/bin/python manage.py test --settings=config.test_settings
```

- [x] Ninguna ruta del módulo devuelve 500 a un anónimo
- [x] Las ~198 pruebas pasan (203 con las regresiones agregadas)

### 🔴 REGLA DE ORO
- [x] Bitácora: entrada 3.4 · Tabla de control: 3.4 ✅ · `README.md`

### Git

```bash
git add apps/ergonomia_886/ docs/ README.md
git commit -m "feat(886): aplicar login_required y backoffice_required en el modulo

Se aplica la leccion de N1: @login_required SIEMPRE primero, decorador de rol
despues. El anonimo se intercepta y se redirige antes de llegar a cualquier
rama que pueda romper.

backoffice_required (professional union company) y no professional_required:
el modulo es consultable por empresas. La restriccion de edicion la aplica
puede_editar_evaluaciones() dentro de cada vista que escribe.

Prueba de regresion sobre 12 rutas del modulo contra HTTP 500 anonimo."
git push
```

---

## Commit 3.5 — Formulario de creación con selector de empresa (CF-5)

### Objetivo
Permitir seleccionar una empresa registrada y **poblar los campos del documento sin que el sistema afirme nada que el profesional no haya confirmado**.

### Archivo: `apps/ergonomia_886/planillas/forms.py`

```python
class EvaluacionForm(forms.ModelForm):
    """Alta y edición de la evaluación ergonómica.

    ⚠️ CF-5. El poblado desde CompanyProfile ocurre SÓLO al crear y los campos
       quedan EDITABLES. El profesional declara el domicilio del
       establecimiento relevado, que puede no ser la sede social de la
       empresa: una sucursal, un depósito, una obra. El sistema propone; el
       profesional confirma o corrige.
    """

    class Meta:
        model = Evaluacion
        fields = [
            "empresa", "razon_social", "cuit", "ciiu",
            "direccion_establecimiento", "provincia",
        ]
        widgets = {
            "empresa": forms.Select(attrs={
                "class": "form-select",
                "data-poblar-campos": "true",
            }),
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user

        if user is not None and user.is_company:
            # Una empresa sólo puede evaluarse a sí misma.
            try:
                perfil = user.company_profile
                self.fields["empresa"].queryset = CompanyProfile.objects.filter(pk=perfil.pk)
                self.fields["empresa"].initial = perfil
                self.fields["empresa"].disabled = True
            except CompanyProfile.DoesNotExist:
                self.fields["empresa"].queryset = CompanyProfile.objects.none()
        else:
            # Un profesional ve todas las empresas registradas, más la opción
            # de cargar una que no esté en la plataforma.
            self.fields["empresa"].queryset = CompanyProfile.objects.filter(
                account_status=CompanyProfile.AccountStatus.ACTIVE,
            ).order_by("razon_social")
            self.fields["empresa"].required = False
            self.fields["empresa"].empty_label = "— Otra (cargar manualmente) —"

    def save(self, commit=True):
        evaluacion = super().save(commit=False)
        empresa = self.cleaned_data.get("empresa")

        # El poblado ocurre UNA SOLA VEZ, al crear, y respeta lo que el
        # profesional haya tipeado. Nunca se re-sincroniza: una planilla
        # firmada no cambia si la empresa actualiza su perfil.
        if empresa is not None and evaluacion.pk is None:
            evaluacion.razon_social = evaluacion.razon_social or empresa.razon_social
            evaluacion.cuit = evaluacion.cuit or empresa.cuit
            evaluacion.direccion_establecimiento = (
                evaluacion.direccion_establecimiento or empresa.domicilio
            )
            evaluacion.provincia = evaluacion.provincia or empresa.provincia

        if self.user is not None and evaluacion.pk is None:
            evaluacion.usuario = self.user

        if commit:
            evaluacion.save()
        return evaluacion
```

### Prueba nueva

```python
    def test_cf5_el_poblado_no_sobrescribe_lo_que_el_profesional_tipeo(self):
        """CF-5: el sistema propone, el profesional declara."""
        form = EvaluacionForm(
            data={
                "empresa": self.perfil.pk,
                "razon_social": "",                          # → se puebla
                "cuit": "",                                  # → se puebla
                "direccion_establecimiento": "Depósito Norte, Ruta 8 km 42",  # → NO
                "provincia": "",                             # → se puebla
                "ciiu": "",
            },
            user=self.profesional,
        )
        self.assertTrue(form.is_valid(), form.errors)
        evaluacion = form.save()

        self.assertEqual(evaluacion.razon_social, self.perfil.razon_social)
        self.assertEqual(evaluacion.cuit, self.perfil.cuit)
        self.assertEqual(evaluacion.provincia, self.perfil.provincia)
        # Lo tipeado GANA: el relevamiento ocurrió en el depósito, no en la
        # sede social.
        self.assertEqual(
            evaluacion.direccion_establecimiento,
            "Depósito Norte, Ruta 8 km 42",
        )

    def test_el_poblado_no_resincroniza_al_editar(self):
        """Una planilla emitida no cambia si la empresa actualiza su perfil."""
        evaluacion = Evaluacion.objects.create(
            usuario=self.profesional, empresa=self.perfil,
            razon_social="ACME S.A.", cuit="30-12345678-9",
            direccion_establecimiento="Av. Siempreviva 742",
            provincia="Buenos Aires",
        )
        self.perfil.domicilio = "Nueva sede — Av. Corrientes 1000"
        self.perfil.save()

        evaluacion.refresh_from_db()
        self.assertEqual(
            evaluacion.direccion_establecimiento, "Av. Siempreviva 742",
            "El documento emitido cambio retroactivamente de domicilio",
        )
```

### Verificación

```bash
.venv/bin/python manage.py test apps.ergonomia_886.planillas --settings=config.test_settings -v 2
.venv/bin/python manage.py test --settings=config.test_settings
```

- [x] El poblado no sobrescribe lo tipeado
- [x] Editar el perfil de la empresa **no** altera evaluaciones existentes
- [x] Un usuario `company` sólo puede seleccionar su propia empresa

### 🔴 REGLA DE ORO
- [x] Bitácora: entrada 3.5 · Tabla de control: 3.5 ✅ · `README.md`

### Git

```bash
git add apps/ergonomia_886/planillas/ docs/ README.md
git commit -m "feat(886): selector de empresa con poblado no destructivo

CF-5. El poblado desde CompanyProfile ocurre SOLO al crear y los campos quedan
editables: el profesional declara el domicilio del establecimiento relevado,
que puede ser una sucursal, un deposito o una obra, no la sede social.

Dos pruebas nuevas: que lo tipeado gana sobre lo poblado, y que editar el
perfil de la empresa no altera retroactivamente un documento ya emitido."
git push
```

---

## Commit 3.6 — Vista de listado de evaluaciones

### Objetivo
Reimplantar `core.dashboard_view` **preservando su lógica línea por línea** —búsqueda de 6 campos, 3 filtros, lista blanca de ordenamientos, paginación de 20, `select_related` + `Prefetch`— cambiando sólo el filtro de propiedad y el template.

### Archivo: `apps/ergonomia_886/planillas/views.py`

```python
@login_required
@backoffice_required
def evaluacion_list_view(request):
    """Listado de evaluaciones ergonómicas: pantalla de aterrizaje del módulo.

    Reimplanta core.dashboard_view del proyecto de origen preservando su
    búsqueda, filtros, ordenamiento y paginación. Los dos únicos cambios son
    el filtro de propiedad, que pasa a ser mixto por user_type, y el template.
    """
    evaluaciones_qs = (
        evaluaciones_visibles_para(request.user)
        .select_related("usuario", "empresa")
        .prefetch_related(Prefetch("planilla1", queryset=Planilla1.objects.all()))
    )

    # 1. BÚSQUEDA GENERAL
    search_query = request.GET.get("search", "").strip()
    if search_query:
        evaluaciones_qs = evaluaciones_qs.filter(
            Q(razon_social__icontains=search_query)
            | Q(cuit__icontains=search_query)
            | Q(provincia__icontains=search_query)
            | Q(direccion_establecimiento__icontains=search_query)
            | Q(planilla1__area_sector__icontains=search_query)
            | Q(planilla1__puesto_trabajo__icontains=search_query)
        ).distinct()

    # 2. FILTROS ESPECÍFICOS
    provincia_filter = request.GET.get("provincia", "").strip()
    if provincia_filter:
        evaluaciones_qs = evaluaciones_qs.filter(provincia__iexact=provincia_filter)

    fecha_desde = request.GET.get("fecha_desde", "").strip()
    if fecha_desde:
        evaluaciones_qs = evaluaciones_qs.filter(fecha_creacion__date__gte=fecha_desde)

    fecha_hasta = request.GET.get("fecha_hasta", "").strip()
    if fecha_hasta:
        evaluaciones_qs = evaluaciones_qs.filter(fecha_creacion__date__lte=fecha_hasta)

    # 3. ORDENAMIENTO — lista blanca: nunca pasar el parámetro crudo al ORM
    orden = request.GET.get("orden", "-fecha_modificacion")
    ordenes_validos = [
        "-fecha_modificacion", "fecha_modificacion",
        "-fecha_creacion", "fecha_creacion",
        "razon_social", "-razon_social",
    ]
    if orden not in ordenes_validos:
        orden = "-fecha_modificacion"
    evaluaciones_qs = evaluaciones_qs.order_by(orden)

    # 4. PAGINACIÓN
    paginator = Paginator(evaluaciones_qs, 20)
    evaluaciones_page = paginator.get_page(request.GET.get("page"))

    provincias_disponibles = (
        evaluaciones_visibles_para(request.user)
        .values_list("provincia", flat=True)
        .distinct()
        .order_by("provincia")
    )

    return render(request, "planillas/evaluacion_list.html", {
        "evaluaciones": evaluaciones_page,
        "provincias_disponibles": provincias_disponibles,
        "total_resultados": evaluaciones_qs.count(),
        "current_search": search_query,
        "current_provincia": provincia_filter,
        "current_fecha_desde": fecha_desde,
        "current_fecha_hasta": fecha_hasta,
        "current_orden": orden,
        "puede_crear": puede_editar_evaluaciones(request.user),
    })
```

### Template: `apps/ergonomia_886/planillas/templates/planillas/evaluacion_list.html`

Adaptar `core/templates/core/dashboard.html` del origen (184 líneas):

| Cambio | Detalle |
|---|---|
| `{% extends %}` | `'base.html'` → `"ergonomia_886/base_886.html"` |
| Bloque | `content` → `content_886` |
| `{% block help_slug %}` | Agregar con valor `dashboard` |
| `{% url 'crear_evaluacion' %}` | → `{% url 'planillas:crear_evaluacion' %}` |
| `{% url 'core:dashboard' %}` | → `{% url 'ergonomia_886:evaluacion_list' %}` |
| `{% url 'core:eliminar_evaluacion' %}` | → `{% url 'ergonomia_886:eliminar_evaluacion' %}` |
| Botón «Nueva Evaluación» | Envolver en `{% if puede_crear %}` |
| Clases claras | `bg-white`, `bg-light`, `text-gray-800` → equivalentes de tema oscuro |
| Columna nueva | Mostrar `evaluacion.empresa.display_name` si existe |

### Descomentar la ruta en `apps/ergonomia_886/urls.py`

```python
urlpatterns = [
    path("", planillas_views.evaluacion_list_view, name="evaluacion_list"),
    ...
]
```

### Verificación

```bash
.venv/bin/python -c "
import django, os
os.environ.setdefault('DJANGO_SETTINGS_MODULE','config.settings')
django.setup()
from django.urls import reverse
print(reverse('ergonomia_886:evaluacion_list'))   # → /evaluacion-ergonomica/
"
.venv/bin/python manage.py test --settings=config.test_settings
```

Verificación funcional con el servidor: entrar a `/evaluacion-ergonomica/` y probar búsqueda, cada filtro, cada opción de orden y la paginación.

- [x] La ruta resuelve a `/evaluacion-ergonomica/`
- [x] Búsqueda por los 6 campos, 3 filtros, 6 ordenamientos y paginación funcionan
- [x] El widget de ayuda carga el slug `dashboard`
- [x] Un usuario `company` **no** ve el botón «Nueva Evaluación»

### 🔴 REGLA DE ORO
- [x] Bitácora: entrada 3.6 · Tabla de control: 3.6 ✅ · `README.md`

### Git

```bash
git add apps/ergonomia_886/ docs/ README.md
git commit -m "feat(886): listado de evaluaciones como pantalla de aterrizaje

Reimplanta core.dashboard_view preservando su busqueda de 6 campos, 3 filtros,
lista blanca de 6 ordenamientos, paginacion de 20 y optimizacion con
select_related + Prefetch.

Los dos unicos cambios son el filtro de propiedad, que pasa a ser mixto por
user_type, y el template, que se integra al tema del backoffice.

El boton de alta solo aparece para profesionales: emitir un protocolo es un
acto profesional."
git push
```

---

## Commit 3.7 — Vista de eliminación de evaluación

```python
@login_required
@backoffice_required
@require_POST
def eliminar_evaluacion_view(request, evaluacion_id):
    """Elimina una evaluación. Sólo el profesional que la creó.

    ⚠️ Una empresa NO puede borrar un protocolo aunque lo vea: es
       documentación emitida por un profesional bajo su matrícula.
    """
    if not puede_editar_evaluaciones(request.user):
        raise Http404

    evaluacion = get_object_or_404(
        Evaluacion, pk=evaluacion_id, usuario=request.user,
    )
    razon_social = evaluacion.razon_social
    evaluacion.delete()

    messages.success(
        request, f"Evaluación de «{razon_social}» eliminada correctamente.",
    )
    return redirect("ergonomia_886:evaluacion_list")
```

> **El filtro es `usuario=request.user` y no `evaluaciones_visibles_para()`**, deliberadamente: ver no es lo mismo que borrar. Y el `raise Http404` en lugar de `HttpResponseForbidden` mantiene la garantía de no enumeración.

### Ruta

```python
    path("<int:evaluacion_id>/eliminar/", planillas_views.eliminar_evaluacion_view,
         name="eliminar_evaluacion"),
```

### Prueba

```python
    def test_una_empresa_no_puede_eliminar_un_protocolo(self):
        self.client.force_login(self.usuario_empresa)
        url = reverse("ergonomia_886:eliminar_evaluacion", args=[self.evaluacion.pk])
        self.assertEqual(self.client.post(url).status_code, 404)
        self.assertTrue(Evaluacion.objects.filter(pk=self.evaluacion.pk).exists())

    def test_un_profesional_no_puede_eliminar_la_evaluacion_de_otro(self):
        self.client.force_login(self.otro_profesional)
        url = reverse("ergonomia_886:eliminar_evaluacion", args=[self.evaluacion.pk])
        self.assertEqual(self.client.post(url).status_code, 404)
        self.assertTrue(Evaluacion.objects.filter(pk=self.evaluacion.pk).exists())
```

### 🔴 REGLA DE ORO
- [x] Bitácora: entrada 3.7 · Tabla de control: 3.7 ✅ · `README.md`

### Git

```bash
git add apps/ergonomia_886/ docs/ README.md
git commit -m "feat(886): eliminacion de evaluacion restringida al autor

Solo el profesional que creo el protocolo puede eliminarlo. Una empresa lo ve
pero no lo borra: es documentacion emitida bajo la matricula de un
profesional.

Responde 404 y no 403 para conservar la garantia de no enumeracion."
git push
```

---

## Commit 3.8 — Índices de consulta

### Objetivo
`Evaluacion` no tiene ningún índice más allá de la PK. El listado filtra por propietario y ordena por `-fecha_modificacion`: exactamente el patrón que estos índices cubren. Con tablas vacías es el momento de agregarlos.

```python
class Evaluacion(models.Model):
    ...

    class Meta:
        verbose_name = "Evaluación ergonómica"
        verbose_name_plural = "Evaluaciones ergonómicas"
        indexes = [
            # Patrón del listado del profesional: filtrar por propietario y
            # ordenar por última modificación.
            models.Index(fields=["usuario", "-fecha_modificacion"],
                         name="idx_eval_usuario_fmod"),
            # Mismo patrón para el portal de empresa.
            models.Index(fields=["empresa", "-fecha_modificacion"],
                         name="idx_eval_empresa_fmod"),
            # Búsqueda por CUIT, que es el identificador natural.
            models.Index(fields=["cuit"], name="idx_eval_cuit"),
        ]
```

```bash
.venv/bin/python manage.py makemigrations planillas --name indices_consulta
.venv/bin/python manage.py migrate --noinput
.venv/bin/python manage.py migrate --check
.venv/bin/python manage.py test --settings=config.test_settings
```

> ⚠️ **Los nombres de índice tienen tope de 30 caracteres en Django.** Verificar que los tres nombres elegidos no lo excedan.

### 🔴 REGLA DE ORO
- [x] Bitácora: entrada 3.8 · Tabla de control: 3.8 ✅ · `README.md`

### Git

```bash
git add apps/ergonomia_886/ docs/ README.md
git commit -m "perf(886): indices de consulta sobre Evaluacion

La tabla no tenia ningun indice mas alla de la PK. Los tres cubren los
patrones reales: listado del profesional, portal de empresa y busqueda por
CUIT. Con tablas vacias es el momento de agregarlos."
git push
```

---

## Commit 3.9 — Pruebas de propiedad, saneamiento y no regresión

### Objetivo
Consolidar la cobertura de todo lo que la Fase 3 introdujo.

> 🛑 **Detención P-2 si se decide crear usuarios de prueba fuera de fixtures.** La recomendación es **no detenerse**: crear los usuarios dentro de `setUpTestData()` con contraseñas de prueba fijas en el código de test es la práctica estándar y no involucra credenciales reales.

### Archivo: `apps/ergonomia_886/planillas/tests_integracion.py`

Cubre: T-3 (profesional no ve lo de otro), T-4 (empresa ve lo suyo), T-5 (trainee sin acceso), T-6 (sin 500 anónimo), T-8 (poblado no destructivo).

```python
class PropiedadMixtaTests(TestCase):
    """D-9: la evaluación pertenece a un profesional y opcionalmente a una empresa."""

    @classmethod
    def setUpTestData(cls):
        User = get_user_model()
        cls.prof_a = User.objects.create_professional(
            email="prof-a@test.local", password="clave-de-prueba", username="prof-a")
        cls.prof_b = User.objects.create_professional(
            email="prof-b@test.local", password="clave-de-prueba", username="prof-b")
        cls.user_empresa = User.objects.create_company(
            email="empresa@test.local", password="clave-de-prueba", username="empresa")
        cls.trainee = User.objects.create_trainee(
            cuil="20-11111111-1", email="trab@test.local")

        cls.perfil = CompanyProfile.objects.create(
            user=cls.user_empresa, razon_social="ACME S.A.",
            cuit="30-12345678-9", contacto_nombre="Contacto",
            domicilio="Av. Siempreviva 742", provincia="Buenos Aires")

        cls.eval_a = Evaluacion.objects.create(
            usuario=cls.prof_a, empresa=cls.perfil, razon_social="ACME S.A.",
            cuit="30-12345678-9", direccion_establecimiento="Av. Siempreviva 742",
            provincia="Buenos Aires")
        cls.eval_b = Evaluacion.objects.create(
            usuario=cls.prof_b, razon_social="OTRA S.R.L.", cuit="30-99999999-9",
            direccion_establecimiento="Otra 100", provincia="Córdoba")

    def test_un_profesional_solo_ve_las_suyas(self):
        visibles = evaluaciones_visibles_para(self.prof_a)
        self.assertIn(self.eval_a, visibles)
        self.assertNotIn(self.eval_b, visibles)

    def test_una_empresa_ve_las_de_su_empresa(self):
        visibles = evaluaciones_visibles_para(self.user_empresa)
        self.assertIn(self.eval_a, visibles)
        self.assertNotIn(self.eval_b, visibles)

    def test_un_trainee_no_ve_ninguna(self):
        self.assertEqual(evaluaciones_visibles_para(self.trainee).count(), 0)

    def test_una_evaluacion_ajena_responde_404_y_no_403(self):
        """No enumeración: un 403 confirmaría que el recurso existe."""
        self.client.force_login(self.prof_a)
        url = reverse("planillas:detalle_evaluacion", args=[self.eval_b.pk])
        self.assertEqual(self.client.get(url).status_code, 404)

    def test_una_empresa_no_puede_crear_evaluaciones(self):
        self.assertFalse(puede_editar_evaluaciones(self.user_empresa))
        self.assertTrue(puede_editar_evaluaciones(self.prof_a))
```

### Verificación final de la fase

```bash
.venv/bin/python manage.py test --settings=config.test_settings
.venv/bin/python manage.py check
.venv/bin/python manage.py makemigrations --check --dry-run
```

**Total esperado: ~205 pruebas.**

### 🔴 REGLA DE ORO
- [x] Bitácora: entrada 3.9, con el total de pruebas · Tabla de control: 3.9 ✅ · `README.md`

### Git

```bash
git add apps/ergonomia_886/ docs/ README.md
git commit -m "test(886): cubrir propiedad mixta, saneamiento y no enumeracion

Cubre las pruebas T-3 a T-8 del plan de no regresion: visibilidad por
user_type, 404 en lugar de 403 para recursos ajenos, empresa sin permiso de
edicion, ausencia de HTTP 500 anonimo y poblado no destructivo desde
CompanyProfile."
git push
```

---

## ✅ Cierre de la Fase 3

| Verificación | Criterio |
|---|---|
| Un profesional ve sólo las suyas | ✅ D-9 |
| Una empresa ve las de su empresa | ✅ D-9 |
| Un `trainee` no accede | ✅ D-9 |
| Recurso ajeno → **404**, no 403 | ✅ No enumeración |
| Ninguna ruta del módulo da 500 a un anónimo | ✅ No repite N1 |
| El poblado no sobrescribe lo tipeado | ✅ CF-5 |
| Editar la empresa no altera documentos emitidos | ✅ CF-5 |
| `CLAVES_PROHIBIDAS` ampliada y verificada | ✅ CF-4 |

---

# FASE 4 — INTEGRACIÓN DE UI

**Objetivo:** que el módulo se vea y se navegue como el resto del backoffice, y **activar la tarjeta «Evaluaciones»**.

---

## Commit 4.1 — 🎯 Activar la tarjeta «Evaluaciones»

### Objetivo
**Es el objetivo de negocio declarado de toda la integración.** La tarjeta deja de decir «Próximamente».

### Archivo: `templates/dashboard/home.html`, líneas 79-96

```html
<!-- ANTES: Card EVALUACIONES (desactivado) -->
<div class="col-md-6 col-lg-5">
    <div class="card dashboard-card disabled-card bg-dark border-secondary h-100">
        <div class="card-body text-center py-5 px-4">
            <div class="card-icon text-secondary">
                <i class="bi bi-clipboard-check"></i>
            </div>
            <h3 class="card-title text-secondary">Evaluaciones</h3>
            <p class="card-text text-muted mb-4">
                Evaluaciones de riesgos ergonómicos, iluminación, ruido y más.
                Todo según normativa vigente.
            </p>
            <span class="badge bg-warning text-dark fs-6 px-3 py-2">
                <i class="bi bi-clock me-1"></i>Próximamente
            </span>
        </div>
    </div>
</div>
```

```html
<!-- DESPUÉS: Card EVALUACIONES (activo) -->
<div class="col-md-6 col-lg-5">
    <a href="{% url 'ergonomia_886:evaluacion_list' %}" class="text-decoration-none">
        <div class="card dashboard-card bg-dark border-primary h-100">
            <div class="card-body text-center py-5 px-4">
                <div class="card-icon text-primary">
                    <i class="bi bi-clipboard-check"></i>
                </div>
                <h3 class="card-title text-white">Evaluaciones</h3>
                <p class="card-text text-secondary mb-4">
                    Protocolo de Ergonomía SRT 886/15: identificación de factores,
                    evaluación de 13 riesgos y planillas en el formulario oficial.
                </p>
                <span class="badge bg-primary fs-6 px-3 py-2">
                    <i class="bi bi-check-circle me-1"></i>Disponible
                </span>
            </div>
        </div>
    </a>
</div>
```

### Cada cambio y su motivo

| Cambio | Motivo |
|---|---|
| Envolver en `<a href>` | Replica exactamente el patrón de la tarjeta Capacitaciones (línea 100), que ya funciona |
| Quitar `disabled-card` | Es la clase que aplica el aspecto atenuado |
| `border-secondary` → `border-primary`, `text-secondary` → `text-primary` / `text-white` | Distingue Evaluaciones (azul) de Capacitaciones (verde) |
| Badge `bg-warning` «Próximamente» → `bg-primary` «Disponible» | Es el objetivo del trabajo |
| **Reescribir el texto descriptivo** | El texto actual promete «iluminación, ruido y más», que **este módulo no entrega**. Prometer funcionalidad inexistente en la pantalla principal es peor que decir «Próximamente» |

> **[PROPUESTA] Nota de producto.** Iluminación y ruido son módulos futuros. Cuando existan, corresponde una tarjeta por módulo o un submenú dentro de Evaluaciones. No ampliar la promesa antes de tiempo.

### Verificación

```bash
.venv/bin/python manage.py runserver
# Entrar a /dashboard/ con un usuario profesional
```

- [x] La tarjeta dice **«Disponible»**, no «Próximamente»
- [x] Al hacer clic navega a `/evaluacion-ergonomica/`
- [x] El texto **no promete iluminación ni ruido**
- [x] La tarjeta de Capacitaciones sigue funcionando igual
- [x] El dashboard de empresa no se rompió

### 🔴 REGLA DE ORO
- [x] Bitácora: entrada 4.1 · Tabla de control: 4.1 ✅ · `README.md`

### Git

```bash
git add templates/dashboard/home.html docs/ README.md
git commit -m "feat(dashboard): activar la tarjeta Evaluaciones

Es el objetivo de negocio declarado de la integracion: la tarjeta deja de
decir Proximamente y pasa a ser el acceso al modulo de Ergonomia SRT 886/15.

Se reescribe el texto descriptivo: el anterior prometia iluminacion y ruido,
que este modulo no entrega. Prometer funcionalidad inexistente en la pantalla
principal es peor que decir Proximamente."
git push
```

---

## Commit 4.2 — Entrada de navegación en el navbar

### Archivo: `templates/base_dashboard.html`, tras el `<li>` de Capacitaciones (línea 42)

```django
<li class="nav-item">
    <a class="nav-link {% if 'evaluacion-ergonomica' in request.path %}active{% endif %}"
       href="{% url 'ergonomia_886:evaluacion_list' %}">
        <i class="bi bi-clipboard-check me-1"></i>Evaluaciones
    </a>
</li>
```

> Se usa `request.path` y no `request.resolver_match.url_name` porque el módulo tiene muchos nombres de vista y todos deben marcar el ítem como activo. Es el mismo criterio que ya usan Nómina y Agenda (líneas 45 y 51).

### Verificación

- [ ] El ítem aparece para `professional` y para `company`
- [ ] Se marca activo en **todas** las pantallas del módulo
- [ ] El navbar no se desborda en pantalla angosta

### 🔴 REGLA DE ORO
- [ ] Bitácora: entrada 4.2 · Tabla de control: 4.2 ✅ · `README.md`

### Git

```bash
git add templates/base_dashboard.html docs/ README.md
git commit -m "feat(dashboard): entrada Evaluaciones en el navbar del backoffice"
git push
```

---

## Commit 4.3 — Cuarta stat del dashboard con import diferido

### Objetivo
Agregar la cantidad de evaluaciones ergonómicas **sin que `apps.dashboard` dependa del módulo**, para que el módulo siga siendo desmontable.

### Archivo: `apps/dashboard/views.py`

```python
def _contar_evaluaciones_ergonomicas(user):
    """Cuenta las evaluaciones del módulo 886.

    El import es diferido y tolerante a fallo deliberadamente: apps.dashboard
    no debe depender del módulo de Ergonomía. Si el módulo se desinstala, el
    dashboard sigue funcionando y la stat simplemente no se muestra.
    """
    try:
        from apps.ergonomia_886.planillas.models import Evaluacion
    except ImportError:
        return None
    return Evaluacion.objects.filter(usuario=user).count()


def _professional_dashboard(request):
    ...
    stats = {
        "capacitaciones_total": presencial_count,
        "links_generados": links_count,
        "trabajadores_capacitados": total_accesses,
        "evaluaciones_ergonomicas": _contar_evaluaciones_ergonomicas(request.user),
    }
    return render(request, "dashboard/home.html", {"stats": stats})
```

### Template — renderizar sólo si no es `None`

```django
{% if stats.evaluaciones_ergonomicas is not None %}
<div class="col-md-3">
    <div class="stat-card bg-dark border border-secondary">
        <div class="d-flex align-items-center">
            <div class="me-3">
                <i class="bi bi-clipboard-check text-primary" style="font-size: 2rem;"></i>
            </div>
            <div>
                <div class="stat-number text-primary">{{ stats.evaluaciones_ergonomicas }}</div>
                <small class="text-secondary">Evaluaciones ergonómicas</small>
            </div>
        </div>
    </div>
</div>
{% endif %}
```

> Las tres stats existentes usan `col-md-4`. Con la cuarta hay que pasar las cuatro a `col-md-3`.

### Verificación de desmontabilidad

```bash
# Comentar temporalmente las 4 apps del modulo en INSTALLED_APPS
# y confirmar que /dashboard/ sigue cargando sin la stat.
```

- [ ] La stat aparece con el módulo instalado
- [ ] **Con el módulo desinstalado, el dashboard sigue funcionando**

### 🔴 REGLA DE ORO
- [ ] Bitácora: entrada 4.3, con la prueba de desmontabilidad · Tabla de control: 4.3 ✅ · `README.md`

### Git

```bash
git add apps/dashboard/ templates/ docs/ README.md
git commit -m "feat(dashboard): cuarta stat con evaluaciones ergonomicas

El import es diferido y tolerante a fallo: apps.dashboard no debe depender del
modulo de Ergonomia. Con el modulo desinstalado el dashboard sigue funcionando
y la stat no se muestra. Verificado."
git push
```

---

## Commit 4.4 — Ajustes de contraste al tema oscuro

### Objetivo
Los 28 templates del módulo fueron diseñados sobre Bootstrap claro; el backoffice usa `data-bs-theme="dark"`.

### Clases a revisar

| Clase clara | Reemplazo oscuro |
|---|---|
| `bg-white` | `bg-dark` |
| `bg-light` | `bg-secondary bg-opacity-10` |
| `text-gray-800`, `text-dark` | `text-light` |
| `table` sin variante | `table table-dark` |
| `card` sin borde | `card bg-dark border-secondary` |
| `form-control` / `form-select` | Heredan del tema; verificar `placeholder` |
| `badge bg-light` | `badge bg-secondary` |

### Recorrido obligatorio — 30 pantallas

| # | Pantalla | Atención especial |
|---|---|---|
| 1 | Listado de evaluaciones | Tabla, filtros, paginación |
| 2 | Crear evaluación | Selector de empresa |
| 3 | Detalle / hub | Badges de estado de cada planilla |
| 4 | Planilla 1 | **Formset de 9 factores: la tabla más densa del módulo** |
| 5–13 | Planillas 2A–2I | Checklists de casillas |
| 14 | Planilla 3 | Formset de medidas |
| 15 | Planilla 4 | Campos de fecha |
| 16–28 | Los 13 formularios de factor | **Los 5 con JavaScript** |
| 29 | Wizard de resumen | Semáforo de 13 estados |
| 30 | Panel de documentos | 7 botones de acción |

**Los cinco formularios con JavaScript [VERIFICADO]:** `factor_form_base.html:139`, `vibracion_mano_brazo_form.html:233`, `posturas_forzadas_form.html:358`, `bipedestacion_form.html:204`, `vibracion_cuerpo_entero_form.html:405`.

### Verificación crítica del widget de ayuda

**Los 23 templates con `{% block help_slug %}` deben cargar su slug correcto.** Es un fallo silencioso: sin verificación, el widget cargaría `home` en todas partes.

```
Abrir la consola del navegador y en cada pantalla verificar:
    document.getElementById('helpWidget').dataset.pageSlug
Debe coincidir con el slug de esa pantalla, no con "home".
```

- [ ] Las 30 pantallas son legibles sobre fondo oscuro
- [ ] Los 5 formularios con JavaScript funcionan
- [ ] **Los 23 slugs de ayuda son los correctos**

### 🔴 REGLA DE ORO
- [ ] Bitácora: entrada 4.4, con la tabla de las 30 pantallas y los 23 slugs verificados
- [ ] Tabla de control: 4.4 ✅ · `README.md`

### Git

```bash
git add apps/ergonomia_886/ docs/ README.md
git commit -m "style(886): adaptar los 28 templates del modulo al tema oscuro

Los templates fueron disenados sobre Bootstrap claro; el backoffice usa
data-bs-theme=dark.

Verificados los 23 slugs de ayuda contextual: es un fallo silencioso, sin
excepcion ni log, que dejaria el widget cargando el slug home en todas las
pantallas."
git push
```

---

## Commit 4.5 — Loggers del módulo y verificación de CF-1

### Loggers en `config/settings.py`

```python
LOGGING = {
    ...
    "loggers": {
        "apps.certificates": {"handlers": ["console"], "level": "INFO"},
        "apps.quiz": {"handlers": ["console"], "level": "INFO"},

        # --- Módulo de Ergonomía SRT 886/15 ---
        # Los logs registran identificadores y métricas, NUNCA payloads ni
        # contenido de informes (CF-4).
        "apps.ergonomia_886": {"handlers": ["console"], "level": "INFO"},
        "apps.ergonomia_886.exportaciones.reports": {"handlers": ["console"], "level": "INFO"},
        "apps.ergonomia_886.help_ai": {"handlers": ["console"], "level": "INFO"},
    },
}
```

### 🔴 Verificación integral de CF-1 — fin de la Fase 4

```bash
echo "=== 1. Apps separadas en INSTALLED_APPS ==="
.venv/bin/python -c "
import django, os
os.environ.setdefault('DJANGO_SETTINGS_MODULE','config.settings')
django.setup()
from django.conf import settings
print('  apps.ergobot_ai            :', 'apps.ergobot_ai' in settings.INSTALLED_APPS)
print('  apps.ergonomia_886.help_ai :', 'apps.ergonomia_886.help_ai' in settings.INSTALLED_APPS)
"

echo
echo "=== 2. Ninguna importa codigo de la otra ==="
grep -ri "ergobot" apps/ergonomia_886/ && echo "🔴 VIOLACION" || echo "  OK: help_ai no menciona ergobot"
grep -ri "help_ai" apps/ergobot_ai/    && echo "🔴 VIOLACION" || echo "  OK: ergobot no menciona help_ai"

echo
echo "=== 3. Las 22 pruebas de help_ai ==="
.venv/bin/python manage.py test apps.ergonomia_886.help_ai --settings=config.test_settings

echo
echo "=== 4. Prefijos de URL distintos ==="
.venv/bin/python -c "
import django, os
os.environ.setdefault('DJANGO_SETTINGS_MODULE','config.settings')
django.setup()
from django.urls import reverse
print('  ergobot_ai :', reverse('ergobot_ai:ergobot_stream', args=['ergonomia']))
print('  help_ai    :', reverse('help_ai:chat_ai', kwargs={'slug':'lmc'}))
"

echo
echo "=== 5. El chequeo automatico E007 ==="
.venv/bin/python manage.py check
```

**Verificación funcional, con el servidor levantado:**

- [ ] El widget de ayuda responde en 3 pantallas del módulo con slugs distintos
- [ ] **El chatbot Ergobot responde en `/capacitacion/`**
- [ ] Las respuestas son coherentes con el dominio de cada uno

### 🔴 REGLA DE ORO
- [ ] Bitácora: entrada 4.5, **con la salida completa de la verificación de CF-1**
- [ ] Tabla de control: 4.5 ✅ · `README.md`

### Git

```bash
git add config/settings.py docs/ README.md
git commit -m "feat(886): loggers del modulo y verificacion integral de CF-1

Tres loggers que registran identificadores y metricas, nunca payloads ni
contenido de informes (CF-4).

CF-1 verificada de forma integral: apps separadas en INSTALLED_APPS, ninguna
menciona a la otra en su codigo, las 22 pruebas de help_ai pasan, los prefijos
de URL son distintos, el chequeo E007 esta limpio, y ambos asistentes responden
en sus respectivos dominios."
git push
```

---

## ✅ Cierre de la Fase 4

> **🎯 El objetivo de negocio está cumplido.** La tarjeta «Evaluaciones» del dashboard dejó de decir «Próximamente» y es el acceso a un módulo funcionando.

**Total esperado: ~205 pruebas en verde.** Las Fases 5 y 6 agregan valor sobre algo que ya anda y **pueden posponerse sin bloquear un despliegue**.

---

# FASE 5 — APROVECHAMIENTO

**Objetivo:** cerrar las deudas que el destino resuelve gratis y conectar los dos dominios.
**Característica:** **fraccionable.** Cada commit aporta valor por separado y puede posponerse.

---

## Commit 5.1 — Evidencia de vibración adjuntable (O-5, D-1)

### Objetivo
Cerrar la deuda D-1: `VibracionCE_Eval` declara dos campos de archivo (`evaluaciones/models.py:383-384`) que en el origen **no eran servibles** porque no había `MEDIA_ROOT`. El destino sí lo tiene.

### Trabajo

1. **Verificar que la carga funciona:** `MEDIA_ROOT = BASE_DIR / "media"` ya existe (`config/settings.py:146`) y `config/urls.py:64-65` sirve `/media/` en `DEBUG`.
2. **Control de acceso.** ⚠️ **Punto crítico:** el hallazgo H2 del destino documenta que los certificados PDF son descargables sin autenticación por URL directa. **No repetir ese error.** La evidencia de vibración contiene datos de un puesto de trabajo concreto y debe servirse por una vista con verificación de propiedad, no por `/media/` directo.
3. **Adjuntar al ZIP** en `exportaciones/packaging.py`, cerrando el hueco G-9.
4. **Verificar que `sanitize_payload()` sigue excluyendo `foto_montaje` y `certificado_calibracion`** — ya están en `CLAVES_PROHIBIDAS`.

### Verificación

- [ ] Se puede cargar una foto y un certificado en un factor de VCE
- [ ] **Un usuario ajeno no puede descargarlos por URL directa**
- [ ] El ZIP los incluye
- [ ] `sanitize_payload()` los sigue excluyendo (CF-4)

### 🔴 REGLA DE ORO · Git

```bash
git add apps/ergonomia_886/ config/ docs/ README.md
git commit -m "feat(886): evidencia de vibracion de cuerpo entero adjuntable

Cierra D-1 y el hueco G-9: los dos campos de archivo de VibracionCE_Eval
existian pero no eran servibles sin MEDIA_ROOT, que el destino si tiene.

Se sirven por vista con verificacion de propiedad y NO por /media/ directo:
no repetir el hallazgo H2 del destino, donde los certificados PDF son
descargables sin autenticacion por URL directa."
git push
```

---

## Commit 5.2 — Aclaración de firma en planillas oficiales (O-2, CF-5)

### Objetivo
Cerrar parcialmente D-3 y el hueco G-1. Las 12 páginas oficiales piden tres firmas y hoy salen todas en blanco.

### 🔴 Regla que gobierna este commit — CF-5

| Recuadro | Fuente de la aclaración | Si el dato falta |
|---|---|---|
| **Empleador** | `evaluacion.empresa.contacto_nombre` + `contacto_cargo` | **En blanco** |
| **Responsable de Higiene y Seguridad** | `evaluacion.usuario.display_name` + `profession` + `license_number` | **En blanco** |
| **Responsable de Medicina del Trabajo** | — | **SIEMPRE en blanco** |

> **El tercer recuadro se deja vacío siempre y sin excepción.** No hay ningún dato en el sistema que identifique al médico laboral, y **CF-5 prohíbe que un documento oficial afirme lo que nadie declaró**. Imprimir ahí el nombre del profesional de Higiene y Seguridad sería una falsedad documental.
>
> Igualmente, si un `CustomUser` no tiene `profession` o `license_number` cargados —ambos son `blank=True, default=""`—, esa parte de la aclaración **también** queda vacía.
>
> **Sólo se imprime la aclaración impresa. El trazo manuscrito lo hace el profesional.**

### Pruebas obligatorias

```python
def test_cf5_el_recuadro_de_medicina_sale_siempre_en_blanco(self): ...
def test_cf5_un_profesional_sin_matricula_produce_aclaracion_vacia(self): ...
def test_cf5_una_evaluacion_sin_empresa_deja_el_recuadro_del_empleador_vacio(self): ...
```

- [ ] Los tres casos de CF-5 cubiertos por prueba
- [ ] Las 24 pruebas de `test_official_pdf.py` siguen pasando
- [ ] **Inspección visual: las aclaraciones no pisan las líneas de firma del formulario oficial**
- [ ] **La curva de Fanger y la escala de Borg siguen íntegras (CF-6)**

### 🔴 REGLA DE ORO · Git

```bash
git add apps/ergonomia_886/exportaciones/ docs/ README.md
git commit -m "feat(886): aclaracion de firma en las planillas oficiales

Cierra parcialmente D-3 y el hueco G-1 usando CustomUser.profession y
license_number, que el destino ya tiene.

CF-5: el recuadro de Medicina del Trabajo sale SIEMPRE en blanco. No hay dato
que identifique al medico laboral y un documento oficial no puede afirmar lo
que nadie declaro. Si falta profession o license_number, esa aclaracion
tambien queda vacia.

Solo se imprime la aclaracion: el trazo manuscrito lo hace el profesional."
git push
```

---

## Commit 5.3 — Trabajadores estructurados (O-3, CF-4, CF-5)

### Modelo

```python
class Planilla1(models.Model):
    evaluacion = models.OneToOneField(Evaluacion, on_delete=models.CASCADE, primary_key=True)

    trabajadores = models.ManyToManyField(
        "company.CompanyWorker",
        blank=True,
        related_name="planillas_ergonomicas",
        verbose_name="Trabajadores relevados",
        help_text="Trabajadores de la nómina alcanzados por este relevamiento.",
    )

    # ⚠️ Respaldo histórico. La exportación imprime SIEMPRE este campo, NUNCA
    #    la relación: un cambio de nómina no puede alterar un protocolo
    #    emitido, y el relevamiento puede alcanzar a personal no registrado
    #    en la plataforma (CF-5).
    nombres_trabajadores = models.TextField(blank=True)
```

### Regla de derivación

Al guardar: si `trabajadores` tiene elementos **y `nombres_trabajadores` está vacío**, se puebla con los nombres. **Si el profesional ya escribió algo, no se sobrescribe.**

`nro_trabajadores` **no** se deriva de `trabajadores.count()`: el formulario oficial pide el total del puesto, que puede exceder a los relevados nominalmente.

### 🔴 Verificación de CF-4

Este commit es el que introduce la superficie que el commit 3.2 anticipó.

```bash
.venv/bin/python manage.py test apps.ergonomia_886.exportaciones --settings=config.test_settings
```

- [ ] La prueba de saneamiento del commit 3.2 **sigue pasando con la relación real poblada**
- [ ] Un `GeneratedReport.payload_json` real no contiene CUIL, DNI ni email
- [ ] La planilla oficial imprime `nombres_trabajadores`, no la relación
- [ ] Una evaluación sin empresa no ofrece el selector y el campo de texto funciona

### 🔴 REGLA DE ORO · Git

```bash
git add apps/ergonomia_886/ docs/ README.md
git commit -m "feat(886): vincular la Planilla 1 con la nomina de la empresa

M2M opcional hacia company.CompanyWorker. nombres_trabajadores se conserva
como respaldo historico: la exportacion imprime SIEMPRE ese campo y NUNCA la
relacion, porque un cambio de nomina no puede alterar un protocolo emitido y
el relevamiento puede alcanzar a personal no registrado (CF-5).

La derivacion solo actua si el campo esta vacio: lo tipeado por el profesional
gana siempre.

CF-4: la superficie de datos personales que esta relacion introduce ya estaba
cubierta por la ampliacion de CLAVES_PROHIBIDAS del commit 3.2. Verificado
con la relacion real poblada."
git push
```

---

## Commit 5.4 — Sincronización con la agenda (O-4, CF-2)

### Objetivo
**La integración de mayor valor de negocio.** El profesional ve el vencimiento de las medidas correctivas ergonómicas en la misma agenda que los vencimientos de capacitación.

### Decisión de implementación

**Llamada explícita desde la vista, NO señal `post_save`.** Las señales son difíciles de razonar y de testear; una llamada explícita desde `Planilla4UpdateView.form_valid()` es rastreable.

### Archivo nuevo: `apps/ergonomia_886/planillas/agenda.py`

```python
# apps/ergonomia_886/planillas/agenda.py
"""Proyección de las medidas correctivas hacia la agenda de la empresa.

⚠️ La dirección es UNA SOLA: la agenda refleja el protocolo, nunca al revés.
   Marcar completado un AgendaEvent NO escribe fecha_cierre, porque eso sería
   que una vista de calendario modifique un documento oficial. La vista de
   agenda enlaza a la Planilla 4 para que el cierre se registre donde
   corresponde.

⚠️ CF-2: `_prioridad_por_nivel()` MAPEA un nivel ya persistido a una prioridad
   de calendario. No calcula, no reclasifica y no deriva ningún nivel de
   riesgo. La prioridad de un evento de agenda no es un nivel de riesgo.
"""

from django.utils import timezone

from apps.company.models import AgendaEvent


_PRIORIDAD_POR_NIVEL = {
    1: AgendaEvent.Priority.LOW,       # Tolerable
    2: AgendaEvent.Priority.HIGH,      # Moderado
    3: AgendaEvent.Priority.URGENT,    # No Tolerable
}


def sincronizar_medida_con_agenda(seguimiento):
    """Crea o actualiza el evento de agenda de una medida correctiva."""
    evaluacion = seguimiento.medida_especifica.planilla3.evaluacion
    empresa = evaluacion.empresa
    if empresa is None:
        return None            # empresa no usuaria: no hay agenda donde colgarla

    fecha = seguimiento.fecha_impl_ing or seguimiento.fecha_impl_admin
    if fecha is None:
        return None            # sin fecha comprometida no hay vencimiento

    descripcion = seguimiento.medida_especifica.descripcion
    evento, _ = AgendaEvent.objects.update_or_create(
        company=empresa,
        related_object_type="ergonomia_886.SeguimientoMedida",
        related_object_id=str(seguimiento.pk),
        defaults={
            "title": f"Medida correctiva ergonómica — {descripcion[:80]}",
            "description": seguimiento.medida_especifica.observaciones or "",
            "event_type": AgendaEvent.EventType.EVALUATION_DUE,
            "due_at": timezone.make_aware(
                timezone.datetime.combine(fecha, timezone.datetime.min.time())
            ),
            "status": (
                AgendaEvent.EventStatus.COMPLETED
                if seguimiento.fecha_cierre
                else AgendaEvent.EventStatus.PENDING
            ),
            "priority": _PRIORIDAD_POR_NIVEL.get(
                seguimiento.nivel_riesgo, AgendaEvent.Priority.MEDIUM
            ),
            "assigned_professional": evaluacion.usuario,
        },
    )
    return evento
```

> **`update_or_create` con clave natural** `(company, related_object_type, related_object_id)`: reeditar la Planilla 4 actualiza el evento en lugar de duplicarlo. Es el mismo patrón que ya usa `generate_cert_expiry_events` **[VERIFICADO]**.
>
> **`EVALUATION_DUE` ya existe en el enum** **[VERIFICADO — `apps/company/models.py:210`]**. No hay que agregar nada al modelo del destino.

### Pruebas

```python
def test_guardar_la_planilla4_crea_un_evento_de_agenda(self): ...
def test_reeditarla_actualiza_el_evento_sin_duplicarlo(self): ...
def test_cerrar_la_medida_marca_el_evento_como_completado(self): ...
def test_una_evaluacion_sin_empresa_no_crea_evento_y_no_falla(self): ...
def test_una_medida_sin_fecha_comprometida_no_crea_evento(self): ...
def test_cf2_la_prioridad_no_altera_el_nivel_de_riesgo_persistido(self): ...
```

### 🔴 REGLA DE ORO · Git

```bash
git add apps/ergonomia_886/ docs/ README.md
git commit -m "feat(886): proyectar las medidas correctivas hacia la agenda

La integracion de mayor valor de negocio: el profesional ve el vencimiento de
las medidas correctivas ergonomicas en la misma agenda que los vencimientos de
capacitacion.

Llamada explicita desde la vista y no signal post_save: las senales son
dificiles de razonar y de testear.

update_or_create con clave natural (company, related_object_type,
related_object_id): reeditar la Planilla 4 actualiza el evento en lugar de
duplicarlo. Mismo patron que generate_cert_expiry_events.

EVALUATION_DUE ya existia en el enum de AgendaEvent: no se toca el modelo del
destino.

La direccion es una sola: la agenda refleja el protocolo, nunca al reves.
CF-2: la prioridad de calendario mapea un nivel ya persistido, no lo calcula."
git push
```

---

## Commit 5.5 — Enlace desde la agenda hacia la Planilla 4

### Objetivo
Cerrar el circuito: desde el evento de agenda, ir a la Planilla 4 donde el cierre se registra formalmente.

En `templates/company/agenda_list.html`, para eventos con `related_object_type == "ergonomia_886.SeguimientoMedida"`, mostrar un enlace «Ver medida en el protocolo».

> ⚠️ **`apps.company` no debe importar el módulo.** El enlace se construye en el template a partir de `related_object_id`, o mediante un `templatetag` del propio módulo. **No agregar un import de `apps.ergonomia_886` en `apps/company/views.py`**: rompería la desmontabilidad verificada en el commit 4.3.

### 🔴 REGLA DE ORO · Git

```bash
git add templates/ apps/ docs/ README.md
git commit -m "feat(886): enlazar los eventos de agenda con su Planilla 4

Cierra el circuito: desde el evento se llega a la planilla donde el cierre se
registra formalmente. El enlace se construye sin que apps.company importe el
modulo, preservando la desmontabilidad."
git push
```

---

## Commit 5.6 — Sugerencia de capacitaciones por nivel de riesgo (O-6)

### Objetivo
**El argumento de producto que justifica la fusión de ambos sistemas.** Si una evaluación arroja nivel alto en levantamiento manual de cargas, sugerir el módulo de capacitación correspondiente para los trabajadores de ese puesto.

### 🔴 Restricción de CF-2

> La sugerencia **lee** el nivel persistido en `RiskEvaluation.resultado_global` o en `BaseFactorEvaluation.nivel_riesgo`. **No lo calcula, no lo deriva y no lo reinterpreta.** Es consumo de un resultado, no autoridad sobre él.

### Mapeo factor → módulo de capacitación **[PROPUESTA]**

Declarativo, en el módulo, sin que `apps.training` conozca al módulo 886:

```python
# apps/ergonomia_886/evaluaciones/sugerencias.py   [PROPUESTA]
"""Sugerencia de capacitación a partir de un nivel de riesgo YA CALCULADO.

⚠️ CF-2: este módulo LEE niveles persistidos. No calcula, no deriva y no
   reinterpreta ninguna clasificación. La autoridad sigue siendo
   calculators.py sin excepción.
"""

SUGERENCIAS_POR_FACTOR = {
    "lmc":                    "ergonomia",
    "transporte":             "ergonomia",
    "empuje_inicial":         "ergonomia",
    "posturas_forzadas":      "ergonomia",
    "repetitivos_ms":         "ergonomia",
    # Los slugs deben existir en TrainingModule. Los que no tengan modulo
    # propio apuntan al general de ergonomia.
}

NIVELES_QUE_DISPARAN_SUGERENCIA = {"medio", "alto"}
```

### Verificación

- [ ] La sugerencia aparece sólo con nivel `medio` o `alto`
- [ ] El enlace lleva a un `TrainingModule` que existe y está activo
- [ ] **Ningún nivel se recalcula** (CF-2)
- [ ] `apps.training` no importa nada del módulo

### 🔴 REGLA DE ORO · Git

```bash
git add apps/ergonomia_886/ templates/ docs/ README.md
git commit -m "feat(886): sugerir capacitaciones segun el nivel de riesgo

El argumento de producto que justifica la fusion de ambos sistemas: una
evaluacion con nivel alto en levantamiento manual sugiere el modulo de
capacitacion correspondiente para los trabajadores de ese puesto.

CF-2: la sugerencia LEE el nivel persistido. No calcula, no deriva y no
reinterpreta ninguna clasificacion."
git push
```

---

## ✅ Cierre de la Fase 5

| Deuda / oportunidad | Estado |
|---|---|
| D-1 · `MEDIA_ROOT` y evidencia de VCE | ✅ Cerrada |
| D-3 · Firmantes | ✅ Cerrada parcialmente (respetando CF-5) |
| O-3 · Trabajadores estructurados | ✅ |
| O-4 · Agenda | ✅ |
| O-6 · Capacitaciones sugeridas | ✅ |

---

# FASE 6 — CONTENT SECURITY POLICY

**Objetivo:** endurecer la seguridad de todo ErgoSolutions con el middleware de CSP del módulo.
**Característica:** **independiente.** Puede ejecutarse en cualquier momento, incluso antes de las Fases 3-5.

> **Estado tras DA-2.13:** ya están adelantados el vendor local, los nonces,
> los listeners y el middleware bloqueante mínimo porque la suite de Fase 2
> los exigía. Los commits 6.1–6.3 verificarán/documentarán esa base y 6.2
> mantiene su objetivo principal de extraer los scripts; 6.4–6.7 siguen
> pendientes íntegros.

## Por qué esta fase va al final y no al principio

> **[HALLAZGO H-K] El módulo funciona sin CSP.** Sus 6 templates usan el nonce como `<script nonce="{{ request.csp_nonce }}">`. Sin el middleware, la variable renderiza vacío y produce `<script nonce="">`, **que se ejecuta con normalidad** porque no hay política activa que lo restrinja. El widget de ayuda no usa nonce en absoluto.
>
> **[HALLAZGO H-E] El frontend del destino es masivamente incompatible:**
>
> | Elemento | Cantidad | Ubicación |
> |---|---:|---|
> | Referencias a `cdn.jsdelivr.net` | **6** | `base_dashboard.html` (3), `base_landing.html` (3) |
> | Bloques `<script>` inline | **5** | `training/training_page.html:59`, `quiz/quiz_widget.html:23`, `dashboard/online_links.html:119`, `presencial/capacitacion.html:139`, `presencial/quiz.html:113` |
> | Manejadores en línea | **3** | `dashboard/online_links.html` (1), `presencial/quiz.html` (2) |
>
> Activar el CSP sin remediar esos 14 puntos **deja las 33 pantallas del destino sin Bootstrap CSS ni JavaScript.**

---

## Commit 6.1 — Migrar CDN a `vendor/` local

```django
{# templates/base_dashboard.html — ANTES (lineas 10, 12, 110) #}
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
<link href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.0/font/bootstrap-icons.css" rel="stylesheet">
<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>

{# DESPUÉS #}
{% load static %}
<link href="{% static 'vendor/bootstrap/bootstrap-5.3.3.min.css' %}" rel="stylesheet">
<link href="{% static 'vendor/bootstrap-icons/bootstrap-icons-1.11.3.min.css' %}" rel="stylesheet">
<script src="{% static 'vendor/bootstrap/bootstrap.bundle-5.3.3.min.js' %}"></script>
```

Ídem en `base_landing.html`, que además usa Bootstrap **Icons 1.10.0** — dos versiones del mismo paquete en el mismo sitio.

### Cinco beneficios además del CSP

1. Elimina una dependencia externa en tiempo de request: hoy, si jsdelivr no responde, el backoffice se renderiza sin CSS ni JavaScript.
2. Elimina una fuga de datos de navegación hacia un tercero en cada carga.
3. WhiteNoise versiona por hash y cachea indefinidamente: más rápido que el CDN tras la primera visita.
4. Unifica versiones: hoy conviven Icons 1.11.0 y 1.10.0.
5. Los archivos ya están en el repositorio desde el commit 2.7.

### Verificación

**[PENDIENTE]** El salto 5.3.0 → 5.3.3 es de parche y no introduce cambios incompatibles conocidos, pero **debe verificarse visualmente**. Icons 1.10.0/1.11.0 → 1.11.3 puede cambiar nombres de algunos íconos: revisar los `bi bi-*` usados.

- [ ] Cero referencias a `cdn.jsdelivr.net`
- [ ] Las 33 pantallas del destino se ven correctamente
- [ ] **Ningún ícono aparece como cuadrado vacío**

### 🔴 REGLA DE ORO · Git

```bash
git add templates/ docs/ README.md
git commit -m "refactor(templates): servir Bootstrap desde vendor/ local

Elimina las 6 referencias a cdn.jsdelivr.net. Es prerequisito del CSP, y
ademas: elimina una dependencia externa en tiempo de request, elimina una fuga
de datos de navegacion hacia un tercero, aprovecha el versionado por hash de
WhiteNoise y unifica versiones (convivian Icons 1.11.0 y 1.10.0)."
git push
```

---

## Commit 6.2 — Extraer los 5 bloques `<script>` inline

**[PENDIENTE]** Inspeccionar los cinco uno por uno: si alguno depende de variables de contexto de Django renderizadas en el template, extraerlo exige pasar esos datos por atributos `data-*`. Es el trabajo real de este commit y no se puede estimar sin leerlos.

| Template | Línea | Destino |
|---|---|---|
| `training/training_page.html` | 59 | `static/js/training_page.js` |
| `quiz/quiz_widget.html` | 23 | `static/js/quiz_widget.js` |
| `dashboard/online_links.html` | 119 | `static/js/online_links.js` |
| `presencial/capacitacion.html` | 139 | `static/js/presencial_capacitacion.js` |
| `presencial/quiz.html` | 113 | `static/js/presencial_quiz.js` |

Patrón para pasar contexto:

```django
{# ANTES #}
<script>
  const moduleSlug = "{{ module.slug }}";
  ...
</script>

{# DESPUÉS #}
<div id="quiz-root" data-module-slug="{{ module.slug }}"></div>
<script src="{% static 'js/quiz_widget.js' %}"></script>
```

```javascript
// static/js/quiz_widget.js
const raiz = document.getElementById('quiz-root');
const moduleSlug = raiz.dataset.moduleSlug;
```

### 🔴 REGLA DE ORO · Git

```bash
git commit -m "refactor(templates): extraer los cinco bloques script inline

Prerequisito del CSP. El contexto de Django se pasa por atributos data-*."
git push
```

---

## Commit 6.3 — Reemplazar los 3 manejadores en línea

```html
<!-- ANTES -->
<button onclick="copiarLink('{{ link.id }}')">Copiar</button>

<!-- DESPUÉS -->
<button class="js-copiar-link" data-link-id="{{ link.id }}">Copiar</button>
```

```javascript
document.querySelectorAll('.js-copiar-link').forEach((boton) => {
  boton.addEventListener('click', () => copiarLink(boton.dataset.linkId));
});
```

### Verificación

```bash
grep -rn "onclick=\|onchange=\|onsubmit=\|onload=\|oninput=" templates/
# → no debe devolver nada
```

### 🔴 REGLA DE ORO · Git

```bash
git commit -m "refactor(templates): reemplazar manejadores en linea por addEventListener

script-src-attr 'none' del CSP prohibe los manejadores en linea."
git push
```

---

## Commit 6.4 — Verificación visual de las 33 pantallas

**No hay código.** Es un commit de verificación documentada.

Recorrer las 33 pantallas del destino más las 30 del módulo con la consola del navegador abierta, registrando en la bitácora una tabla con: pantalla, estado visual, errores de consola, funcionalidad JavaScript.

- [ ] Las 63 pantallas se ven correctamente
- [ ] **Cero errores en la consola**
- [ ] Toda la funcionalidad JavaScript opera
- [ ] **El chatbot Ergobot y el widget de ayuda responden (CF-1)**

### 🔴 REGLA DE ORO · Git

```bash
git add docs/ README.md
git commit -m "docs(886): verificacion visual previa a la activacion del CSP

Recorrido de las 63 pantallas con la consola abierta. Tabla completa en la
bitacora."
git push
```

---

## Commit 6.5 — Portar el middleware con modo `Report-Only`

### Archivo nuevo: `config/middleware.py`

Portado de `ergonomia_srt/middleware.py` **sin cambios funcionales**, más una extensión: la política configurable en modo observación.

```python
# config/middleware.py
"""Cabeceras de seguridad de ErgoSolutions.

Portado del módulo de Ergonomía SRT 886/15, con una extensión: la cabecera
puede emitirse en modo Report-Only mediante el setting CSP_REPORT_ONLY, para
observar violaciones antes de bloquear. Es la práctica estándar para
introducir CSP en un sitio existente.
"""

from __future__ import annotations

import secrets

from asgiref.sync import iscoroutinefunction, markcoroutinefunction
from django.conf import settings


class ContentSecurityPolicyMiddleware:
    """Genera un nonce por respuesta y bloquea recursos/script no autorizados."""

    sync_capable = True
    async_capable = True

    def __init__(self, get_response):
        self.get_response = get_response
        self.is_async = iscoroutinefunction(get_response)
        if self.is_async:
            markcoroutinefunction(self)

    @staticmethod
    def _prepare_request(request) -> None:
        request.csp_nonce = secrets.token_urlsafe(18)

    @staticmethod
    def _finalize_response(request, response):
        nonce = request.csp_nonce
        politica = "; ".join((
            "default-src 'self'",
            f"script-src 'self' 'nonce-{nonce}'",
            "script-src-attr 'none'",
            "style-src 'self' 'unsafe-inline'",
            "font-src 'self'",
            "img-src 'self' data:",
            "connect-src 'self'",
            "object-src 'none'",
            "base-uri 'self'",
            "frame-ancestors 'self'",
            "form-action 'self'",
        ))

        cabecera = (
            "Content-Security-Policy-Report-Only"
            if getattr(settings, "CSP_REPORT_ONLY", False)
            else "Content-Security-Policy"
        )
        response[cabecera] = politica
        response["Referrer-Policy"] = "same-origin"
        response["Permissions-Policy"] = (
            "camera=(), microphone=(), geolocation=(), payment=()"
        )
        return response

    def __call__(self, request):
        self._prepare_request(request)
        if self.is_async:
            return self.__acall__(request)
        response = self.get_response(request)
        return self._finalize_response(request, response)

    async def __acall__(self, request):
        response = await self.get_response(request)
        return self._finalize_response(request, response)
```

### Registrar — la posición importa

**Después de `WhiteNoiseMiddleware` y antes de `SessionMiddleware`**, replicando la posición del origen **[VERIFICADO]**:

```python
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "config.middleware.ContentSecurityPolicyMiddleware",   # ← NUEVO
    "django.contrib.sessions.middleware.SessionMiddleware",
    ...
]

# CSP en modo observación: emite Content-Security-Policy-Report-Only, que
# registra violaciones en la consola del navegador sin bloquear nada.
# Pasar a False (commit 6.7) tras el período de observación.
CSP_REPORT_ONLY = env.bool("CSP_REPORT_ONLY", default=True)
```

### 🔴 REGLA DE ORO · Git

```bash
git add config/ docs/ README.md .env.example
git commit -m "feat(security): portar el middleware de CSP en modo Report-Only

Portado del modulo de Ergonomia sin cambios funcionales, mas la extension de
modo observacion: emite Content-Security-Policy-Report-Only, que registra
violaciones sin bloquear.

Se registra despues de WhiteNoise y antes de Session, replicando la posicion
del proyecto de origen.

ErgoSolutions gana ademas Referrer-Policy y Permissions-Policy, que no tenia."
git push
```

---

## Commit 6.6 — Período de observación

Con `CSP_REPORT_ONLY = True`, recorrer las 63 pantallas con la consola abierta y registrar **toda** violación reportada.

Cada violación se corrige. **No se relaja la política para acomodar una violación**: se corrige el código que la produce.

- [ ] **Cero violaciones de CSP en las 63 pantallas**
- [ ] Los 6 templates del módulo reciben un nonce real (no cadena vacía)

### 🔴 REGLA DE ORO · Git

```bash
git commit -m "fix(security): resolver las violaciones detectadas en Report-Only

Cada violacion se corrige en el codigo que la produce. La politica no se
relaja para acomodar una violacion."
git push
```

---

## Commit 6.7 — Activar el CSP en modo bloqueante

```python
CSP_REPORT_ONLY = env.bool("CSP_REPORT_ONLY", default=False)   # ← el defecto cambia
```

### Verificación final

```bash
.venv/bin/python manage.py runserver
curl -sI http://127.0.0.1:8000/dashboard/ | grep -i "content-security\|referrer\|permissions"
```

- [ ] La cabecera es `Content-Security-Policy`, ya no `Report-Only`
- [ ] Las 63 pantallas funcionan con cero violaciones
- [ ] **El chatbot Ergobot y el widget de ayuda responden (CF-1)**
- [ ] Los 5 formularios de factor con JavaScript funcionan

### 🔴 REGLA DE ORO · Git

```bash
git add config/settings.py docs/ README.md
git commit -m "feat(security): activar el CSP en modo bloqueante

Tras el periodo de observacion sin violaciones, la politica pasa a bloquear.

ErgoSolutions queda con default-src 'self', script-src con nonce por respuesta,
script-src-attr 'none', Referrer-Policy y Permissions-Policy."
git push
```

---

# CIERRE DE LA INTEGRACIÓN

## Verificación final integral

```bash
cd /Users/praguirre/ergocapacitacion

.venv/bin/python manage.py check
.venv/bin/python manage.py check --deploy
.venv/bin/python manage.py makemigrations --check --dry-run
.venv/bin/python manage.py migrate --check
.venv/bin/python manage.py test --settings=config.test_settings

# Integridad de artefactos
shasum -a 256 apps/ergonomia_886/exportaciones/official/templates_bin/res_srt_886_15-formulario.pdf
# → bc0d0753943888779abd0936f6c4dc2e128766c7cf6370a4a2fb19073aad59f4

# CF-1
grep -ri "ergobot" apps/ergonomia_886/  || echo "OK CF-1"
grep -ri "help_ai" apps/ergobot_ai/     || echo "OK CF-1"
```

## Checklist de aceptación

### Condiciones fundamentales

- [ ] **CF-1** · `help_ai` y `ergobot_ai` coexisten; ninguna importa de la otra; las 22 pruebas pasan; ambos asistentes responden
- [ ] **CF-2** · Ningún nivel de riesgo se calcula fuera de `calculators.py`
- [ ] **CF-3** · `calc_data` íntegro; los 13 artefactos con su SHA-256; 7 en `approved`
- [ ] **CF-4** · `CLAVES_PROHIBIDAS` ampliada; `trace_include_sensitive_data=False`; verificado con la relación real
- [ ] **CF-5** · Planilla no completada sale en blanco; recuadro médico siempre vacío; poblado no destructivo
- [ ] **CF-6** · SHA-256 del PDF coincide; curva de Fanger y escala de Borg íntegras; sin dependencias de Excel

### Bloqueantes

- [ ] **B1** · `AUTH_USER_MODEL`, sin migración generada
- [ ] **B2** · 4 apps bajo `apps/ergonomia_886/`; 102 imports y 48 rutas reescritos
- [ ] **B3** · `app_name` en `planillas` y `help_ai`; 35 referencias calificadas
- [ ] **B4** · `DatabaseCache` y `createcachetable`
- [ ] **B5** · CSP activo (o registrado como deuda con fecha)
- [ ] **B6** · Ruta de documentos de ayuda anclada a `BASE_DIR`
- [ ] **B7** · `pypdf` y `pillow` declarados
- [ ] **B8** · `config/test_settings.py`

### Regresiones del destino

- [ ] **N1** · Ninguna ruta devuelve 500 a un anónimo
- [ ] **N2** · La ficha del trabajador renderiza con `QuizState`
- [ ] **H-D**, **H-F** · Namespaces y settings de login corregidos

### Objetivo de negocio

- [ ] 🎯 **La tarjeta «Evaluaciones» dice «Disponible» y es el acceso al módulo**

## Preparación del despliegue

> 🛑 **DETENCIÓN P-1 obligatoria antes de desplegar:**
>
> ```
> 🛑 DETENCIÓN — Despliegue — Motivo P-1
>
> Necesito que agregues vos estas variables al .env de producción, Pablo:
>
>     # Módulo de Ergonomía SRT 886/15 — todas tienen valor por defecto.
>     # Declarar sólo las que quieras cambiar.
>     CHAT_AI_MODEL=<el modelo con el que se validaron los informes>
>     CSP_REPORT_ONLY=False
>
> Motivo: no debo manejar el .env real de producción.
>
> Recordá además que el despliegue necesita, antes de arrancar los procesos:
>
>     python manage.py migrate --noinput
>     python manage.py migrate --check
>     python manage.py createcachetable
>     python manage.py collectstatic --noinput
>
> Qué hago cuando termines: ejecuto la prueba de humo autenticada en producción.
> ```

### Runbook de despliegue

```bash
# 1. Compuertas
python manage.py makemigrations --check --dry-run
python manage.py migrate --noinput
python manage.py migrate --check

# 2. Infraestructura del módulo
python manage.py createcachetable
python manage.py collectstatic --noinput

# 3. Chequeo de despliegue
python manage.py check --deploy

# 4. Reiniciar procesos

# 5. Prueba de humo autenticada:
#    /dashboard/ → tarjeta Evaluaciones → crear evaluación →
#    Planilla 1 → factor LMC → wizard → descargar protocolo oficial
```

## Estado final esperado

| Métrica | Antes | Después |
|---|---:|---:|
| Apps Django propias | 9 | **13** |
| Modelos de dominio | 13 | **45** |
| Pruebas | 32 | **~205** |
| Migraciones propias | 15 | **28** |
| Templates | 33 | **63** |
| Regresiones críticas abiertas | 2 | **0** |
| Tarjeta «Evaluaciones» | 🟡 Próximamente | 🟢 **Disponible** |

## Deudas que este roadmap NO cierra

| ID | Deuda | Por qué |
|---|---|---|
| **D-4** | Planilla 2 no distingue «NO» de «sin responder» | Requiere cambiar 9 modelos y la lógica de export. CF-5 lo compensa funcionalmente |
| **D-5** | Interfaz de una sola instancia por Planilla 2 | El modelo y la exportación ya soportan N |
| **D-9** | No existe el «protocolo cerrado» | **La deuda funcionalmente más importante** para un producto que emite documentación legal |
| **D-10** | `planillas` importa helpers privados de `evaluaciones` | Se arrastra tal cual |
| **H1** | Sin backup automatizado de producción | **Riesgo #1 del proyecto.** Ajeno al código |
| **H2** | Certificados descargables sin autenticación | Ajeno al módulo |
| **H12** | SSE sobre workers WSGI sync | **Se agrava:** ahora hay dos consumidores de SSE. Requiere migrar a ASGI |
| **H4** | `main` 40 commits atrás | Conviene resolverla antes de que la brecha crezca |

---

*Roadmap de ejecución emitido el 2 de agosto de 2026, sobre el documento de diseño `INTEGRACION_MODULO_ERGONOMIA_886_PROPUESTA_TECNICA.md` y la verificación directa del código de ambos proyectos.*

*58 commits · 7 fases · 2 repositorios · 6 condiciones vinculantes.*
