# Integración del módulo de Ergonomía SRT 886/15 en ErgoSolutions — Informe técnico y propuesta

**Proyecto padre (absorbe):** ErgoSolutions — `/Users/praguirre/ergocapacitacion` — rama `release/beta`
**Proyecto a integrar (se absorbe):** ErgoApp SRT 886 — `/Users/praguirre/ergonomia_srt` — rama `main`
**Documento:** `docs/INTEGRACION_MODULO_ERGONOMIA_886_PROPUESTA_TECNICA.md`
**Versión:** 1.0
**Fecha:** 2 de agosto de 2026
**Naturaleza:** análisis y diseño. **No se modificó ni una línea de código de ninguno de los dos proyectos.**

---

## Control documental

| Ítem | Valor |
|---|---|
| Propósito | (a) Informe técnico del estado real de ambos proyectos; (b) propuesta completa de integración del módulo de evaluación ergonómica SRT 886/15 dentro de ErgoSolutions |
| Método | Lectura directa del código fuente de ambos proyectos, ejecución de las dos suites de pruebas, resolución de URLs contra el URLconf real e introspección de dependencias instaladas, el 02/08/2026 |
| Audiencia | Arquitecto o desarrollador que ejecute la integración; asistente IA de desarrollo |
| Premisa de datos | **Los datos de ErgoApp SRT 886 son ficticios y descartables.** No hay migración de datos en ningún punto de esta propuesta |
| Restricción vinculante | Las seis condiciones fundamentales CF-1 a CF-6 de `ESTADO_TECNICO_COMPLETO_E_INTEGRACION_ERGOCAPACITACION_2026-08-01.md` §9.5 |

### Convención de marcado

| Marca | Significado |
|---|---|
| **[VERIFICADO]** | Comprobado leyendo el código o ejecutando un comando en la fecha de este documento. Se indica archivo y línea |
| **[PROPUESTA]** | Diseño nuevo. No existe todavía en ningún proyecto |
| **[HALLAZGO]** | Discrepancia entre lo que afirma la documentación existente y lo que dice el código. **Gana el código** |
| **[PENDIENTE]** | No se pudo verificar en esta etapa. Requiere comprobación antes de ejecutar |

### Comandos de verificación ejecutados

```
# ErgoApp SRT 886
cd /Users/praguirre/ergonomia_srt
git branch --show-current                → main
git log --oneline -1                     → 8b61e62
./venv/bin/python --version              → Python 3.11.2
./venv/bin/python manage.py test --settings=ergonomia_srt.test_settings
                                         → Ran 160 tests — OK

# ErgoSolutions
cd /Users/praguirre/ergocapacitacion
git branch --show-current                → release/beta
.venv/bin/python --version               → Python 3.11.2
.venv/bin/python manage.py check         → System check identified no issues (0 silenced)
.venv/bin/python manage.py makemigrations --check --dry-run
                                         → No changes detected
.venv/bin/python manage.py test apps     → Ran 32 tests — OK
```

Todos ejecutados el 02/08/2026 con resultado transcripto literalmente. **[VERIFICADO]**

---

# PARTE I — SÍNTESIS EJECUTIVA

## 1.1 Veredicto de viabilidad

**La integración es viable y su complejidad es sensiblemente menor de lo que estimaba la documentación previa.**

La razón es una sola y es la premisa de este trabajo: **los datos de ErgoApp son descartables**. Eso elimina de un plumazo la parte más cara y riesgosa de cualquier fusión de sistemas —migración de datos, renombrado de tablas con preservación de registros, mapeo de usuarios, reconciliación de identidades— y reduce el trabajo a tres cosas: mover código, reescribir referencias y normalizar el dominio contra entidades que el destino ya tiene.

Sobre esa base, la verificación directa del código produjo cuatro resultados que **simplifican** el plan respecto de lo previsto:

| # | Hallazgo | Efecto sobre el plan |
|---|---|---|
| 1 | La migración `planillas/migrations/0001_initial.py:13,28` **ya** usa `swappable_dependency(settings.AUTH_USER_MODEL)`. Se comprobó que `deconstruct()` del FK a `User` y del FK a `settings.AUTH_USER_MODEL` son **idénticos** | El bloqueante B1 **no genera migración alguna**. Es un cambio de una línea, sin efecto en el estado de migraciones |
| 2 | Los `app_label` de las cinco apps de origen (`core`, `planillas`, `evaluaciones`, `exportaciones`, `help_ai`) **no colisionan** con ninguno de los nueve del destino | No hace falta tocar `app_label` ni renombrar tablas. Las migraciones existentes se conservan intactas |
| 3 | Toda la API de `openai-agents` que usa ErgoApp (`Agent`, `Runner`, `RunConfig`, `ItemHelpers`, y el campo `trace_include_sensitive_data` que sostiene CF-4) **existe en la versión 0.6.9 instalada en el destino** | El salto de `openai-agents` 0.3.3 → 0.6.9 y de `openai` 1.x → 2.x no es bloqueante |
| 4 | Ningún template de ErgoApp usa `<script>` sin nonce ni manejadores en línea | El módulo 886 es **compatible con CSP tal como está** |

Y produjo dos que lo **complican** respecto de lo previsto, ambos del lado del destino:

| # | Hallazgo | Efecto sobre el plan |
|---|---|---|
| 5 | `templates/base_dashboard.html:10,12,110` y `templates/base_landing.html` cargan Bootstrap y Bootstrap Icons desde `cdn.jsdelivr.net`; hay además 5 bloques `<script>` inline y 3 manejadores en línea en templates del destino | Portar el CSP de ErgoApp **rompe todo el frontend de ErgoSolutions**. No es "auditar": es un trabajo de remediación previo con alcance propio |
| 6 | `help_ai/prompts.py:14-15` resuelve la ruta de los documentos de ayuda como `Path(__file__).resolve().parent.parent / "static" / "ayuda" / "help_texts"` | Al anidar la app, esa ruta apunta a un directorio inexistente. **Es un bloqueante duro no documentado** |

## 1.2 Estrategia recomendada, en una página

Se propone **trasplantar cuatro de las cinco apps de ErgoApp a un paquete contenedor `apps/ergonomia_886/`**, disolver la quinta (`core`) dentro del dashboard existente, y montar todo bajo un prefijo de URL único.

```
apps/ergonomia_886/          ← paquete contenedor, sin modelos propios
    planillas/               ← protocolo documental. Raíz del dominio: Evaluacion
    evaluaciones/            ← 13 factores, motor de cálculo, artefactos normativos
    exportaciones/           ← planillas oficiales, detalle técnico, informes LLM, ZIP
    help_ai/                 ← ayuda contextual + chat SSE   (CF-1: NO se fusiona con ergobot_ai)
```

`core` **no se trasplanta**: su autenticación se descarta íntegramente en favor de `apps.accounts`, y su única pieza de valor —el dashboard de evaluaciones con búsqueda, filtros y paginación— se reimplanta como una vista nueva dentro de `apps.dashboard`, que es donde vive el punto de entrada del profesional.

Los `app_label` se conservan (`planillas`, `evaluaciones`, `exportaciones`, `help_ai`), de modo que **las diez migraciones existentes se copian sin tocar** y las tablas se crean desde cero con sus nombres actuales.

La tarjeta «Evaluaciones» de `templates/dashboard/home.html:79-96` deja de decir «Próximamente» y pasa a enlazar a `/evaluacion-ergonomica/`, que es el listado de evaluaciones ergonómicas del profesional.

El orden de trabajo es:

```
Fase 0 → Reparar N1 y N2 de ErgoSolutions y crear config/test_settings.py   (previo, ajeno al módulo)
Fase 1 → Adaptar ErgoApp en su propio repositorio y dejar 160 tests en verde
Fase 2 → Trasplante mecánico + primer arranque en el destino
Fase 3 → Normalización de dominio contra CompanyProfile y CustomUser
Fase 4 → Integración de UI: dashboard, tarjeta, navegación, ayuda
Fase 5 → Aprovechamiento: firmantes, evidencia, agenda, trabajadores
Fase 6 → CSP (opcional y separable, con remediación previa del frontend del destino)
```

**La Fase 6 se separó deliberadamente del resto.** La documentación previa la ubicaba en la Fase 0 como prerrequisito; la verificación del frontend del destino demuestra que eso convertiría un trabajo de integración en un trabajo de refactorización de todo el frontend. El módulo 886 funciona sin CSP —sus scripts llevan `nonce` pero un atributo `nonce` vacío es inocuo cuando no hay política activa—, de modo que el endurecimiento puede hacerse después, sin bloquear la entrega.

## 1.3 Esfuerzo estimado

Estimación por fase, en jornadas de trabajo efectivo de un desarrollador que conozca ambos proyectos. **[PROPUESTA]**

| Fase | Contenido | Esfuerzo | Riesgo |
|---|---|---:|---|
| **0** | Reparar N1 + N2, `config/test_settings.py`, `CACHES`, `pypdf`, `createcachetable` | 1,0 j | Bajo |
| **1** | `AUTH_USER_MODEL`, `app_name` en 2 apps, 34 referencias de URL, driver, CORS | 1,0 j | Bajo |
| **2** | Mover 4 apps, reescribir 102 imports, 26 rutas de catálogo, 12 `model_path`, rutas de archivos, templates, URLs | 2,5 j | **Medio** |
| **3** | `Evaluacion.empresa`, filtros por tipo de usuario, propiedad mixta | 2,0 j | Medio |
| **4** | Dashboard de evaluaciones, tarjeta, navegación, widget de ayuda | 1,5 j | Bajo |
| **5** | Firmantes, evidencia VCE, agenda, trabajadores estructurados | 3,0 j | Bajo |
| **6** | CSP: remediar frontend del destino + portar middleware | 2,0 j | **Alto** |
| | **Total sin Fase 6** | **11,0 j** | |
| | **Total con Fase 6** | **13,0 j** | |

## 1.4 Riesgos principales

| # | Riesgo | Probabilidad | Impacto | Mitigación |
|---|---|---|---|---|
| **R-1** | El trasplante rompe alguna de las 160 pruebas por una referencia de import o de URL no actualizada | **Alta** | Medio | La suite es el criterio de aceptación de la Fase 2. Reescritura asistida por búsqueda exhaustiva; inventario completo en §6 y Anexo A |
| **R-2** | Portar el CSP deja el frontend del destino sin estilos ni JavaScript | **Alta si se hace sin remediar** | **Alto** | Fase 6 separada, con remediación previa de CDN y scripts inline. Verificación pantalla por pantalla |
| **R-3** | Las regresiones N1/N2 abiertas del destino se confunden con fallas introducidas por la integración | Alta | Medio | **Fase 0 obligatoria**: integrar sobre base sana. Es la única dependencia dura de orden |
| **R-4** | Las cuotas de `help_ai` y de informes dejan de ser globales por falta de `CACHES` compartida | Media | Medio | `DatabaseCache` + `createcachetable` en Fase 0. Verificación explícita en §11 |
| **R-5** | El streaming SSE de `help_ai` degrada el servicio al correr sobre workers WSGI sync | Media | **Alto** en producción | Hallazgo H12 preexistente del destino. Se documenta; la solución (ASGI) excede este alcance |
| **R-6** | Diferencia de versión de `openai` (1.x → 2.x) altera el comportamiento del SDK | Baja | Medio | API verificada como presente en 0.6.9. Las 38 pruebas de IA usan `patch` y no llaman al proveedor |
| **R-7** | Los tres artefactos normativos con criterios internos (D-11) se presentan como oficiales en un sistema con más exposición | Media | **Alto (producto, no técnico)** | Fuera de alcance técnico. Requiere decisión profesional nominal. Ver §12 |

---

# PARTE II — INFORME TÉCNICO DE ErgoSolutions (proyecto padre)

## 2.1 Infraestructura y entorno **[VERIFICADO]**

| Componente | Valor | Fuente |
|---|---|---|
| Ruta | `/Users/praguirre/ergocapacitacion` | — |
| Repositorio | `github.com/praguirre/ergocapacitacion` | — |
| Rama activa | **`release/beta`** | `git branch --show-current` |
| Entorno virtual | `.venv` (con punto) | — |
| Python local | 3.11.2 | `.venv/bin/python --version` |
| Python producción | 3.10.12 | `ESTADO_TECNICO_CONSOLIDADO §2.3` |
| Django | 5.2.10 | `pip list` |
| Configuración | `config/settings.py`, `config/urls.py` | — |
| Base de datos | `env.db("DATABASE_URL")` — URL única | `config/settings.py:85-87` |
| Driver | `psycopg[binary] 3.3.2` (**psycopg 3**) | `pip list` |
| Servidor | Gunicorn WSGI; `config/asgi.py` existe pero no se usa | `ESTADO_TECNICO_CONSOLIDADO H12` |
| Estáticos | WhiteNoise `CompressedManifestStaticFilesStorage` | `config/settings.py:133-140` |
| `MEDIA_ROOT` | ✅ `BASE_DIR / "media"` | `config/settings.py:145-146` |
| `CACHES` | ❌ **No definido** → `LocMemCache` por defecto | Ausencia verificada en `config/settings.py` |
| CSP / nonce | ❌ **No existe** | `config/settings.py:52-61` |
| `LANGUAGE_CODE` | **`es-ar`** | `config/settings.py:121` |
| `TIME_ZONE` | `America/Argentina/Buenos_Aires` | `config/settings.py:122` |
| Modelo de usuario | **`accounts.CustomUser`** | `config/settings.py:90` |
| Modelo de IA | `OPENAI_MODEL`, defecto `gpt-4.1-mini-2025-04-14` | `config/settings.py:195` |
| `test_settings` | ❌ **No existe** | `ls config/` |

> **[HALLAZGO] H-A — `LANGUAGE_CODE` del destino es correcto.**
> El documento de ErgoApp (deuda D-8) consigna que «el destino tiene el mismo problema a verificar» respecto de `LANGUAGE_CODE = 'en-us'`. **Es falso.** `config/settings.py:121` declara `LANGUAGE_CODE = "es-ar"`. El problema es exclusivo del origen y se resuelve al adoptar la configuración del destino.

> **[HALLAZGO] H-B — ErgoSolutions no tiene configuración de pruebas aislada.**
> ErgoApp corre su suite con `--settings=ergonomia_srt.test_settings`, que fuerza SQLite en memoria, `LocMemCache`, hashers rápidos y `StaticFilesStorage` no manifestado. ErgoSolutions **no tiene equivalente**: `ls config/` devuelve sólo `asgi.py`, `settings.py`, `urls.py`, `wsgi.py`. Sin un `config/test_settings.py`, las 160 pruebas trasplantadas exigirán PostgreSQL con permisos de creación de base y fallarán por el `ManifestStaticFilesStorage` al renderizar templates. **Es un prerrequisito de la Fase 0 que ninguna documentación previa menciona.**

## 2.2 Dependencias

`requirements.txt`, 9 líneas **[VERIFICADO]**:

```
Django>=5.2
psycopg[binary]>=3.2
django-environ>=0.11
django-bootstrap5>=25.1
whitenoise>=6.7
reportlab>=4.0
openai>=1.0
openai-agents>=0.0.19
uvicorn>=0.30.0
```

Versiones realmente instaladas en `.venv`, contrastadas con las del origen **[VERIFICADO]**:

| Paquete | ErgoSolutions | ErgoApp SRT 886 | Observación |
|---|---|---|---|
| `Django` | **5.2.10** | 5.2.7 | Compatible |
| `psycopg` | **3.3.2** | — | Driver del destino |
| `psycopg2-binary` | — | 2.9.10 | Se descarta |
| `django-bootstrap5` | **26.1** | 25.2 | Compatible |
| `reportlab` | **4.4.9** | 4.5.1 | Compatible |
| `pypdf` | ❌ **ausente** | **6.14.2** | **Hay que agregarlo** |
| `openai` | **2.15.0** | 1.109.1 | Salto de versión mayor |
| `openai-agents` | **0.6.9** | 0.3.3 | Salto significativo |
| `sse-starlette` | 3.2.0 | 3.0.2 | Declarada en origen, **no se usa** |
| `httpx-sse` | 0.4.3 | 0.4.2 | Transitiva |
| `whitenoise` | 6.11.0 | 6.11.0 | Idéntica |
| `django-environ` | 0.12.0 | 0.12.0 | Idéntica |
| `uvicorn` | 0.40.0 | 0.37.0 | Compatible |
| `gunicorn` | ❌ ausente en venv | 23.0.0 | Producción del destino lo usa igual |
| `django-cors-headers` | — | 4.9.0 | Se descarta |
| `pillow` | **12.1.0** | 11.3.0 | **Instalada pero NO declarada** en ninguno de los dos `requirements.txt` |
| `weasyprint` | — | 66.0 | Instalada sin declarar, sin uso. Se descarta |

> **[VERIFICADO] Riesgo del salto de `openai-agents` acotado.** Se introspeccionó el paquete 0.6.9 del destino: `Agent`, `Runner`, `RunConfig` e `ItemHelpers` están presentes; `Runner.run` y `Runner.run_streamed` existen; y `RunConfig` conserva el campo **`trace_include_sensitive_data`**, que es el que sostiene CF-4. La superficie de API que consumen `help_ai/agents.py`, `help_ai/views.py:16,108,112` y `exportaciones/reports/llm.py:16,82,92,96` está cubierta.

> **[VERIFICADO] `pillow` no está declarada en ninguno de los dos proyectos.** Es dependencia obligatoria de `ImageField`, que ambos usan: `CompanyProfile.logo` (`apps/company/models.py:120`) y `VibracionCE_Eval.foto_montaje` (`evaluaciones/models.py:383`). Corresponde al hallazgo N8 del informe del destino y debe declararse.

## 2.3 Arquitectura y aplicaciones

Nueve aplicaciones propias bajo el paquete `apps/`, con nombres punteados `apps.<nombre>` **[VERIFICADO — `config/settings.py:38-48`]**:

| App | `name` | `label` efectivo | Modelos | Rol |
|---|---|---|---|---|
| `apps.accounts` | `apps.accounts` | `accounts` | `CustomUser` | Identidad y autenticación triple |
| `apps.landing` | `apps.landing` | `landing` | — | Home institucional pública |
| `apps.dashboard` | `apps.dashboard` | `dashboard` | — | Portal de backoffice (profesional + empresa) |
| `apps.presencial` | `apps.presencial` | `presencial` | `PresencialSession` | Modalidad presencial |
| `apps.company` | `apps.company` | `company` | `CompanyProfile`, `CompanyWorker`, `AgendaEvent`, `ContactRequest` | Backoffice de empresa |
| `apps.training` | `apps.training` | `training` | `TrainingModule`, `CapacitacionLink`, `LinkShareLog` | Módulos de capacitación |
| `apps.quiz` | `apps.quiz` | `quiz` | `Question`, `Choice`, `QuizAttempt`, `QuizState` | Evaluación de conocimiento |
| `apps.certificates` | `apps.certificates` | `certificates` | `Certificate` | Certificación |
| `apps.ergobot_ai` | `apps.ergobot_ai` | `ergobot_ai` | — | Chatbot docente (164 líneas) |

Ninguna declara `label` explícito **[VERIFICADO — `apps/*/apps.py`]**, por lo que Django deriva el label de la última componente del nombre punteado. **Este hecho es la base de la decisión de arquitectura D-2 de §7.2.**

> **Precisión menor.** El informe consolidado del propio destino consigna «10 aplicaciones Django propias». El conteo verificado sobre `config/settings.py:38-48` es de **9** entradas en `LOCAL_APPS`. La diferencia no afecta a ninguna decisión de esta propuesta, pero el número que aplica para verificar colisiones de `app_label` es **9**.

Inventario cuantitativo, según el informe consolidado del propio proyecto: 103 archivos Python sin migraciones, 7.924 líneas, 15 migraciones, 13 modelos de dominio, 33 templates, 32 pruebas.

## 2.4 Modelo de datos

### `accounts.CustomUser` **[VERIFICADO — `apps/accounts/models.py:80-317`]**

`AbstractBaseUser + PermissionsMixin`, con `USERNAME_FIELD = "email"` y `REQUIRED_FIELDS = []`.

| Grupo | Campos | Línea |
|---|---|---|
| Discriminador | `user_type ∈ {professional, trainee, company}` | `:94-99` |
| Comunes | `email` (unique, indexado), `first_name`, `last_name`, `full_name` (legacy, sincronizado en `save()`) | `:104-127` |
| **Profesional** | `username` (unique, nullable), `dni`, **`profession`**, **`license_number`** | `:132-159` |
| Trabajador | `cuil` (unique, indexado), `job_title`, `company_name`, `employer_email`, `safety_responsible_email` | `:164-193` |
| Suscripción | `subscription_tier`, `subscription_status`, `subscription_expires` | `:209-225` |
| Control | `is_active`, `is_staff`, `is_visible_in_directory`, `date_joined` | `:230-237` |

Propiedades relevantes: `is_professional`, `is_trainee`, `is_company`, **`is_backoffice_user`** (`professional ∪ company`, `:278-286`), `display_name`, `has_active_subscription`.

> **`profession` y `license_number` son la pieza que habilita imprimir la aclaración de firma en las planillas oficiales de la SRT.** Ver oportunidad O-2 en §7.6.

### `company.CompanyProfile` **[VERIFICADO — `apps/company/models.py:10-145`]**

`OneToOneField` a `CustomUser` con `limit_choices_to={'user_type': 'company'}` (`:26-32`).

| Campo | Tipo | Línea | Correspondencia en `Evaluacion` |
|---|---|---|---|
| `razon_social` | `CharField(300)` | `:37` | ✅ `Evaluacion.razon_social` `CharField(255)` |
| `nombre_comercial` | `CharField(300)` | `:41` | — |
| `cuit` | `CharField(20)` **unique** | `:48` | ✅ `Evaluacion.cuit` `CharField(13)` |
| `rubro` | `CharField(200)` | `:54` | ≈ `Evaluacion.ciiu` (no equivalente) |
| `cantidad_trabajadores` | `PositiveIntegerField` | `:60` | ≈ `Planilla1.nro_trabajadores` |
| `contacto_nombre` | `CharField(200)` | `:68` | — (habilita O-2) |
| `contacto_cargo`, `contacto_telefono` | `CharField` | `:72,78` | — |
| `domicilio` | `CharField(400)` | `:88` | ✅ `Evaluacion.direccion_establecimiento` `CharField(255)` |
| `localidad` | `CharField(200)` | `:94` | — |
| `provincia` | `CharField(100)` | `:100` | ✅ `Evaluacion.provincia` `CharField(100)` |
| `account_status` | `CharField(30)` choices | `:110` | — |
| `logo` | `ImageField('company_logos/')` | `:120` | — |

**Cuatro de los seis campos de negocio de `planillas.Evaluacion` ya existen aquí, estructurados.** Es el fundamento de la oportunidad O-1.

### `company.CompanyWorker` **[VERIFICADO — `apps/company/models.py:148-200`]**

FK a `CompanyProfile` y a `CustomUser` (limitado a `trainee`), `employee_code` (legajo), `department` (sector), `position` (puesto), `is_active`, `start_date`, `end_date`, `notes`. Constraint único `uq_company_worker` sobre `(company, worker)` (`:192-197`).

### `company.AgendaEvent` **[VERIFICADO — `apps/company/models.py:203-290`]**

| Grupo | Campos | Línea |
|---|---|---|
| Relaciones | `company`, `worker` (nullable), `created_by`, `assigned_professional` | `:226-262` |
| Contenido | `title`, `description` | `:235-236` |
| Clasificación | `event_type ∈ {training_due, certificate_expiry, professional_visit, **evaluation_due**, reminder, other}` | `:206-212` |
| Estado | `status ∈ {pending, completed, overdue, cancelled}`, `priority` | `:214-224` |
| Temporalidad | `start_at` (nullable), `due_at` (**obligatorio**) | `:249-252` |
| **Vínculo genérico** | **`related_object_type`**, **`related_object_id`** | `:263-271` |

Índices compuestos en `(company, status, due_at)` y `(company, event_type, due_at)` (`:279-282`).

> **El enum ya contiene `evaluation_due`.** No hay que agregarlo: el modelo fue diseñado previendo este caso. Es el fundamento de la oportunidad O-4.

### `company.ContactRequest` **[VERIFICADO — `apps/company/models.py:293-339`]**

Solicitud empresa → profesional, con constraint único parcial condicionado a `status='pending'` (`:330-336`).

### Dominio de capacitación

`TrainingModule`, `CapacitacionLink`, `LinkShareLog`, `Question`, `Choice`, `QuizAttempt`, `QuizState`, `Certificate`, `PresencialSession`. Sin interacción directa con el módulo 886 salvo por la oportunidad O-6.

## 2.5 Mapa de URLs **[VERIFICADO — `config/urls.py`]**

| Prefijo | Módulo | Namespace | Línea |
|---|---|---|---|
| `/admin/` | `django.contrib.admin` | — | `:15` |
| `/dashboard/` | `apps.dashboard.urls` | **`dashboard`** | `:20` |
| `/` | `apps.landing.urls` | **`landing`** | `:25` |
| `/acceso/` | `apps.accounts.urls` | ⚠️ **ninguno** | `:30` |
| `/capacitacion/` | `apps.training.urls` | ⚠️ **ninguno** | `:31` |
| `/quiz/` | `apps.quiz.urls` | ⚠️ **ninguno** | `:32` |
| `/certificados/` | `apps.certificates.urls` | ⚠️ **ninguno** | `:33` |
| **`/ai/`** | **`apps.ergobot_ai.urls`** | ⚠️ **ninguno** | `:34` |
| `/auth/` | `apps.accounts.urls_professional` | **`accounts_professional`** | `:39-45` |
| `/empresa/auth/` | `apps.accounts.urls_company` | **`accounts_company`** | `:50-56` |
| `/c/` | `apps.training.urls_public` | ⚠️ **ninguno** | `:61` |

Anidado dentro de `/dashboard/` **[VERIFICADO — `apps/dashboard/urls.py`]**:

| Prefijo | Módulo | Namespace resultante |
|---|---|---|
| `/dashboard/presencial/` | `apps.presencial.urls` | — |
| `/dashboard/empresa/` | `apps.company.urls` | **`dashboard:company`** |

> **[HALLAZGO] H-C — El prefijo `/ai/` ya está ocupado en el destino.**
> `config/urls.py:34` monta `apps.ergobot_ai.urls` bajo `/ai/`, produciendo `/ai/ergobot/<slug>/stream/` **[VERIFICADO: `reverse('ergobot_stream', args=['ergonomia'])` → `/ai/ergobot/ergonomia/stream/`]**. ErgoApp monta `help_ai` bajo el mismo `/ai/`, produciendo `/ai/guide/<slug>/` y `/ai/chat/<slug>/`. Los sub-paths no colisionan literalmente, pero montar dos productos distintos bajo el mismo prefijo contradice CF-1, que exige que sean identificables como separados. **Se propone montar `help_ai` dentro del prefijo del módulo 886.** Ver §7.4.

> **[HALLAZGO] H-D — `apps.ergobot_ai.urls` tampoco declara `app_name`.**
> `apps/ergobot_ai/urls.py` no tiene `app_name`, de modo que `ergobot_stream` vive en el espacio de nombres global del destino, igual que los nombres de `planillas` y `help_ai` en el origen. El destino ya padece el mismo defecto que B3 señala en el origen; conviene corregirlo en el mismo movimiento.

## 2.6 Plantillas **[VERIFICADO]**

Tres plantillas base en `templates/`:

| Plantilla | Bloques | Estilos y scripts |
|---|---|---|
| `base.html` | `title`, `extra_head`, `content` | `{% bootstrap_css %}` / `{% bootstrap_javascript %}` de `django_bootstrap5`; `static 'css/app.css'` |
| `base_dashboard.html` | `title`, `extra_css`, `content`, `extra_js` | **CDN jsdelivr** (`:10`, `:12`, `:110`); `static 'css/dashboard.css'` |
| `base_landing.html` | — | **CDN jsdelivr** |

Directorios de templates: `accounts/`, `company/`, `dashboard/`, `includes/`, `landing/`, `presencial/`, `quiz/`, `training/`. **Ninguno colisiona con los del origen** (`core/`, `planillas/`, `evaluaciones/`, `exportaciones/`).

> **[HALLAZGO] H-E — El destino depende de CDN externo y de scripts inline. Es el obstáculo real del CSP.**
> Verificado por búsqueda exhaustiva en `templates/`:
>
> | Elemento | Cantidad | Archivos |
> |---|---:|---|
> | Referencias a `cdn.jsdelivr.net` | **6** | `base_dashboard.html` (3), `base_landing.html` (3) |
> | Bloques `<script>` inline | **5** | `training/training_page.html:59`, `quiz/quiz_widget.html:23`, `dashboard/online_links.html:119`, `presencial/capacitacion.html:139`, `presencial/quiz.html:113` |
> | Manejadores en línea (`onclick=`, etc.) | **3** | `dashboard/online_links.html` (1), `presencial/quiz.html` (2) |
>
> Contra la política de ErgoApp (`default-src 'self'`, `script-src 'self' 'nonce-…'`, `script-src-attr 'none'`), **las 6 referencias CDN se bloquean** —dejando todo el sitio sin Bootstrap CSS ni JS—, **los 5 bloques inline se bloquean** por falta de nonce y **los 3 manejadores se bloquean** por `script-src-attr 'none'`. El informe previo describía esto como «auditar que las 9 apps existentes no usen scripts en línea»; la magnitud real es una remediación de frontend con alcance propio.

## 2.7 Estado actual, deudas y regresiones abiertas **[VERIFICADO]**

La suite del destino está en verde: `Ran 32 tests — OK`. `manage.py check` no reporta issues y `makemigrations --check` devuelve `No changes detected`.

Sin embargo, **el proyecto arrastra dos regresiones críticas verificadas**, reproducidas contra el código:

### N1 — Nueve rutas del backoffice devuelven HTTP 500 a usuarios anónimos

**Causa raíz verificada por resolución de URLs:**

```
reverse('professional_login')                       → NoReverseMatch
reverse('accounts_professional:professional_login') → /auth/login/     ✅
reverse('landing')                                  → NoReverseMatch
reverse('trainee_landing')                          → /acceso/          ✅
```

Los decoradores invocan los nombres inexistentes **[VERIFICADO — `apps/accounts/decorators.py:27,54,92,122,152`]**:

```python
:27   url = login_url or reverse('professional_login')   # NoReverseMatch
:54   url = login_url or reverse('landing')              # NoReverseMatch
:92   url = login_url or reverse('professional_login')   # NoReverseMatch
:122  url = login_url or reverse('professional_login')   # NoReverseMatch
:152  return redirect('professional_login')              # NoReverseMatch
```

Y once vistas de `apps/company/views.py` usan `@company_required` **sin** `@login_required` que intercepte al anónimo antes **[VERIFICADO — `:33, 96, 168, 215, 247, 285, 338, 378, 408, 422, 454`]**, más `apps/dashboard/views.py:373,386` con `@professional_required`.

> **[HALLAZGO] H-F — Dos settings del destino apuntan a nombres de URL que no resuelven.**
> Verificado ejecutando `reverse()` sobre los valores declarados:
>
> | Setting | Valor | Resuelve |
> |---|---|---|
> | `LOGIN_URL` | `'trainee_landing'` | ✅ `/acceso/` |
> | `LOGIN_REDIRECT_URL` | `'training_home'` | ✅ `/capacitacion/` |
> | **`PROFESSIONAL_LOGIN_URL`** | `'professional_login'` | 🔴 **NO RESUELVE** |
> | **`PROFESSIONAL_LOGIN_REDIRECT_URL`** | `'dashboard'` | 🔴 **NO RESUELVE** |
>
> `config/settings.py:109-110`. Es la misma familia de defecto que N1 y no figura como hallazgo independiente en el informe consolidado del destino. Conviene corregirlo en el mismo commit de la Fase 0.

### N2 — La ficha del trabajador rompe con HTTP 500

**[VERIFICADO — `apps/company/views.py:202`]**:

```python
'is_approved': qs.is_approved if qs else False,   # QuizState no tiene is_approved
```

El modelo `QuizState` expone `attempts_used`, `lockout_until`, `retake_available_at`, `last_completed_at` y `last_passed`. El campo con esa semántica es **`last_passed`**.

### Deudas restantes del destino, relevantes para esta integración

| ID | Deuda | Relevancia para el módulo 886 |
|---|---|---|
| **H12** | Vistas `async` sobre workers WSGI sync: cada chat ocupa un worker completo | **Alta.** `help_ai` es streaming SSE y agrava el problema |
| **N8** | `pillow` obligatoria y no declarada | Media. `VibracionCE_Eval.foto_montaje` la necesita |
| **N3** | Directorio de profesionales inalcanzable (`is_visible_in_directory` sin control de activación) | Baja. Ajena al módulo |
| **H1** | Sin backup automatizado de la base de producción | **Alta operativa.** Ajena al módulo, pero condiciona cualquier despliegue |
| **H4** | `main` 40 commits y 6 meses por detrás de `release/beta` | Media. Confunde a quien clone el repositorio |
| — | Árbol de trabajo con cambios sin commitear: `docs/` untracked, `.gitignore` y `README.md` modificados, 4 `.md` movidos a `docs/` | Baja. Conviene consolidar antes de abrir la rama de integración |

---

# PARTE III — INFORME TÉCNICO DE ErgoApp SRT 886 (proyecto a integrar)

## 3.1 Infraestructura y entorno **[VERIFICADO]**

| Componente | Valor | Fuente |
|---|---|---|
| Ruta | `/Users/praguirre/ergonomia_srt` | — |
| Repositorio | `github.com/praguirre/ergonomia_srt` | — |
| Rama | `main` | `git branch --show-current` |
| Commit | `8b61e62` | `git log --oneline -1` |
| Entorno virtual | `venv` (sin punto) | — |
| Python | 3.11.2 | `./venv/bin/python --version` |
| Django | 5.2.7 | `pip list` |
| Configuración | `ergonomia_srt/settings.py`, `ergonomia_srt/urls.py` | — |
| Base de datos | PostgreSQL, parámetros sueltos `DB_NAME`/`DB_USER`/… | `settings.py:136-145` |
| Driver | `psycopg2-binary 2.9.10` | `pip list` |
| Base de pruebas | SQLite en memoria | `ergonomia_srt/test_settings.py:11-17` |
| `CACHES` | **`DatabaseCache`**, tabla `ergoapp_cache` | `settings.py:149-156` |
| CSP | **Middleware propio con nonce** | `settings.py:102`, `middleware.py` |
| CORS | `django-cors-headers`, restringido a localhost | `settings.py:91,104,227-230` |
| `MEDIA_ROOT` | ❌ **No definido** | Ausencia verificada en `settings.py` |
| `LANGUAGE_CODE` | ⚠️ **`en-us`** con interfaz íntegramente en español | `settings.py:180` |
| `TIME_ZONE` | `America/Argentina/Buenos_Aires` | `settings.py:182` |
| Modelo de usuario | `auth.User` (defecto de Django) | Sin `AUTH_USER_MODEL` en `settings.py` |
| Modelo de IA | `CHAT_AI_MODEL`, defecto `gpt-5.6-luna` | `settings.py:40` |
| Suite | **160 pruebas, OK** | Ejecutada 02/08/2026 |

### Variables de entorno con valor por defecto **[VERIFICADO — `settings.py:40-75`]**

| Variable | Defecto | Función |
|---|---|---|
| `CHAT_AI_MODEL` | `gpt-5.6-luna` | Modelo del chat de ayuda **y** de los informes |
| `CHAT_AI_AGENT_CACHE_SIZE` | 64 | Tamaño del `lru_cache` de agentes de ayuda |
| `CHAT_AI_RATE_LIMIT` | 20 | Consultas de chat por ventana |
| `CHAT_AI_RATE_WINDOW_SECONDS` | 60 | Ventana del chat |
| `CHAT_AI_STREAM_TIMEOUT_SECONDS` | 120 | Tope duro del stream |
| `CHAT_AI_HEARTBEAT_SECONDS` | 10 | Latido SSE |
| `CHAT_AI_MAX_QUESTION_CHARS` | 2000 | Tope de pregunta |
| `CHAT_AI_MAX_THREAD_MESSAGES` | 20 | Tope de historial |
| `CHAT_AI_MAX_MESSAGE_CHARS` | 4000 | Tope por mensaje |
| `REPORT_AI_TIMEOUT_SECONDS` | 90 | Tope de generación de informe |
| `REPORT_AI_RATE_LIMIT` | 10 | Informes por hora y usuario |
| `REPORT_AI_RATE_WINDOW_SECONDS` | 3600 | Ventana de informes |
| `EXPORT_RATE_LIMIT` | 60 | Descargas por ventana |
| `EXPORT_RATE_WINDOW_SECONDS` | 300 | Ventana de descargas |

Los 14 settings deben portarse íntegros al destino. Son los que sostienen las cuotas exigidas por CF-1 y CF-4.

## 3.2 Arquitectura y aplicaciones **[VERIFICADO]**

| App | Archivos `.py` | Líneas | Templates | `app_name` | Responsabilidad |
|---|---:|---:|---:|---|---|
| `core` | 8 | 159 | 3 | ✅ `core` | Autenticación, dashboard, borrado |
| `planillas` | 10 | ~1.100 | 6 | ❌ **ninguno** | Protocolo documental. **Modelo raíz `Evaluacion`** |
| `evaluaciones` | 20 | ~9.168 | 16 | ✅ `evaluaciones` | 13 factores, motor de cálculo, wizard |
| `help_ai` | 13 | **1.052** | 0 | ❌ **ninguno** | Ayuda contextual y chat SSE |
| `exportaciones` | 28 | **4.077** | 2 | ✅ `exportaciones` | Documentos oficiales, detalle, informes, ZIP |
| `ergonomia_srt` | 7 | 395 | 1 | — | Configuración y middleware |

Ningún `apps.py` declara `label` explícito **[VERIFICADO — `core/apps.py`, `planillas/apps.py`, `evaluaciones/apps.py`, `exportaciones/apps.py`, `help_ai/apps.py`]**.

### Patrones de diseño que deben preservarse

**Catálogos declarativos.** `evaluaciones/catalog.py:39-261` define los 13 factores como tupla de `FactorDefinition` (dataclass congelada, `:16-36`). De ahí se derivan automáticamente los enums, las URLs (`evaluaciones/urls.py:13-28`, materializadas en bucle) y las clases de vista. `exportaciones/official/catalog.py:39-60` replica el patrón para las 12 planillas oficiales.

**Separación entre cálculo y redacción.**

| Capa | Módulo | Autoridad |
|---|---|---|
| Cálculo | `evaluaciones/calculators.py` | **Única autoridad** sobre niveles, límites y clasificaciones |
| Juicio profesional | `evaluaciones/views.py` (`review_factor`) | Confirma o modifica, con justificación registrada |
| Redacción | `exportaciones/reports/llm.py` | Sólo prosa. **Nunca decide un nivel** |

**Trazabilidad con checksum.** Cada cálculo persiste en `calc_data["calculation_trace"]` la versión del motor y, por artefacto aplicado, nombre de archivo, versión de datos, fecha de vigencia, fuente normativa y SHA-256.

**Estados operativos explícitos.** `calc_data["estado_resultado"] ∈ {borrador, calculado, desactualizado}`, más los derivados `sin_iniciar`, `no_aplicable` y `revisado`. Un borrador o un resultado desactualizado bloquean el cierre y deshabilitan la generación de informes.

## 3.3 Mapa de URLs **[VERIFICADO — `ergonomia_srt/urls.py`]**

| Prefijo | Módulo | `app_name` | Línea |
|---|---|---|---|
| `/admin/` | `django.contrib.admin` | — | `:22` |
| `/planillas/` | `planillas.urls` | ❌ **ninguno** | `:23` |
| `/` | `core.urls` | ✅ `core` | `:29` |
| `/ai/` | `help_ai.urls` | ❌ **ninguno** | `:30` |
| `/evaluaciones/` | `evaluaciones.urls` | ✅ `evaluaciones` | `:31` |
| `/exportaciones/` | `exportaciones.urls` | ✅ `exportaciones` | `:32` |

Nombres de URL que hoy viven en el **espacio global** y que deben pasar a namespace:

| App | Nombres | Archivo |
|---|---|---|
| `planillas` | `crear_evaluacion`, `detalle_evaluacion`, `planilla1`, `planilla2a`…`planilla2i`, `planilla3`, `planilla4` (**14 nombres**) | `planillas/urls.py:7-27` |
| `help_ai` | `help_guide`, `chat_ai` (**2 nombres**) | `help_ai/urls.py:9-10` |

> **Trampa de nomenclatura documentada y confirmada.** El kwarg `<int:evaluacion_id>` significa la PK de `planillas.Evaluacion` en `planillas` y en `exportaciones`, pero la PK de `evaluaciones.RiskEvaluation` en `evaluaciones` **[VERIFICADO — `evaluaciones/urls.py:20-26` vs `exportaciones/urls.py:8-11`]**. Son números distintos para la misma evaluación. Todo enlace entre apps debe construirse con `risk_eval.evaluacion_id`, nunca con el kwarg de la URL.

## 3.4 Modelo de datos

### Diagrama actual **[VERIFICADO]**

```
auth.User  (⚠️ django.contrib.auth.models.User — planillas/models.py:4,9)
    │ 1
    │ N
planillas.Evaluacion ──────────────────────── raíz del dominio
    ├─ 1:1  Planilla1 ──── 1:N  FactorRiesgo   (9 filas: A…I)
    ├─ 1:N  Planilla2A … Planilla2I           (9 modelos independientes)
    ├─ 1:1  Planilla3 ──── 1:N  MedidaEspecifica ──── 1:1  SeguimientoMedida
    ├─ 1:1  evaluaciones.RiskEvaluation
    │           ├─ 1:N  LMC_Eval
    │           ├─ 1:N  EmpujeInicial_Eval / EmpujeSostenida_Eval
    │           ├─ 1:N  TraccionInicial_Eval / TraccionSostenida_Eval
    │           ├─ 1:N  Transporte_Eval
    │           ├─ 1:N  Bipedestacion_Eval
    │           ├─ 1:N  RepetitivosMS_Eval
    │           ├─ 1:N  PosturasForzadas_Eval
    │           ├─ 1:N  VibracionMB_Eval
    │           ├─ 1:N  VibracionCE_Eval ──── 1:N  VCESegment
    │           ├─ 1:N  ConfortTermico_Eval
    │           └─ 1:N  EstresContacto_Eval
    ├─ 1:N  exportaciones.GeneratedReport
    └─ 1:N  exportaciones.ExportAudit
```

### `planillas.Evaluacion` **[VERIFICADO — `planillas/models.py:8-19`]**

| Campo | Tipo | Línea | Observación |
|---|---|---|---|
| `usuario` | `ForeignKey(User)` | `:9` | **Único punto del proyecto que importa `auth.models.User`** |
| `razon_social` | `CharField(255)` | `:10` | Duplica `CompanyProfile.razon_social` |
| `cuit` | `CharField(13)` | `:11` | Duplica `CompanyProfile.cuit` |
| `ciiu` | `CharField(10)` nullable | `:12` | Sin equivalente en el destino |
| `direccion_establecimiento` | `CharField(255)` | `:13` | Duplica `CompanyProfile.domicilio` |
| `provincia` | `CharField(100)` | `:14` | Duplica `CompanyProfile.provincia` |
| `fecha_creacion` / `fecha_modificacion` | `DateTimeField` auto | `:15-16` | — |

### Protocolo documental **[VERIFICADO — `planillas/models.py`]**

- **`Planilla1`** (`:22-37`) — `OneToOneField(Evaluacion, primary_key=True)`. Campos: `area_sector`, `puesto_trabajo`, `nro_trabajadores`, `procedimiento_escrito`, `capacitacion`, **`nombres_trabajadores` (`TextField`, `:29`)**, `manifestacion_temprana`, `ubicacion_sintoma`, `tarea_1/2/3`.
- **`FactorRiesgo`** (`:40-57`) — matriz A–I, 9 filas por planilla, `unique_together('planilla1','tipo_factor')`. Niveles **1 Tolerable · 2 Moderado · 3 No Tolerable**.
- **`Planilla2A`…`Planilla2I`** (`:61-174`) — nueve modelos con `ForeignKey(Evaluacion)`, admiten **N instancias** por evaluación. Booleanos `p1_*` (identificación) y `p2_*` (nivel).
- **`Planilla3`** (`:177-193`) — `OneToOneField(Evaluacion, primary_key=True)`, tres medidas generales con fecha, `tarea_analizada`, `observaciones_generales`.
- **`MedidaEspecifica`** (`:195-202`) — N por planilla. **El número de orden no se persiste**: se deriva de `order_by('pk')`.
- **`SeguimientoMedida`** (`:205-221`) — `OneToOneField(MedidaEspecifica)`, constituye la Planilla 4: `nombre_puesto`, `fecha_evaluacion`, `nivel_riesgo`, `fecha_impl_admin`, `fecha_impl_ing`, `fecha_cierre`.

### Dominio cuantitativo **[VERIFICADO — `evaluaciones/models.py`]**

- **`RiskEvaluation`** (`:26-60`) — `OneToOneField(Evaluacion)`. Campos: `estado`, `factores_requeridos` (JSON), `resultado_global`, `resumen_json`, `creado_por` (**`settings.AUTH_USER_MODEL`, `:48-49`** ✅).
- **`BaseFactorEvaluation`** (`:62-102`) — abstracta. `risk_evaluation`, `factor_slug`, `nivel_riesgo`, `aplicable`, `observaciones`, **`calc_data` (`JSONField`)**, marcas de tiempo.
- **13 modelos de factor** (`:104-490`) + **`VCESegment`** (`:399-467`).
- **`VibracionCE_Eval`** declara los dos campos de archivo del proyecto: `foto_montaje = ImageField('evidencia_vce/')` (`:383`) y `certificado_calibracion = FileField('certificados_vce/')` (`:384`). **Sin `MEDIA_ROOT`, hoy no son servibles.**

### Modelos de exportación **[VERIFICADO — `exportaciones/models.py`]**

- **`GeneratedReport`** (`:38-101`) — `evaluacion`, `tipo`, `factor_slug`, `estado`, `payload_json`, `inputs_hash`, `contenido_markdown`, `modelo_llm`, `prompt_version`, `tokens_*`, `duracion_ms`, `generado_por` (**`settings.AUTH_USER_MODEL`, `:71-72`** ✅). Constraint único `(evaluacion, tipo, factor_slug, inputs_hash)` (`:89`).
- **`ExportAudit`** (`:103-…`) — `evaluacion`, `usuario` (**`settings.AUTH_USER_MODEL`, `:111-112`** ✅), `tipo`, `detalle`, `bytes_entregados`, `creado_en`. **Nunca guarda el contenido.**

### Migraciones **[VERIFICADO]**

| App | Migraciones | Dependencia de usuario |
|---|---|---|
| `planillas` | `0001_initial` | **`swappable_dependency(settings.AUTH_USER_MODEL)` en `:13`; FK con `to=settings.AUTH_USER_MODEL` en `:28`** |
| `evaluaciones` | `0001` … `0007` | `swappable_dependency` en `0001:14`; FK en `0001:28` |
| `exportaciones` | `0001_initial`, `0002_generatedreport` | `swappable_dependency` en `0001:14` y `0002:13` |
| `core`, `help_ai` | Ninguna (sin modelos) | — |

Estado: `makemigrations --check` → `No changes detected`.

> **[HALLAZGO] H-G — El estado de migraciones de `planillas` ya es agnóstico del modelo de usuario.**
> Es el hallazgo de mayor impacto práctico de este análisis, y contradice a `ESTADO_TECNICO_COMPLETO §9.3 B1`, que afirma: *«Genera una migración de alteración de clave foránea.»*
>
> **Verificación empírica ejecutada en el proyecto de origen:**
>
> ```
> deconstruct(ForeignKey(User))                     = ('usuario', 'django.db.models.ForeignKey', [],
>                                                      {'on_delete': CASCADE, 'to': 'auth.user'})
> deconstruct(ForeignKey(settings.AUTH_USER_MODEL)) = ('usuario', 'django.db.models.ForeignKey', [],
>                                                      {'on_delete': CASCADE, 'to': 'auth.user'})
> IDENTICOS -> True
> ```
>
> Django serializa un FK al modelo de usuario activo como `settings.AUTH_USER_MODEL` con `swappable_dependency`, sin importar cómo se escribió en el código fuente. Por eso `planillas/migrations/0001_initial.py:13,28` **ya contiene la forma correcta**. Cambiar `planillas/models.py:9` no altera el estado de migraciones: **`makemigrations` seguirá diciendo `No changes detected`.**
>
> **Consecuencia:** B1 deja de ser un bloqueante de datos y pasa a ser un bloqueante de import, de una línea, sin migración asociada. Ver §6.1.

## 3.5 Los cuatro bloques funcionales que aporta

### Bloque 1 — Protocolo documental

Planilla 1 (identificación de factores + matriz A–I), Planillas 2A a 2I (checklists de evaluación inicial, con correspondencia 1:1 con el formulario oficial), Planilla 3 (medidas correctivas y preventivas) y Planilla 4 (matriz de seguimiento).

| Planilla | Ítems Paso 1 | Ítems Paso 2 | Factor cuantitativo asociado |
|---|---:|---:|---|
| 2A Levantamiento/descenso | 3 | 6 | `lmc` |
| 2B Empuje/arrastre | 3 | 7 | `empuje_inicial`, `empuje_sostenida`, `traccion_inicial`, `traccion_sostenida` |
| 2C Transporte manual | 5 | 4 | `transporte` |
| 2D Bipedestación | 1 | 4 | `bipedestacion` |
| 2E Movimientos repetitivos | 1 | 4 | `repetitivos_ms` |
| 2F Posturas forzadas | 1 | 6 | `posturas_forzadas` |
| 2G Vibraciones | 3 + 2 | 2 + 2 | `vibracion_mano_brazo`, `vibracion_cuerpo_entero` |
| 2H Confort térmico | 1 | 1 | `confort_termico` |
| 2I Estrés de contacto | 1 | 4 | `estres_contacto` |

**Limitaciones conocidas que la integración no resuelve:** la interfaz gestiona una sola instancia por Planilla 2 aunque el modelo admite N (`planillas/views.py:171` usa `.first()`); y los booleanos no distinguen «NO» de «sin responder», lo que la exportación resuelve con la regla de CF-5.

### Bloque 2 — Evaluaciones cuantitativas

13 factores con motor determinístico. Calculadoras registradas por decorador en `evaluaciones/calculators.py`:

`calc_lmc` · `calc_empuje_inicial` · `calc_empuje_sostenida` · `calc_traccion_inicial` · `calc_traccion_sostenida` · `calc_transporte` · `calc_bipedestacion` · `calc_repetitivos_ms` · `calc_posturas_forzadas` · `calc_vibracion_mano_brazo` · `calc_vibracion_cuerpo_entero` · `calc_confort_termico` · `calc_estres_contacto`

**Artefactos normativos versionados [VERIFICADO — `ls evaluaciones/data/`]:** **13 archivos JSON** más un `README.md`.

| Archivo | Bytes | Fuente declarada |
|---|---:|---|
| `lmc_tablas.json` | 2.707 | Resolución MTEySS 295/2003, Anexo I |
| `empuje_inicial.json` | 3.245 | Resolución SRT 3345/2015 — Tabla 1 |
| `empuje_sostenida.json` | 4.015 | Resolución SRT 3345/2015 — Tabla 2 |
| `traccion_inicial.json` | 4.512 | Res. SRT 3345/2015 — Tabla 3, **con ajuste interno declarado (1460→140 N)** |
| `traccion_sostenida.json` | 3.909 | Resolución SRT 3345/2015 — Tabla 4 |
| `transporte_limites.json` | 2.003 | Res. SRT 3345/2015, Anexo I, Tabla 1 |
| `repetitivos_ms_limites.json` | 1.168 | Res. MTEySS 295/2003, Nivel de Actividad Manual |
| `posturas_forzadas_puntajes.json` | 1.808 | Método REBA — Hignett y McAtamney, 2000 |
| `vibracion_mano_brazo_limites.json` | 1.476 | Res. MTEySS 295/2003 **con umbral de acción interno** |
| `vibracion_cuerpo_entero_limites.json` | 1.440 | Directiva 2002/44/CE art. 3.2 + Res. MTEySS 295/2003 |
| `confort_termico_umbrales.json` | 1.527 | Res. SRT 886/2015, Planilla 2H (curvas de Fanger) |
| `bipedestacion_limites.json` | 1.697 | **Criterio interno de cribado** |
| `estres_contacto_criterios.json` | 1.924 | Res. SRT 886/2015, Planilla 2I, **extendida con matriz interna** |

> **[HALLAZGO] H-H — Son 13 artefactos normativos, no 14.**
> `ESTADO_TECNICO_COMPLETO §5.3` dice «14 archivos en `evaluaciones/data/`». El listado real contiene 14 archivos, pero **uno es `README.md`**: los artefactos normativos consumidos por el motor son **13**, uno por factor, coincidiendo con `FactorDefinition.data_files` del catálogo. La corrección importa porque el checklist de verificación exige «los 14 artefactos normativos se cargan y su SHA-256 se registra», y ese criterio nunca se cumpliría.

**Carga de datos [VERIFICADO — `evaluaciones/calculators.py:55-75`]:** doble estrategia, primero como recurso de paquete con `importlib_resources.files("evaluaciones.data")` (`:71`) y como respaldo desde el filesystem con `os.path.dirname(__file__)` (`:59`). **La segunda sobrevive al movimiento de la app; la primera contiene una ruta de paquete literal que debe actualizarse.**

### Bloque 3 — Exportaciones e informes

**Documentos en formulario oficial de la SRT.** Plantilla `exportaciones/official/templates_bin/res_srt_886_15-formulario.pdf` (251.599 bytes, 12 páginas, PDF 1.6, Carta 612×792 pt, sin AcroForm), con verificación de SHA-256 `bc0d0753943888779abd0936f6c4dc2e128766c7cf6370a4a2fb19073aad59f4` al cargarse **[VERIFICADO — `exportaciones/official/catalog.py:19-21`]**.

La técnica es **superposición**: ReportLab genera una capa transparente y `pypdf` la fusiona sobre la página oficial. **La capa base nunca se modifica**, de modo que la curva de confort de Fanger de la Planilla 2H y la escala de Borg de la 2E se conservan. Las coordenadas de las 12 páginas están en `exportaciones/official/maps/*.json` **[VERIFICADO — 12 archivos]**.

**Detalle técnico por factor.** PDF A4 propio: encabezado, estado operativo, todos los inputs con etiquetas legibles, juicio profesional, tramos de VCE, fuentes normativas con SHA-256, observaciones y volcado íntegro de `calc_data`.

**Informe profesional con LLM.** Siete apartados generados con `settings.CHAT_AI_MODEL`, con estos controles **[VERIFICADO — `exportaciones/reports/llm.py`]**:

| Control | Implementación | Línea |
|---|---|---|
| Privacidad | `CLAVES_PROHIBIDAS` de 11 claves, aplicada recursivamente por `sanitize_payload()` | `:25-31`, `:50-63` |
| Contexto mínimo | Se reconstruye sólo con razón social, área/sector, puesto y provincia | `:65-71` |
| Tope de payload | `MAX_PAYLOAD_CHARS = 24_000` | `:34` |
| Aislamiento | El agente **no** se cachea con `lru_cache`, a diferencia del chat | `:82` |
| Trazas | `RunConfig(trace_include_sensitive_data=False)` | `:96` |
| Caché económica | Por `inputs_hash`: el segundo pedido idéntico no consume tokens | `:112`, `:162` |
| Cuota | 10 informes/hora + lease anti-concurrencia | `exportaciones/reports/limits.py` |
| El modelo no decide niveles | El PDF imprime un anexo generado desde el payload, no desde el texto | `exportaciones/reports/pdf.py` |

Contenido de `CLAVES_PROHIBIDAS` **[VERIFICADO — `exportaciones/reports/llm.py:25-31`]**:

```python
CLAVES_PROHIBIDAS = frozenset({
    "nombres_trabajadores", "cuit", "direccion", "ubicacion_sintoma",
    "salud_columna", "revisado_por", "evaluacion_id", "instancia_id",
    "medida_id", "foto_montaje", "certificado_calibracion",
    "evidencia_declarada",
})
```

**Paquete ZIP.** `LEEME.txt` con los criterios aplicados + protocolo oficial completo + detalle técnico de los factores iniciados.

Rutas expuestas **[VERIFICADO — `exportaciones/urls.py`]**:

| Ruta | Nombre | Método | Controles |
|---|---|---|---|
| `/exportaciones/<id>/` | `panel` | GET | sesión + propiedad |
| `/exportaciones/<id>/oficial/protocolo-completo.pdf` | `protocolo_completo` | GET | propiedad + 60/300 s |
| `/exportaciones/<id>/oficial/<planilla_slug>.pdf` | `planilla_oficial` | GET | propiedad + 60/300 s |
| `/exportaciones/<id>/detalle/todos.pdf` | `factores_detalle_todos` | GET | propiedad + 60/300 s |
| `/exportaciones/<id>/detalle/<factor_slug>.pdf` | `factor_detalle` | GET | propiedad + 60/300 s |
| `/exportaciones/<id>/informe/<factor_slug>/` | `informe_factor` | **POST** | propiedad + CSRF + estado calculado + lease + 10/h |
| `/exportaciones/<id>/paquete.zip` | `paquete_zip` | GET | propiedad + 60/300 s |

### Bloque 4 — Ayuda contextual estática y dinámica

**33 documentos Markdown** en `static/ayuda/help_texts/` **[VERIFICADO — `ls | wc -l` → 33]**: 2 globales (`guia_para_el_usuario.md`, `guia_general.md`) y 31 de página (18 fijos + 13 derivados de `FactorDefinition.help_slug`).

El catálogo lo confirma **[VERIFICADO — `help_ai/catalog.py:6-32`]**:

```python
GLOBAL_HELP_SLUGS = ("guia_para_el_usuario", "guia_general")           # 2
PAGE_HELP_SLUGS = ( ...18 slugs fijos... ) + tuple(d.help_slug for d in FACTOR_DEFINITIONS)   # 18 + 13 = 31
```

> **[HALLAZGO] H-I — Son 33 documentos de ayuda, no 34.**
> `ESTADO_TECNICO_COMPLETO §5.5` y su tabla de CF-1 consignan «34 documentos Markdown». El conteo real es **33**, y coincide exactamente con el catálogo: 2 globales + 18 páginas fijas + 13 factores. Se corrige aquí porque el inventario de trasplante debe ser exacto.

Características **[VERIFICADO]**:

- **Versionado por SHA-256** del contenido combinado. Chat y guía comparten versión; si el contenido cambia, el cliente debe recargar (HTTP 409). `help_ai/prompts.py`.
- **Streaming SSE** sobre ASGI con latido, timeout duro y cancelación cooperativa. `help_ai/views.py:108-112`.
- **Cuotas con lease activo + contador por ventana**, sobre `django.core.cache` **[VERIFICADO — `help_ai/limits.py:24-57`]**. `acquire_chat_lease()` usa `cache.add()` como cerrojo distribuido: **con `LocMemCache` el cerrojo es por proceso y la cuota se multiplica por la cantidad de workers.**
- **Caché de agentes** con `lru_cache(maxsize=settings.CHAT_AI_AGENT_CACHE_SIZE)` por `(slug, versión)` **[VERIFICADO — `help_ai/agents.py:11-12`]**.
- El agente **declara explícitamente que no ve** los datos de la evaluación **[VERIFICADO — `help_ai/agents.py:27-32`]**.

## 3.6 Seguridad **[VERIFICADO]**

| Control | Implementación |
|---|---|
| Autenticación | `LoginRequiredMixin` / `@login_required` en todas las vistas de negocio |
| Autorización | Filtro por propietario: `get_object_or_404(Evaluacion, pk=…, usuario=request.user)` — `planillas/views.py:73,128,171,319,377,389`; `evaluaciones/views.py:37-46,681`; `exportaciones/views.py:53` |
| No enumeración | **404 en lugar de 403** para recursos ajenos |
| CSRF | Middleware estándar; el endpoint de informes es POST |
| CSP | Middleware propio con nonce por respuesta — `ergonomia_srt/middleware.py:10-59` |
| Cabeceras de descarga | `X-Content-Type-Options: nosniff`, `Cache-Control: private, no-store`, `Content-Disposition: attachment` |
| Límites de uso | Cuotas de chat, informes y descargas |
| Datos hacia el LLM | `CLAVES_PROHIBIDAS` aplicada recursivamente |
| Logs | Identificadores y métricas, nunca payloads |

**Modelo de propiedad actual: por usuario individual.** No hay noción de organización, ni de compartir una evaluación, ni de que una empresa vea las suyas. **Es la brecha funcional que la integración cierra.**

## 3.7 Calidad y pruebas **[VERIFICADO — ejecución 02/08/2026]**

```
Found 160 test(s).
Ran 160 tests in 2.081s
OK
System check identified no issues (0 silenced).
```

| Archivo | Pruebas |
|---|---:|
| `evaluaciones/tests.py` | 45 |
| `exportaciones/tests/test_official_pdf.py` | 24 |
| `exportaciones/tests/test_serializers.py` | 23 |
| `help_ai/tests.py` | **22** |
| `exportaciones/tests/test_permissions.py` | 21 |
| `exportaciones/tests/test_reports_llm.py` | 16 |
| `exportaciones/tests/test_reports_pdf.py` | 8 |
| `planillas/tests.py` | 1 |
| `core/tests.py` | 0 |

**Ninguna prueba llama al proveedor del modelo:** todas usan `patch`. La suite corre sin red y sin consumir cuota. Durante la ejecución se observaron tres mensajes de log esperados (fallo simulado de tabla REBA, timeout simulado del chat, documento de ayuda inexistente), correspondientes a casos de error deliberadamente provocados.

## 3.8 Deudas técnicas del origen

| ID | Deuda | Severidad | ¿La integración la resuelve? |
|---|---|---|---|
| **D-1** | `MEDIA_ROOT` sin configurar, con dos campos de archivo en uso | Media | ✅ **Sí** — el destino lo tiene |
| **D-2** | Propiedad por usuario, sin noción de empresa | **Alta** | ✅ **Sí** — `CompanyProfile` |
| **D-3** | Sin campos de firmantes: los recuadros salen vacíos | Media | ✅ **Sí** — `profession` + `license_number` |
| **D-4** | Los booleanos de Planilla 2 no distinguen «NO» de «sin responder» | Media | ❌ No |
| **D-5** | La interfaz gestiona una sola instancia por Planilla 2 | Media | ❌ No |
| **D-6** | `planillas` y `help_ai` sin `app_name` | Media | ✅ Se resuelve en Fase 1 |
| **D-7** | `weasyprint` instalado sin declarar | Baja | ✅ Se limpia al migrar dependencias |
| **D-8** | `LANGUAGE_CODE = 'en-us'` con interfaz en español | Baja | ✅ **Sí** — el destino usa `es-ar` |
| **D-9** | No existe el concepto de «protocolo cerrado» | Media | ❌ No |
| **D-10** | `planillas/views.py:30` importa helpers privados de `evaluaciones.views` | Baja | ❌ No |
| **D-11** | Tres artefactos con criterios internos, no tablas oficiales | **Alta (producto)** | ❌ No — requiere validación profesional |

---
# PARTE IV — ANÁLISIS DE SOLAPAMIENTO Y ELIMINACIÓN DE DUPLICACIÓN

> **Principio rector.** Cuando ambos sistemas resuelven la misma necesidad, se conserva **una sola** implementación. Si a la que se conserva le falta algo, **se la extiende**; no se mantiene la otra en paralelo. La única excepción es CF-1, que es una condición vinculante y no una duplicación.

## Cuadro resumen de las 12 decisiones

| # | Área | Se conserva | Se descarta | Extensión necesaria |
|---|---|---|---|---|
| 1 | Autenticación y usuarios | `apps.accounts` (destino) | `core` completo (origen) | 1 línea en `planillas/models.py` |
| 2 | Dashboard del profesional | `apps.dashboard` (destino) | `core.dashboard_view` como app | Vista nueva de listado + tarjeta |
| 3 | Entidad empresa / cliente | `CompanyProfile` (destino) | Nada: los campos de texto se **conservan** como respaldo histórico | FK `Evaluacion.empresa` + poblado al crear |
| 4 | Trabajadores | `CompanyWorker` (destino) | Nada: `nombres_trabajadores` se conserva | M2M opcional + derivación de texto |
| 5 | Asistente IA | **Ambos** (CF-1) | Nada | Sólo el setting del modelo |
| 6 | Agenda y seguimiento | **Ambos**, con sincronización | Nada | Señal que crea `AgendaEvent` |
| 7 | Generación de PDF | Ambos motores ReportLab | Nada | Agregar `pypdf` |
| 8 | Plantilla base y navegación | `base_dashboard.html` (destino) | `templates/base.html` del origen | Bloque `help_slug` + widget |
| 9 | Estáticos y Bootstrap | **`vendor/` local del origen** | CDN del destino (a plazo) | Migrar `base_dashboard.html` |
| 10 | Configuración del modelo de IA | `OPENAI_MODEL` (destino) como base | `CHAT_AI_MODEL` como variable independiente | `CHAT_AI_MODEL` pasa a derivar de `OPENAI_MODEL` |
| 11 | Caché | `DatabaseCache` (origen) | `LocMemCache` implícito del destino | `createcachetable` en despliegue |
| 12 | Content Security Policy | Middleware del origen | Nada | **Remediar el frontend del destino primero** |

---

## Área 1 — Autenticación y usuarios

### Qué hace cada proyecto

| | ErgoSolutions | ErgoApp SRT 886 |
|---|---|---|
| Modelo | `accounts.CustomUser` sobre `AbstractBaseUser + PermissionsMixin` | `django.contrib.auth.models.User` estándar |
| Identificador | `USERNAME_FIELD = "email"` | `username` |
| Tipos de usuario | **3**: `professional`, `trainee`, `company` | Ninguno |
| Backends | **3**: `ProfessionalBackend`, `CuilEmailBackend`, `ModelBackend` | Sólo `ModelBackend` |
| Campos profesionales | `profession`, `license_number`, `dni`, `username` | Ninguno |
| Registro | Tres flujos diferenciados (`/auth/`, `/empresa/auth/`, `/acceso/`) | `UserCreationForm` estándar en `core/views.py:14-28` |
| Decoradores | `professional_required`, `company_required`, `backoffice_required`, `trainee_required` | `@login_required` |
| Vistas | `apps/accounts/views_professional.py`, `views_company.py`, `views.py` | `core/views.py:14-32` + `auth_views.LoginView` |

### Decisión

**Se conserva `apps.accounts` íntegramente. Se descarta por completo la autenticación de `core`.**

No hay discusión posible: el destino tiene un sistema de identidad estrictamente superior —tres tipos de usuario, tres backends, campos profesionales, tres flujos de registro— y el origen tiene el `User` estándar de Django sin ninguna extensión. Además, `AUTH_USER_MODEL` sólo puede haber uno por proyecto.

### Qué se le extiende a lo conservado

**Nada.** `apps.accounts` no necesita ningún campo nuevo para soportar el módulo 886. Sus campos `profession` y `license_number` ya cubren lo que el módulo necesita para los firmantes.

### Qué hay que adaptar en el origen

Una sola línea **[VERIFICADO — `planillas/models.py:4,9`]**:

```python
# ANTES — planillas/models.py:4,9
from django.contrib.auth.models import User
...
usuario = models.ForeignKey(User, on_delete=models.CASCADE)

# DESPUÉS
from django.conf import settings
...
usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
```

`evaluaciones/models.py:48-49`, `exportaciones/models.py:71-72` y `exportaciones/models.py:111-112` **ya usan `settings.AUTH_USER_MODEL` correctamente** **[VERIFICADO]**. Sólo `planillas` requiere el cambio.

### Impacto de la decisión

- **No se migran usuarios**: los de ErgoApp son ficticios.
- **No se genera migración**: verificado en H-G. El estado de migraciones ya es swappable.
- Las vistas del módulo que hoy hacen `usuario=request.user` siguen funcionando sin cambios, porque `request.user` pasa a ser un `CustomUser`.
- `core/templates/core/login.html` y `core/templates/core/registro.html` se descartan.
- El campo `user.username` que usa `templates/base.html:26` del origen (`Hola, {{ user.username }}`) desaparece con esa plantilla; el destino usa `{{ request.user.display_name }}`.
- **Punto de atención [PROPUESTA]:** `CustomUser.username` es `null=True, blank=True` para los trainees. Cualquier código del módulo 886 que asuma `username` no vacío debe revisarse. La búsqueda no encontró ninguno fuera de `templates/base.html`, que se descarta.

---

## Área 2 — Dashboard del profesional

### Qué hace cada proyecto

| | ErgoSolutions | ErgoApp SRT 886 |
|---|---|---|
| Punto de entrada | `/dashboard/` → `apps/dashboard/views.py:30 home()` | `/` → `core/views.py:37 dashboard_view()` |
| Despacho | Por tipo de usuario: `_professional_dashboard()` / `_company_dashboard()` (`:34-36`) | Único |
| Contenido | Stats + tarjetas de herramientas | **Listado de evaluaciones** |
| Búsqueda | — | ✅ 6 campos: razón social, CUIT, provincia, dirección, área/sector, puesto (`core/views.py:49-56`) |
| Filtros | — | ✅ Provincia, fecha desde, fecha hasta (`:59-69`) |
| Ordenamiento | — | ✅ 6 opciones con lista blanca (`:72-81`) |
| Paginación | ❌ (hallazgo N13 del destino) | ✅ 20 por página (`:84-86`) |
| Optimización de consulta | — | ✅ `select_related` + `Prefetch` (`:40-44`) |

### Decisión

**Se conserva `apps.dashboard` como punto de entrada. Se descarta `core` como aplicación, pero se preserva íntegramente la lógica de `core.dashboard_view` reimplantándola como una vista nueva dentro del módulo 886.**

El razonamiento es que se trata de dos cosas distintas que comparten el nombre «dashboard»:

- El **dashboard del destino** es el portal del profesional: el menú de herramientas del que cuelgan Capacitaciones y —a partir de esta integración— Evaluaciones.
- El **dashboard del origen** es el **listado de evaluaciones ergonómicas**: la pantalla de trabajo del módulo.

No compiten: se anidan. El listado del origen pasa a ser la pantalla de aterrizaje del módulo, un nivel por debajo del portal.

### Qué se le extiende a lo conservado

**[PROPUESTA]** Se agrega a `apps.dashboard`:

1. La tarjeta «Evaluaciones» activada, enlazando a `ergonomia_886:evaluacion_list` (§7.7).
2. Una entrada de navegación «Evaluaciones» en `base_dashboard.html`, junto a «Capacitaciones».
3. Opcionalmente, una cuarta stat en el panel del profesional: cantidad de evaluaciones ergonómicas.

Y se crea, dentro del módulo:

```
apps/ergonomia_886/planillas/views.py :: evaluacion_list_view()
```

que **preserva línea por línea** la lógica de `core/views.py:37-106` —búsqueda de 6 campos, filtro de provincia, filtros de fecha, lista blanca de ordenamientos, paginación de 20, `select_related` + `Prefetch`— cambiando únicamente:

- el filtro de propiedad, que pasa a ser mixto por `user_type` (§4.3);
- el template, que pasa a extender `base_dashboard.html`;
- la app en la que vive, que pasa a ser `planillas` en lugar de `core`.

**Por qué en `planillas` y no en `apps.dashboard`:** porque consulta `Evaluacion`, `Planilla1` y sus filtros son del dominio del protocolo. Ponerla en `apps.dashboard` obligaría a esa app a importar modelos del módulo 886, invirtiendo la dependencia y haciendo el módulo no desmontable.

### Qué se descarta

- `core/urls.py` completo (6 rutas).
- `core/views.py:14-32` — `registro_view` y `logout_view`.
- `core/templates/core/login.html`, `registro.html`.
- `core/apps.py`, `core/admin.py`, `core/models.py` (sin modelos), `core/tests.py` (0 pruebas).

Se preservan, reimplantados: `core/views.py:37-106` (`dashboard_view`), `core/views.py:108-118` (`eliminar_evaluacion_view`) y `core/templates/core/dashboard.html` como base del nuevo template.

### Impacto de la decisión

- La app `core` **desaparece**. No se registra en `INSTALLED_APPS`. No tiene migraciones que aplicar (no tiene modelos).
- Las 7 referencias `{% url 'core:dashboard' %}` y las 4 restantes de `core:*` en templates del origen deben reescribirse **[VERIFICADO — inventario en §6.3]**.
- Los 4 `redirect('core:...')` de `core/views.py` desaparecen con el archivo.
- `core/tests.py` tiene 0 pruebas: **descartarlo no reduce la cobertura**. El total sigue siendo 160.
- **Ganancia colateral:** la paginación que el hallazgo N13 del destino reclama para sus listados llega ya implementada en el módulo, y su patrón puede replicarse.

---

## Área 3 — Entidad empresa / cliente

### Qué hace cada proyecto

| | ErgoSolutions | ErgoApp SRT 886 |
|---|---|---|
| Entidad | `CompanyProfile`, modelo dedicado | Ninguna: campos de texto en cada `Evaluacion` |
| Razón social | `razon_social` `CharField(300)` | `razon_social` `CharField(255)` |
| CUIT | `cuit` `CharField(20)` **unique** | `cuit` `CharField(13)` sin restricción |
| Domicilio | `domicilio` `CharField(400)` + `localidad` | `direccion_establecimiento` `CharField(255)` |
| Provincia | `provincia` `CharField(100)` | `provincia` `CharField(100)` |
| Actividad | `rubro` `CharField(200)` | `ciiu` `CharField(10)` |
| Identidad | `OneToOne` con `CustomUser(user_type='company')` | — |
| Reutilización | Una empresa, N relaciones | **Se retipea en cada evaluación nueva** |

### Decisión

**Se conserva `CompanyProfile` como entidad canónica de empresa. Se le agrega a `Evaluacion` una clave foránea hacia ella. Y —esto es lo importante— NO se descartan los campos de texto de `Evaluacion`.**

Esta es la única de las 12 áreas donde la regla de «una sola implementación» se aplica con una excepción deliberada y fundamentada.

### Por qué se conservan los campos de texto

Porque **una planilla oficial firmada es un documento legal que debe reflejar los datos vigentes al momento del relevamiento, no los actuales de la empresa.**

Si el domicilio del establecimiento se leyera por `evaluacion.empresa.domicilio`, entonces el día que la empresa mude su planta y actualice su perfil, **todas las planillas históricas cambiarían de domicilio retroactivamente**. Un protocolo presentado ante la ART en marzo pasaría a declarar una dirección donde el relevamiento nunca ocurrió. Eso no es una inconsistencia estética: es una falsedad documental.

Por lo tanto los campos de texto no son duplicación: son **respaldo histórico del documento emitido**, y la FK es la vinculación operativa. Son dos cosas semánticamente distintas que casualmente contienen el mismo valor en el momento de la creación.

Nótese además que esto es **coherente con CF-5**: si el sistema no puede afirmar lo que el profesional no respondió, tampoco puede afirmar un domicilio que el relevamiento no registró.

### Qué se le extiende a lo conservado

**[PROPUESTA]** Sobre `planillas.Evaluacion`:

```python
class Evaluacion(models.Model):
    # --- Vinculación operativa (nueva) -------------------------------------
    empresa = models.ForeignKey(
        "company.CompanyProfile",
        on_delete=models.PROTECT,
        related_name="evaluaciones_ergonomicas",
        null=True, blank=True,
        verbose_name="Empresa evaluada",
        help_text="Empresa registrada en la plataforma. Al seleccionarla se "
                  "copian sus datos a los campos del documento.",
    )
    usuario = models.ForeignKey(              # se CONSERVA el nombre — ver más abajo
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="evaluaciones_ergonomicas",
        verbose_name="Profesional responsable",
    )

    # --- Respaldo histórico del documento emitido (se conservan) -----------
    # Se pueblan desde `empresa` al crear la evaluación y NO se re-sincronizan.
    # Una planilla firmada no debe cambiar si la empresa actualiza su perfil.
    razon_social = models.CharField(max_length=255)
    cuit = models.CharField(max_length=13)
    direccion_establecimiento = models.CharField(max_length=255)
    provincia = models.CharField(max_length=100)
    ciiu = models.CharField(max_length=10, blank=True, null=True)
```

`on_delete=models.PROTECT` es deliberado: borrar una empresa que tiene protocolos emitidos debe fallar, no arrastrarlos.

`null=True, blank=True` también: permite que un profesional evalúe una empresa que **no** es usuaria de la plataforma, tipeando los datos como hoy. Es el caso de uso mayoritario al principio y no se puede romper.

**[PROPUESTA]** Sobre el formulario de creación, en `planillas/forms.py`:

- Si el usuario es `company`: la empresa se fija a su propio perfil y los cuatro campos se rellenan y muestran en solo lectura.
- Si el usuario es `professional`: se ofrece un selector de empresas vinculadas más la opción «Otra (cargar manualmente)». Al elegir una, los cuatro campos se prellenan y quedan editables —el profesional puede corregir el domicilio de una sucursal específica.

### Qué se descarta

**Nada.** Es la particularidad de esta área.

`ciiu` no tiene equivalente en `CompanyProfile` y **no debe mapearse contra `rubro`**: CIIU es un código de clasificación industrial de hasta 10 caracteres y `rubro` es texto libre de 200. Se conserva `ciiu` como campo propio de la evaluación.

### Impacto de la decisión

- Requiere **una migración nueva** en `planillas`: agregar el campo `empresa`. Sobre tablas vacías es trivial.
- Habilita el filtro por empresa del Área 2 y la agenda del Área 6.

#### Decisión sobre el nombre del campo `usuario`

Se evaluó renombrar `usuario` → `profesional`, que sería semánticamente más preciso en un sistema con tres tipos de usuario. **Se decide conservar `usuario`.**

El motivo es el coste real medido. El campo aparece **38 veces** en el código del origen, sin contar migraciones **[VERIFICADO]**:

| Ubicación | Apariciones | Naturaleza |
|---|---:|---|
| `core/views.py` | 3 | Se descarta con el archivo |
| `planillas/views.py` | 6 | Filtros de propiedad |
| `evaluaciones/views.py` | 2 | Uno es el lookup relacional `evaluacion__usuario=user` (`:49`) |
| `exportaciones/views.py` | 3 | Filtros de propiedad y auditoría |
| `planillas/tests.py`, `evaluaciones/tests.py` | 2 | Construcción de fixtures |
| `exportaciones/tests/*` | **22** | Construcción de fixtures en las 5 suites |
| **Total** | **38** | |

Renombrar obliga a tocar **22 puntos dentro de las suites de prueba** sin ningún beneficio funcional, e introduce una clase de error particularmente incómoda: un `FieldError` en tiempo de consulta, no de import, que sólo se manifiesta al ejecutar la rama afectada. Dado que la Fase 2 usa «las 160 pruebas pasan» como criterio de aceptación, contaminar las suites con un cambio cosmético degrada la señal de esa verificación.

El `verbose_name="Profesional responsable"` aporta la claridad semántica buscada sin ninguno de esos costes. Si el renombrado se considera necesario, corresponde a una tarea posterior e independiente, con la integración ya estabilizada.

---

## Área 4 — Trabajadores

### Qué hace cada proyecto

| | ErgoSolutions | ErgoApp SRT 886 |
|---|---|---|
| Entidad | `CompanyWorker`, modelo relacional | `Planilla1.nombres_trabajadores`, `TextField` |
| Identidad | FK a `CustomUser(user_type='trainee')` | Texto libre |
| Legajo | `employee_code` | — |
| Sector | `department` | `Planilla1.area_sector` (de la evaluación, no del trabajador) |
| Puesto | `position` | `Planilla1.puesto_trabajo` (íd.) |
| Alta / baja | `start_date`, `end_date`, `is_active` | — |
| Unicidad | Constraint `(company, worker)` | — |
| Historial de capacitación | ✅ vía `QuizAttempt`, `Certificate` | — |

### Decisión

**Se conserva `CompanyWorker` como entidad canónica de trabajador. Se conserva TAMBIÉN `nombres_trabajadores` como respaldo histórico, por el mismo criterio del Área 3.**

### Qué se le extiende a lo conservado

**[PROPUESTA]** Sobre `Planilla1`, una relación opcional:

```python
class Planilla1(models.Model):
    evaluacion = models.OneToOneField(Evaluacion, on_delete=models.CASCADE, primary_key=True)

    # --- Vinculación estructurada (nueva, opcional) ------------------------
    trabajadores = models.ManyToManyField(
        "company.CompanyWorker",
        blank=True,
        related_name="planillas_ergonomicas",
        verbose_name="Trabajadores relevados",
        help_text="Trabajadores de la nómina alcanzados por este relevamiento.",
    )

    # --- Respaldo histórico del documento (se conserva) --------------------
    # Si `trabajadores` está poblado, este campo se deriva de él al guardar;
    # si no, el profesional lo tipea. La planilla oficial imprime SIEMPRE
    # este campo, nunca la relación.
    nombres_trabajadores = models.TextField(blank=True)
```

La regla de derivación **[PROPUESTA]**: al guardar, si `trabajadores` tiene elementos y `nombres_trabajadores` está vacío, se puebla con los nombres de la relación. Si el profesional ya escribió algo, **no se sobrescribe**: el texto tipeado gana siempre, porque puede incluir trabajadores que no están en la nómina de la plataforma.

**Por qué la exportación debe leer el `TextField` y no la relación:** por el mismo argumento del Área 3. Si un trabajador se da de baja o cambia de sector, la planilla firmada no puede cambiar. Además, es la única forma de respetar CF-5 en el caso de un relevamiento sobre personal no registrado en la plataforma.

`nro_trabajadores` se conserva como campo independiente y **no** se deriva de `trabajadores.count()`: el formulario oficial pide el número de trabajadores del puesto, que puede ser mayor que el de los relevados nominalmente.

### Qué se descarta

**Nada.**

### Impacto de la decisión

- Requiere una migración nueva en `planillas` (tabla intermedia M2M). Trivial sobre base vacía.
- **Introduce una dependencia de `planillas` hacia `apps.company`.** Es aceptable y ya existe por el Área 3, pero conviene que sea **la única dirección**: `apps.company` no debe importar nada del módulo 886.
- Habilita la oportunidad O-6: cruzar el resultado de un factor con el historial de capacitación de los trabajadores de ese puesto.
- **Riesgo [PROPUESTA]:** los trabajadores están vinculados a una `CompanyProfile`, no a una `Evaluacion`. Si la evaluación no tiene `empresa` (caso de empresa no usuaria), el selector de trabajadores debe quedar vacío y el campo de texto es el único camino. El formulario debe manejar ese caso explícitamente.

---

## Área 5 — Asistente IA

> ⛔ **Esta área está gobernada por CF-1, que es una condición vinculante. No admite discusión de diseño.**

### Qué hace cada proyecto

| Dimensión | `help_ai` (ErgoApp 886) | `ergobot_ai` (ErgoSolutions) |
|---|---|---|
| Volumen | **1.052 líneas**, 13 archivos **[VERIFICADO]** | **164 líneas**, 9 archivos **[VERIFICADO]** |
| Propósito | Asistencia **de pantalla** sobre el protocolo SRT 886/15 | Asistente **docente** sobre módulos de capacitación |
| Fuente de conocimiento | **33 documentos Markdown** en el filesystem, uno por pantalla | Contenido de `TrainingModule` consultado en base |
| Construcción del contexto | Estática por slug de pantalla (`help_ai/prompts.py`) | Dinámica desde el ORM (`apps/ergobot_ai/agents.py:18`) |
| Versionado del contexto | **SHA-256** del contenido combinado; HTTP 409 si cambió | Ninguno |
| Transporte | Streaming SSE con latido, timeout duro y cancelación | Streaming SSE simple |
| Cuotas | **Lease activo + contador por ventana** (`help_ai/limits.py:24-57`) | Ninguna |
| Validación de entrada | Normalización de hilo, topes de longitud, roles permitidos | Mínima (`views.py:16-33`) |
| Caché de agentes | `lru_cache` por `(slug, versión)` (`agents.py:11`) | Ninguna |
| Política de datos | Declara explícitamente que **no ve** los datos de la evaluación | No aplica |
| Usuario objetivo | Profesional de Higiene y Seguridad | Trabajador en capacitación |
| Pruebas | **22** | **0** (`apps/ergobot_ai/tests.py`, 3 líneas) |

### Decisión

**Ambas se conservan como aplicaciones separadas e independientes. Está prohibido fusionarlas, reemplazar una por la otra, o unificar sus vistas, agentes o prompts.**

### Por qué no son duplicación

Comparten proveedor (`openai-agents`) y protocolo de transporte (SSE). Todo lo demás difiere: propósito, usuario, fuente de conocimiento, arquitectura de contexto y garantías.

La diferencia decisiva es la **arquitectura de contexto**, y es la razón por la que la fusión es técnicamente imposible, no sólo inconveniente:

- `help_ai` lee su contexto de **archivos Markdown estáticos** identificados por slug de pantalla, y lo versiona por SHA-256 para garantizar que el asistente responda sobre exactamente la misma versión de la guía que el usuario tiene abierta.
- `ergobot_ai` construye su contexto **dinámicamente desde la base de datos**, con `await TrainingModule.objects.filter(slug=...).afirst()` **[VERIFICADO — `apps/ergobot_ai/agents.py:18`]**.

No hay un denominador común: un contexto que vive en la base no puede versionarse por SHA-256 de archivo, y un contexto que vive en archivos no puede reflejar la edición de un módulo de capacitación.

### Consecuencias concretas de fusionarlas

1. **Se perdería el versionado por SHA-256**, que es lo que garantiza que el asistente no contradiga la documentación que el profesional está leyendo. En un dominio normativo eso es inaceptable.
2. **Se perderían las cuotas y el control de concurrencia.** `help_ai/limits.py` es además el patrón que `exportaciones/reports/limits.py` replica para los informes. Degradarlo debilita ambos.
3. **Se romperían las 22 pruebas de `help_ai`** y, por dependencia de patrón, la coherencia de las 16 de `test_reports_llm.py`.

En sentido inverso, reemplazar `ergobot_ai` por `help_ai` tampoco sirve: `ergobot_ai` sería incapaz de reflejar el contenido editable de los módulos de capacitación.

### Qué SÍ se unifica

**Únicamente el setting del modelo de lenguaje.** Ver Área 10.

### Impacto de la decisión

- `INSTALLED_APPS` del destino tendrá **dos** apps de IA: `apps.ergobot_ai` y `apps.ergonomia_886.help_ai`.
- Ninguna importa código de la otra. **[VERIFICADO]** hoy `help_ai` sólo importa de `evaluaciones.catalog` (`help_ai/catalog.py:3`), y `ergobot_ai` sólo de `apps.training.models`.
- Conviven en prefijos de URL distintos: `/ai/` para el chatbot docente y `/evaluacion-ergonomica/ayuda/` para la ayuda del protocolo (§7.4).
- **Coste asumido conscientemente:** dos implementaciones de streaming SSE y dos definiciones de agente. Es el precio de dos productos distintos, y CF-1 lo declara aceptable de forma explícita.

### ⚠️ Conflicto detectado entre CF-1 y B3

> **[HALLAZGO] H-J — El criterio de verificación de CF-1 «las 22 pruebas de `help_ai` pasan sin modificación» es incompatible con el bloqueante B3.**
>
> B3 exige agregar `app_name = "help_ai"` a `help_ai/urls.py`. Pero `help_ai/tests.py` invoca los nombres de URL sin namespace en **9 puntos** **[VERIFICADO]**:
>
> ```
> help_ai/tests.py:143   reverse("chat_ai", kwargs={"slug": slug})
> help_ai/tests.py:147   reverse("help_guide", kwargs={"slug": slug})
> help_ai/tests.py:190   reverse("chat_ai", kwargs={"slug": "lmc"})
> help_ai/tests.py:202   reverse("chat_ai", kwargs={"slug": "slug-inexistente"})
> help_ai/tests.py:213   reverse("help_guide", kwargs={"slug": "lmc"})
> help_ai/tests.py:227   reverse("chat_ai", kwargs={"slug": "lmc"})
> help_ai/tests.py:247   reverse("help_guide", kwargs={"slug": "lmc"})
> help_ai/tests.py:257   reverse("chat_ai", kwargs={"slug": "lmc"})
> help_ai/tests.py:483   reverse("chat_ai", kwargs={"slug": "lmc"})
> ```
>
> En cuanto exista `app_name`, esos 9 `reverse()` lanzan `NoReverseMatch`. **Es imposible cumplir literalmente ambas condiciones.**
>
> **Resolución propuesta.** La intención de CF-1 es proteger la **semántica y la cobertura** de las pruebas —que sigan siendo 22, que sigan cubriendo lo mismo, que no se relajen ni se borren para acomodar una fusión—, no su texto literal. La adaptación de `reverse("chat_ai")` a `reverse("help_ai:chat_ai")` es un cambio mecánico impuesto por B3, ajeno al espíritu de CF-1.
>
> **Se reformula el criterio de verificación así:**
>
> - ❌ ~~«Las 22 pruebas de `help_ai` pasan sin modificación»~~
> - ✅ **«Las 22 pruebas de `help_ai` pasan. Los únicos cambios admitidos en `help_ai/tests.py` son la calificación con namespace de los 9 `reverse()` y la actualización de rutas de import. Ninguna aserción, ningún `patch`, ningún caso de prueba y ninguna cuota puede modificarse ni eliminarse.»**

> **Decisión de Arquitectura DA-2.9 — ejecución 03/08/2026.** Al montar las
> URLs se comprobó que dos aserciones literales todavía exigían `/ai/chat/` y
> `/ai/guide/`. Mantenerlas requeriría volver a montar `help_ai` bajo `/ai/`,
> violando CF-1 y la decisión de prefijos separados. Se acota la excepción a
> reemplazar esas dos expectativas por el prefijo público nuevo, actualizar
> la expectativa ASGI a `config.asgi.application`, actualizar los targets de
> `patch` como rutas de import diferidas y agregar
> el email requerido por `CustomUser` al fixture. Casos, cuotas y todas las
> demás aserciones permanecen intactos.
>
> El diff de `help_ai/tests.py` debe revisarse explícitamente contra DA-2.9 en
> la Fase 2. Cualquier cambio fuera de namespaces/imports, esas tres
> expectativas de integración y el email del fixture incumple CF-1.

> **Decisión de Arquitectura DA-2.12 — ejecución 03/08/2026.** El ejemplo de
> `checks.py` recolectaba 47 rutas (`26 + 12 + 9`) pese a declarar 48: omitía
> el paquete `apps.ergonomia_886.evaluaciones.data` usado como cadena por
> `calculators.py`. El chequeo ejecutado agrega explícitamente ese paquete y
> verifica 48 rutas reales. Además, la búsqueda textual propuesta para CF-1
> se disparaba contra el comentario vinculante de `help_ai/apps.py` que
> documenta la propia separación. Se reemplaza por análisis AST de imports
> estáticos y llamadas literales a `import_string()`: detecta acoplamiento de
> código, que es la prohibición de CF-1, sin penalizar comentarios ni tests
> que documenten la condición.

> **Decisión de Arquitectura DA-2.13 — ejecución 03/08/2026.** La compuerta de
> Fase 2 exige las 196 pruebas en verde, pero dos pruebas de `help_ai` ya
> exigían el CSP y la ausencia global de CDN que el plan ubicaba en Fase 6.
> Como la Fase 6 se declara independiente y el criterio de fase no puede
> relajarse, se adelanta el mínimo seguro: middleware CSP bloqueante portado
> sin extensión, seis referencias CDN reemplazadas por `vendor/`, nonce en
> los cinco scripts inline y tres handlers HTML reemplazados por listeners.
> La Fase 6 conserva la extracción de scripts, QA visual de 63 pantallas,
> modo Report-Only, observación y activación final. También se adaptan rutas
> de paquete, targets de `patch`, URLs `core:` y fixtures al `CustomUser` real;
> ninguna aserción se elimina ni se relaja.

---

## Área 6 — Agenda y seguimiento

### Qué hace cada proyecto

| | ErgoSolutions | ErgoApp SRT 886 |
|---|---|---|
| Entidad | `AgendaEvent` | `SeguimientoMedida` |
| Alcance | Genérico, cualquier entidad | Específico: una medida correctiva |
| Propietario | `CompanyProfile` | `MedidaEspecifica` (1:1) |
| Fechas | `start_at`, `due_at` (obligatoria) | `fecha_impl_admin`, `fecha_impl_ing`, `fecha_cierre` |
| Estado | `pending`/`completed`/`overdue`/`cancelled` | Implícito: `fecha_cierre` poblada o no |
| Prioridad | `low`…`urgent` | `nivel_riesgo` 1–3 |
| Vínculo genérico | **`related_object_type` + `related_object_id`** | — |
| Tipo | Enum con **`evaluation_due` ya presente** | — |
| Vista | `/dashboard/empresa/agenda/` con filtros | Formulario de Planilla 4 |
| Automatización | `generate_cert_expiry_events` (comando) | — |

### Decisión

**Se conservan ambas. No son duplicación: son capas distintas del mismo hecho.**

`SeguimientoMedida` es **el registro documental de la Planilla 4 del protocolo oficial**. Sus tres fechas son campos del formulario de la SRT y se imprimen en el PDF oficial. No puede reemplazarse por un `AgendaEvent` sin romper CF-6 y la correspondencia campo a campo con el formulario.

`AgendaEvent` es **la herramienta operativa de gestión** de la empresa: la vista de calendario donde el usuario ve qué le vence.

La duplicación real no está en los modelos, sino en que hoy **el vencimiento de una medida correctiva no aparece en la agenda**. Eso se resuelve con sincronización, no con fusión.

### Qué se le extiende a lo conservado

**[PROPUESTA]** Una señal `post_save` sobre `SeguimientoMedida` que proyecta el compromiso hacia la agenda:

```python
# apps/ergonomia_886/planillas/signals.py   [PROPUESTA]

@receiver(post_save, sender=SeguimientoMedida)
def sincronizar_agenda(sender, instance, **kwargs):
    """Proyecta la fecha comprometida de una medida hacia la agenda de la empresa.

    La agenda es una vista operativa: no es fuente de verdad. La autoridad
    documental sigue siendo SeguimientoMedida, que es lo que imprime la
    Planilla 4 oficial.
    """
    evaluacion = instance.medida_especifica.planilla3.evaluacion
    empresa = evaluacion.empresa
    if empresa is None:
        return  # evaluación de empresa no usuaria: no hay agenda donde colgarla

    fecha = instance.fecha_impl_ing or instance.fecha_impl_admin
    if fecha is None:
        return

    completado = instance.fecha_cierre is not None

    AgendaEvent.objects.update_or_create(
        company=empresa,
        related_object_type="ergonomia_886.SeguimientoMedida",
        related_object_id=str(instance.pk),
        defaults={
            "title": f"Medida correctiva — {instance.medida_especifica.descripcion[:80]}",
            "event_type": AgendaEvent.EventType.EVALUATION_DUE,
            "due_at": _a_datetime_local(fecha),
            "status": (AgendaEvent.EventStatus.COMPLETED if completado
                       else AgendaEvent.EventStatus.PENDING),
            "priority": _prioridad_por_nivel(instance.nivel_riesgo),
            "assigned_professional": evaluacion.profesional,
            "description": instance.medida_especifica.observaciones or "",
        },
    )
```

Puntos de diseño deliberados:

- **`update_or_create` con clave natural** `(company, related_object_type, related_object_id)`: reeditar la Planilla 4 actualiza el evento, no lo duplica. Es el mismo patrón que ya usa `generate_cert_expiry_events` **[VERIFICADO — `apps/company/management/commands/generate_cert_expiry_events.py:50-56`]**.
- **`event_type` es `EVALUATION_DUE`**, que ya existe en el enum **[VERIFICADO — `apps/company/models.py:210`]**. No hay que agregar nada al modelo del destino.
- **La dirección es una sola:** la agenda refleja el protocolo, nunca al revés. Marcar completado un `AgendaEvent` **no** escribe `fecha_cierre`, porque eso sería que la agenda modifique un documento oficial. La vista de agenda debe enlazar a la Planilla 4 para que el cierre se registre donde corresponde.
- **`if empresa is None: return`** evita el caso de evaluación sobre empresa no usuaria.
- El mapeo `nivel_riesgo` → `priority` **[PROPUESTA]**: 1 Tolerable → `low`, 2 Moderado → `high`, 3 No Tolerable → `urgent`.

### Qué se descarta

**Nada.**

### Impacto de la decisión

- **Es la integración de mayor valor de negocio de todas.** El profesional ve el vencimiento de las medidas correctivas ergonómicas en la misma agenda que los vencimientos de capacitación.
- No requiere migración: usa campos existentes de `AgendaEvent`.
- **Riesgo [PROPUESTA]:** las señales `post_save` son difíciles de razonar y de testear. Debe cubrirse con pruebas propias: creación, actualización, cierre, y el caso `empresa is None`. Si se prefiere evitar señales, la alternativa es llamar a la función explícitamente desde `Planilla4UpdateView.form_valid()` (`planillas/views.py:347`), que es más rastreable. **Recomendación: la llamada explícita desde la vista**, por trazabilidad.
- Se agrava el hallazgo N9 del destino: el valor `overdue` del enum de `AgendaEvent` no lo escribe nadie. Conviene resolverlo en la misma tanda.

---

## Área 7 — Generación de PDF

### Qué hace cada proyecto

| | ErgoSolutions | ErgoApp SRT 886 |
|---|---|---|
| Motor | ReportLab 4.4.9 | ReportLab 4.5.1 + **`pypdf` 6.14.2** |
| Uso | Certificados de capacitación; planilla de asistencia presencial | Planillas oficiales, detalle técnico, informes, resumen del wizard |
| Técnica | Generación desde cero | **Superposición** sobre PDF oficial |
| Tamaño | A4 | Carta 612×792 pt (oficial) y A4 (propios) |
| Fusión de PDF | ❌ no la necesita | ✅ `pypdf` |

### Decisión

**Se conservan ambos usos. No hay duplicación funcional: resuelven problemas distintos con la misma biblioteca.**

Unificar sería un error: los certificados son documentos propios de diseño libre, y las planillas oficiales son superposición sobre un PDF de terceros cuya integridad está protegida por CF-6.

### Qué se le extiende a lo conservado

Una línea en `requirements.txt`:

```
pypdf>=5.0,<7.0
```

**[VERIFICADO]** `pypdf` está instalado en el venv del origen (6.14.2) y **ausente** del venv del destino. Sin él, la generación de planillas oficiales falla en tiempo de import.

Conviene además declarar `pillow`, hoy instalada en ambos venvs y ausente de ambos `requirements.txt` (hallazgo N8 del destino).

### Qué se descarta

**Nada del código.** Sí se descarta `weasyprint` (deuda D-7), instalada en el venv del origen, no declarada y no usada en ninguna parte.

### Impacto de la decisión

- El destino pasa a tener dos familias de generación de PDF conviviendo. Es aceptable: comparten biblioteca, no comparten código.
- **[PROPUESTA] Oportunidad no explorada:** el destino imprime la firma del profesional de forma fija en los certificados (hallazgo H20 del destino: «firma hardcodeada»). El módulo 886 aporta el patrón correcto —leer `profession` y `license_number` del `CustomUser`— que resolvería esa deuda. Queda registrado, fuera del alcance de esta integración.

---

## Área 8 — Plantilla base y navegación

### Qué hace cada proyecto

| | ErgoSolutions | ErgoApp SRT 886 |
|---|---|---|
| Plantillas base | `base.html` (3 bloques), `base_dashboard.html`, `base_landing.html` | `templates/base.html` única |
| Bloques de `base.html` | `title`, `extra_head`, `content` | `title`, `content`, **`help_slug`** |
| Bloques de `base_dashboard.html` | `title`, `extra_css`, `content`, `extra_js` | — |
| Navegación | Navbar con Dashboard, Capacitaciones, Nómina, Agenda + dropdown de usuario | Navbar con marca, saludo y logout |
| Widget de ayuda | ❌ | ✅ Botón flotante + offcanvas con pestañas Guía y Chat (`base.html:49-113`) |
| Tema | Oscuro (`data-bs-theme="dark"`) | Claro (por defecto de Bootstrap) |
| Templates que extienden | — | 10 extienden `base.html` directamente **[VERIFICADO]** |

### Decisión

**Se conserva `base_dashboard.html` del destino como plantilla base del módulo. Se descarta `templates/base.html` del origen. Se le trasplanta a `base_dashboard.html` el bloque `help_slug` y el widget de ayuda.**

El módulo 886 es una herramienta del backoffice del profesional. Debe verse y navegarse como el resto del backoffice: mismo navbar, mismo tema oscuro, mismo dropdown de usuario, mismo footer. Mantener dos identidades visuales dentro del mismo dominio sería exactamente la duplicación que este trabajo busca eliminar.

### Qué se le extiende a lo conservado

**[PROPUESTA]** Sobre `templates/base_dashboard.html`:

1. **Bloque `help_slug`**, con valor por defecto vacío:

```django
{% block extra_js %}{% endblock %}

{% if help_slug_activo %}
  {% include "ergonomia_886/_help_widget.html" %}
{% endif %}
```

2. **El widget de ayuda extraído a un `include`** en lugar de vivir en la base. Así sólo se renderiza en las pantallas del módulo 886 y no aparece en Capacitaciones, Nómina ni Agenda, donde no tendría contenido que mostrar.

**Por qué un `include` condicional y no un bloque en la base:** porque el widget consulta `{% url 'help_guide' %}` y `{% url 'chat_ai' %}`, que sólo existen si el módulo está instalado. Ponerlo incondicionalmente en `base_dashboard.html` acoplaría el layout global del destino al módulo 886, impidiendo desmontarlo.

3. **Entrada de navegación** «Evaluaciones» en el navbar, visible para `professional` y `company`, junto a «Capacitaciones».

### Qué hay que adaptar en el origen

Los **10 templates** que extienden `base.html` directamente **[VERIFICADO]**:

```
core/dashboard.html          → se reimplanta como planillas/evaluacion_list.html
core/login.html              → se descarta
core/registro.html           → se descarta
planillas/crear_evaluacion.html
planillas/detalle_evaluacion.html
planillas/planilla1_form.html
planillas/planilla2_structured_form.html
planillas/planilla3_form.html
planillas/planilla4_form.html
evaluaciones/factor_form_base.html      ← del que cuelgan 13 templates de factor
evaluaciones/wizard_resumen.html
exportaciones/panel_exportacion.html
```

Cada uno pasa de `{% extends "base.html" %}` a `{% extends "base_dashboard.html" %}`, y su contenido de `{% block content %}` se mantiene sin cambios.

**Los 13 formularios de factor no requieren tocarse:** extienden `evaluaciones/factor_form_base.html`, de modo que basta cambiar esa única plantilla intermedia **[VERIFICADO]**.

### Qué se descarta

- `templates/base.html` del origen (122 líneas).
- Su navbar, su saludo `Hola, {{ user.username }}` y sus enlaces a `core:login`, `core:registro`, `core:logout`.

Se preserva, extraído: el widget de ayuda (`base.html:49-113`) y las 5 referencias a estáticos de `vendor/` (`base.html:115-119`).

### Impacto de la decisión

- **23 templates del origen declaran `{% block help_slug %}`** **[VERIFICADO]**. Ese bloque debe seguir existiendo en la cadena de herencia o los 23 fallan silenciosamente —el widget cargaría siempre el slug `home`. Es un fallo sin excepción y difícil de detectar: **debe verificarse pantalla por pantalla** (§11.4).
- El tema pasa de claro a oscuro. Los 28 templates del módulo fueron diseñados sobre Bootstrap claro. **[PENDIENTE]** Es previsible que haya ajustes de contraste —tablas, badges, formularios—, especialmente en las tablas densas de las Planillas 2. No se puede cuantificar sin verlo renderizado. Se estima medio día dentro de la Fase 4.
- El `{% csrf_token %}` del formulario de chat (`base.html:99`) debe conservarse al extraer el widget.

---

## Área 9 — Estáticos y Bootstrap

### Qué hace cada proyecto

| | ErgoSolutions | ErgoApp SRT 886 |
|---|---|---|
| Bootstrap CSS/JS | **CDN jsdelivr 5.3.0** en `base_dashboard.html` y `base_landing.html`; `django_bootstrap5` en `base.html` | **Local** `static/vendor/bootstrap/bootstrap-5.3.3.min.css` y `.bundle.min.js` |
| Bootstrap Icons | **CDN jsdelivr** 1.11.0 / 1.10.0 | **Local** `static/vendor/bootstrap-icons/` + fuentes `.woff`/`.woff2` |
| Otros vendor | — | `marked-15.0.12.min.js`, `purify-3.2.6.min.js` |
| Estáticos propios | `css/app.css`, `css/dashboard.css`, `js/quiz.js`, `js/ergobot_chat.js` | `ayuda/css/help_widget.css`, `ayuda/js/help_widget.js`, `js/planilla_logic.js` |
| Almacenamiento | WhiteNoise `CompressedManifestStaticFilesStorage` | Idéntico |

Inventario completo verificado: el origen aporta **44 archivos** en `static/` (33 de ayuda `.md`, 4 vendor JS/CSS, 2 fuentes, 1 README, 1 CSS de ayuda, 1 JS de ayuda, 1 JS de planillas, 1 CSS/JS bootstrap); el destino tiene **4**. **No hay una sola colisión de nombre de archivo.** **[VERIFICADO]**

### Decisión

**Se conserva el enfoque del origen: servir Bootstrap y Bootstrap Icons localmente desde `static/vendor/`. Se migra `base_dashboard.html` y `base_landing.html` del destino para que dejen de usar CDN.**

Es la única de las 12 áreas donde **el origen aporta la mejor práctica y el destino debe adaptarse**.

### Por qué el local gana

1. **Es prerrequisito del CSP.** Con `default-src 'self'`, las 6 referencias a `cdn.jsdelivr.net` se bloquean y el sitio queda sin estilos. No hay forma de tener CSP restrictivo y CDN simultáneamente sin relajar la política.
2. **Elimina una dependencia externa en tiempo de request.** Hoy, si jsdelivr no responde, el backoffice de ErgoSolutions se renderiza sin CSS ni JavaScript.
3. **Elimina una fuga de datos de navegación** hacia un tercero en cada carga de página.
4. **Es coherente con WhiteNoise**, que ambos proyectos ya usan con almacenamiento manifestado: los estáticos locales se versionan por hash y se cachean indefinidamente, lo que es más rápido que el CDN tras la primera visita.
5. **Unifica versiones.** Hoy el destino carga Bootstrap Icons 1.11.0 en el dashboard y **1.10.0 en la landing** **[VERIFICADO]** — dos versiones distintas del mismo paquete en el mismo sitio.

### Qué se le extiende a lo conservado

Nada al origen. Al destino, la migración de sus dos plantillas base:

```django
{# ANTES — templates/base_dashboard.html:10,12,110 #}
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
<link href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.0/font/bootstrap-icons.css" rel="stylesheet">
<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>

{# DESPUÉS #}
<link href="{% static 'vendor/bootstrap/bootstrap-5.3.3.min.css' %}" rel="stylesheet">
<link href="{% static 'vendor/bootstrap-icons/bootstrap-icons-1.11.3.min.css' %}" rel="stylesheet">
<script src="{% static 'vendor/bootstrap/bootstrap.bundle-5.3.3.min.js' %}"></script>
```

**[PENDIENTE]** El salto de Bootstrap 5.3.0 → 5.3.3 es de parche dentro de la misma minor y no introduce cambios incompatibles conocidos, pero **debe verificarse visualmente** en las pantallas del destino. El de Bootstrap Icons 1.10.0/1.11.0 → 1.11.3 puede cambiar nombres de algunos íconos: conviene una revisión de los `bi bi-*` usados.

### Qué se descarta

- Las 6 referencias a `cdn.jsdelivr.net`.
- La dependencia de `django_bootstrap5` para servir assets en `base.html` **se conserva**: `django_bootstrap5` se sigue usando para el renderizado de formularios en ambos proyectos, que es su función principal.

### Impacto de la decisión

- Habilita el Área 12 (CSP). Sin esta área resuelta, aquella es imposible.
- Puede ejecutarse **de forma independiente y anticipada**, sin relación con el módulo 886. Es un buen candidato para la Fase 0.
- Aumenta el tamaño del repositorio en ~700 KB (Bootstrap + Icons + fuentes). Irrelevante.
- **Riesgo bajo pero real:** un cambio de plantilla base afecta a las 33 pantallas del destino simultáneamente. Requiere pasada visual completa.

---

## Área 10 — Configuración del modelo de IA

### Qué hace cada proyecto

| | ErgoSolutions | ErgoApp SRT 886 |
|---|---|---|
| Setting | `OPENAI_MODEL` | `CHAT_AI_MODEL` |
| Defecto | `gpt-4.1-mini-2025-04-14` (`config/settings.py:195`) | `gpt-5.6-luna` (`settings.py:40`) |
| Lectura | `getattr(settings, "OPENAI_MODEL", ...)` con defecto duplicado (`ergobot_ai/agents.py:33`) | `settings.CHAT_AI_MODEL` directo |
| Consumidores | `ergobot_ai` | `help_ai` **y** los informes profesionales de `exportaciones` |
| Clave de API | `OPENAI_API_KEY` | `OPENAI_API_KEY` — **mismo nombre en ambos** |
| Settings asociados | Ninguno | 13 settings más (cuotas, timeouts, topes) |

### Decisión

**Se unifica en `OPENAI_MODEL` como base de configuración de la organización, y `CHAT_AI_MODEL` se conserva como sobrescritura opcional del módulo 886.**

Es la **única unificación que CF-1 admite**, y está expresamente prevista en la decisión 3 de §9.6 del documento de origen.

### Implementación

**[PROPUESTA]** En `config/settings.py`:

```python
# =====================================================
# OPENAI — configuración común de la organización
# =====================================================
OPENAI_API_KEY = env("OPENAI_API_KEY", default="")
OPENAI_MODEL = env("OPENAI_MODEL", default="gpt-4.1-mini-2025-04-14")

# Modelo del módulo de Ergonomía 886. Por defecto usa el de la organización;
# se puede fijar uno distinto sin afectar al chatbot docente.
CHAT_AI_MODEL = env("CHAT_AI_MODEL", default=OPENAI_MODEL)
```

Con este esquema:

- Si la organización sólo define `OPENAI_MODEL`, **ambos asistentes usan el mismo modelo**. Hay un solo lugar donde decidir.
- Si el módulo 886 necesita un modelo distinto —por ejemplo uno con más capacidad de razonamiento para los informes profesionales— basta declarar `CHAT_AI_MODEL` en el `.env`.
- **Ningún código de `help_ai` ni de `exportaciones` cambia**: siguen leyendo `settings.CHAT_AI_MODEL`.
- **Ningún código de `ergobot_ai` cambia**: sigue leyendo `settings.OPENAI_MODEL`.

Esa última propiedad es lo que hace la unificación compatible con CF-1: **es una unificación de configuración, no de código.** Las dos apps siguen sin conocerse.

### Qué se le extiende a lo conservado

Los otros **13 settings de ErgoApp** (`CHAT_AI_*`, `REPORT_AI_*`, `EXPORT_*`) se portan **sin renombrar**. Son específicos del módulo y no tienen equivalente en el destino. Renombrarlos obligaría a tocar `help_ai/limits.py`, `help_ai/views.py` y `exportaciones/reports/limits.py`, sin beneficio.

### Qué se descarta

El defecto duplicado en `apps/ergobot_ai/agents.py:33`:

```python
model=getattr(settings, "OPENAI_MODEL", "gpt-4.1-mini-2025-04-14"),   # el defecto ya está en settings
```

**[PROPUESTA]** Debe pasar a `model=settings.OPENAI_MODEL`. Tener el mismo valor por defecto en dos lugares es una trampa de mantenimiento: cambiar el modelo en `settings.py` no surtiría efecto si el setting llegara a faltar.

### Impacto de la decisión

- **Punto de atención [PENDIENTE]:** el defecto del origen es `gpt-5.6-luna` y el del destino `gpt-4.1-mini-2025-04-14`. Adoptar el del destino significa que los informes profesionales del módulo 886 pasarían a generarse con un modelo distinto del que se validó. El informe de exportación documenta que la validación se hizo con `gpt-5.6-luna`, midiendo 804 palabras y 13 segundos. **Debe decidirse explícitamente qué modelo usa el módulo en producción y declararlo en el `.env`**, no dejarlo al defecto.
- `OPENAI_API_KEY` tiene el mismo nombre en ambos: no hay nada que hacer.

---

## Área 11 — Caché

### Qué hace cada proyecto

| | ErgoSolutions | ErgoApp SRT 886 |
|---|---|---|
| `CACHES` | ❌ **No definido** → `LocMemCache` por defecto de Django | ✅ `DatabaseCache`, tabla `ergoapp_cache`, TTL 300 s, 5.000 entradas |
| Alcance | **Por proceso** | **Compartido entre procesos** |
| Consumidores | Ninguno explícito | Cuotas de chat, de informes y de descargas |
| Creación de tabla | — | `manage.py createcachetable` — **paso de despliegue, no migración** |

### Decisión

**Se adopta el `DatabaseCache` del origen. Se descarta el `LocMemCache` implícito del destino.**

### Por qué es un bloqueante y no una preferencia

Porque las cuotas del módulo 886 no son un contador aproximado: son un **cerrojo distribuido**.

**[VERIFICADO — `help_ai/limits.py:24-38`]**:

```python
def acquire_chat_lease(user_id: int) -> ChatLease:
    active_key = f"help-ai:active:{user_id}"
    if not cache.add(active_key, 1, timeout=settings.CHAT_AI_STREAM_TIMEOUT_SECONDS):
        raise ChatLimitExceeded("Ya existe una consulta del asistente en curso...", retry_after=2)
    ...
```

`cache.add()` devuelve `False` si la clave ya existe. Con `LocMemCache`, **cada worker tiene su propio diccionario en memoria**, de modo que:

- El lease anti-concurrencia deja de funcionar: un usuario puede abrir N streams simultáneos, uno por worker.
- La cuota de 20 consultas por minuto pasa a ser 20 × N.
- La cuota de 10 informes por hora pasa a ser 10 × N — y **cada informe es una llamada facturada al proveedor del modelo**.
- La cuota de 60 descargas por 5 minutos pasa a ser 60 × N.

Con los 3 workers que la auditoría del destino documenta, todas las cuotas se triplican silenciosamente. **No hay ningún síntoma visible: el sistema simplemente deja de protegerse.**

### Qué se le extiende a lo conservado

Se porta el bloque tal cual a `config/settings.py` **[PROPUESTA]**:

```python
# =====================================================
# CACHÉ COMPARTIDA ENTRE PROCESOS
# =====================================================
# Imprescindible para que las cuotas del módulo de Ergonomía (chat de ayuda,
# informes profesionales y descargas) sean globales y no por worker.
# Requiere `manage.py createcachetable` como paso de despliegue: la tabla
# NO se crea por migración.
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.db.DatabaseCache",
        "LOCATION": "ergoapp_cache",
        "TIMEOUT": 300,
        "OPTIONS": {"MAX_ENTRIES": 5000},
    }
}
```

**[PROPUESTA]** Se recomienda renombrar `LOCATION` de `ergoapp_cache` a `ergosolutions_cache`, dado que la caché pasa a ser de todo el proyecto y no sólo del módulo. Es un cambio de una cadena, sin impacto en el código, y evita que dentro de un año alguien se pregunte qué es «ergoapp». **Si se hace, debe reflejarse en el runbook de despliegue.**

### Qué se descarta

El `LocMemCache` implícito. Nótese que **nadie lo usa hoy en el destino**: no hay una sola llamada a `cache.*` en `apps/`. Descartarlo no rompe nada. **[VERIFICADO por ausencia]**

### Impacto de la decisión

- **Nuevo paso obligatorio de despliegue:** `manage.py createcachetable`, antes de arrancar los procesos. Debe agregarse al runbook. Olvidarlo produce un error en la primera consulta al chat, no al arrancar.
- **`config/test_settings.py` debe sobrescribir `CACHES` con `LocMemCache`**, exactamente como hace `ergonomia_srt/test_settings.py:20-26`, o las 160 pruebas intentarán usar una tabla que no existe en la base de test.
- **Beneficio colateral:** el destino gana caché compartida utilizable por sus propias apps. `ergobot_ai`, que hoy no tiene cuotas ninguna, podría adoptar el mismo patrón de `help_ai/limits.py` sin infraestructura adicional. **Queda como oportunidad, fuera de alcance.**

---

## Área 12 — Content Security Policy

### Qué hace cada proyecto

| | ErgoSolutions | ErgoApp SRT 886 |
|---|---|---|
| Middleware CSP | ❌ **No existe** | ✅ `ContentSecurityPolicyMiddleware` (`ergonomia_srt/middleware.py:10-59`) |
| Nonce por respuesta | ❌ | ✅ `request.csp_nonce = secrets.token_urlsafe(18)` (`:24`) |
| Soporte ASGI | — | ✅ `sync_capable` y `async_capable` (`:13-20`) |
| `Referrer-Policy` | ❌ | ✅ `same-origin` (`:44`) |
| `Permissions-Policy` | ❌ | ✅ cámara, micrófono, geolocalización y pagos deshabilitados (`:45-47`) |
| Templates compatibles | ❌ **6 CDN + 5 scripts inline + 3 handlers** | ✅ **6 scripts con nonce, 0 inline, 0 handlers** |

Política emitida **[VERIFICADO — `middleware.py:29-43`]**:

```
default-src 'self'; script-src 'self' 'nonce-…'; script-src-attr 'none';
style-src 'self' 'unsafe-inline'; font-src 'self'; img-src 'self' data:;
connect-src 'self'; object-src 'none'; base-uri 'self';
frame-ancestors 'self'; form-action 'self'
```

### Decisión

**Se adopta el middleware del origen, pero NO como prerrequisito de la integración: como una fase posterior e independiente, precedida por la remediación del frontend del destino (Área 9).**

Ésta es la desviación más significativa de este documento respecto de la planificación previa, y merece justificarse.

### Por qué NO puede ir en la Fase 0

`ESTADO_TECNICO_COMPLETO §9.3 B4` recomienda portar el middleware «en un commit propio y previo, con verificación de las pantallas existentes», y describe la tarea como «auditar que las 9 apps existentes no usen scripts en línea».

La auditoría se hizo y el resultado es que **el destino es masivamente incompatible con esa política**:

| Elemento incompatible | Cantidad | Efecto al activar el CSP |
|---|---:|---|
| `<link>` y `<script>` a `cdn.jsdelivr.net` | **6** | Bloqueados por `default-src 'self'`. **Todo el sitio pierde Bootstrap CSS y JS** |
| Bloques `<script>` inline sin nonce | **5** | Bloqueados por `script-src 'self' 'nonce-…'` |
| Manejadores en línea (`onclick=`, …) | **3** | Bloqueados por `script-src-attr 'none'` |

Poner esto en la Fase 0 significa que **antes de trasplantar una sola línea del módulo 886 hay que refactorizar el frontend completo de ErgoSolutions**, arriesgando las 33 pantallas existentes en un trabajo que no aporta ninguna funcionalidad de ergonomía. Si algo sale mal, la integración queda bloqueada por una causa ajena.

### Por qué el módulo funciona sin CSP

> **[HALLAZGO] H-K — Los templates de ErgoApp NO dejan de funcionar sin el middleware.**
>
> `ESTADO_TECNICO_COMPLETO §3.3` afirma: *«Si no se porta, los scripts del widget de ayuda y del indicador de espera de los informes dejan de ejecutarse.»* **Es incorrecto.**
>
> Verificado: **6 templates** usan el nonce, todos en la forma `<script nonce="{{ request.csp_nonce }}">`:
>
> ```
> evaluaciones/templates/evaluaciones/factor_form_base.html:139
> evaluaciones/templates/evaluaciones/vibracion_mano_brazo_form.html:233
> evaluaciones/templates/evaluaciones/posturas_forzadas_form.html:358
> evaluaciones/templates/evaluaciones/bipedestacion_form.html:204
> evaluaciones/templates/evaluaciones/vibracion_cuerpo_entero_form.html:405
> evaluaciones/templates/evaluaciones/_force_scope_checklist.html:28
> ```
>
> Sin el middleware, `request.csp_nonce` no existe y Django renderiza la variable como cadena vacía, produciendo `<script nonce="">`. **Un atributo `nonce` vacío es inocuo: sin cabecera `Content-Security-Policy` activa, el navegador no aplica ninguna restricción y el script se ejecuta normalmente.**
>
> Además, el widget de ayuda de `base.html:115-119` **no usa nonce en absoluto**: sus cinco scripts son `src=` a archivos locales. **[VERIFICADO]**
>
> **Consecuencia: el módulo 886 es funcionalmente completo sin CSP.** El CSP es una mejora de seguridad deseable, no una dependencia funcional. Eso es lo que permite separarlo del camino crítico.

### Secuencia propuesta

```
Fase 9-A  →  Migrar base_dashboard.html y base_landing.html de CDN a vendor/ local   (Área 9)
Fase 9-B  →  Extraer los 5 bloques <script> inline a archivos .js estáticos
Fase 9-C  →  Reemplazar los 3 manejadores en línea por addEventListener
Fase 9-D  →  Verificación visual y funcional de las 33 pantallas del destino
Fase 9-E  →  Portar el middleware y registrarlo en MIDDLEWARE
Fase 9-F  →  Verificación con la consola del navegador abierta: cero violaciones de CSP
```

Las fases 9-A a 9-D pueden ejecutarse en cualquier momento, incluso antes de la integración, y aportan valor por sí solas. Sólo 9-E y 9-F dependen de que estén completas.

### Qué se le extiende a lo conservado

El middleware se porta **sin cambios funcionales**, a `config/middleware.py`. Su posición en `MIDDLEWARE` debe replicar la del origen: **después de `WhiteNoiseMiddleware` y antes de `SessionMiddleware`** **[VERIFICADO — `ergonomia_srt/settings.py:100-110`]**.

**[PROPUESTA]** Se recomienda una única extensión: hacer la política configurable por setting, para poder ejecutar un período de observación con `Content-Security-Policy-Report-Only` antes de aplicarla en modo bloqueante. Es la práctica estándar para introducir CSP en un sitio existente y reduce a casi cero el riesgo de la fase 9-E.

### Impacto de la decisión

- El módulo 886 **pierde temporalmente** el endurecimiento que tenía en su proyecto de origen. Debe registrarse como deuda explícita con fecha de resolución, no como olvido.
- Se ganan además `Referrer-Policy` y `Permissions-Policy` para todo ErgoSolutions, que hoy no tiene ninguna de las dos.
- **[PENDIENTE]** Los 5 bloques `<script>` inline del destino deben inspeccionarse uno por uno: si alguno depende de variables de contexto de Django renderizadas en el template, extraerlo a un `.js` estático exige pasar esos datos por `data-*` attributes. Es el trabajo real de la fase 9-B y no se puede estimar sin leerlos.

---
# PARTE V — MATRIZ DE COMPATIBILIDAD TÉCNICA

**Leyenda de veredictos:** 🟢 Compatible · 🟡 Requiere adaptación · 🔴 Bloqueante · 🔵 Oportunidad (el destino resuelve una deuda del origen)

## 5.1 Plataforma y entorno

| # | Aspecto | ErgoApp SRT 886 | ErgoSolutions | Veredicto | Acción |
|---|---|---|---|:---:|---|
| 1 | Django | 5.2.7 | **5.2.10** | 🟢 | Ninguna. Misma minor |
| 2 | Python local | 3.11.2 | 3.11.2 | 🟢 | Ninguna |
| 3 | Python producción | — | 3.10.12 | 🟡 | **[PENDIENTE]** Verificar que el módulo no use sintaxis exclusiva de 3.11 antes del despliegue |
| 4 | Driver PostgreSQL | `psycopg2-binary` 2.9.10 | **`psycopg[binary]` 3.3.2** | 🟡 | Adoptar psycopg 3. **No requiere cambios de código**: el ORM abstrae el driver |
| 5 | Configuración de BD | Parámetros sueltos `DB_*` | `DATABASE_URL` única | 🟡 | Adoptar la del destino. Se descartan 5 variables del `.env` del origen |
| 6 | Servidor | Gunicorn WSGI / Uvicorn ASGI | Gunicorn WSGI (ASGI preparado, no ejecutado) | 🟡 | Ver fila 24 |
| 7 | Estáticos | WhiteNoise `CompressedManifest` | WhiteNoise `CompressedManifest` | 🟢 | Ninguna |
| 8 | `TIME_ZONE` | `America/Argentina/Buenos_Aires` | Idéntico | 🟢 | Ninguna |
| 9 | `LANGUAGE_CODE` | ⚠️ `en-us` | **`es-ar`** | 🔵 | Adoptar la del destino. **Cierra D-8** |
| 10 | `DEFAULT_AUTO_FIELD` | `BigAutoField` | `BigAutoField` | 🟢 | Ninguna |

## 5.2 Modelo de datos y aplicaciones

| # | Aspecto | ErgoApp SRT 886 | ErgoSolutions | Veredicto | Acción |
|---|---|---|---|:---:|---|
| 11 | **Modelo de usuario** | `auth.User` (`planillas/models.py:4,9`) | **`accounts.CustomUser`** | 🔴 **B1** | Cambiar a `settings.AUTH_USER_MODEL`. **Sin migración** (H-G) |
| 12 | Estado de migraciones vs. usuario | Ya `swappable_dependency` | — | 🟢 | **Ninguna.** Verificado en H-G |
| 13 | **Layout de apps** | Plano (`core`, `planillas`, …) | Paquete `apps/` | 🔴 **B2** | Mover a `apps/ergonomia_886/`. **102 imports** a reescribir |
| 14 | `app_label` | `planillas`, `evaluaciones`, `exportaciones`, `help_ai`, `core` | `accounts`, `landing`, `dashboard`, `presencial`, `company`, `training`, `quiz`, `certificates`, `ergobot_ai` | 🟢 | **Ninguna: no hay colisión.** Los labels se conservan y las migraciones no se tocan |
| 15 | Migraciones a copiar | 10 archivos (`planillas` 1, `evaluaciones` 7, `exportaciones` 2) | 15 propias | 🟢 | Copiar sin modificar |
| 16 | Entidad empresa | ❌ texto libre en `Evaluacion` | ✅ `CompanyProfile` | 🔵 | FK nueva + migración |
| 17 | Entidad trabajador | ❌ `TextField` | ✅ `CompanyWorker` | 🔵 | M2M opcional + migración |
| 18 | Firmantes | ❌ recuadros vacíos | ✅ `profession`, `license_number` | 🔵 | **Cierra D-3** |
| 19 | `MEDIA_ROOT` | ❌ **no definido** | ✅ `BASE_DIR / "media"` | 🔵 | **Cierra D-1** |

## 5.3 URLs, plantillas y estáticos

| # | Aspecto | ErgoApp SRT 886 | ErgoSolutions | Veredicto | Acción |
|---|---|---|---|:---:|---|
| 20 | **`app_name` en URLs** | ❌ falta en `planillas` (14 nombres) y `help_ai` (2) | Namespaces en uso; ⚠️ falta en 5 includes propios | 🔴 **B3** | Agregar `app_name`. **35 referencias** a calificar |
| 21 | Prefijo `/ai/` | `help_ai` | **`ergobot_ai` ya lo ocupa** | 🟡 | Montar `help_ai` bajo el prefijo del módulo (H-C) |
| 22 | Colisión de nombres de URL | `dashboard`, `crear_evaluacion`, `detalle_evaluacion`, `planilla*` en espacio global | `ergobot_stream`, nombres de `accounts`, `training`, `quiz`, `certificates` en espacio global | 🟡 | Resuelto por la fila 20 |
| 23 | Plantillas base | `templates/base.html` propia con `help_slug` | `base.html`, `base_dashboard.html`, `base_landing.html` | 🟡 | Adaptar 10 templates. Portar bloque y widget |
| 24 | Directorios de templates | `core/`, `planillas/`, `evaluaciones/`, `exportaciones/` | `accounts/`, `company/`, `dashboard/`, `includes/`, `landing/`, `presencial/`, `quiz/`, `training/` | 🟢 | **Ninguna: no hay colisión** |
| 25 | Archivos estáticos | 44 archivos (`ayuda/`, `vendor/`, `js/planilla_logic.js`) | 4 archivos (`css/`, `js/`) | 🟢 | **Ninguna: no hay colisión de nombres** |
| 26 | Bootstrap | **Local** `vendor/` 5.3.3 | **CDN jsdelivr** 5.3.0 + `django_bootstrap5` | 🟡 | Migrar el destino a local (Área 9) |
| 27 | Bootstrap Icons | **Local** 1.11.3 con fuentes | **CDN** 1.11.0 y 1.10.0 (dos versiones) | 🟡 | Idem |
| 28 | **Rutas de archivos de datos** | `help_ai/prompts.py:14-15` usa `parent.parent` | — | 🔴 **B6** | Ver §6.6. **No documentado previamente** |

## 5.4 Dependencias

| # | Paquete | ErgoApp | ErgoSolutions | Veredicto | Acción |
|---|---|---|---|:---:|---|
| 29 | `pypdf` | 6.14.2 | ❌ **ausente** | 🔴 **B7** | Agregar a `requirements.txt`. Sin él falla el import de `official/overlay.py` |
| 30 | `pillow` | 11.3.0 instalada, no declarada | 12.1.0 instalada, no declarada | 🟡 | Declarar en `requirements.txt` (N8) |
| 31 | `reportlab` | 4.5.1 | 4.4.9 | 🟢 | Ninguna |
| 32 | `openai` | 1.109.1 | **2.15.0** | 🟡 | API verificada compatible |
| 33 | `openai-agents` | 0.3.3 | **0.6.9** | 🟡 | **[VERIFICADO]** `Agent`, `Runner`, `RunConfig`, `ItemHelpers` y `trace_include_sensitive_data` presentes en 0.6.9 |
| 34 | `django-bootstrap5` | 25.2 | 26.1 | 🟢 | Ninguna |
| 35 | `django-cors-headers` | 4.9.0 | — | 🟡 | **Descartar.** El destino no expone API a terceros |
| 36 | `sse-starlette` | 3.0.2 declarada, **no usada** | 3.2.0 instalada | 🟢 | Descartar de la declaración |
| 37 | `weasyprint` | 66.0 instalada, no declarada, **no usada** | — | 🟡 | **Descartar.** Cierra D-7 |
| 38 | `gunicorn` | 23.0.0 | ausente del venv local | 🟢 | Producción del destino lo usa igual |
| 39 | `whitenoise`, `django-environ` | 6.11.0 / 0.12.0 | Idénticas | 🟢 | Ninguna |

## 5.5 Infraestructura transversal

| # | Aspecto | ErgoApp SRT 886 | ErgoSolutions | Veredicto | Acción |
|---|---|---|---|:---:|---|
| 40 | **Caché** | `DatabaseCache` compartida | ❌ **no definida** → `LocMemCache` | 🔴 **B4** | Portar bloque + `createcachetable`. Ver Área 11 |
| 41 | **CSP y nonce** | Middleware propio | ❌ no existe | 🟡 **B5** | **Degradado de bloqueante a adaptación.** Ver H-K y Área 12 |
| 42 | Compatibilidad de templates con CSP | ✅ 6 scripts con nonce, 0 inline, 0 handlers | ❌ 6 CDN, 5 inline, 3 handlers | 🔴 | Remediación previa del frontend del destino |
| 43 | `Referrer-Policy` / `Permissions-Policy` | ✅ | ❌ | 🔵 | Llegan con el middleware |
| 44 | Configuración de pruebas | ✅ `ergonomia_srt/test_settings.py` | ❌ **no existe** | 🔴 **B8** | Crear `config/test_settings.py`. Ver H-B |
| 45 | Setting del modelo de IA | `CHAT_AI_MODEL` | `OPENAI_MODEL` | 🟡 | `CHAT_AI_MODEL` deriva de `OPENAI_MODEL`. Área 10 |
| 46 | Clave de API | `OPENAI_API_KEY` | `OPENAI_API_KEY` | 🟢 | Ninguna. Mismo nombre |
| 47 | Settings de cuotas y topes | 13 settings `CHAT_AI_*`, `REPORT_AI_*`, `EXPORT_*` | — | 🟡 | Portar sin renombrar |
| 48 | Streaming SSE sobre WSGI | Diseñado para ASGI | Corre sobre workers WSGI sync (H12) | 🟡 | **Riesgo R-5.** Fuera de alcance |
| 49 | Logging | Sin configuración propia | `LOGGING` con dos loggers | 🟢 | Agregar loggers del módulo **[PROPUESTA]** |
| 50 | Regresiones abiertas del destino | — | **N1 y N2 verificadas** | 🔴 | **Fase 0 obligatoria** |

## 5.6 Resumen de veredictos

| Veredicto | Cantidad | Filas |
|---|---:|---|
| 🟢 Compatible, sin acción | **16** | 1, 2, 7, 8, 10, 12, 14, 15, 24, 25, 31, 34, 36, 38, 39, 46 |
| 🟡 Requiere adaptación | **19** | 3, 4, 5, 6, 21, 22, 23, 26, 27, 30, 32, 33, 35, 37, 41, 45, 47, 48, 49 |
| 🔴 Bloqueante o crítico | **9** | 11 (B1), 13 (B2), 20 (B3), 28 (B6), 29 (B7), 40 (B4), 42, 44 (B8), 50 (N1/N2) |
| 🔵 Oportunidad | **6** | 9, 16, 17, 18, 19, 43 |
| | **50** | |

> **Los bloqueantes pasaron de 5 (documentación previa) a 8.** Se degradó uno (B5, CSP) y se agregaron cuatro no documentados: **B6** (rutas de archivos de `help_ai`), **B7** (`pypdf` ausente), **B8** (sin configuración de pruebas) y la remediación previa del frontend del destino (fila 42). El balance neto de esfuerzo, sin embargo, es **favorable**, porque B1 y B2 resultaron mucho más baratos de lo previsto.

---

# PARTE VI — BLOQUEANTES DUROS Y SU RESOLUCIÓN

## 6.1 B1 — Modelo de usuario

| Ítem | Detalle |
|---|---|
| **Qué es** | `planillas` importa y referencia `django.contrib.auth.models.User` directamente |
| **Dónde** | `planillas/models.py:4` (import) y `planillas/models.py:9` (FK) |
| **Por qué bloquea** | ErgoSolutions define `AUTH_USER_MODEL = "accounts.CustomUser"` (`config/settings.py:90`). Un FK a `auth.User` en ese proyecto apunta a un modelo que no es el de usuario activo y cuya tabla no se crea, porque `django.contrib.auth` no genera `auth_user` cuando el modelo está swapped. Django lo detecta en el chequeo de sistema |
| **Severidad** | Afecta la **tabla raíz de todo el dominio** |

### Código actual **[VERIFICADO]**

```python
# planillas/models.py
 4  from django.contrib.auth.models import User
...
 8  class Evaluacion(models.Model):
 9      usuario = models.ForeignKey(User, on_delete=models.CASCADE)
```

### Resolución

```python
# planillas/models.py
 3  from django.db import models
 4  from django.conf import settings              # ← reemplaza el import de User
...
 8  class Evaluacion(models.Model):
 9      usuario = models.ForeignKey(
10          settings.AUTH_USER_MODEL,
11          on_delete=models.CASCADE,
12      )
```

> **Hallazgo de ejecución — 03/08/2026.** La premisa de cero migraciones es
> correcta solo para el reemplazo de `User` por `settings.AUTH_USER_MODEL`.
> El `verbose_name` propuesto adicionalmente sí genera
> `planillas.0002_alter_evaluacion_usuario`. Como no aporta compatibilidad y
> contradice el criterio de aceptación, se retiró: el commit 1.1 cambia
> exclusivamente la referencia swappable y `makemigrations --check --dry-run`
> vuelve a informar `No changes detected`.

`evaluaciones/models.py:48-49`, `exportaciones/models.py:71-72` y `exportaciones/models.py:111-112` **ya usan la forma correcta** y no requieren cambios **[VERIFICADO]**.

### Riesgo que introduce la corrección

**Ninguno.** Es el bloqueante más barato de los ocho, contra lo que preveía la documentación.

> **[VERIFICADO]** El cambio **no genera migración**. Comprobado empíricamente en el proyecto de origen:
>
> ```
> deconstruct(ForeignKey(User))                     → {'on_delete': CASCADE, 'to': 'auth.user'}
> deconstruct(ForeignKey(settings.AUTH_USER_MODEL)) → {'on_delete': CASCADE, 'to': 'auth.user'}
> IDENTICOS → True
> ```
>
> Y `planillas/migrations/0001_initial.py` ya contiene `migrations.swappable_dependency(settings.AUTH_USER_MODEL)` en `:13` y `to=settings.AUTH_USER_MODEL` en `:28`.
>
> **Criterio de verificación:** tras el cambio, `makemigrations --check --dry-run` debe seguir devolviendo `No changes detected` **en el proyecto de origen**. Si generara una migración, algo más cambió y hay que investigarlo antes de continuar.

En el destino, la migración `0001_initial` de `planillas` resolverá la FK contra `accounts.CustomUser` automáticamente al aplicarse sobre base vacía. Eso es exactamente para lo que existe `swappable_dependency`.

---

## 6.2 B2 — Layout de apps

| Ítem | Detalle |
|---|---|
| **Qué es** | Las apps del origen son paquetes de primer nivel; las del destino viven bajo `apps/` con nombres punteados |
| **Dónde** | `ergonomia_srt/settings.py:92-96` vs `config/settings.py:38-48`; y los 102 imports absolutos del origen |
| **Por qué bloquea** | Sin mover las apps, `INSTALLED_APPS` del destino tendría entradas de primer nivel mezcladas con `apps.*`, y los paquetes quedarían fuera de la convención del proyecto. Los imports absolutos dejarían de resolver |
| **Severidad** | Alta en volumen, baja en dificultad. Es trabajo mecánico exhaustivo |

### Inventario exacto de referencias a reescribir **[VERIFICADO]**

**Imports absolutos entre apps: 102 apariciones en 16 archivos.**

| Archivo | Imports | Observación |
|---|---:|---|
| `exportaciones/tests/test_serializers.py` | 39 | |
| `exportaciones/tests/test_official_pdf.py` | 15 | |
| `exportaciones/tests/test_permissions.py` | 12 | |
| `exportaciones/tests/test_reports_llm.py` | 12 | |
| `exportaciones/tests/test_reports_pdf.py` | 7 | |
| `exportaciones/serializers.py` | 3 | |
| `exportaciones/views.py` | 3 | |
| `exportaciones/packaging.py` | 2 | |
| `evaluaciones/tests.py` | 2 | |
| `core/views.py` | 1 | Se descarta con el archivo |
| `planillas/views.py` | 1 | `from evaluaciones.views import ...` (D-10) |
| `evaluaciones/models.py` | 1 | |
| `evaluaciones/admin.py` | 1 | |
| `evaluaciones/views.py` | 1 | |
| `exportaciones/models.py` | 1 | |
| `help_ai/catalog.py` | 1 | `from evaluaciones.catalog import FACTOR_DEFINITIONS` |
| **Total** | **102** | **85 de ellos en suites de prueba** |

> **Hallazgo de ejecución — 03/08/2026.** Este inventario de 102 corresponde
> al repositorio de origen e incluye el import de `core/views.py`, que se
> descarta junto con `core`. El trasplante efectivo contiene 101 imports en 15
> archivos; 87 están en suites (los 85 de `exportaciones/tests/` más dos de
> `evaluaciones/tests.py`). Los 101 fueron reescritos y el import descartado
> quedó contabilizado, no omitido.

**Grafo de acoplamiento entre apps [VERIFICADO]:**

```
core         → planillas                                    (se descarta)
planillas    → evaluaciones.views    (helpers privados — D-10)
evaluaciones → planillas.models, help_ai.catalog
exportaciones→ planillas.models, evaluaciones.{catalog,models,views}
help_ai      → evaluaciones.catalog
```

> Nótese que **`help_ai` importa de `evaluaciones`**, no de `ergobot_ai`. CF-1 exige que `help_ai` y `ergobot_ai` no se importen mutuamente, cosa que se cumple y se seguirá cumpliendo.

**Rutas de importación en cadenas literales — no las detecta ningún refactor automático:**

| Archivo | Cantidad | Contenido |
|---|---:|---|
| `evaluaciones/catalog.py` | **26** | 13 `form_path="evaluaciones.forms.X"` + 13 `model_path="evaluaciones.models.X"` |
| `exportaciones/official/catalog.py` | **12** | `model_path="planillas.models.PlanillaN"` |
| `exportaciones/serializers.py:22-32` | **9** | `PLANILLA2_MODELOS = {"planilla2a": "planillas.models.Planilla2A", …}` |
| `evaluaciones/calculators.py:71` | **1** | `importlib_resources.files("evaluaciones.data")` |
| **Total** | **48** | |

**Éstas son las más peligrosas del trasplante:** son cadenas de texto resueltas en tiempo de ejecución con `import_string()`. Un olvido no produce un `ImportError` al arrancar, sino un fallo diferido al abrir una pantalla concreta.

### Resolución

Estructura de destino:

```
apps/ergonomia_886/
    __init__.py
    planillas/
    evaluaciones/
    exportaciones/
    help_ai/
```

Reescrituras, en este orden:

```
1. from planillas.        → from apps.ergonomia_886.planillas.
2. from evaluaciones.     → from apps.ergonomia_886.evaluaciones.
3. from exportaciones.    → from apps.ergonomia_886.exportaciones.
4. from help_ai.          → from apps.ergonomia_886.help_ai.
5. "evaluaciones.forms.   → "apps.ergonomia_886.evaluaciones.forms.      (13)
6. "evaluaciones.models.  → "apps.ergonomia_886.evaluaciones.models.     (13)
7. "planillas.models.     → "apps.ergonomia_886.planillas.models.        (21)
8. "evaluaciones.data"    → "apps.ergonomia_886.evaluaciones.data"        (1)
9. name = 'X'             → name = 'apps.ergonomia_886.X'   en los 4 apps.py
```

### Sobre `app_label`: por qué NO hay que tocarlo

> **[VERIFICADO]** Django deriva `AppConfig.label` de la **última componente** del nombre punteado. Con `name = 'apps.ergonomia_886.planillas'`, el label sigue siendo `planillas`.
>
> Los labels resultantes del módulo serían `planillas`, `evaluaciones`, `exportaciones`, `help_ai`. Contrastados con los nueve del destino —`accounts`, `landing`, `dashboard`, `presencial`, `company`, `training`, `quiz`, `certificates`, `ergobot_ai`— **no hay una sola colisión**.
>
> **Consecuencias:**
> - No hace falta declarar `label` explícito en ningún `apps.py`.
> - **Las 10 migraciones existentes se copian sin modificar.** No hay `SeparateDatabaseAndState`, no hay renombrado de tablas.
> - Las tablas se crean con sus nombres actuales: `planillas_evaluacion`, `evaluaciones_lmc_eval`, `exportaciones_exportaudit`, etc.
>
> Esto contradice `ESTADO_TECNICO_COMPLETO §9.3 B2`, que lista «`app_label` en las migraciones existentes» entre lo que hay que actualizar y advierte sobre `SeparateDatabaseAndState`. **Con base vacía y sin colisión de labels, nada de eso es necesario.**

### Riesgo que introduce la corrección

**Medio, y concentrado en las 48 cadenas literales.** Mitigaciones:

1. Ejecutar los pasos 5 a 8 **antes** que los 1 a 4, mientras las cadenas todavía son fáciles de encontrar por su prefijo.
2. Tras el trasplante, verificar que `import_string()` resuelve para las 48. Un chequeo de arranque **[PROPUESTA]**:

```python
# apps/ergonomia_886/checks.py   [PROPUESTA]
from django.core.checks import Error, register
from django.utils.module_loading import import_string

@register()
def check_rutas_del_catalogo(app_configs, **kwargs):
    """Falla el `manage.py check` si alguna ruta declarativa no resuelve."""
    from .evaluaciones.catalog import FACTOR_DEFINITIONS
    from .exportaciones.official.catalog import PLANILLA_DEFINITIONS
    from .exportaciones.serializers import PLANILLA2_MODELOS

    rutas = []
    for d in FACTOR_DEFINITIONS:
        rutas += [d.form_path, d.model_path]
    rutas += [p.model_path for p in PLANILLA_DEFINITIONS]
    rutas += list(PLANILLA2_MODELOS.values())

    errores = []
    for ruta in rutas:
        try:
            import_string(ruta)
        except ImportError:
            errores.append(Error(f"Ruta declarativa no resoluble: {ruta}", id="ergonomia_886.E001"))
    return errores
```

Con eso, un olvido pasa de ser un HTTP 500 diferido a un fallo de `manage.py check` en tiempo de arranque. **Es la mitigación más valiosa de todo el plan y cuesta 20 líneas.**

3. Las 160 pruebas son la red final: 85 de los 102 imports viven en suites, de modo que un olvido allí revienta de inmediato.

---

## 6.3 B3 — Namespaces de URL

| Ítem | Detalle |
|---|---|
| **Qué es** | `planillas/urls.py` y `help_ai/urls.py` no declaran `app_name`, de modo que 16 nombres de URL viven en el espacio global |
| **Dónde** | `planillas/urls.py` (14 nombres), `help_ai/urls.py:9-10` (2 nombres) |
| **Por qué bloquea** | En un proyecto con 13 apps, nombres como `dashboard`, `crear_evaluacion` o `detalle_evaluacion` son candidatos naturales a colisión. Una colisión de nombres de URL en Django **no produce error**: la última definición gana silenciosamente, y el enlace lleva a otra pantalla |
| **Severidad** | Media, pero con modo de fallo silencioso |

### Nombres afectados **[VERIFICADO]**

| App | Nombres | Origen |
|---|---|---|
| `planillas` | `crear_evaluacion`, `detalle_evaluacion`, `planilla1`, `planilla2a`…`planilla2i`, `planilla3`, `planilla4` | `planillas/urls.py:7-27` |
| `help_ai` | `help_guide`, `chat_ai` | `help_ai/urls.py:9-10` |

### Inventario exacto de referencias a calificar **[VERIFICADO]**

| Referencia | Templates | Python | Total | Destino |
|---|---:|---:|---:|---|
| `detalle_evaluacion` | 6 | 5 | **11** | `planillas:detalle_evaluacion` |
| `planilla1`…`planilla4` (12 nombres) | 12 | 0 | **12** | `planillas:planillaN` |
| `crear_evaluacion` | 1 | 0 | **1** | `planillas:crear_evaluacion` |
| `chat_ai` | 1 | 6 | **7** | `help_ai:chat_ai` |
| `help_guide` | 1 | 3 | **4** | `help_ai:help_guide` |
| **Subtotal a calificar** | **21** | **14** | **35** | |
| `core:*` (dashboard 7, registro 2, logout 1, login 1, eliminar_evaluacion 1) | 12 | 4 | **16** | Se descartan o se reapuntan |

Ubicación de las 14 referencias en Python:

```
planillas/views.py:62,140,179,347,397     redirect('detalle_evaluacion', ...)     →  5
help_ai/tests.py:143,190,202,227,257,483  reverse("chat_ai", ...)                 →  6
help_ai/tests.py:147,213,247              reverse("help_guide", ...)              →  3
```

### Resolución

```python
# apps/ergonomia_886/planillas/urls.py
from django.urls import path
from . import views

app_name = "planillas"          # ← nuevo

urlpatterns = [ ... ]           # sin cambios
```

```python
# apps/ergonomia_886/help_ai/urls.py
from django.urls import path
from .views import chat_view, guide_view

app_name = "help_ai"            # ← nuevo

urlpatterns = [ ... ]           # sin cambios
```

Y las 35 referencias se califican. Nótese que en `templates/base.html` del origen, las dos referencias del widget de ayuda están **dentro de atributos `data-*`**:

```django
data-guide-url-template="{% url 'help_guide' slug='__slug__' %}"
data-chat-url-template="{% url 'chat_ai' slug='__slug__' %}"
```

Ese template se descarta, pero el widget se preserva como `include` (Área 8) y **ambas líneas deben calificarse allí**.

### Riesgo que introduce la corrección

**Bajo pero con un conflicto normativo que debe resolverse antes.**

Los 9 `reverse()` de `help_ai/tests.py` deben calificarse, lo que colisiona con el criterio literal de CF-1 «las 22 pruebas pasan sin modificación». **Ver H-J en el Área 5 para la resolución propuesta y el criterio de verificación reformulado.** Debe aceptarse formalmente antes de ejecutar la Fase 1.

**[PROPUESTA] Mitigación adicional:** aprovechar el mismo commit para agregar `app_name` a los cinco includes del destino que tampoco lo tienen (`apps.accounts.urls`, `apps.training.urls`, `apps.quiz.urls`, `apps.certificates.urls`, `apps.ergobot_ai.urls` — H-D). Es el mismo tipo de trabajo y cierra el defecto de raíz en vez de dejarlo a medias.

---

## 6.4 B4 — Caché compartida

| Ítem | Detalle |
|---|---|
| **Qué es** | ErgoSolutions no define `CACHES`, de modo que Django usa `LocMemCache`, que es **por proceso** |
| **Dónde** | Ausencia en `config/settings.py`; consumidores en `help_ai/limits.py:24-57` y `exportaciones/reports/limits.py` |
| **Por qué bloquea** | Las cuotas del módulo se implementan con `cache.add()` como cerrojo distribuido. Con caché por proceso, el lease anti-concurrencia deja de funcionar y las tres cuotas se multiplican por la cantidad de workers, **sin ningún síntoma visible** |
| **Severidad** | Alta. Afecta control de gasto (informes facturados) y protección anti-abuso |

### Resolución

Portar el bloque `CACHES` a `config/settings.py` y ejecutar `createcachetable` como paso de despliegue. Ver Área 11 para el código y el detalle.

### Riesgo que introduce la corrección

| Riesgo | Mitigación |
|---|---|
| Olvidar `createcachetable` → error en la primera consulta al chat, no al arrancar | Agregarlo al runbook **y** verificarlo con una prueba de humo autenticada sobre `/…/ayuda/chat/…` |
| Las 160 pruebas intentan usar la tabla de caché en la base de test | `config/test_settings.py` debe sobrescribir `CACHES` con `LocMemCache`, como hace `ergonomia_srt/test_settings.py:20-26` |
| `DatabaseCache` agrega carga a PostgreSQL | Despreciable con `MAX_ENTRIES: 5000` y TTL de 300 s. Es la elección deliberada del origen para tener cuotas globales sin desplegar Redis |

---

## 6.5 B5 — Content Security Policy *(degradado)*

| Ítem | Detalle |
|---|---|
| **Qué es** | ErgoSolutions no tiene middleware de CSP ni `request.csp_nonce` |
| **Dónde** | `config/settings.py:52-61` (MIDDLEWARE sin CSP); origen en `ergonomia_srt/middleware.py:10-59` |
| **Estado** | 🟡 **Degradado de bloqueante a adaptación diferible** |

### Por qué se degrada

**[VERIFICADO — H-K]** Los 6 templates del origen que usan el nonce lo hacen como `<script nonce="{{ request.csp_nonce }}">`. Sin el middleware, la variable renderiza vacío y produce `<script nonce="">`, que **se ejecuta con normalidad** porque no hay política CSP activa que lo restrinja. El widget de ayuda no usa nonce en absoluto.

**El módulo 886 es funcionalmente completo sin CSP.**

### Por qué no puede resolverse rápido

**[VERIFICADO — H-E]** El frontend del destino es masivamente incompatible: 6 referencias a CDN, 5 bloques `<script>` inline y 3 manejadores en línea. Activar el CSP sin remediarlos deja las 33 pantallas del destino sin Bootstrap CSS ni JavaScript.

### Resolución

Fase 6, separada del camino crítico, con la secuencia 9-A a 9-F detallada en el Área 12. Se recomienda un período previo con `Content-Security-Policy-Report-Only`.

### Riesgo que introduce la corrección

**Alto si se hace sin remediar; bajo si se sigue la secuencia.** El riesgo de *no* hacerlo es aceptar una deuda de seguridad conocida, que debe registrarse con responsable y fecha.

---

## 6.6 B6 — Rutas de archivos de `help_ai` *(no documentado previamente)*

| Ítem | Detalle |
|---|---|
| **Qué es** | `help_ai` resuelve la ubicación de los 33 documentos Markdown de ayuda subiendo dos niveles desde su propio archivo |
| **Dónde** | `help_ai/prompts.py:14-15` |
| **Por qué bloquea** | Al anidar la app bajo `apps/ergonomia_886/`, esa ruta deja de apuntar a la raíz del proyecto. Ningún documento de ayuda se encuentra, y `md()` lanza `HelpContentError` para todos |
| **Severidad** | Alta. Inutiliza el sistema de ayuda completo y rompe las 22 pruebas de `help_ai` |

### Código actual **[VERIFICADO]**

```python
# help_ai/prompts.py
14  BASE_DIR = Path(__file__).resolve().parent.parent
15  HELP_TEXTS_PATH = BASE_DIR / "static" / "ayuda" / "help_texts"
```

Hoy: `help_ai/prompts.py` → `parent` = `help_ai/` → `parent.parent` = raíz del proyecto → `<raíz>/static/ayuda/help_texts/` ✅

Tras el trasplante: `apps/ergonomia_886/help_ai/prompts.py` → `parent.parent` = `apps/ergonomia_886/` → `apps/ergonomia_886/static/ayuda/help_texts/` ❌

La consecuencia es total: `md()` (`help_ai/prompts.py:32-48`) está escrita deliberadamente para **no** degradar silenciosamente —«nunca reemplaza una ausencia por texto vacío»— y lanza `HelpContentError` en cada llamada.

### Resolución **[PROPUESTA]**

Dos opciones. **Se recomienda la A.**

**Opción A — Anclar a `settings.BASE_DIR` (recomendada).** Los documentos de ayuda siguen siendo estáticos del proyecto:

```python
from django.conf import settings

HELP_TEXTS_PATH = Path(settings.BASE_DIR) / "static" / "ayuda" / "help_texts"
```

**Ventajas:** los 33 `.md` viven junto al resto de estáticos, `collectstatic` los recoge igual, y el widget de ayuda puede seguir sirviéndolos por URL estática si alguna vez conviene. **Coste:** introduce una dependencia de Django en un módulo que hoy es agnóstico.

**Opción B — Moverlos dentro de la app:**

```python
BASE_DIR = Path(__file__).resolve().parent          # ← un solo nivel
HELP_TEXTS_PATH = BASE_DIR / "help_texts"
```

con los 33 archivos en `apps/ergonomia_886/help_ai/help_texts/`. **Ventaja:** la app queda autocontenida y desmontable. **Coste:** salen de `static/`, de modo que `collectstatic` ya no los recoge; hay que confirmar que ningún otro componente los sirva como estáticos.

### Verificación

`help_ai/tests.py` incluye una prueba que valida la lectura del documento de un slug inexistente (`slug-que-no-existe.md`), observada durante la ejecución de la suite. **Las 22 pruebas de `help_ai` son la verificación natural de este bloqueante:** si la ruta queda mal, fallan todas.

### Riesgo que introduce la corrección

**Bajo.** Es un cambio de dos líneas con verificación automática inmediata. **El riesgo real era no haberlo detectado**, porque el síntoma —«el chat de ayuda no responde en ninguna pantalla»— aparecería recién en pruebas manuales.

### Comprobación de los demás cálculos de rutas **[VERIFICADO]**

Se auditaron todos los cálculos de ruta de archivo del origen:

| Archivo | Línea | Expresión | ¿Sobrevive al movimiento? |
|---|---|---|---|
| `evaluaciones/calculators.py` | `:59` | `os.path.dirname(__file__)` + `/data` | ✅ **Sí** — relativa al propio paquete |
| `evaluaciones/calculators.py` | `:71` | `importlib_resources.files("evaluaciones.data")` | ⚠️ **Cadena literal**, hay que actualizarla. Tiene respaldo en `:59`, de modo que no rompe, pero degrada a la vía lenta |
| `exportaciones/official/catalog.py` | `:15-17` | `Path(__file__).resolve().parent` + `/templates_bin`, `/maps` | ✅ **Sí** — relativa al propio paquete |
| `help_ai/prompts.py` | `:14-15` | `parent.parent` + `/static/...` | 🔴 **No** — es B6 |

**Es el único caso.** El PDF oficial, los 12 mapas de calibración y los 13 artefactos normativos viajan correctamente con sus paquetes.

---

## 6.7 B7 — `pypdf` ausente en el destino

| Ítem | Detalle |
|---|---|
| **Qué es** | `pypdf` es la biblioteca que fusiona la capa de datos sobre el PDF oficial de la SRT. Está instalada en el venv del origen (6.14.2) y **ausente** del destino |
| **Dónde** | `requirements.txt` del destino (9 líneas, sin `pypdf`); consumidor en `exportaciones/official/overlay.py` |
| **Por qué bloquea** | Sin `pypdf` no hay superposición, y sin superposición no hay documentos oficiales. Además viola CF-6, que **prohíbe** la única alternativa (rellenar el `.xls` oficial) |
| **Severidad** | Alta, resolución trivial |

### Resolución

```diff
  Django>=5.2
  psycopg[binary]>=3.2
  django-environ>=0.11
  django-bootstrap5>=25.1
  whitenoise>=6.7
  reportlab>=4.0
+ pypdf>=5.0,<7.0
+ pillow>=10.0
  openai>=1.0
  openai-agents>=0.0.19
  uvicorn>=0.30.0
```

`pillow` se agrega en el mismo movimiento: está instalada en ambos venvs, es obligatoria para los dos `ImageField` del proyecto integrado y no está declarada en ninguno de los dos `requirements.txt` (hallazgo N8).

### Riesgo que introduce la corrección

**Ninguno.** El fallo sin la corrección sería un `ImportError` al arrancar, inmediato y evidente.

**[PROPUESTA]** Conviene aprovechar para fijar cotas superiores en las dependencias del destino, hoy declaradas sólo con `>=`. `openai>=1.0` admite instalar la 2.x —que es lo que efectivamente ocurrió— y también admitirá una futura 3.x con cambios incompatibles.

---

## 6.8 B8 — Configuración de pruebas inexistente en el destino

| Ítem | Detalle |
|---|---|
| **Qué es** | ErgoApp corre su suite con `--settings=ergonomia_srt.test_settings`. ErgoSolutions no tiene equivalente |
| **Dónde** | `ergonomia_srt/test_settings.py` (existe) vs `config/` (no lo tiene) **[VERIFICADO — `ls config/`]** |
| **Por qué bloquea** | Sin él, las 160 pruebas trasplantadas (a) exigen PostgreSQL con permisos de creación de base; (b) usan `DatabaseCache` sobre una tabla inexistente en la base de test; (c) fallan al renderizar templates por `CompressedManifestStaticFilesStorage` sin `collectstatic` previo |
| **Severidad** | Alta. **Sin esto no hay criterio de aceptación verificable para ninguna fase** |

### Qué hace el del origen **[VERIFICADO — `ergonomia_srt/test_settings.py`]**

```python
from .settings import *

DATABASES = {"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": ":memory:"}}
CACHES = {"default": {"BACKEND": "…locmem.LocMemCache", "LOCATION": "ergoapp-tests"}}
PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]
STORAGES = {
    "default":     {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {"BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"},
}
```

### Resolución **[PROPUESTA]**

```python
# config/test_settings.py   [PROPUESTA]
"""Configuración aislada para la suite automatizada de ErgoSolutions.

Evita que las pruebas dependan de permisos para crear bases PostgreSQL y
garantiza que nunca operen sobre la base configurada en `.env`.
"""
import os
from .settings import *  # noqa: F403

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": os.environ.get("ERGOSOLUTIONS_TEST_DATABASE_NAME", ":memory:"),
    }
}

# La tabla de DatabaseCache es infraestructura de despliegue, no una migración.
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "ergosolutions-tests",
    }
}

PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]

# Las pruebas de render no ejecutan collectstatic.
STORAGES = {
    "default":     {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {"BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"},
}

# El envío de correo no debe salir del proceso durante las pruebas.
EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"
```

### Verificación previa **[PENDIENTE]**

**Las 32 pruebas actuales del destino deben seguir pasando bajo la nueva configuración** antes de trasplantar nada:

```bash
.venv/bin/python manage.py test apps --settings=config.test_settings
```

Hoy pasan con `config.settings` sobre PostgreSQL. El cambio a SQLite podría exponer dependencias del motor —por ejemplo `UniqueConstraint` con `condition` en `ContactRequest` (`apps/company/models.py:330-336`), que SQLite soporta pero con semántica de índice parcial. **Debe comprobarse en la Fase 0, no asumirse.**

### Riesgo que introduce la corrección

**Bajo, pero con una advertencia:** SQLite y PostgreSQL no son intercambiables. Una suite que pasa en SQLite puede ocultar un defecto que sólo aparece en PostgreSQL. **[PROPUESTA]** Si aparecen divergencias, la alternativa es conservar PostgreSQL en las pruebas y limitar el `test_settings` a sobrescribir `CACHES`, `STORAGES`, `PASSWORD_HASHERS` y `EMAIL_BACKEND` — que son los cuatro cambios realmente imprescindibles.

---

## 6.9 Cuadro resumen de bloqueantes

| ID | Bloqueante | Archivo:línea | Esfuerzo | Riesgo de la corrección | Fase |
|---|---|---|---|---|:---:|
| **B1** | Modelo de usuario | `planillas/models.py:4,9` | 1 línea | **Nulo** — sin migración (H-G) | 1 |
| **B2** | Layout de apps | 102 imports + 48 cadenas literales | 2,5 j | **Medio** — mitigado con `checks.py` | 2 |
| **B3** | Namespaces de URL | `planillas/urls.py`, `help_ai/urls.py:9-10` + 35 referencias | 0,5 j | Bajo — resolver H-J antes | 1 |
| **B4** | Caché compartida | Ausencia en `config/settings.py` | 0,2 j | Bajo — recordar `createcachetable` | 0 |
| **B5** | CSP *(degradado)* | `config/settings.py:52-61` | 2,0 j | **Alto** — requiere remediar 14 puntos del frontend | 6 |
| **B6** | Rutas de `help_ai` | `help_ai/prompts.py:14-15` | 2 líneas | Bajo — 22 pruebas lo verifican | 2 |
| **B7** | `pypdf` ausente | `requirements.txt` del destino | 1 línea | Nulo | 0 |
| **B8** | Sin `test_settings` | `config/` | 0,3 j | Bajo — verificar los 32 tests antes | 0 |

---
# PARTE VII — ARQUITECTURA DE DESTINO PROPUESTA

## 7.1 Principio de organización

El módulo se instala como un **paquete contenedor identificable y desmontable**: `apps/ergonomia_886/`. Todo lo que pertenece al protocolo SRT 886/15 vive dentro; nada de ErgoSolutions depende de él salvo tres puntos de contacto explícitos y documentados.

Las tres reglas que hacen esto verificable:

1. **La dependencia es unidireccional.** El módulo importa de `apps.company` y `apps.accounts`. **Ninguna app del destino importa nada del módulo.**
2. **Los puntos de contacto son exactamente tres:** una línea en `config/urls.py`, una tarjeta en `templates/dashboard/home.html` y una entrada de navegación en `templates/base_dashboard.html`.
3. **Desmontarlo son cinco pasos:** quitar las 4 entradas de `INSTALLED_APPS`, la línea de `config/urls.py`, los dos puntos de plantilla, y borrar el directorio.

Esto no es purismo: es lo que permite que el módulo se pueda deshabilitar si algo sale mal en producción, sin revertir la rama entera.

## 7.2 Decisiones de arquitectura

| # | Decisión | Opciones evaluadas | **Resolución** | Motivo |
|---|---|---|---|---|
| **D-1** | Qué hacer con `core` | Disolver / conservar como app | **Disolver** | Login y registro ya existen en el destino con tres backends. `core/tests.py` tiene 0 pruebas, así que no hay pérdida de cobertura. Su dashboard se reimplanta en `planillas` |
| **D-2** | `app_label` de las apps trasplantadas | Conservar / prefijar (`ergonomia_886_planillas`) | **Conservar** | **[VERIFICADO]** No hay colisión con los 9 labels del destino. Conservar mantiene las 10 migraciones intactas y evita `SeparateDatabaseAndState` |
| **D-3** | Estructura del paquete | Paquete contenedor / 4 apps sueltas en `apps/` | **Paquete contenedor** | Hace el módulo identificable y desmontable. Con labels planos, no cuesta nada |
| **D-4** | Prefijo de URL | `/evaluacion-ergonomica/` · `/886/` · `/protocolo/` | **`/evaluacion-ergonomica/`** | Legible, en español, sin jerga normativa. Deja lugar a futuros módulos (`/evaluacion-ruido/`, `/evaluacion-iluminacion/`) |
| **D-5** | Dónde montar `help_ai` | `/ai/` (como en origen) / dentro del prefijo del módulo | **Dentro del módulo** | `/ai/` ya está ocupado por `ergobot_ai` (H-C). Además refuerza CF-1: son dos productos distintos en dos lugares distintos |
| **D-6** | Relación entre los dos asistentes IA | — | **Sin opciones: rige CF-1** | Coexisten como apps separadas |
| **D-7** | Setting del modelo de IA | `CHAT_AI_MODEL` / `OPENAI_MODEL` | **`CHAT_AI_MODEL` deriva de `OPENAI_MODEL`** | Única unificación admitida por CF-1. Ver Área 10 |
| **D-8** | Driver PostgreSQL | psycopg2 / psycopg 3 | **psycopg 3**, el del destino | No requiere cambios de código |
| **D-9** | Multi-tenencia | Por usuario / por empresa / mixta | **Mixta** | La evaluación pertenece a un profesional **y** opcionalmente a una empresa. Ver §7.6 |
| **D-10** | CORS | Conservar / quitar | **Quitar** | El destino no expone API para terceros |
| **D-11** | Nombre del campo `usuario` | Conservar / renombrar a `profesional` | **Conservar** | 38 apariciones, 22 en suites de prueba. Ver Área 3 |
| **D-12** | CSP | Fase 0 / fase separada | **Fase separada (6)** | El frontend del destino requiere remediación previa. Ver H-K y Área 12 |

## 7.3 Árbol de directorios resultante

```
/Users/praguirre/ergocapacitacion/
├── config/
│   ├── settings.py                    ← + CACHES, + 14 settings del módulo,
│   │                                    + CHAT_AI_MODEL derivado, + 4 apps
│   ├── test_settings.py               ← NUEVO (B8)
│   ├── middleware.py                  ← NUEVO en Fase 6 (CSP)
│   ├── urls.py                        ← + 1 línea: /evaluacion-ergonomica/
│   ├── asgi.py
│   └── wsgi.py
│
├── apps/
│   ├── accounts/                      ← sin cambios
│   ├── landing/                       ← sin cambios
│   ├── dashboard/
│   │   ├── views.py                   ← sin cambios (la vista de listado va en planillas)
│   │   └── urls.py                    ← sin cambios
│   ├── company/                       ← sin cambios
│   ├── training/  quiz/  certificates/  presencial/   ← sin cambios
│   ├── ergobot_ai/                    ← sin cambios (CF-1)
│   │
│   └── ergonomia_886/                 ★ NUEVO — paquete contenedor del módulo
│       ├── __init__.py
│       ├── checks.py                  ← [PROPUESTA] valida las 48 rutas declarativas
│       │
│       ├── planillas/                 ← app: protocolo documental
│       │   ├── __init__.py
│       │   ├── apps.py                ← name = 'apps.ergonomia_886.planillas'
│       │   ├── models.py              ← Evaluacion (+ empresa), Planilla1 (+ trabajadores),
│       │   │                            FactorRiesgo, Planilla2A–2I, Planilla3,
│       │   │                            MedidaEspecifica, SeguimientoMedida
│       │   ├── forms.py
│       │   ├── views.py               ← + evaluacion_list_view, + eliminar_evaluacion_view
│       │   ├── signals.py             ← [PROPUESTA] sincronización con AgendaEvent
│       │   ├── urls.py                ← app_name = "planillas"
│       │   ├── admin.py
│       │   ├── tests.py
│       │   ├── migrations/            ← 0001_initial (copiada) + 0002 (empresa) + 0003 (M2M)
│       │   └── templates/planillas/
│       │       ├── evaluacion_list.html         ← reimplantado desde core/dashboard.html
│       │       ├── crear_evaluacion.html
│       │       ├── detalle_evaluacion.html
│       │       ├── planilla1_form.html
│       │       ├── planilla2_structured_form.html
│       │       ├── planilla3_form.html
│       │       └── planilla4_form.html
│       │
│       ├── evaluaciones/              ← app: 13 factores y motor de cálculo
│       │   ├── apps.py                ← name = 'apps.ergonomia_886.evaluaciones'
│       │   ├── catalog.py             ← 26 rutas actualizadas
│       │   ├── calculators.py         ← 1 ruta de recurso actualizada
│       │   ├── models.py  forms.py  views.py  choices.py  pdf.py  admin.py  urls.py
│       │   ├── tests.py               ← 45 pruebas
│       │   ├── data/                  ← 13 artefactos normativos + README.md
│       │   ├── fixtures/
│       │   ├── migrations/            ← 0001 … 0007 (copiadas sin modificar)
│       │   └── templates/evaluaciones/    ← 16 templates
│       │
│       ├── exportaciones/             ← app: documentos oficiales e informes
│       │   ├── apps.py                ← name = 'apps.ergonomia_886.exportaciones'
│       │   ├── models.py  serializers.py  packaging.py  views.py  urls.py
│       │   ├── vocabulario.py  admin.py
│       │   ├── official/
│       │   │   ├── catalog.py         ← 12 model_path actualizados
│       │   │   ├── builders.py  overlay.py  calibrate.py
│       │   │   ├── maps/              ← 12 JSON de calibración
│       │   │   └── templates_bin/
│       │   │       └── res_srt_886_15-formulario.pdf   ← SHA-256 verificado al cargar
│       │   ├── reports/
│       │   │   ├── llm.py             ← sanitize_payload — CF-4
│       │   │   ├── limits.py  pdf.py  prompts.py
│       │   ├── migrations/            ← 0001, 0002 (copiadas sin modificar)
│       │   ├── templates/exportaciones/
│       │   └── tests/                 ← 92 pruebas en 5 archivos
│       │
│       └── help_ai/                   ← app: ayuda contextual + chat (CF-1)
│           ├── apps.py                ← name = 'apps.ergonomia_886.help_ai'
│           ├── prompts.py             ← B6: ruta corregida
│           ├── agents.py  catalog.py  limits.py  views.py  urls.py  tracing.py
│           └── tests.py               ← 22 pruebas
│
├── templates/
│   ├── base.html                      ← sin cambios
│   ├── base_dashboard.html            ← + navegación Evaluaciones, + include del widget,
│   │                                    Fase 6: CDN → vendor/ local
│   ├── base_landing.html              ← Fase 6: CDN → vendor/ local
│   ├── dashboard/
│   │   └── home.html                  ← ★ tarjeta Evaluaciones ACTIVADA (§7.7)
│   └── ergonomia_886/
│       └── _help_widget.html          ← NUEVO: widget extraído de base.html del origen
│
├── static/
│   ├── css/  js/                      ← existentes
│   ├── ayuda/
│   │   ├── css/help_widget.css
│   │   ├── js/help_widget.js
│   │   └── help_texts/                ← 33 documentos .md
│   ├── js/planilla_logic.js
│   └── vendor/                        ← Bootstrap 5.3.3, Icons 1.11.3, marked, DOMPurify
│
├── media/                             ← ya existe. + evidencia_vce/, + certificados_vce/
├── requirements.txt                   ← + pypdf, + pillow
└── docs/
    └── INTEGRACION_MODULO_ERGONOMIA_886_PROPUESTA_TECNICA.md   ← este documento
```

## 7.4 URLs y namespaces

### Registro en `config/urls.py` **[PROPUESTA]**

Una sola línea nueva:

```python
urlpatterns = [
    path("admin/", admin.site.urls),
    path("dashboard/", include("apps.dashboard.urls", namespace="dashboard")),
    path("", include("apps.landing.urls", namespace="landing")),
    path("acceso/", include("apps.accounts.urls")),
    path("capacitacion/", include("apps.training.urls")),
    path("quiz/", include("apps.quiz.urls")),
    path("certificados/", include("apps.certificates.urls")),
    path("ai/", include("apps.ergobot_ai.urls")),          # chatbot docente — sin cambios

    # ★ Módulo de Ergonomía SRT 886/15
    path(
        "evaluacion-ergonomica/",
        include(
            ("apps.ergonomia_886.urls", "ergonomia_886"),
            namespace="ergonomia_886",
        ),
    ),

    path("auth/", include((..., "accounts_professional"), namespace="accounts_professional")),
    path("empresa/auth/", include((..., "accounts_company"), namespace="accounts_company")),
    path("c/", include("apps.training.urls_public")),
]
```

### URLconf del módulo — `apps/ergonomia_886/urls.py` **[PROPUESTA]**

```python
# apps/ergonomia_886/urls.py   [PROPUESTA]
from django.urls import include, path

from .planillas import views as planillas_views

app_name = "ergonomia_886"

urlpatterns = [
    # Aterrizaje del módulo: listado de evaluaciones ergonómicas.
    # Reimplanta core.dashboard_view con su búsqueda, filtros y paginación.
    path("", planillas_views.evaluacion_list_view, name="evaluacion_list"),
    path("<int:evaluacion_id>/eliminar/", planillas_views.eliminar_evaluacion_view,
         name="eliminar_evaluacion"),

    path("protocolo/",     include("apps.ergonomia_886.planillas.urls")),
    path("factores/",      include("apps.ergonomia_886.evaluaciones.urls")),
    path("documentos/",    include("apps.ergonomia_886.exportaciones.urls")),
    path("ayuda/",         include("apps.ergonomia_886.help_ai.urls")),
]
```

### Mapa de URLs resultante

| URL final | Namespace completo | Origen |
|---|---|---|
| `/evaluacion-ergonomica/` | `ergonomia_886:evaluacion_list` | `core:dashboard` reimplantado |
| `/evaluacion-ergonomica/<id>/eliminar/` | `ergonomia_886:eliminar_evaluacion` | `core:eliminar_evaluacion` |
| `/evaluacion-ergonomica/protocolo/crear/` | `ergonomia_886:planillas:crear_evaluacion` | `crear_evaluacion` |
| `/evaluacion-ergonomica/protocolo/<id>/` | `ergonomia_886:planillas:detalle_evaluacion` | `detalle_evaluacion` |
| `/evaluacion-ergonomica/protocolo/<id>/planilla1/` | `ergonomia_886:planillas:planilla1` | `planilla1` |
| … `planilla2a` … `planilla2i`, `planilla3`, `planilla4` | `ergonomia_886:planillas:planillaN` | idem |
| `/evaluacion-ergonomica/factores/<id>/lmc/` | `ergonomia_886:evaluaciones:lmc_form_by_eval` | `evaluaciones:*` |
| … los 13 factores × 2 variantes | idem | idem |
| `/evaluacion-ergonomica/factores/<id>/resumen/` | `ergonomia_886:evaluaciones:wizard_resumen_by_eval` | idem |
| `/evaluacion-ergonomica/documentos/<id>/` | `ergonomia_886:exportaciones:panel` | `exportaciones:*` |
| `/evaluacion-ergonomica/documentos/<id>/oficial/<slug>.pdf` | `ergonomia_886:exportaciones:planilla_oficial` | idem |
| `/evaluacion-ergonomica/ayuda/guide/<slug>/` | `ergonomia_886:help_ai:help_guide` | `help_guide` |
| `/evaluacion-ergonomica/ayuda/chat/<slug>/` | `ergonomia_886:help_ai:chat_ai` | `chat_ai` |

> **Consecuencia sobre B3.** Con `app_name` en el URLconf del módulo, los namespaces quedan **anidados a dos niveles**: `ergonomia_886:planillas:planilla1`. Las 35 referencias de B3 deben calificarse con el prefijo completo. Las que ya tenían namespace (`evaluaciones:*`, `exportaciones:*` — 10 referencias en templates y 21 en Python) **también** deben prefijarse.
>
> **[PROPUESTA] Alternativa más barata:** no declarar `app_name` en `apps/ergonomia_886/urls.py` y montar los includes con sus namespaces planos (`planillas:`, `evaluaciones:`, `exportaciones:`, `help_ai:`). Se pierde el prefijo de módulo en los nombres, pero se ahorran 31 reescrituras adicionales y las referencias existentes de `evaluaciones:*` y `exportaciones:*` quedan intactas.
>
> **Recomendación: la alternativa plana.** El agrupamiento físico en `apps/ergonomia_886/` ya da identidad al módulo; el prefijo en cada nombre de URL aporta poco y multiplica el trabajo mecánico —que es justamente donde está el riesgo R-1. Si más adelante se agregan módulos con nombres de URL en conflicto, el prefijo puede introducirse entonces.

### Prefijos ocupados — verificación de colisión **[VERIFICADO]**

| Prefijo | Ocupante | ¿Colisiona con `/evaluacion-ergonomica/`? |
|---|---|---|
| `/admin/`, `/dashboard/`, `/acceso/`, `/capacitacion/`, `/quiz/`, `/certificados/`, `/ai/`, `/auth/`, `/empresa/auth/`, `/c/` | Apps del destino | ❌ No |
| `/` | `apps.landing.urls` | ❌ No. Es un catch-all de rutas concretas, no un patrón abierto |

## 7.5 Registro en `INSTALLED_APPS` **[PROPUESTA]**

```python
LOCAL_APPS = [
    "apps.accounts",
    "apps.landing",
    "apps.dashboard",
    "apps.presencial",
    "apps.company",
    "apps.training",
    "apps.quiz",
    "apps.certificates",
    "apps.ergobot_ai",              # chatbot docente — CF-1: NO se fusiona

    # ── Módulo de Ergonomía SRT 886/15 ──────────────────────────────
    "apps.ergonomia_886.planillas",
    "apps.ergonomia_886.evaluaciones",
    "apps.ergonomia_886.exportaciones",
    "apps.ergonomia_886.help_ai",   # ayuda del protocolo — CF-1: NO se fusiona
]
```

**Orden deliberado:** `planillas` antes que `evaluaciones` y `exportaciones`, porque contiene el modelo raíz del que dependen las claves foráneas de las demás. Django resuelve el orden de migraciones por dependencias declaradas, no por `INSTALLED_APPS`, pero mantenerlo coherente ayuda a leer el archivo.

**`apps.ergonomia_886` no se registra**: es un paquete contenedor sin modelos ni `AppConfig`. Sólo agrupa.

## 7.6 Multi-tenencia y propiedad **[PROPUESTA]**

La decisión D-9 establece propiedad **mixta**: una evaluación pertenece a un profesional y, opcionalmente, a una empresa. El filtro debe depender del `user_type`.

```python
# apps/ergonomia_886/planillas/querysets.py   [PROPUESTA]

def evaluaciones_visibles_para(user):
    """Devuelve las evaluaciones que `user` puede ver, según su tipo.

    - professional : las que él creó.
    - company      : las de su propia empresa, sin importar qué profesional las hizo.
    - trainee      : ninguna. El módulo es del backoffice.
    """
    qs = Evaluacion.objects.all()

    if user.is_professional:
        return qs.filter(usuario=user)

    if user.is_company:
        try:
            return qs.filter(empresa=user.company_profile)
        except CompanyProfile.DoesNotExist:
            return qs.none()

    return qs.none()
```

Reglas complementarias:

| Regla | Justificación |
|---|---|
| Todas las vistas del módulo llevan `@login_required` **y** `@backoffice_required` | `backoffice_required` = `professional ∪ company` (`CustomUser.is_backoffice_user`). El orden importa: `@login_required` primero, para no repetir el defecto N1 |
| El recurso ajeno responde **404, no 403** | Preserva la garantía de no enumeración del origen |
| Una empresa **no puede crear ni editar** evaluaciones: sólo consultarlas y descargar sus documentos | Emitir un protocolo es un acto profesional. Un usuario `company` no tiene matrícula |
| Un profesional ve las suyas aunque la empresa no sea usuaria de la plataforma | `empresa` es nullable |

> **[PROPUESTA] Punto abierto que debe decidirse antes de la Fase 3.** ¿Un profesional puede ver las evaluaciones que **otro** profesional hizo para una empresa con la que ambos trabajan? El modelo de `ContactRequest` sugiere que la relación empresa–profesional es explícita y podría habilitarlo. La propuesta conservadora —y la que se implementa arriba— es **no**: cada profesional ve sólo lo suyo, que es el comportamiento actual de ErgoApp. Ampliarlo después es aditivo; restringirlo después rompe expectativas.

## 7.7 La tarjeta «Evaluaciones» del dashboard

### Estado actual **[VERIFICADO — `templates/dashboard/home.html:79-96`]**

```html
<!-- Card EVALUACIONES (desactivado) -->
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

### Estado propuesto **[PROPUESTA]**

```html
<!-- Card EVALUACIONES (activo) -->
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
                    evaluación de 13 riesgos y planillas oficiales.
                </p>
                <span class="badge bg-primary fs-6 px-3 py-2">
                    <i class="bi bi-check-circle me-1"></i>Disponible
                </span>
            </div>
        </div>
    </a>
</div>
```

Cambios y su motivo:

| Cambio | Motivo |
|---|---|
| Se envuelve en `<a href="{% url 'ergonomia_886:evaluacion_list' %}">` | Replica exactamente el patrón de la tarjeta Capacitaciones (`:100`), que ya funciona |
| Se quita `disabled-card` | Es la clase que aplica el aspecto atenuado |
| `border-secondary` → `border-primary`; `text-secondary` → `text-primary` / `text-white` | Distingue Evaluaciones (azul) de Capacitaciones (verde). Consistente con el ícono del navbar |
| Badge `bg-warning` «Próximamente» → `bg-primary` «Disponible» | Es el objetivo declarado |
| Se reescribe el texto descriptivo | **Importante:** el texto actual promete «iluminación, ruido y más», que **este módulo no entrega**. Prometer funcionalidad inexistente en la pantalla principal es peor que decir «Próximamente». El texto nuevo describe exactamente lo que hay |

> **[PROPUESTA] Nota de producto.** Iluminación y ruido son módulos futuros. Cuando existan, corresponde una tarjeta por módulo o un submenú dentro de Evaluaciones —no ampliar la promesa de esta tarjeta antes de tiempo.

### Stats del dashboard **[PROPUESTA]**

`apps/dashboard/views.py:44-58` calcula tres stats. Se propone una cuarta:

```python
def _professional_dashboard(request):
    ...
    stats = {
        "capacitaciones_total": presencial_count,
        "links_generados": links_count,
        "trabajadores_capacitados": total_accesses,
        "evaluaciones_ergonomicas": _contar_evaluaciones(request.user),   # ← nueva
    }
```

Con la salvedad de la regla 1 de §7.1: `apps.dashboard` **no debe importar** modelos del módulo. La forma correcta es un import diferido dentro de la función, con degradación limpia si el módulo no está instalado:

```python
def _contar_evaluaciones(user):
    """Cuenta evaluaciones ergonómicas. Devuelve None si el módulo no está instalado."""
    try:
        from apps.ergonomia_886.planillas.models import Evaluacion
    except ImportError:
        return None
    return Evaluacion.objects.filter(usuario=user).count()
```

Y el template renderiza la stat sólo si no es `None`. Así el dashboard sigue funcionando con el módulo desmontado.

## 7.8 Navegación

**[PROPUESTA]** En `templates/base_dashboard.html`, tras el `<li>` de Capacitaciones (`:37-42`):

```django
<li class="nav-item">
    <a class="nav-link {% if 'evaluacion-ergonomica' in request.path %}active{% endif %}"
       href="{% url 'ergonomia_886:evaluacion_list' %}">
        <i class="bi bi-clipboard-check me-1"></i>Evaluaciones
    </a>
</li>
```

Se usa `request.path` en lugar de `request.resolver_match.url_name` porque el módulo tiene muchos nombres de vista y todos deben marcar el ítem como activo. Es el mismo criterio que ya usan los ítems de Nómina y Agenda (`:45`, `:51`).

## 7.9 Widget de ayuda contextual

**[PROPUESTA]** `templates/ergonomia_886/_help_widget.html` — extraído de `templates/base.html:49-113` del origen, con las dos URLs calificadas:

```django
{# templates/ergonomia_886/_help_widget.html #}
{# Widget de ayuda contextual del módulo SRT 886/15.                        #}
{# Se incluye SOLO en las pantallas del módulo: fuera de él no hay contenido #}
{# de ayuda que mostrar y sus URLs no estarían disponibles.                  #}
{# CF-1: este widget pertenece a help_ai. NO tiene relación con ergobot_ai.  #}

<button id="helpToggle" class="btn btn-primary rounded-circle position-fixed bottom-0 end-0 m-4 shadow-lg"
        style="width:60px;height:60px;z-index:1050;" type="button"
        aria-label="Abrir ayuda contextual" title="Abrir ayuda contextual">
  <i class="bi bi-question-lg fs-4"></i>
</button>

<div id="helpWidget" class="offcanvas offcanvas-end" tabindex="-1"
     data-page-slug="{% block help_slug %}home{% endblock %}"
     data-guide-url-template="{% url 'help_ai:help_guide' slug='__slug__' %}"
     data-chat-url-template="{% url 'help_ai:chat_ai' slug='__slug__' %}">
  ...  {# pestañas Guía y Chat IA, sin cambios respecto del origen #}
</div>
```

**Punto delicado [PENDIENTE]:** `{% block help_slug %}` dentro de un `{% include %}` **no funciona** — los bloques no atraviesan la frontera del include. La solución es pasar el slug por contexto:

```django
{# en base_dashboard.html #}
{% if help_slug %}
  {% include "ergonomia_886/_help_widget.html" %}
{% endif %}
```

y que cada vista del módulo aporte `help_slug` en su contexto, en lugar de declararlo como bloque de plantilla. **Esto implica tocar los 23 templates que hoy usan `{% block help_slug %}`** y sus vistas correspondientes.

**[PROPUESTA] Alternativa de menor impacto:** conservar el mecanismo de bloques creando una plantilla intermedia del módulo:

```
templates/ergonomia_886/base_886.html
    {% extends "base_dashboard.html" %}
    {% block content_wrapper %}
        {% block content %}{% endblock %}
        {# widget con {% block help_slug %}home{% endblock %} #}
    {% endblock %}
```

y que los 10 templates del módulo extiendan `ergonomia_886/base_886.html` en lugar de `base_dashboard.html`. **Los 23 `{% block help_slug %}` siguen funcionando sin tocarlos**, porque la herencia de bloques sí atraviesa `{% extends %}`.

**Recomendación: la plantilla intermedia.** Cuesta un archivo, evita tocar 23 templates más sus vistas, y tiene la ventaja de dar al módulo un punto único donde ajustar su layout.

---

# PARTE VIII — MODELO DE DATOS INTEGRADO

## 8.1 Diagrama de relaciones final **[PROPUESTA]**

```
accounts.CustomUser  (AUTH_USER_MODEL)
    │
    ├── 1:1 ──> company.CompanyProfile ────────────────────┐
    │                │                                     │
    │                ├── 1:N ──> company.CompanyWorker     │
    │                ├── 1:N ──> company.AgendaEvent  <────┼──┐ (sincronización
    │                └── 1:N ──> company.ContactRequest    │  │  desde Planilla 4)
    │                                                      │  │
    │ N (usuario / profesional responsable)     N (empresa)│  │
    ▼                                                      ▼  │
════ ergonomia_886.planillas.Evaluacion ═══════════ raíz del dominio
    │       · usuario     FK  → accounts.CustomUser   [CASCADE]
    │       · empresa     FK  → company.CompanyProfile [PROTECT, nullable]   ★ NUEVO
    │       · razon_social, cuit, ciiu, direccion_establecimiento, provincia
    │         ↑ respaldo histórico del documento emitido — NO se re-sincronizan
    │
    ├─ 1:1  Planilla1
    │         · trabajadores  M2M → company.CompanyWorker  [nullable]        ★ NUEVO
    │         · nombres_trabajadores TextField ← respaldo histórico
    │         └─ 1:N  FactorRiesgo            (9 filas: A…I)
    │
    ├─ 1:N  Planilla2A … Planilla2I           (9 modelos, N instancias c/u)
    │
    ├─ 1:1  Planilla3
    │         └─ 1:N  MedidaEspecifica
    │                   └─ 1:1  SeguimientoMedida  ──► crea/actualiza AgendaEvent ─┘
    │                                                  (related_object_type/id)
    │
    ├─ 1:1  evaluaciones.RiskEvaluation
    │         · creado_por FK → accounts.CustomUser [SET_NULL]
    │         ├─ 1:N  LMC_Eval
    │         ├─ 1:N  EmpujeInicial_Eval  / EmpujeSostenida_Eval
    │         ├─ 1:N  TraccionInicial_Eval / TraccionSostenida_Eval
    │         ├─ 1:N  Transporte_Eval
    │         ├─ 1:N  Bipedestacion_Eval
    │         ├─ 1:N  RepetitivosMS_Eval
    │         ├─ 1:N  PosturasForzadas_Eval
    │         ├─ 1:N  VibracionMB_Eval
    │         ├─ 1:N  VibracionCE_Eval ──── 1:N  VCESegment
    │         │         · foto_montaje           ImageField → media/evidencia_vce/     ★ ahora servible
    │         │         · certificado_calibracion FileField → media/certificados_vce/  ★ ahora servible
    │         ├─ 1:N  ConfortTermico_Eval
    │         └─ 1:N  EstresContacto_Eval
    │
    ├─ 1:N  exportaciones.GeneratedReport   · generado_por FK → CustomUser [SET_NULL]
    └─ 1:N  exportaciones.ExportAudit       · usuario     FK → CustomUser [SET_NULL]
```

**Puntos de contacto con el dominio preexistente — sólo tres, todos salientes:**

| # | Desde | Hacia | Cardinalidad | `on_delete` |
|---|---|---|---|---|
| 1 | `Evaluacion.usuario` | `accounts.CustomUser` | N:1 | `CASCADE` |
| 2 | `Evaluacion.empresa` | `company.CompanyProfile` | N:1 nullable | **`PROTECT`** |
| 3 | `Planilla1.trabajadores` | `company.CompanyWorker` | M:N | tabla intermedia |

Más una relación **lógica, no de base**: `SeguimientoMedida` → `AgendaEvent` vía `related_object_type` + `related_object_id`, que son campos de texto. **Deliberadamente no es una FK**, para no obligar a `apps.company` a conocer el módulo.

## 8.2 Vinculación con `CompanyProfile`

### Definición **[PROPUESTA]**

```python
empresa = models.ForeignKey(
    "company.CompanyProfile",
    on_delete=models.PROTECT,
    related_name="evaluaciones_ergonomicas",
    null=True, blank=True,
    verbose_name="Empresa evaluada",
)
```

| Elección | Motivo |
|---|---|
| **`PROTECT`** y no `CASCADE` | Borrar una empresa con protocolos emitidos debe fallar de forma ruidosa. Un protocolo es documentación legal con obligación de conservación |
| **`PROTECT`** y no `SET_NULL` | `SET_NULL` dejaría protocolos huérfanos de empresa sin que nadie se entere. Los campos de texto seguirían teniendo los datos, pero se perdería la trazabilidad relacional |
| **`null=True`** | Permite evaluar empresas que no son usuarias de la plataforma — el caso mayoritario al principio |
| Referencia por cadena `"company.CompanyProfile"` | Evita el import y con él cualquier riesgo de ciclo entre `planillas` y `company` |

### Poblado de los campos de respaldo **[PROPUESTA]**

```python
# apps/ergonomia_886/planillas/forms.py   [PROPUESTA]

class EvaluacionForm(forms.ModelForm):
    def save(self, commit=True):
        evaluacion = super().save(commit=False)
        empresa = self.cleaned_data.get("empresa")

        # Los campos del documento se pueblan UNA SOLA VEZ, al crear.
        # Nunca se re-sincronizan: la planilla debe reflejar los datos
        # vigentes al momento del relevamiento (ver Área 3 y CF-5).
        if empresa and evaluacion.pk is None:
            evaluacion.razon_social = evaluacion.razon_social or empresa.razon_social
            evaluacion.cuit = evaluacion.cuit or empresa.cuit
            evaluacion.direccion_establecimiento = (
                evaluacion.direccion_establecimiento or empresa.domicilio
            )
            evaluacion.provincia = evaluacion.provincia or empresa.provincia

        if commit:
            evaluacion.save()
        return evaluacion
```

La condición `evaluacion.pk is None` es la que garantiza la inmutabilidad histórica. El `or` preserva lo que el profesional haya tipeado: si corrigió el domicilio para una sucursal específica, su valor gana.

> **[PROPUESTA] Advertencia sobre longitudes.** Los campos del origen son más cortos que los del destino:
>
> | Campo | `CompanyProfile` | `Evaluacion` | Riesgo |
> |---|---:|---:|---|
> | Razón social | 300 | **255** | Truncamiento en 45 caracteres |
> | CUIT | 20 | **13** | Truncamiento en 7 caracteres |
> | Domicilio | 400 | **255** | Truncamiento en 145 caracteres |
>
> Copiar sin validar produciría un `DataError` en PostgreSQL. **Dos opciones:** ampliar los campos de `Evaluacion` a las longitudes del destino (recomendado — es una migración trivial sobre tablas vacías, y evita perder datos), o truncar explícitamente con aviso al usuario. **Recomendación: ampliar.** El formulario oficial de la SRT tiene ancho limitado, pero eso es un problema de renderizado del PDF, no de almacenamiento.
>
> Nótese que `CompanyProfile.cuit` es `CharField(20)` porque admite el formato `XX-XXXXXXXX-X` con guiones (13 caracteres) más margen. `Evaluacion.cuit` con 13 es justo. Ampliarlo a 20 alinea ambos.

## 8.3 Vinculación con `CustomUser`

**No requiere ningún cambio de definición** más allá de B1. Los cuatro FK al modelo de usuario quedan así:

| Modelo | Campo | `on_delete` | Estado |
|---|---|---|---|
| `planillas.Evaluacion` | `usuario` | `CASCADE` | 🔧 **B1**: cambiar a `settings.AUTH_USER_MODEL` |
| `evaluaciones.RiskEvaluation` | `creado_por` | `SET_NULL` | ✅ Ya correcto |
| `exportaciones.GeneratedReport` | `generado_por` | `SET_NULL` | ✅ Ya correcto |
| `exportaciones.ExportAudit` | `usuario` | `SET_NULL` | ✅ Ya correcto |

> **[PROPUESTA] Observación sobre `CASCADE` en `Evaluacion.usuario`.** Borrar un profesional borra en cascada todas sus evaluaciones, sus 13 factores, sus informes generados y su auditoría de descargas. Para documentación con valor legal es agresivo. **`PROTECT` sería más correcto**, obligando a reasignar antes de dar de baja. Se señala como mejora recomendada, pero **no se propone cambiarlo en esta integración**: alteraría el comportamiento actual de ErgoApp y merece decidirse aparte, junto con la política de baja de profesionales del destino.

### Uso de `profession` y `license_number` **[PROPUESTA]**

Habilita la oportunidad O-2 (firmantes). Las 12 páginas oficiales piden tres firmas: empleador, responsable de Higiene y Seguridad, y responsable de Medicina del Trabajo. Hoy salen en blanco (deuda D-3, hueco G-1).

Con los datos disponibles se puede imprimir la **aclaración** bajo la línea de firma, dejando el trazo manuscrito al profesional:

| Recuadro | Fuente de la aclaración |
|---|---|
| Empleador | `evaluacion.empresa.contacto_nombre` + `contacto_cargo` |
| Responsable de Higiene y Seguridad | `evaluacion.usuario.display_name` + `profession` + `license_number` |
| Responsable de Medicina del Trabajo | **Se deja en blanco** |

> **El tercer recuadro debe quedar vacío.** No hay ningún dato en el sistema que identifique al médico laboral, y **CF-5 prohíbe que un documento oficial afirme lo que nadie declaró**. Imprimir ahí el nombre del profesional de Higiene y Seguridad sería una falsedad documental. El hueco G-1 se cierra parcialmente, y eso es lo correcto.
>
> Si un `CustomUser` no tiene `profession` ni `license_number` cargados —ambos son `blank=True, default=""`—, la aclaración correspondiente **también se deja en blanco**, por el mismo criterio.

## 8.4 Campos conservados como respaldo histórico

Resumen consolidado de la decisión transversal de las Áreas 3 y 4.

| Campo | Modelo | Fuente estructurada equivalente | Por qué se conserva |
|---|---|---|---|
| `razon_social` | `Evaluacion` | `empresa.razon_social` | La planilla firmada declara la razón social vigente al relevamiento |
| `cuit` | `Evaluacion` | `empresa.cuit` | Ídem. Una empresa puede reorganizarse societariamente |
| `direccion_establecimiento` | `Evaluacion` | `empresa.domicilio` | **El caso más claro:** el relevamiento ocurrió en un domicilio físico concreto |
| `provincia` | `Evaluacion` | `empresa.provincia` | Ídem, y determina la jurisdicción de presentación |
| `ciiu` | `Evaluacion` | *(ninguna)* | No tiene equivalente. `rubro` es texto libre, CIIU es un código |
| `nombres_trabajadores` | `Planilla1` | `trabajadores` (M2M) | Puede incluir personal no registrado en la plataforma. Un cambio de nómina no debe alterar un protocolo emitido |
| `nro_trabajadores` | `Planilla1` | *(ninguna)* | Es el total del puesto, que puede exceder a los relevados nominalmente |

**Regla única y explícita, que debe quedar como comentario en el modelo:**

> Los campos de respaldo se pueblan desde la fuente estructurada **al crear** la evaluación, y **nunca se re-sincronizan**. La exportación lee **siempre** el campo de respaldo, **nunca** la relación. Un documento oficial emitido no cambia porque cambien los datos maestros.

## 8.5 Migraciones necesarias

**Todas parten de tablas vacías.** No hay migración de datos en ningún punto.

### Migraciones que se copian sin modificar — 10 archivos **[VERIFICADO]**

| App | Archivos | Motivo por el que no se tocan |
|---|---|---|
| `planillas` | `0001_initial.py` | Ya usa `swappable_dependency` (`:13`) y `to=settings.AUTH_USER_MODEL` (`:28`). El `app_label` no cambia (D-2) |
| `evaluaciones` | `0001` … `0007` (7 archivos) | Ídem |
| `exportaciones` | `0001_initial.py`, `0002_generatedreport.py` | Ídem |

### Migraciones nuevas — 3 archivos **[PROPUESTA]**

**`planillas/0002_evaluacion_empresa.py`** — vinculación con el dominio de empresa:

```python
operations = [
    migrations.AddField(
        model_name="evaluacion",
        name="empresa",
        field=models.ForeignKey(
            blank=True, null=True,
            on_delete=django.db.models.deletion.PROTECT,
            related_name="evaluaciones_ergonomicas",
            to="company.companyprofile",
            verbose_name="Empresa evaluada",
        ),
    ),
    # Alineación de longitudes con CompanyProfile — ver §8.2
    migrations.AlterField(model_name="evaluacion", name="razon_social",
                          field=models.CharField(max_length=300)),
    migrations.AlterField(model_name="evaluacion", name="cuit",
                          field=models.CharField(max_length=20)),
    migrations.AlterField(model_name="evaluacion", name="direccion_establecimiento",
                          field=models.CharField(max_length=400)),
    migrations.AlterField(model_name="evaluacion", name="usuario",
                          field=models.ForeignKey(
                              on_delete=django.db.models.deletion.CASCADE,
                              related_name="evaluaciones_ergonomicas",
                              to=settings.AUTH_USER_MODEL,
                              verbose_name="Profesional responsable")),
]

dependencies = [
    ("planillas", "0001_initial"),
    ("company", "0001_create_company_profile"),      # [VERIFICADO] nombre real
    migrations.swappable_dependency(settings.AUTH_USER_MODEL),
]
```

**`planillas/0003_planilla1_trabajadores.py`** — trabajadores estructurados:

```python
operations = [
    migrations.AddField(
        model_name="planilla1",
        name="trabajadores",
        field=models.ManyToManyField(
            blank=True,
            related_name="planillas_ergonomicas",
            to="company.companyworker",
            verbose_name="Trabajadores relevados",
        ),
    ),
]

dependencies = [
    ("planillas", "0002_evaluacion_empresa"),
    ("company", "0002_create_company_worker"),       # [VERIFICADO] nombre real
]
```

**`planillas/0004_indices.py`** — índices de consulta **[PROPUESTA]**:

```python
operations = [
    migrations.AddIndex(
        model_name="evaluacion",
        index=models.Index(fields=["usuario", "-fecha_modificacion"],
                           name="idx_eval_usuario_fmod"),
    ),
    migrations.AddIndex(
        model_name="evaluacion",
        index=models.Index(fields=["empresa", "-fecha_modificacion"],
                           name="idx_eval_empresa_fmod"),
    ),
]
```

**Justificación de los índices:** el listado del módulo filtra por propietario y ordena por `-fecha_modificacion` **[VERIFICADO — `core/views.py:40,72,81`]**, que es exactamente el patrón que estos índices cubren. `Evaluacion` no tiene hoy ningún índice más allá de la PK. Con base vacía es el momento de agregarlos.

### Orden de aplicación

```
1. accounts.*, company.*         (ya aplicadas en el destino)
2. planillas.0001_initial        → crea planillas_evaluacion con FK a accounts_customuser
3. evaluaciones.0001 … 0007      → depende de planillas.0001
4. exportaciones.0001, 0002      → depende de planillas.0001
5. planillas.0002, 0003, 0004    → depende de company
```

### Verificación obligatoria

Se aplica el protocolo de seis pasos que ErgoApp adoptó tras el incidente del 01/08/2026 **[VERIFICADO — `INCIDENTE_MIGRACION_TRANSPORTE_2026-08-01.md` §7]**:

1. Generar y revisar la migración.
2. Ejecutar las pruebas con base creada desde cero.
3. Aplicar en el ambiente destino.
4. `migrate --check`.
5. Reiniciar los procesos.
6. Prueba de humo autenticada.

> **Por qué este protocolo importa especialmente aquí.** El incidente documentado ocurrió porque una migración generada y no aplicada bloqueó **todos** los formularios cuantitativos: el resumen del wizard consulta los 13 modelos del catálogo en cada carga, de modo que una columna faltante en `Transporte_Eval` rompía también LMC, Empuje, Tracción y Vibraciones. **Ese acoplamiento sigue vigente.** `makemigrations --check` y `migrate --check` resuelven problemas distintos y ambos son necesarios.

## 8.6 Tabla de caché

`ergosolutions_cache` **no se crea por migración**. Es un paso de despliegue:

```bash
.venv/bin/python manage.py createcachetable
```

Debe ejecutarse **antes** de arrancar los procesos y quedar registrado en el runbook de despliegue. Ver B4.

---
# PARTE IX — CUMPLIMIENTO DE LAS CONDICIONES FUNDAMENTALES

> Las seis condiciones de `ESTADO_TECNICO_COMPLETO_E_INTEGRACION_ERGOCAPACITACION_2026-08-01.md` §9.5 son **requisitos vinculantes**. Esta parte demuestra, condición por condición, cómo la propuesta las respeta y cómo se verifica el cumplimiento.

## CF-1 — `help_ai` y `ergobot_ai` NO se fusionan. Coexisten.

### Cómo la respeta la propuesta

| Exigencia de CF-1 | Cómo se cumple | Referencia |
|---|---|---|
| Aplicaciones separadas e independientes | `apps.ergobot_ai` y `apps.ergonomia_886.help_ai` son entradas distintas de `INSTALLED_APPS` | §7.5 |
| Prohibido fusionarlas | La propuesta no contempla ninguna fusión de vistas, agentes ni prompts. `help_ai` conserva sus 13 archivos y sus 1.052 líneas; `ergobot_ai` sus 9 archivos y 164 líneas | Área 5 |
| Prohibido reemplazar una por la otra | Se demuestra en el Área 5 que sus arquitecturas de contexto son incompatibles: archivos versionados por SHA-256 vs. consulta al ORM | Área 5 |
| Ninguna importa código de la otra | **[VERIFICADO]** `help_ai/catalog.py:3` importa sólo de `evaluaciones.catalog`; `apps/ergobot_ai/agents.py:4` importa sólo de `apps.training.models`. La propuesta no agrega ningún import cruzado | §6.2 |
| Se conserva el versionado por SHA-256 | `help_ai/prompts.py` se porta íntegro. El único cambio es la ruta de `HELP_TEXTS_PATH` (B6), que **no altera el algoritmo de versionado** | §6.6 |
| Se conservan las cuotas y el lease | `help_ai/limits.py` se porta sin cambios. **Y se refuerza:** B4 garantiza `DatabaseCache` compartida, sin la cual el lease no funcionaría | §6.4 |
| Sólo se unifica el setting del modelo | `CHAT_AI_MODEL` pasa a derivar de `OPENAI_MODEL` por defecto. **Ningún código de ninguna de las dos apps cambia** | Área 10 |

### Separación física reforzada por la propuesta

| Dimensión | `ergobot_ai` | `help_ai` |
|---|---|---|
| Ubicación | `apps/ergobot_ai/` | `apps/ergonomia_886/help_ai/` |
| Prefijo de URL | `/ai/` | `/evaluacion-ergonomica/ayuda/` |
| Namespace | *(sin `app_name` — H-D)* | `help_ai` |
| Setting del modelo | `OPENAI_MODEL` | `CHAT_AI_MODEL` (derivado) |
| Widget | `js/ergobot_chat.js` en pantallas de capacitación | `ayuda/js/help_widget.js` en pantallas del módulo 886 |

La decisión D-5 —montar `help_ai` dentro del prefijo del módulo en lugar de `/ai/`— **fortalece CF-1**: en el proyecto de origen ambos habrían compartido prefijo, lo que habría sugerido que son el mismo producto.

### ⚠️ Conflicto detectado y su resolución

**[HALLAZGO H-J]** El criterio de verificación «las 22 pruebas de `help_ai` pasan **sin modificación**» es **incompatible con B3**, que obliga a agregar `app_name = "help_ai"`. Los 9 `reverse()` de `help_ai/tests.py` dejarían de resolver.

**Resolución propuesta y criterio reformulado:**

> **«Las 22 pruebas de `help_ai` pasan. Los únicos cambios admitidos en `help_ai/tests.py` son (a) la calificación con namespace de los 9 `reverse()` y (b) la actualización de rutas de import. Ninguna aserción, ningún `patch`, ningún caso de prueba y ninguna cuota puede modificarse ni eliminarse.»**

**Esto requiere aceptación formal antes de ejecutar la Fase 1**, y el diff de `help_ai/tests.py` debe revisarse línea por línea contra ese criterio.

### Verificación de cumplimiento

- [ ] `apps.ergobot_ai` y `apps.ergonomia_886.help_ai` figuran como apps separadas en `INSTALLED_APPS`
- [ ] `grep -r "ergobot" apps/ergonomia_886/` no devuelve resultados
- [ ] `grep -r "help_ai" apps/ergobot_ai/` no devuelve resultados
- [ ] Las 22 pruebas de `help_ai` pasan
- [ ] El diff de `help_ai/tests.py` contiene **sólo** los dos tipos de cambio admitidos
- [ ] El widget de ayuda contextual responde en las pantallas del módulo 886
- [ ] El chatbot docente responde en las pantallas de capacitación
- [ ] `settings.CHAT_AI_MODEL` y `settings.OPENAI_MODEL` existen y son legibles por separado

---

## CF-2 — El motor de cálculo es la única autoridad sobre los niveles de riesgo

### Cómo la respeta la propuesta

**La propuesta no toca ni una línea de `evaluaciones/calculators.py`.** El único cambio en toda la app `evaluaciones` es mecánico: 26 rutas del catálogo, 1 ruta de recurso y los imports absolutos.

| Riesgo para CF-2 | Por qué la propuesta no lo introduce |
|---|---|
| Que una vista nueva calcule un nivel | La única vista nueva es `evaluacion_list_view`, que **lee** y pagina. No calcula nada |
| Que la sincronización con la agenda derive un nivel | `_prioridad_por_nivel()` **mapea** `SeguimientoMedida.nivel_riesgo` —un dato ya persistido— a la prioridad de un evento de calendario. **No calcula ni reclasifica ningún nivel de riesgo**, y la prioridad de la agenda no es un nivel de riesgo |
| Que el dashboard muestre un nivel calculado al vuelo | El listado muestra los campos persistidos. Si en el futuro se agregara una columna de nivel global, debe leer `RiskEvaluation.resultado_global`, nunca recalcular |
| Que el módulo de capacitaciones sugiera cursos según un nivel | La oportunidad O-6 **lee** el nivel persistido para sugerir un módulo. Es consumo, no autoridad |

### La única excepción prevista se conserva

La **revisión profesional** de `evaluaciones/views.py` (`review_factor`) sigue siendo la única forma de modificar una clasificación, y queda auditada en `calc_data["revision_profesional"]` con su justificación obligatoria. La propuesta no la altera.

### Verificación de cumplimiento

- [ ] `git diff` sobre `evaluaciones/calculators.py` muestra **sólo** el cambio de la ruta de recurso de `:71`
- [ ] Las 45 pruebas de `evaluaciones/tests.py` pasan sin modificación de aserciones
- [ ] El PDF del informe sigue imprimiendo el anexo generado **desde el payload**, no desde el texto del modelo
- [ ] Ninguna vista, plantilla o señal nueva escribe en `nivel_riesgo` ni en `calc_data["clasificacion_*"]`
- [ ] `grep -rn "nivel_riesgo\s*=" apps/ergonomia_886/` sólo devuelve asignaciones dentro de `calculators.py` y de la revisión profesional

---

## CF-3 — La trazabilidad normativa no se recorta

### Cómo la respeta la propuesta

`calc_data` es un `JSONField` de `BaseFactorEvaluation` **[VERIFICADO — `evaluaciones/models.py:62-102`]**. La propuesta **no introduce ninguna capa que lo filtre, trunque ni normalice**.

| Punto de riesgo | Estado en la propuesta |
|---|---|
| Serialización para el listado | `evaluacion_list_view` consulta `Evaluacion` y `Planilla1`. **No toca `calc_data`** |
| Sincronización con la agenda | `AgendaEvent` recibe título, fecha, prioridad y descripción. **No recibe ni resume `calc_data`** |
| Los 13 artefactos normativos | Viajan íntegros con la app. Su carga por `os.path.dirname(__file__)` (`:59`) sobrevive al movimiento **[VERIFICADO]** |
| El SHA-256 de cada artefacto | Se calcula al cargar el archivo. Los archivos son idénticos byte a byte tras la copia, de modo que **los checksums no cambian** |
| El PDF de detalle técnico | Sigue volcando `calc_data` íntegro |

### Punto de atención sobre el saneamiento

`sanitize_payload()` **sí** recorta datos antes de enviarlos al modelo de lenguaje. **Eso no viola CF-3**, porque:

- Actúa sobre una **copia del payload de salida**, no sobre `calc_data` persistido.
- `GeneratedReport.payload_json` guarda el payload **saneado** como evidencia de lo que efectivamente se envió, que es información adicional, no un reemplazo.
- Es exactamente lo que CF-4 exige.

La propuesta conserva ambos comportamientos sin cambios.

### Verificación de cumplimiento

- [ ] `makemigrations --check` no genera ninguna alteración sobre `calc_data`
- [ ] El PDF de detalle técnico de un factor calculado incluye `calculation_trace` con `engine_version` y el SHA-256 de su artefacto
- [ ] Los 13 artefactos de `evaluaciones/data/` son idénticos byte a byte a los del origen (`diff -r` o `sha256sum`)
- [ ] Las 23 pruebas de `test_serializers.py` pasan sin modificación de aserciones

---

## CF-4 — Los datos personales no salen hacia el proveedor del modelo

### Cómo la respeta la propuesta

`exportaciones/reports/llm.py` **se porta sin ningún cambio funcional**. Sólo se actualizan sus imports.

| Control | Estado en la propuesta | Verificación |
|---|---|---|
| `CLAVES_PROHIBIDAS` de 11 claves | **Intacta** | `llm.py:25-31` |
| `sanitize_payload()` recursivo | **Intacto** | `llm.py:50-63` |
| Reconstrucción del contexto mínimo | **Intacta** — sólo razón social, área/sector, puesto y provincia | `llm.py:65-71` |
| `trace_include_sensitive_data=False` | **Intacto.** **[VERIFICADO]** el campo existe en `openai-agents` 0.6.9 del destino | `llm.py:96` |
| Agente sin `lru_cache` | **Intacto** | `llm.py:82` |
| Logs sin payloads | **Intacto** | — |

### El riesgo nuevo que la integración introduce, y cómo se neutraliza

**La integración amplía la superficie de datos personales disponibles.** Antes, un `Planilla1.nombres_trabajadores` era texto libre. Ahora, `Planilla1.trabajadores` es una relación a `CompanyWorker`, que a su vez enlaza a `CustomUser` con **CUIL, DNI, email y nombre real**.

Si un serializador incluyera la relación en el payload, se filtrarían datos personales de trabajadores identificables **a pesar de que `CLAVES_PROHIBIDAS` está intacta**, porque las claves nuevas (`trabajadores`, `worker`, `cuil`, `employee_code`) no figuran en la lista.

**[PROPUESTA] Medida obligatoria:** ampliar `CLAVES_PROHIBIDAS` en el mismo commit que introduce la relación M2M:

```python
CLAVES_PROHIBIDAS = frozenset({
    # --- originales, sin modificar ---
    "nombres_trabajadores", "cuit", "direccion", "ubicacion_sintoma",
    "salud_columna", "revisado_por", "evaluacion_id", "instancia_id",
    "medida_id", "foto_montaje", "certificado_calibracion",
    "evidencia_declarada",
    # --- nuevas: superficie introducida por la integración ---
    "trabajadores", "worker", "workers", "cuil", "dni", "email",
    "employee_code", "empresa_id", "company", "company_id",
    "contacto_nombre", "contacto_telefono", "license_number",
})
```

**Esto es una ampliación, no una modificación:** las 12 claves originales se conservan literalmente. CF-4 prohíbe relajar el saneamiento, no reforzarlo.

**Regla de diseño complementaria:** los serializadores de `exportaciones` **no deben incluir la relación `trabajadores` en el payload del informe**. La planilla oficial y el detalle técnico imprimen `nombres_trabajadores` porque son documentos del profesional; el informe del LLM no lo necesita para nada.

### Verificación de cumplimiento

- [ ] `CLAVES_PROHIBIDAS` contiene las 12 claves originales **más** las nuevas
- [ ] Las 16 pruebas de `test_reports_llm.py` pasan sin modificación de aserciones
- [ ] **[PROPUESTA]** Prueba nueva: un payload que contenga `trabajadores` con CUIL y DNI sale saneado
- [ ] `RunConfig(trace_include_sensitive_data=False)` sigue presente y el campo existe en la versión instalada
- [ ] Inspección manual de un `GeneratedReport.payload_json` real: no contiene nombres, CUIT, CUIL, DNI, direcciones ni datos de salud

---

## CF-5 — Un documento oficial nunca afirma lo que el profesional no respondió

### Cómo la respeta la propuesta

La regla de export se conserva sin cambios: **una respuesta se marca «NO» sólo si la planilla fue guardada alguna vez; si nunca se completó, la página sale en blanco.**

`exportaciones/serializers.py:107-112` implementa la regla **[VERIFICADO]**:

```python
instancias = list(modelo.objects.filter(evaluacion=evaluacion).order_by("pk"))
if not instancias:
    return [{**cabecera, "existe": False, "tarea_nro": "", "respuestas": {}}]
```

La marca `existe: False` propaga hacia los builders, que omiten las marcas SI/NO. La propuesta no toca este código.

### Los tres puntos donde la integración podría violarla, y cómo se evitan

| # | Riesgo introducido | Cómo se evita |
|---|---|---|
| 1 | **Poblado automático desde `CompanyProfile`.** Copiar el domicilio de la empresa a `direccion_establecimiento` podría afirmar una dirección donde el relevamiento nunca ocurrió | El poblado ocurre **sólo al crear**, el campo queda **editable** por el profesional, y su valor tipeado gana siempre (`or` en el `save()`). El profesional declara el domicilio del establecimiento relevado, que puede no ser la sede social |
| 2 | **Firmantes automáticos.** Imprimir un nombre en el recuadro de Medicina del Trabajo sería afirmar que ese profesional revisó el protocolo | **El tercer recuadro se deja en blanco**, porque no hay dato. Y si `profession` o `license_number` están vacíos, la aclaración correspondiente **también** queda en blanco. §8.3 |
| 3 | **Trabajadores derivados.** Poblar `nombres_trabajadores` desde la nómina podría afirmar que se relevó a trabajadores que no estuvieron presentes | La derivación **sólo actúa si el campo está vacío**, y el profesional puede editarla. La relación M2M la puebla él explícitamente, no un proceso automático. Área 4 |

**El hilo común de los tres:** ningún dato se afirma en un documento oficial sin que un profesional lo haya puesto ahí, directa o deliberadamente.

### Verificación de cumplimiento

- [ ] Evaluación con Planilla 2A nunca guardada → la página 2 del protocolo sale **en blanco**, sin marcas «NO»
- [ ] Evaluación con Planilla 2A guardada con todo en `False` → la página 2 sale con marcas «NO»
- [ ] Evaluación de una empresa registrada → el profesional puede editar los cuatro campos poblados
- [ ] Profesional sin `license_number` → la aclaración de firma correspondiente sale en blanco
- [ ] El recuadro de Medicina del Trabajo sale **siempre** en blanco
- [ ] Las 24 pruebas de `test_official_pdf.py` pasan sin modificación de aserciones

---

## CF-6 — La superposición no altera el formulario oficial

### Cómo la respeta la propuesta

`exportaciones/official/` se porta **sin ningún cambio funcional**. Sólo se actualizan las 12 cadenas `model_path` de `catalog.py` y los imports.

| Elemento | Estado en la propuesta | Verificación |
|---|---|---|
| Plantilla oficial | Se copia **byte a byte**: 251.599 bytes | `official/templates_bin/res_srt_886_15-formulario.pdf` |
| SHA-256 declarado | `bc0d0753943888779abd0936f6c4dc2e128766c7cf6370a4a2fb19073aad59f4` — **sin cambios** | `official/catalog.py:20` |
| Verificación al cargar | **Intacta.** Si el archivo no coincide, lanza `OfficialTemplateError` | `official/catalog.py:24-25` |
| Los 12 mapas de calibración | Se copian sin modificar | `official/maps/*.json` |
| Motor de superposición | Sin cambios: capa ReportLab + fusión `pypdf` | `official/overlay.py` |
| Tamaño de página | `(612.0, 792.0)` — Carta, sin cambios | `official/catalog.py:21` |

### La resolución de rutas sobrevive al movimiento

**[VERIFICADO — `exportaciones/official/catalog.py:15-17`]**:

```python
BASE_DIR = Path(__file__).resolve().parent          # relativa al propio paquete
TEMPLATES_DIR = BASE_DIR / "templates_bin"
MAPS_DIR = BASE_DIR / "maps"
```

A diferencia de `help_ai/prompts.py` (B6), esta ruta es **relativa al propio paquete** y no sube niveles. Al mover `exportaciones/` a `apps/ergonomia_886/exportaciones/`, el PDF y los mapas viajan con ella y las rutas siguen resolviendo. **No requiere ninguna acción.**

### La prohibición del `.xls` se mantiene

La propuesta **no contempla en ningún punto** generar planillas rellenando el `.xls` oficial. El motivo está medido y documentado: escribir el `.xls` destruye los 19 registros de dibujo y los 7 objetos embebidos, perdiendo la curva de confort de Fanger de la Planilla 2H y la escala de Borg de la 2E.

`pypdf` es **la única forma de cumplir CF-6**, y por eso B7 (su ausencia en el destino) es un bloqueante y no una molestia.

### Verificación de cumplimiento

- [ ] `sha256sum` del PDF trasplantado coincide con `OFFICIAL_PDF_SHA256`
- [ ] `pypdf` está declarado en `requirements.txt` e instalado
- [ ] Las 24 pruebas de `test_official_pdf.py` pasan
- [ ] Descarga manual del protocolo completo: 12 páginas, tamaño Carta, abre sin advertencias
- [ ] **Inspección visual de la página 8 (Planilla 2H):** la curva de confort de Fanger está íntegra
- [ ] **Inspección visual de la página 5 (Planilla 2E):** la escala de Borg está íntegra
- [ ] No existe ninguna dependencia de `xlrd`, `xlutils`, `xlwt` ni `openpyxl` en el proyecto integrado

---

## Cuadro resumen de cumplimiento

| Condición | Riesgo que la integración introduce | Medida | Estado |
|---|---|---|---|
| **CF-1** | Que la unificación de settings derive en unificación de código | `CHAT_AI_MODEL` deriva de `OPENAI_MODEL` sin tocar código. Separación física y de URL reforzada | ✅ Cumple, **con H-J a resolver formalmente** |
| **CF-2** | Que una capa de integración calcule o derive un nivel | Ninguna capa nueva calcula. `_prioridad_por_nivel()` mapea, no clasifica | ✅ Cumple |
| **CF-3** | Que un serializador recorte `calc_data` | Ninguna capa nueva lo toca. Los artefactos viajan íntegros | ✅ Cumple |
| **CF-4** | **Superficie ampliada de datos personales** por la relación con `CompanyWorker` | **Ampliar `CLAVES_PROHIBIDAS`** en el mismo commit. No incluir la relación en el payload | ⚠️ **Cumple sólo si se aplica la medida** |
| **CF-5** | Poblado automático de empresa, firmantes y trabajadores | Poblado sólo al crear, campos editables, recuadro médico siempre en blanco | ✅ Cumple |
| **CF-6** | Que falte `pypdf` y se busque una alternativa | B7 lo declara bloqueante. Rutas verificadas como estables | ✅ Cumple |

> **Las dos condiciones que requieren acción explícita son CF-1 (aceptar el criterio reformulado de H-J) y CF-4 (ampliar `CLAVES_PROHIBIDAS`).** Las otras cuatro se cumplen por construcción, sin trabajo adicional.

---
# PARTE X — PLAN DE INTEGRACIÓN POR FASES Y COMMITS

## 10.1 Dependencias entre fases

```
Fase 0 (destino)          Fase 1 (origen)
   B4, B7, B8,               B1, B3,
   N1, N2, H-F               driver, CORS
       │                          │
       └──────────┬───────────────┘
                  ▼
            Fase 2 — Trasplante
              B2, B6, templates, URLs
                  │
                  ▼
            Fase 3 — Normalización de dominio
              empresa, propiedad mixta, CF-4
                  │
                  ▼
            Fase 4 — Integración de UI
              dashboard, tarjeta, navegación, ayuda
                  │
        ┌─────────┴─────────┐
        ▼                   ▼
   Fase 5              Fase 6 — CSP
   Aprovechamiento     (independiente, puede
   O-2…O-6              adelantarse desde el inicio)
```

**Las Fases 0 y 1 son paralelizables**: ocurren en repositorios distintos y no se tocan. **Las Fases 2, 3 y 4 son estrictamente secuenciales.** La Fase 5 se puede fraccionar. La Fase 6 es independiente de todo.

## 10.2 Fase 0 — Preparación del destino

**Objetivo:** integrar sobre una base sana. Todo ocurre en `ergocapacitacion`, rama `release/beta`, y **nada de esto depende del módulo 886.**

| Commit | Contenido | Archivos | Bloqueante |
|---|---|---|---|
| **0.1** | Consolidar el árbol de trabajo: commitear `docs/`, `.gitignore` y `README.md` pendientes | raíz | — |
| **0.2** | Corregir los nombres de URL de los decoradores | `apps/accounts/decorators.py:27,54,92,122,152` | **N1** |
| **0.3** | Restaurar `@login_required` antes de `@company_required` / `@professional_required` en las 13 vistas | `apps/company/views.py` (11), `apps/dashboard/views.py:373,386` | **N1** |
| **0.4** | Corregir `PROFESSIONAL_LOGIN_URL` y `PROFESSIONAL_LOGIN_REDIRECT_URL` | `config/settings.py:109-110` | **H-F** |
| **0.5** | Corregir `qs.is_approved` → `bool(qs.last_passed)` | `apps/company/views.py:202` | **N2** |
| **0.6** | Tests de regresión: acceso anónimo a todas las rutas de backoffice; `nomina_detail` con `QuizState` | `apps/company/tests.py`, `apps/dashboard/tests.py` | **N1, N2** |
| **0.7** | Crear `config/test_settings.py` y verificar que los 32 tests pasan bajo él | `config/test_settings.py` | **B8** |
| **0.8** | Agregar `CACHES` con `DatabaseCache`; documentar `createcachetable` en el runbook | `config/settings.py` | **B4** |
| **0.9** | Agregar `pypdf` y `pillow` a `requirements.txt`; fijar cotas superiores | `requirements.txt` | **B7** |
| **0.10** | Agregar `app_name` a los 5 includes del destino que no lo tienen | `apps/{accounts,training,quiz,certificates,ergobot_ai}/urls.py` + referencias | **H-D** |

### Criterio de aceptación de la Fase 0

```bash
.venv/bin/python manage.py check
.venv/bin/python manage.py makemigrations --check --dry-run     # No changes detected
.venv/bin/python manage.py test apps --settings=config.test_settings   # ≥ 34 tests OK
.venv/bin/python manage.py createcachetable
```

Y una verificación funcional que reproduce N1 **[PROPUESTA]**:

```python
# Ninguna ruta de backoffice devuelve 500 sin sesión
for url in ["/dashboard/", "/dashboard/empresa/nomina/", "/dashboard/empresa/agenda/",
            "/dashboard/empresa/directorio/", "/dashboard/solicitudes-contacto/"]:
    r = Client().get(url)
    assert r.status_code in (302, 403), f"{url} → {r.status_code}"
```

### Punto de verificación

- [ ] Ninguna ruta devuelve HTTP 500 a un usuario anónimo
- [ ] La ficha del trabajador con `QuizState` renderiza correctamente
- [ ] Los 32 tests originales siguen pasando, ahora con `config.test_settings`
- [ ] `createcachetable` ejecutado; la tabla existe

> **Los commits 0.10 y 0.1 son opcionales para la integración**, pero se recomiendan: 0.10 cierra el defecto H-D de raíz en lugar de corregirlo sólo del lado del origen, y 0.1 evita que los cambios de la integración se mezclen con trabajo pendiente ajeno.

## 10.3 Fase 1 — Adaptación de compatibilidad en el origen

**Objetivo:** dejar ErgoApp compatible **dentro de su propio repositorio**, con las 160 pruebas en verde antes de mover nada. Todo ocurre en `ergonomia_srt`, rama `main` o una rama de trabajo.

| Commit | Contenido | Archivos | Bloqueante |
|---|---|---|---|
| **1.1** | `Evaluacion.usuario` → `settings.AUTH_USER_MODEL` | `planillas/models.py:4,9` | **B1** |
| **1.2** | `app_name = "planillas"` + calificar 33 referencias | `planillas/urls.py` + 19 templates + 5 redirects + 9 nombres dinámicos en tests | **B3** |
| **1.3** | `app_name = "help_ai"` + calificar 11 referencias | `help_ai/urls.py` + 2 templates + 9 en `tests.py` | **B3**, ⚠️ **H-J** |
| **1.4** | Quitar `django-cors-headers` de `INSTALLED_APPS`, `MIDDLEWARE` y `requirements.txt` | `ergonomia_srt/settings.py:91,104,227-230`, `requirements.txt` | D-10 |
| **1.5** | Quitar `sse-starlette` de `requirements.txt` (declarada, no usada); documentar el descarte de `weasyprint` | `requirements.txt` | D-7 |
| **1.6** | `LANGUAGE_CODE = 'es-ar'` | `ergonomia_srt/settings.py:180` | D-8 |

### Criterio de aceptación de la Fase 1

```bash
cd /Users/praguirre/ergonomia_srt
./venv/bin/python manage.py test --settings=ergonomia_srt.test_settings   # Ran 160 tests — OK
./venv/bin/python manage.py makemigrations --check --dry-run              # No changes detected
```

> **El segundo comando es el punto de verificación crítico de B1.** Si el commit 1.1 generara una migración, la premisa de H-G sería falsa y **hay que detenerse a investigar** antes de continuar. Según la verificación empírica de §6.1, debe seguir diciendo `No changes detected`.

### Punto de verificación

- [ ] 160 pruebas en verde **en el proyecto de origen**
- [ ] `makemigrations --check` sigue sin detectar cambios
- [ ] `grep -rn "from django.contrib.auth.models import User"` no devuelve resultados
- [ ] Ninguna referencia `{% url %}` ni `reverse()` sin calificar hacia `planillas` o `help_ai`
- [ ] **El diff de `help_ai/tests.py` contiene sólo cambios de namespace** (criterio H-J)
- [ ] El driver sigue siendo psycopg2 en este punto: **el cambio a psycopg 3 ocurre al adoptar el `settings.py` del destino**, no aquí

> **Sobre el driver.** No hay commit propio: el módulo no configura la base de datos. Al integrarse, hereda `DATABASES = env.db("DATABASE_URL")` del destino, que ya usa psycopg 3. Ningún código del módulo referencia el driver. **[VERIFICADO por ausencia de `import psycopg` en las 5 apps.]**

## 10.4 Fase 2 — Trasplante

**Objetivo:** que las 160 pruebas pasen **dentro del proyecto destino**. Es la fase de mayor riesgo mecánico.

| Commit | Contenido | Detalle |
|---|---|---|
| **2.1** | Crear el paquete contenedor | `apps/ergonomia_886/__init__.py` |
| **2.2** | **Actualizar las 48 cadenas literales, ANTES de mover** | 26 en `evaluaciones/catalog.py`, 12 en `official/catalog.py`, 9 en `serializers.py`, 1 en `calculators.py:71` |
| **2.3** | Copiar las 4 apps con sus migraciones y templates | `planillas`, `evaluaciones`, `exportaciones`, `help_ai` |
| **2.4** | Actualizar `name` en los 4 `apps.py` | `name = 'apps.ergonomia_886.<app>'`. **No declarar `label`** (D-2) |
| **2.5** | Reescribir los 102 imports absolutos | 16 archivos, 85 de ellos en suites |
| **2.6** | **Corregir la ruta de los documentos de ayuda** | `help_ai/prompts.py:14-15` — **B6** |
| **2.7** | Copiar los estáticos | 33 `.md` de ayuda, `ayuda/css`, `ayuda/js`, `js/planilla_logic.js`, `vendor/` completo |
| **2.8** | Registrar las 4 apps en `INSTALLED_APPS` y portar los 14 settings del módulo | `config/settings.py` |
| **2.9** | Crear `apps/ergonomia_886/urls.py` y montarlo en `config/urls.py` | 1 línea nueva en `config/urls.py` |
| **2.10** | Crear `templates/ergonomia_886/base_886.html` y adaptar los 10 templates que extendían `base.html` | Área 8, §7.9 |
| **2.11** | Extraer el widget de ayuda a `templates/ergonomia_886/_help_widget.html` | §7.9 |
| **2.12** | Agregar `apps/ergonomia_886/checks.py` para validar las 48 rutas declarativas | §6.2 — **la mitigación más valiosa del plan** |
| **2.13** | Aplicar las migraciones sobre base vacía | `migrate` + `migrate --check` |

### Criterio de aceptación de la Fase 2

```bash
cd /Users/praguirre/ergocapacitacion
.venv/bin/python manage.py check                              # incluye ergonomia_886.E001
.venv/bin/python manage.py makemigrations --check --dry-run   # No changes detected
.venv/bin/python manage.py migrate --check
.venv/bin/python manage.py test --settings=config.test_settings   # ≥ 194 tests OK (160 + 34)
```

### Punto de verificación

- [ ] **Las 160 pruebas del módulo pasan dentro del destino**
- [ ] **Los 32+ tests preexistentes del destino siguen pasando**
- [ ] `manage.py check` no reporta `ergonomia_886.E001` (las 48 rutas resuelven)
- [ ] Las 13 rutas de factor cargan (HTTP 200) para su propietario autenticado
- [ ] Las 9 Planillas 2 cargan y enlazan a su evaluación cuantitativa
- [ ] El widget de ayuda responde en al menos 3 pantallas distintas con slugs distintos
- [ ] Las 12 planillas oficiales se descargan y abren correctamente
- [ ] `sha256sum` del PDF oficial coincide con `OFFICIAL_PDF_SHA256`

> **Orden crítico del commit 2.2.** Las 48 cadenas deben actualizarse **antes** de mover los archivos, mientras el prefijo `"evaluaciones."` / `"planillas."` es fácil de localizar sin falsos positivos. Después del movimiento, esas mismas cadenas se confunden con los nombres de directorio.

## 10.5 Fase 3 — Normalización de dominio

**Objetivo:** vincular el módulo con `CompanyProfile` y `CustomUser`.

| Commit | Contenido | Bloqueante |
|---|---|---|
| **3.1** | `Evaluacion.empresa` + alineación de longitudes + `related_name` — migración `0002` | §8.5 |
| **3.2** | **Ampliar `CLAVES_PROHIBIDAS`** con las claves de la superficie nueva | ⚠️ **CF-4** |
| **3.3** | `evaluaciones_visibles_para(user)` — propiedad mixta por `user_type` | §7.6 |
| **3.4** | Aplicar `@login_required` + `@backoffice_required` a todas las vistas del módulo | §7.6, evita repetir N1 |
| **3.5** | Formulario de creación con selector de empresa y poblado al crear | §8.2 |
| **3.6** | `evaluacion_list_view` — reimplantar `core.dashboard_view` con filtro mixto | Área 2 |
| **3.7** | `eliminar_evaluacion_view` — reimplantar `core.eliminar_evaluacion_view` | Área 2 |
| **3.8** | Índices de consulta — migración `0004` | §8.5 |
| **3.9** | Pruebas nuevas: propiedad mixta, 404 vs 403, poblado al crear, saneamiento de la superficie nueva | §11 |

### Criterio de aceptación de la Fase 3

- [ ] Un profesional ve sólo sus evaluaciones
- [ ] Una empresa ve las suyas, hechas por cualquier profesional
- [ ] Un `trainee` no accede al módulo
- [ ] Un recurso ajeno devuelve **404**, no 403
- [ ] Ninguna ruta del módulo devuelve 500 a un usuario anónimo
- [ ] Al crear una evaluación con empresa seleccionada, los 4 campos se pueblan y quedan editables
- [ ] Un payload con `trabajadores`, `cuil` y `dni` sale saneado (**CF-4**)

## 10.6 Fase 4 — Integración de UI

| Commit | Contenido | Referencia |
|---|---|---|
| **4.1** | **Activar la tarjeta «Evaluaciones»** en `templates/dashboard/home.html:79-96` | §7.7 |
| **4.2** | Entrada «Evaluaciones» en el navbar de `base_dashboard.html` | §7.8 |
| **4.3** | Cuarta stat en el dashboard del profesional, con import diferido | §7.7 |
| **4.4** | Ajustes de contraste de los 28 templates del módulo al tema oscuro | Área 8 |
| **4.5** | Loggers del módulo en `LOGGING` | Matriz fila 49 |

### Criterio de aceptación de la Fase 4

- [ ] La tarjeta dice «Disponible» y navega a `/evaluacion-ergonomica/`
- [ ] El texto de la tarjeta **no promete iluminación ni ruido**
- [ ] El navbar marca «Evaluaciones» como activo en todas las pantallas del módulo
- [ ] Las 28 pantallas del módulo son legibles sobre fondo oscuro
- [ ] El widget de ayuda aparece **sólo** en las pantallas del módulo
- [ ] El chatbot docente sigue funcionando en las pantallas de capacitación (**CF-1**)

## 10.7 Fase 5 — Aprovechamiento

Fraccionable: cada commit aporta valor por separado.

| Commit | Oportunidad | Contenido | Cierra |
|---|---|---|---|
| **5.1** | **O-5** | Evidencia de VCE adjuntable con `MEDIA_ROOT`; incluirla en el ZIP | **D-1**, hueco G-9 |
| **5.2** | **O-2** | Aclaración de firma en las 12 planillas oficiales; recuadro médico **en blanco** | **D-3** parcial, hueco G-1 |
| **5.3** | **O-3** | `Planilla1.trabajadores` M2M + derivación del texto — migración `0003` | Área 4 |
| **5.4** | **O-4** | Sincronización `SeguimientoMedida` → `AgendaEvent` | Área 6 |
| **5.5** | **O-4b** | Enlace desde la agenda hacia la Planilla 4 correspondiente | Área 6 |
| **5.6** | **O-6** | Sugerencia de módulos de capacitación según el nivel de riesgo | Área 4, CF-2 |

### Criterio de aceptación de la Fase 5

- [ ] La foto de montaje y el certificado de calibración se cargan, se sirven y se adjuntan al ZIP
- [ ] Las planillas oficiales imprimen la aclaración de firma del profesional
- [ ] **El recuadro de Medicina del Trabajo sale en blanco** (**CF-5**)
- [ ] Guardar una Planilla 4 con fecha comprometida crea un `AgendaEvent` con `event_type='evaluation_due'`
- [ ] Reeditarla **actualiza** el evento en lugar de duplicarlo
- [ ] Cerrar la medida marca el evento como `completed`
- [ ] Una evaluación **sin** empresa no crea ningún evento y no falla

## 10.8 Fase 6 — Content Security Policy *(independiente)*

| Commit | Contenido | Referencia |
|---|---|---|
| **6.1** | Migrar `base_dashboard.html` y `base_landing.html` de CDN a `vendor/` local | Área 9 |
| **6.2** | Extraer los 5 bloques `<script>` inline a archivos `.js` estáticos | H-E |
| **6.3** | Reemplazar los 3 manejadores en línea por `addEventListener` | H-E |
| **6.4** | Verificación visual y funcional de las 33 pantallas del destino | — |
| **6.5** | Portar el middleware con soporte de `Report-Only` configurable | Área 12 |
| **6.6** | Período de observación en `Report-Only`; recolectar violaciones | Área 12 |
| **6.7** | Activar en modo bloqueante | — |

### Criterio de aceptación de la Fase 6

- [ ] Cero referencias a `cdn.jsdelivr.net` en `templates/`
- [ ] Cero bloques `<script>` sin `nonce` y cero manejadores en línea
- [ ] Con la consola del navegador abierta, **cero violaciones de CSP** en las 33 + 28 pantallas
- [ ] Los 6 templates del módulo que usan `{{ request.csp_nonce }}` reciben un nonce real
- [ ] Las cabeceras `Referrer-Policy` y `Permissions-Policy` se emiten

## 10.9 Resumen de commits

| Fase | Commits | Esfuerzo | Riesgo | ¿Bloquea la siguiente? |
|---|---:|---:|---|---|
| 0 — Preparación del destino | 10 | 1,0 j | Bajo | ✅ Sí |
| 1 — Adaptación del origen | 6 | 1,0 j | Bajo | ✅ Sí |
| 2 — Trasplante | 13 | 2,5 j | **Medio** | ✅ Sí |
| 3 — Normalización de dominio | 9 | 2,0 j | Medio | ✅ Sí |
| 4 — Integración de UI | 5 | 1,5 j | Bajo | ❌ No |
| 5 — Aprovechamiento | 6 | 3,0 j | Bajo | ❌ No |
| 6 — CSP | 7 | 2,0 j | **Alto** | ❌ No — independiente |
| **Total** | **56** | **13,0 j** | | |

---

# PARTE XI — ESTRATEGIA DE NO REGRESIÓN

## 11.1 Principio

**Nada se considera integrado hasta que las dos suites pasan juntas en el proyecto destino.** El objetivo cuantitativo es explícito:

| Momento | ErgoSolutions | ErgoApp | Total |
|---|---:|---:|---:|
| Estado inicial **[VERIFICADO]** | 32 | 160 | — |
| Tras la Fase 0 | ≥ 34 | 160 | — |
| **Tras la Fase 2** | ≥ 34 | 160 | **≥ 194** |
| Tras la Fase 3 | ≥ 34 | ≥ 168 | **≥ 202** |
| Tras la Fase 5 | ≥ 34 | ≥ 175 | **≥ 209** |

**Una prueba que se elimina o cuya aserción se relaja es una regresión**, aunque el total suba.

## 11.2 Pruebas que deben seguir pasando

### De ErgoApp — las 160, sin excepción

| Archivo | Pruebas | Cambios admitidos |
|---|---:|---|
| `evaluaciones/tests.py` | 45 | Sólo rutas de import |
| `exportaciones/tests/test_official_pdf.py` | 24 | Sólo rutas de import |
| `exportaciones/tests/test_serializers.py` | 23 | Sólo rutas de import (39 imports) |
| `help_ai/tests.py` | **22** | **Sólo imports + los 9 `reverse()` con namespace** (H-J, CF-1) |
| `exportaciones/tests/test_permissions.py` | 21 | Imports + `reverse()` con namespace |
| `exportaciones/tests/test_reports_llm.py` | 16 | Sólo rutas de import |
| `exportaciones/tests/test_reports_pdf.py` | 8 | Sólo rutas de import |
| `planillas/tests.py` | 1 | Imports + `reverse()` con namespace |
| `core/tests.py` | 0 | Se descarta — **sin pérdida de cobertura** |

**Regla de revisión de diffs.** Para cada archivo de prueba, el diff debe contener **exclusivamente**:

1. cambios de ruta de import (`from planillas.` → `from apps.ergonomia_886.planillas.`);
2. calificación de nombres de URL (`reverse("chat_ai")` → `reverse("help_ai:chat_ai")`).

Cualquier otra cosa —una aserción modificada, un `patch` retirado, un caso comentado, un `skipTest` agregado— **debe justificarse explícitamente o revertirse**.

### De ErgoSolutions — las 32, más las nuevas de la Fase 0

| Suite | Estado | Riesgo de la integración |
|---|---|---|
| `apps/accounts/tests.py` | Debe pasar | **Medio** — la Fase 0 toca los decoradores |
| `apps/company/tests.py` | Debe pasar | **Medio** — la Fase 0 toca 11 vistas y `views.py:202` |
| `apps/dashboard/tests.py` | Debe pasar | Bajo — la Fase 4 toca el template, no la vista |
| `apps/training/`, `apps/quiz/`, `apps/certificates/` | Deben pasar | Bajo |
| **Nuevas de la Fase 0** | Acceso anónimo a backoffice, `nomina_detail` con `QuizState` | — |

## 11.3 Pruebas nuevas que la integración exige **[PROPUESTA]**

| # | Prueba | Fase | Protege |
|---|---|:---:|---|
| **T-1** | Las 48 rutas declarativas resuelven con `import_string()` | 2 | **B2** |
| **T-2** | Los 33 documentos de ayuda se leen desde la ruta nueva | 2 | **B6** |
| **T-3** | Un profesional no accede a la evaluación de otro (404, no 403) | 3 | §7.6 |
| **T-4** | Una empresa ve las suyas y sólo las suyas | 3 | §7.6 |
| **T-5** | Un `trainee` no accede a ninguna ruta del módulo | 3 | §7.6 |
| **T-6** | Ninguna ruta del módulo devuelve 500 a un usuario anónimo | 3 | **N1**, evita repetirlo |
| **T-7** | Un payload con `trabajadores`, `cuil`, `dni`, `employee_code` sale saneado | 3 | **CF-4** |
| **T-8** | Poblar desde `CompanyProfile` no sobrescribe lo tipeado por el profesional | 3 | **CF-5** |
| **T-9** | Un profesional sin `license_number` produce aclaración en blanco | 5 | **CF-5** |
| **T-10** | El recuadro de Medicina del Trabajo sale **siempre** en blanco | 5 | **CF-5** |
| **T-11** | Guardar una Planilla 4 crea un `AgendaEvent`; reeditarla lo actualiza sin duplicar | 5 | Área 6 |
| **T-12** | Una evaluación sin empresa no crea evento y no lanza excepción | 5 | Área 6 |
| **T-13** | `help_ai` no importa de `ergobot_ai` ni viceversa | 2 | **CF-1** |

**T-13 merece implementarse como prueba automática**, no como revisión manual:

```python
# apps/ergonomia_886/help_ai/tests.py   [PROPUESTA]
def test_cf1_las_dos_apps_de_ia_no_se_conocen(self):
    """CF-1: help_ai y ergobot_ai coexisten sin importarse mutuamente."""
    import pathlib
    base = pathlib.Path(settings.BASE_DIR)

    help_ai_src = "\n".join(
        p.read_text() for p in (base / "apps/ergonomia_886/help_ai").rglob("*.py"))
    ergobot_src = "\n".join(
        p.read_text() for p in (base / "apps/ergobot_ai").rglob("*.py"))

    self.assertNotIn("ergobot", help_ai_src.lower())
    self.assertNotIn("help_ai", ergobot_src)
```

Convierte una condición vinculante en una compuerta automática. Es la forma de que CF-1 no se erosione dentro de seis meses.

## 11.4 Verificación manual — pantallas del módulo

Las 28 pantallas del módulo, tras las Fases 2 y 4. **La columna «Ayuda» es crítica**: los 23 templates con `{% block help_slug %}` fallan de forma silenciosa si la cadena de herencia se rompe —el widget cargaría el slug `home` en todas partes en lugar del específico.

| # | Pantalla | Ruta | Verificar |
|---|---|---|---|
| 1 | Listado de evaluaciones | `/evaluacion-ergonomica/` | Búsqueda, 3 filtros, orden, paginación |
| 2 | Crear evaluación | `…/protocolo/crear/` | Selector de empresa, poblado, edición |
| 3 | Detalle / hub | `…/protocolo/<id>/` | Estado de cada planilla, enlaces |
| 4 | Planilla 1 | `…/protocolo/<id>/planilla1/` | Formset de 9 factores. **Ayuda: `planilla1`** |
| 5–13 | Planillas 2A–2I | `…/protocolo/<id>/planilla2X/` | Checklists, enlace a evaluación. **Ayuda: `planilla2X`** |
| 14 | Planilla 3 | `…/protocolo/<id>/planilla3/` | Formset de medidas. **Ayuda: `planilla3`** |
| 15 | Planilla 4 | `…/protocolo/<id>/planilla4/` | Fechas. **Ayuda: `planilla4`** |
| 16–28 | Los 13 formularios de factor | `…/factores/<id>/<factor>/` | Guardar / Guardar y calcular. **Ayuda: slug del factor** |
| 29 | Wizard de resumen | `…/factores/<id>/resumen/` | 13 estados, resultado global. **Ayuda: `wizard_resumen`** |
| 30 | Panel de exportación | `…/documentos/<id>/` | 7 acciones. **Ayuda: `exportaciones`** |

Cinco de los formularios de factor requieren atención adicional, porque son los que llevan JavaScript con nonce **[VERIFICADO]**:

| Formulario | Template | JavaScript |
|---|---|---|
| Base de factor | `factor_form_base.html:139` | Lógica común de guardado |
| Vibración mano-brazo | `vibracion_mano_brazo_form.html:233` | Cálculo de ejes |
| Posturas forzadas | `posturas_forzadas_form.html:358` | Puntajes REBA |
| Bipedestación | `bipedestacion_form.html:204` | Agravantes |
| Vibración cuerpo entero | `vibracion_cuerpo_entero_form.html:405` | Tramos VCE |

## 11.5 Verificación manual — pantallas del destino

**Ninguna debe cambiar de comportamiento** salvo las dos que la integración toca deliberadamente.

| Pantalla | Riesgo | Fase que lo introduce |
|---|---|---|
| `/dashboard/` profesional | **Alto** — se modifica el template | 4 |
| `/dashboard/` empresa | Medio — misma plantilla base | 4 |
| `/dashboard/capacitaciones/` y sus 4 subpantallas | Medio — plantilla base | 4, 6 |
| `/dashboard/empresa/nomina/` y sus 5 subpantallas | **Alto** — la Fase 0 toca sus vistas | 0 |
| `/dashboard/empresa/agenda/` y sus 4 subpantallas | **Alto** — Fase 0 + sincronización | 0, 5 |
| `/dashboard/empresa/directorio/` | Alto — Fase 0 | 0 |
| `/dashboard/solicitudes-contacto/` | Alto — Fase 0 | 0 |
| `/dashboard/presencial/` y sus 5 subpantallas | Medio — `presencial/quiz.html` tiene 2 handlers inline | 6 |
| `/capacitacion/` con chat Ergobot | **Alto — CF-1** | 6 |
| `/quiz/` completo | Medio — `quiz_widget.html` tiene script inline | 6 |
| `/` landing | Medio — plantilla base | 6 |
| `/acceso/` y los 3 flujos de login | Bajo | 0 |

## 11.6 Verificación de artefactos normativos

| Verificación | Comando | Criterio |
|---|---|---|
| Los 13 JSON son idénticos | `diff -r <origen>/evaluaciones/data <destino>/apps/ergonomia_886/evaluaciones/data` | Sin diferencias |
| El PDF oficial es idéntico | `sha256sum` del archivo | `bc0d0753943888779abd0936f6c4dc2e128766c7cf6370a4a2fb19073aad59f4` |
| Los 12 mapas son idénticos | `diff -r .../official/maps` | Sin diferencias |
| Los 33 `.md` de ayuda son idénticos | `diff -r static/ayuda/help_texts` | Sin diferencias |
| Los checksums se registran en los cálculos | Calcular un factor e inspeccionar `calc_data["calculation_trace"]["sources"][0]["sha256"]` | Presente y de 64 hex |

> **Los artefactos deben copiarse byte a byte.** Una diferencia de fin de línea o de codificación cambia el SHA-256, y con él la trazabilidad de todos los cálculos futuros. Conviene copiar en modo binario y verificar con `diff -r` antes de arrancar.

## 11.7 Compuertas de despliegue

Antes de cada despliegue, y siempre en este orden **[VERIFICADO — protocolo de `INCIDENTE_MIGRACION_TRANSPORTE_2026-08-01.md` §7]**:

```bash
.venv/bin/python manage.py makemigrations --check --dry-run   # ¿modelos sin migración?
.venv/bin/python manage.py migrate --noinput                  # aplicar
.venv/bin/python manage.py migrate --check                    # ¿migraciones sin aplicar?
.venv/bin/python manage.py createcachetable                   # idempotente
.venv/bin/python manage.py collectstatic --noinput
.venv/bin/python manage.py check --deploy
# recién entonces: reiniciar procesos
# y finalmente: prueba de humo autenticada
```

`makemigrations --check` y `migrate --check` **resuelven problemas distintos y ambos son necesarios**: el primero detecta modelos sin migración; el segundo, migraciones sin aplicar. El incidente del 01/08/2026 ocurrió por falta del segundo.

---

# PARTE XII — RIESGOS, DEUDAS HEREDADAS Y FUERA DE ALCANCE

## 12.1 Riesgos de la integración

| # | Riesgo | P | I | Mitigación | Fase |
|---|---|---|---|---|:---:|
| **R-1** | Una de las 48 cadenas literales queda sin actualizar → HTTP 500 diferido al abrir una pantalla | **Alta** | Medio | `checks.py` (T-1) convierte el fallo diferido en fallo de arranque | 2 |
| **R-2** | Activar el CSP deja el frontend del destino sin estilos ni JS | Alta sin remediar | **Alto** | Fase 6 separada, secuencia 6.1→6.7, período en `Report-Only` | 6 |
| **R-3** | N1/N2 se confunden con fallas de la integración | Alta | Medio | **Fase 0 obligatoria.** Única dependencia dura de orden | 0 |
| **R-4** | Cuotas no globales por falta de `CACHES` | Media | Medio | B4 + verificación explícita del lease | 0 |
| **R-5** | SSE sobre workers WSGI degrada el servicio | Media | **Alto** | Preexistente (H12). Se agrava con dos consumidores de SSE | — |
| **R-6** | `openai` 1.x → 2.x altera el comportamiento | Baja | Medio | API verificada presente en 0.6.9. Las 38 pruebas de IA usan `patch` | 2 |
| **R-7** | Los 28 templates no se ven bien sobre tema oscuro | **Alta** | Bajo | Medio día de ajuste previsto en la Fase 4 | 4 |
| **R-8** | El bloque `help_slug` se rompe al cambiar la herencia → widget siempre con slug `home` | Media | Medio | Plantilla intermedia `base_886.html` (§7.9) + verificación de las 23 pantallas | 2, 4 |
| **R-9** | Truncamiento al copiar de `CompanyProfile` a `Evaluacion` | Media | Medio | Ampliar longitudes en la migración `0002` (§8.2) | 3 |
| **R-10** | La superficie de datos personales ampliada se filtra al LLM | Media | **Alto** | **Ampliar `CLAVES_PROHIBIDAS`** + T-7 (**CF-4**) | 3 |
| **R-11** | SQLite en las pruebas oculta un defecto que sólo aparece en PostgreSQL | Baja | Medio | Verificar los 32 tests del destino bajo `test_settings` antes de trasplantar | 0 |
| **R-12** | Las señales de sincronización con la agenda son difíciles de razonar | Media | Bajo | Llamada explícita desde la vista en lugar de `post_save` (Área 6) | 5 |

## 12.2 Deudas heredadas de ErgoApp que la integración NO resuelve

| ID | Deuda | Por qué no se resuelve aquí |
|---|---|---|
| **D-4** | Los booleanos de Planilla 2 no distinguen «NO» de «sin responder» | Requiere cambiar `BooleanField` → `BooleanField(null=True)` en 9 modelos y revisar toda la lógica de export. Es un trabajo con alcance propio. **La regla de CF-5 lo compensa funcionalmente** |
| **D-5** | La interfaz gestiona una sola instancia por Planilla 2 | `planillas/views.py:171` usa `.first()`. El modelo y la exportación ya soportan N. Es una mejora de interfaz, no de integración |
| **D-9** | No existe el concepto de «protocolo cerrado» | Requiere diseñar autor, timestamp y reglas de inmutabilidad. **Es la deuda funcionalmente más importante** para un producto que emite documentación legal |
| **D-10** | `planillas/views.py:30` importa helpers privados de `evaluaciones.views` | Acoplamiento entre apps por API privada. Se arrastra tal cual |
| **D-11** | Tres artefactos con criterios internos, no tablas oficiales | Requiere decisión profesional nominal. **Ver §12.4** |

## 12.3 Deudas del destino y su relación con el orden de trabajo

| ID | Deuda | Relación con la integración |
|---|---|---|
| **N1** | 9 rutas con HTTP 500 anónimo | 🔴 **Bloquea.** Fase 0. Si no se repara, cada 500 durante la integración obliga a investigar si es propio o heredado |
| **N2** | Ficha del trabajador rota | 🔴 **Bloquea.** Fase 0. Mismo motivo |
| **H-F** | `PROFESSIONAL_LOGIN_URL` y `PROFESSIONAL_LOGIN_REDIRECT_URL` no resuelven | 🟡 Misma familia que N1. Corregir en el mismo commit |
| **H-E** | Frontend con CDN, scripts inline y handlers | 🟡 **Condiciona la Fase 6.** No bloquea el resto |
| **H-B** | Sin configuración de pruebas | 🔴 **Bloquea.** Sin ella no hay criterio de aceptación verificable |
| **N8** | `pillow` no declarada | 🟡 Se resuelve junto con `pypdf` |
| **H12** | Vistas async sobre workers WSGI | 🟠 **No bloquea, pero se agrava.** Ver §12.5 |
| **N3** | Directorio inalcanzable | 🔵 Ajena |
| **H1** | Sin backup automatizado de producción | 🔴 **Ajena pero prioritaria.** Es el riesgo #1 del proyecto |
| **H4** | `main` 40 commits atrás | 🔵 Ajena. Conviene resolverla antes de que la integración amplíe la brecha |

> **Sobre el orden.** El informe consolidado del destino ubica el backup (H1) como prioridad 1 y las regresiones (N1, N2) como 2 y 3. **Esta propuesta no altera ese orden**: la Fase 0 recoge N1 y N2 porque son las que bloquean técnicamente la integración, pero H1 es más urgente en términos absolutos y no requiere tocar código.

## 12.4 Riesgo de producto — ✅ RESUELTO el 02/08/2026

> ### ✅ Actualización — las siete aprobaciones fueron otorgadas
>
> **Pablo R. Aguirre adoptó profesionalmente las siete fuentes.** El riesgo descripto en esta sección queda cerrado.
>
> El análisis que sigue se conserva porque **explica qué se aprobó y por qué importaba**, y porque el texto de cada aprobación (el campo `scope` que el commit 1.0 registra) debe derivarse de él. Lo que cambia es el estado, no el análisis.
>
> | Evaluación | Estado al 31/07/2026 | Estado al 02/08/2026 |
> |---|---|---|
> | Bipedestación | `pending` | ✅ **Aprobada** — método de cribado interno adoptado |
> | Estrés de contacto | `pending` | ✅ **Aprobada** — matriz cuantitativa adoptada |
> | Confort térmico | `pending` | ✅ **Aprobada** — digitalización de la curva de Fanger adoptada |
> | Vibración mano-brazo | `pending` | ✅ **Aprobada** — banda de acción interna al 50 % |
> | Vibración cuerpo entero | `pending` | ✅ **Aprobada** — método A(8) de la Directiva 2002/44/CE adoptado |
> | Tracción inicial | `pending` | ✅ **Aprobada** — valor 140 N aceptado expresamente |
> | Transporte | `pending` | ✅ **Aprobada** — Tabla 1 corregida |
>
> **El módulo puede usarse en producción.** El registro nominal y fechado en los artefactos es el commit 1.0 del roadmap.

### Análisis original — por qué estas aprobaciones eran necesarias

**[VERIFICADO — `VALIDACION_PROFESIONAL_FUENTES_EVALUACIONES_2026-07-31.md`]** El propio proyecto de origen documenta que **la evidencia no permite aprobar íntegramente siete de sus fuentes normativas**:

| Evaluación | Estado declarado |
|---|---|
| Bipedestación | **No aprobable** sin justificar la matriz 3×3, los cortes 2/4 h, la atenuación 0,7 y el umbral >100 m/h |
| Estrés de contacto | **No aprobable** como método cuantitativo: la planilla oficial es cualitativa y no prescribe 100/150 kPa ni 30/60 % |
| Confort térmico | **Parcial**: método oficial verificado; digitalización de la curva de Fanger pendiente |
| Vibración mano-brazo | **Parcial**: máximos verificados; la banda de acción del 50 % no está en la tabla oficial |
| Vibración cuerpo entero | Aprobable como método internacional complementario, **no como límite primario** de la Res. 295/03 |
| Tracción inicial | **Parcial**: la sustitución `1460 N → 140 N` requiere decisión profesional explícita |
| Transporte | Fuente verificada y corregida; **falta aprobación profesional nominal** |

**Por qué esto importa para la integración.** Hoy ErgoApp es una aplicación separada, en desarrollo, con datos ficticios. Al integrarse en ErgoSolutions pasa a ser **una herramienta de un producto comercial que emite documentación presentable ante la ART y la SRT**, bajo la marca y la matrícula del profesional titular.

La exposición cambia de naturaleza. Un cribado interno declarado como tal en una aplicación de desarrollo es aceptable; el mismo cribado en un protocolo firmado y presentado ante un organismo de control no lo es.

**Las siete decisiones profesionales que el documento de validación reclamaba —nombre y matrícula del responsable, adopción expresa del método A(8), decisión sobre la banda de VMB, sobre la digitalización de Fanger, sobre los cribados internos y sobre la celda de 140 N— ✅ fueron adoptadas el 02/08/2026.**

El proyecto hizo lo correcto en su momento: los `meta` de los JSON declaraban `professional_approval.status=pending` en lugar de presentar los criterios internos como si fueran normativos. Ese mecanismo es ahora el que registra la aprobación, con responsable, fecha y alcance.

**Queda pendiente sólo el trabajo técnico de registro** (commit 1.0 del roadmap), no la decisión.

## 12.5 Fuera de alcance — infraestructura

| Tema | Situación | Por qué queda fuera |
|---|---|---|
| **Migración a ASGI** | `config/asgi.py` y `uvicorn` existen; producción corre WSGI sync (H12) | Cada chat SSE ocupa un worker completo. Con 3 workers, 3 conversaciones dejan el sitio sin capacidad. **La integración agrega un segundo consumidor de SSE y agrava el problema.** Es un cambio de despliegue con alcance propio |
| **Backup de producción (H1)** | Inexistente | Ajeno al código. **Es el riesgo #1 del proyecto** |
| **Rotación de logs (H3)** | Inexistente | Ajeno al código |
| **Certificados descargables sin auth (H2)** | Abierto | Ajeno al módulo |
| **Emails síncronos (H11)** | Abierto | Ajeno al módulo |
| **Firma hardcodeada en certificados (H20)** | Abierta | El módulo aporta el patrón correcto (§ Área 7), pero aplicarlo excede este alcance |

## 12.6 Fuera de alcance — funcionalidad

| Tema | Estado |
|---|---|
| Módulos de evaluación de **iluminación** y **ruido** | No existen. La tarjeta del dashboard los prometía; el texto propuesto en §7.7 lo corrige |
| Concepto de **protocolo cerrado** (D-9) | No existe en ninguno de los dos proyectos |
| Interfaz de **N instancias por Planilla 2** (D-5) | El modelo lo soporta; la interfaz no |
| Distinción **«NO» vs «sin responder»** (D-4) | Requiere cambio de modelo |
| Compartir una evaluación **entre profesionales** | Ver el punto abierto de §7.6 |
| **Suscripciones** y facturación del módulo | `CustomUser` tiene los campos preparados e inactivos |

## 12.7 Puntos abiertos que requieren decisión antes de ejecutar

| # | Decisión pendiente | Quién decide | Bloquea |
|---|---|---|---|
| **1** | Aceptar el criterio reformulado de CF-1 (H-J) | Titular del proyecto | Fase 1 |
| **2** | Qué modelo de lenguaje usa el módulo en producción (`gpt-5.6-luna` o el del destino) | Titular | Fase 2 |
| **3** | ¿Namespace anidado `ergonomia_886:planillas:` o plano `planillas:`? | Arquitecto | Fase 2 |
| **4** | ¿Un profesional ve las evaluaciones de otro sobre la misma empresa? | Titular | Fase 3 |
| **5** | Ampliar longitudes de `Evaluacion` o truncar al copiar | Arquitecto | Fase 3 |
| **6** | Documentos de ayuda: ¿en `static/` (opción A) o dentro de la app (opción B)? | Arquitecto | Fase 2 |
| **7** | ¿Se ejecuta la Fase 6 (CSP), y cuándo? | Titular | — |
| **8** | ~~Las siete aprobaciones profesionales de las fuentes normativas~~ | ~~Profesional matriculado~~ | ✅ **RESUELTO** — ver nota |

> ### ✅ Actualización del 2 de agosto de 2026 — punto 8 cerrado
>
> **Pablo R. Aguirre otorgó las siete aprobaciones profesionales.** El punto deja de estar abierto.
>
> Queda como **trabajo técnico derivado**, no como decisión pendiente: los siete artefactos siguen declarando `professional_approval.status = "pending"` en su bloque `meta`, y su `provenance_status` arrastra el sufijo `pending_professional_approval`. **Registrar la aprobación de forma nominal y fechada es el commit 1.0 del roadmap de ejecución.**
>
> Tres precisiones que ese commit debe respetar **[VERIFICADO]**:
>
> 1. **`data_version` NO se bumpea.** `evaluaciones/data/README.md` la define como «versión semántica de los **valores** contenidos», y la aprobación no cambia ningún valor. Además, `evaluaciones/tests.py:1035` verifica `data_version == "1.1.0"` para `traccion_inicial`.
> 2. **El SHA-256 de los siete artefactos SÍ cambia**, porque `data_file_sha256()` calcula el hash sobre los bytes del archivo completo, incluido el `meta`. Es el comportamiento correcto: un artefacto con aprobación registrada es un artefacto distinto del que no la tenía, y la trazabilidad debe poder distinguirlos.
> 3. **La prueba de metadatos ya soporta el estado `approved`.** `evaluaciones/tests.py:145-153` valida que, con `status == "approved"`, existan `approved_by` no vacío y `approved_at` como fecha ISO. **No hay que modificar ninguna prueba.**
>
> Los otros seis artefactos permanecen en `not_recorded` y **no se tocan**: son transcripciones literales de fuentes primarias y ese estado es el correcto.
>
> Ver `ROADMAP_INTEGRACION_ERGONOMIA_886.md`, commit 1.0.

---

# ANEXOS

## Anexo A — Inventario de archivos a trasplantar

### A.1 Código Python — 4 apps, 71 archivos

| App | Archivos | Líneas aprox. | Destino |
|---|---:|---:|---|
| `planillas` | 10 | 1.100 | `apps/ergonomia_886/planillas/` |
| `evaluaciones` | 20 | 9.168 | `apps/ergonomia_886/evaluaciones/` |
| `exportaciones` | 28 | 4.077 | `apps/ergonomia_886/exportaciones/` |
| `help_ai` | 13 | 1.052 | `apps/ergonomia_886/help_ai/` |
| **Total** | **71** | **~15.400** | |

**No se trasplanta:** `core/` (8 archivos, 159 líneas) — se disuelve. Se preserva, reimplantada, la lógica de `core/views.py:37-118`.

### A.2 Migraciones — 10 archivos, copiados sin modificar

```
planillas/migrations/0001_initial.py
evaluaciones/migrations/0001_initial.py
evaluaciones/migrations/0002_alter_empujeinicial_eval_altura_agarre_cm_and_more.py
evaluaciones/migrations/0003_transporte_eval_en_plano_horizontal_and_more.py
evaluaciones/migrations/0004_bipedestacion_eval_brazos_elevados_and_more.py
evaluaciones/migrations/0005_vibracionmb_eval_ax_mps2_vibracionmb_eval_ay_mps2_and_more.py
evaluaciones/migrations/0006_vibracionce_eval_calc_details_and_more.py
evaluaciones/migrations/0007_transporte_frecuencias_maximas.py
exportaciones/migrations/0001_initial.py
exportaciones/migrations/0002_generatedreport.py
```

### A.3 Templates — 27 archivos

| Origen | Destino | Cambio |
|---|---|---|
| `planillas/templates/planillas/*.html` (6) | ídem bajo el módulo | `{% extends %}` |
| `evaluaciones/templates/evaluaciones/*.html` (16) | ídem | Sólo `factor_form_base.html` cambia `{% extends %}` |
| `exportaciones/templates/exportaciones/*.html` (2) | ídem | `{% extends %}` |
| `core/templates/core/dashboard.html` | `planillas/templates/planillas/evaluacion_list.html` | Reimplantado |
| `core/templates/core/{login,registro}.html` | — | **Se descartan** |
| `templates/base.html` (origen) | `templates/ergonomia_886/_help_widget.html` | Sólo el widget (`:49-113`) |

### A.4 Artefactos normativos y binarios — **copiar byte a byte**

| Categoría | Cantidad | Ruta de origen | Verificación |
|---|---:|---|---|
| Artefactos normativos JSON | **13** | `evaluaciones/data/*.json` | `diff -r` |
| README de artefactos | 1 | `evaluaciones/data/README.md` | — |
| **PDF oficial de la SRT** | **1** | `exportaciones/official/templates_bin/res_srt_886_15-formulario.pdf` | **SHA-256 `bc0d0753…59f4`**, 251.599 bytes |
| Mapas de calibración | **12** | `exportaciones/official/maps/*.json` | `diff -r` |
| Fixtures | — | `evaluaciones/fixtures/` | — |

### A.5 Estáticos — 44 archivos, sin colisión con el destino

| Categoría | Cantidad | Origen → Destino |
|---|---:|---|
| Documentos de ayuda | **33** | `static/ayuda/help_texts/*.md` |
| CSS del widget | 1 | `static/ayuda/css/help_widget.css` |
| JS del widget | 1 | `static/ayuda/js/help_widget.js` |
| JS de planillas | 1 | `static/js/planilla_logic.js` |
| Bootstrap CSS + JS | 2 | `static/vendor/bootstrap/` |
| Bootstrap Icons CSS | 1 | `static/vendor/bootstrap-icons/` |
| Fuentes de Bootstrap Icons | 2 | `static/vendor/bootstrap-icons/fonts/` |
| `marked` | 1 | `static/vendor/marked/` |
| `DOMPurify` | 1 | `static/vendor/dompurify/` |
| README de vendor | 1 | `static/vendor/README.md` |

### A.6 Referencias a reescribir — resumen cuantitativo

| Tipo | Cantidad | Detección |
|---|---:|---|
| Imports absolutos entre apps | **102** | `grep -rn "from \(core\|planillas\|evaluaciones\|exportaciones\|help_ai\)[. ]"` |
| Rutas en cadenas literales | **48** | Búsqueda manual — **no las detecta ningún refactor automático** |
| — `form_path` / `model_path` de factores | 26 | `evaluaciones/catalog.py` |
| — `model_path` de planillas oficiales | 12 | `exportaciones/official/catalog.py` |
| — `PLANILLA2_MODELOS` | 9 | `exportaciones/serializers.py:22-32` |
| — Recurso de paquete | 1 | `evaluaciones/calculators.py:71` |
| Referencias de URL sin namespace | **35** | 21 en templates, 14 en Python |
| Referencias a `core:*` | **16** | Se descartan o reapuntan |
| `{% extends "base.html" %}` | **10** | Cambian a la plantilla intermedia |
| `name` en `apps.py` | **4** | |
| Cálculos de ruta de archivo | **1** | `help_ai/prompts.py:14-15` (B6) |
| **Total** | **~216** | |

## Anexo B — Dependencias a agregar

```diff
  # requirements.txt de ErgoSolutions
  Django>=5.2,<6.0
  psycopg[binary]>=3.2
  django-environ>=0.11
  django-bootstrap5>=25.1
  whitenoise>=6.7
  reportlab>=4.0,<5.0
+ pypdf>=5.0,<7.0            # superposición sobre el PDF oficial de la SRT — CF-6
+ pillow>=10.0               # requerida por ImageField (logo de empresa, evidencia VCE)
  openai>=1.0
  openai-agents>=0.0.19
  uvicorn>=0.30.0
```

**No se agregan** (se descartan del origen): `psycopg2-binary` (el destino usa psycopg 3), `django-cors-headers` (D-10), `sse-starlette` (declarada, no usada), `gunicorn` (ya en producción del destino), `weasyprint` (D-7, nunca declarada).

## Anexo C — Variables de entorno nuevas

Ninguna es obligatoria: las 14 tienen valor por defecto. Se listan para el `.env.example`.

```bash
# ===========================================================
# Módulo de Ergonomía SRT 886/15
# ===========================================================

# --- Modelo de lenguaje -------------------------------------------------
# Por defecto usa OPENAI_MODEL. Definir sólo para que el módulo use otro.
# CHAT_AI_MODEL=

# --- Chat de ayuda contextual (help_ai) ---------------------------------
CHAT_AI_AGENT_CACHE_SIZE=64          # agentes cacheados por (slug, versión)
CHAT_AI_RATE_LIMIT=20                # consultas por ventana y usuario
CHAT_AI_RATE_WINDOW_SECONDS=60
CHAT_AI_STREAM_TIMEOUT_SECONDS=120   # tope duro del stream SSE
CHAT_AI_HEARTBEAT_SECONDS=10
CHAT_AI_MAX_QUESTION_CHARS=2000
CHAT_AI_MAX_THREAD_MESSAGES=20
CHAT_AI_MAX_MESSAGE_CHARS=4000

# --- Informes profesionales (exportaciones) -----------------------------
REPORT_AI_TIMEOUT_SECONDS=90
REPORT_AI_RATE_LIMIT=10              # informes por hora y usuario
REPORT_AI_RATE_WINDOW_SECONDS=3600

# --- Descarga de documentos ---------------------------------------------
EXPORT_RATE_LIMIT=60                 # descargas por ventana y usuario
EXPORT_RATE_WINDOW_SECONDS=300
```

> **Las cuotas dependen de `CACHES` compartida (B4).** Con `LocMemCache` se multiplican por la cantidad de workers sin ningún síntoma visible.

## Anexo D — Comandos de verificación

```bash
# --- ErgoSolutions ---
cd /Users/praguirre/ergocapacitacion
.venv/bin/python manage.py check
.venv/bin/python manage.py check --deploy
.venv/bin/python manage.py makemigrations --check --dry-run
.venv/bin/python manage.py migrate --check
.venv/bin/python manage.py test --settings=config.test_settings
.venv/bin/python manage.py createcachetable

# --- ErgoApp SRT 886 (durante la Fase 1) ---
cd /Users/praguirre/ergonomia_srt
./venv/bin/python manage.py test --settings=ergonomia_srt.test_settings
./venv/bin/python manage.py makemigrations --check --dry-run

# --- Integridad de artefactos ---
shasum -a 256 apps/ergonomia_886/exportaciones/official/templates_bin/res_srt_886_15-formulario.pdf
diff -r /Users/praguirre/ergonomia_srt/evaluaciones/data \
        apps/ergonomia_886/evaluaciones/data
diff -r /Users/praguirre/ergonomia_srt/static/ayuda/help_texts \
        static/ayuda/help_texts

# --- Verificación de CF-1 ---
grep -ri "ergobot" apps/ergonomia_886/     # debe estar vacío
grep -ri "help_ai" apps/ergobot_ai/        # debe estar vacío

# --- Referencias pendientes de actualizar ---
grep -rn "from \(core\|planillas\|evaluaciones\|exportaciones\|help_ai\)[. ]" apps/ergonomia_886/
grep -rn "{% url '\(crear_evaluacion\|detalle_evaluacion\|planilla\|help_guide\|chat_ai\)" apps/ergonomia_886/
grep -rn "\"planillas.models\.\|\"evaluaciones\.\(forms\|models\|data\)" apps/ergonomia_886/
```

## Anexo E — Glosario

| Término | Significado |
|---|---|
| **SRT 886/15** | Resolución 886/2015 de la Superintendencia de Riesgos del Trabajo. Establece el Protocolo de Ergonomía obligatorio en Argentina |
| **Res. 295/03** | Resolución MTEySS 295/2003. Especificaciones técnicas de ergonomía y valores límite |
| **Res. SRT 3345/15** | Resolución complementaria con las tablas de empuje, tracción y transporte |
| **Planilla 1** | Identificación de factores de riesgo, con la matriz A–I |
| **Planillas 2A–2I** | Checklists de evaluación inicial, una por factor |
| **Planilla 3** | Medidas correctivas y preventivas |
| **Planilla 4** | Matriz de seguimiento de las medidas |
| **Matriz A–I** | Los 9 factores del protocolo: A levantamiento, B empuje/arrastre, C transporte, D bipedestación, E movimientos repetitivos, F postura forzada, G vibraciones, H confort térmico, I estrés de contacto |
| **REBA** | *Rapid Entire Body Assessment*. Método de evaluación de posturas forzadas (Hignett y McAtamney, 2000) |
| **A(8)** | Exposición diaria a vibraciones normalizada a 8 horas |
| **VCE / VMB** | Vibración de cuerpo entero / vibración mano-brazo |
| **NAM** | Nivel de Actividad Manual, para movimientos repetitivos |
| **Escala de Borg** | Escala de esfuerzo percibido, usada en la Planilla 2E |
| **Curva de Fanger** | Curva de confort térmico impresa en la Planilla 2H |
| **CIIU** | Clasificador Industrial Internacional Uniforme |
| **Superposición** | Técnica de generar una capa transparente con ReportLab y fusionarla con `pypdf` sobre el PDF oficial, sin alterarlo (CF-6) |
| **`calc_data`** | `JSONField` con el snapshot de inputs, el estado, la trazabilidad y el juicio profesional de cada factor (CF-3) |
| **`calculation_trace`** | Bloque de `calc_data` con la versión del motor y el SHA-256 de cada artefacto aplicado |
| **Artefacto normativo** | Archivo JSON versionado con las tablas de una fuente normativa, identificado por SHA-256 |
| **Estado operativo** | `sin_iniciar`, `borrador`, `calculado`, `desactualizado`, `no_aplicable`, `revisado` |
| **Revisión profesional** | Única forma autorizada de modificar una clasificación del motor, con justificación registrada (CF-2) |
| **Lease** | Cerrojo distribuido sobre la caché que impide que un usuario abra dos streams simultáneos |
| **SSE** | *Server-Sent Events*. Transporte de streaming unidireccional usado por ambos asistentes |
| **`app_label`** | Identificador corto de una app Django, derivado de la última componente del nombre punteado |
| **`swappable_dependency`** | Declaración de migración que resuelve la dependencia contra el `AUTH_USER_MODEL` vigente |
| **Backoffice** | Área de gestión de ErgoSolutions, accesible a `professional` y `company` |
| **CF-1 … CF-6** | Las seis condiciones fundamentales vinculantes de la integración (Parte IX) |
| **B1 … B8** | Los ocho bloqueantes duros (Parte VI) |
| **N1 … N13, H1 … H20** | Hallazgos del informe de estado de ErgoSolutions |
| **D-1 … D-11** | Deudas técnicas de ErgoApp SRT 886 |
| **H-A … H-K** | Hallazgos nuevos de este documento, donde el código contradice a la documentación previa |

## Anexo F — Hallazgos de este documento

Discrepancias entre la documentación existente y el código verificado. **En todos los casos gana el código.**

| ID | Hallazgo | Fuente contradicha | Efecto |
|---|---|---|---|
| **H-A** | `LANGUAGE_CODE` del destino es `es-ar`, no `en-us` | ErgoApp D-8 | ✅ Simplifica: cierra D-8 sin trabajo |
| **H-B** | ErgoSolutions no tiene configuración de pruebas aislada | No documentado | 🔴 **Nuevo bloqueante B8** |
| **H-C** | El prefijo `/ai/` ya está ocupado por `ergobot_ai` | No documentado | 🟡 Motiva la decisión D-5 |
| **H-D** | `apps.ergobot_ai.urls` tampoco declara `app_name` | No documentado | 🟡 El destino padece el mismo defecto que B3 |
| **H-E** | El frontend del destino tiene 6 CDN, 5 scripts inline y 3 handlers | ErgoApp §9.3 B4 lo describía como «auditar» | 🔴 **Cambia el plan: CSP pasa a la Fase 6** |
| **H-F** | `PROFESSIONAL_LOGIN_URL` y `PROFESSIONAL_LOGIN_REDIRECT_URL` no resuelven | No documentado | 🟡 Misma familia que N1 |
| **H-G** | **La migración de `planillas` ya es `swappable`. B1 no genera migración** | ErgoApp §9.3 B1 | ✅ **Simplifica sustancialmente** |
| **H-H** | Son **13** artefactos normativos, no 14 | ErgoApp §5.3 y checklist §9.8 | ✅ Corrige un criterio incumplible |
| **H-I** | Son **33** documentos de ayuda, no 34 | ErgoApp §5.5 y CF-1 | ✅ Corrige el inventario |
| **H-J** | **CF-1 («22 pruebas sin modificación») es incompatible con B3** | ErgoApp §9.5 CF-1 | ⚠️ **Requiere decisión formal** |
| **H-K** | **Sin CSP, los scripts del módulo siguen funcionando** | ErgoApp §3.3 | ✅ **Permite separar la Fase 6 del camino crítico** |

Adicionalmente, dos precisiones sobre `app_label` y rutas de archivo:

| ID | Precisión | Efecto |
|---|---|---|
| **H-L** | Los `app_label` no colisionan → migraciones intactas, sin `SeparateDatabaseAndState` | ✅ Simplifica B2 |
| **H-M** | `help_ai/prompts.py:14-15` sube dos niveles y se rompe al anidar la app | 🔴 **Nuevo bloqueante B6** |
| **H-N** | Las factorías heredadas del módulo crean usuarios con `create_user()` sin `user_type`; en ErgoSolutions eso produce `trainee`, no `professional` | Roadmap 3.3 («21 pruebas sin modificación») | ⚠️ Se declaró `user_type="professional"` sólo en los fixtures que ejercitan actos profesionales, sin cambiar casos ni aserciones; D-9 permanece estricta |

---

## Cierre

Este documento es **diagnóstico y de diseño**. No se modificó ninguna línea de código de ninguno de los dos proyectos: el único archivo escrito es este.

**Estado verificado de ambos proyectos al 2 de agosto de 2026:**

| Proyecto | Rama | Commit | Suite | Migraciones |
|---|---|---|---|---|
| ErgoSolutions | `release/beta` | — | **32 tests OK** | `No changes detected` |
| ErgoApp SRT 886 | `main` | `8b61e62` | **160 tests OK** | `No changes detected` |

**Los tres puntos que deben decidirse antes de escribir la primera línea de código** son el criterio reformulado de CF-1 (H-J), la ampliación de `CLAVES_PROHIBIDAS` exigida por CF-4, y si la Fase 6 (CSP) entra en el alcance.

**El único punto que debe resolverse antes de usar el módulo en producción no es técnico:** las siete aprobaciones profesionales de las fuentes normativas que el propio proyecto de origen documenta como pendientes.

*Documento redactado el 2 de agosto de 2026 sobre lectura directa del código de ambos proyectos y ejecución de sus dos suites de pruebas.*
