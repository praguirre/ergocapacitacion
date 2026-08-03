# ErgoSolutions

**Plataforma integral para profesionales de Seguridad e Higiene, Salud Ocupacional y Ergonomía.**

## Descripción

ErgoSolutions permite a profesionales gestionar capacitaciones laborales en dos modalidades:

- **Presencial**: Video + Chat IA + Quiz grupal + Planilla PDF de asistencia
- **Online**: Links compartibles + Registro individual + Quiz con reglas + Certificado PDF automático

## Tecnologías

- **Backend**: Django 5.2+ / PostgreSQL
- **Frontend**: Bootstrap 5 / Bootstrap Icons
- **IA**: OpenAI GPT (Ergobot AI) con streaming SSE
- **PDF**: ReportLab
- **Async**: ASGI + Uvicorn

## Instalación

```bash
# 1. Clonar
git clone https://github.com/praguirre/ergocapacitacion.git
cd ergocapacitacion

# 2. Entorno virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# 3. Dependencias
pip install -r requirements.txt

# 4. Variables de entorno
cp .env.example .env
# Editar .env con datos de DB y API keys

# 5. Base de datos
python manage.py migrate

# 6. Datos iniciales
python manage.py seed_quiz         # Preguntas del quiz
python manage.py seed_modules      # Módulos de capacitación

# 7. Superusuario
python manage.py createsuperuser

# 8. Iniciar
python manage.py runserver
```

## Estructura de URLs

| URL | Descripción |
|-----|-------------|
| `/` | Landing institucional |
| `/auth/` | Login/Registro profesionales |
| `/dashboard/` | Panel de profesionales |
| `/dashboard/presencial/` | Modo presencial |
| `/dashboard/capacitaciones/` | Menú de capacitaciones |
| `/acceso/` | Login/Registro trabajadores |
| `/capacitacion/` | Capacitación online (trainees) |
| `/c/<slug>/` | Acceso vía link compartido |
| `/quiz/` | Sistema de evaluaciones |
| `/ai/` | Chatbot Ergobot (SSE) |
| `/admin/` | Panel de administración |

## Documentación

La documentación técnica y operativa está centralizada en
[docs/README.md](docs/README.md). Allí se encuentran los roadmaps, planes de
implementación, runbook de despliegue, mapa conceptual e inventario del
proyecto.

El documento de referencia vigente es el
[**Estado técnico consolidado del 01/08/2026**](docs/ESTADO_TECNICO_CONSOLIDADO_2026-08-01.md):
consolida la auditoría de producción con el estado real del código en
`release/beta`, verifica hallazgo por hallazgo qué sigue vigente y qué cambió, y
define el plan de trabajo priorizado para retomar el desarrollo.

La [auditoría técnica de producción del 30/07/2026](docs/INFORME_TECNICO_AUDITORIA_PRODUCCION_2026-07-30.md)
se conserva íntegra como fotografía histórica del despliegue auditado.

### Integración del módulo de Ergonomía SRT 886/15

- **02/08/2026 — Commit 0.0:** se abrió la rama
  `feature/ergonomia-886` y se creó
  `docs/BITACORA_INTEGRACION_886.md`. El estado de partida quedó verificado con
  160 pruebas del módulo y 32 de ErgoSolutions en `OK`, sin cambios de modelos
  pendientes de migración.
- **02/08/2026 — Commit 0.1:** se consolidó el árbol documental pendiente:
  cuatro documentos de la raíz quedaron verificados bajo `docs/`, se incorporó
  el resto de la documentación técnica preparada y se actualizó `.gitignore`.
  `manage.py check` no reportó issues y el smoke test de `GET /` respondió 200.
- **02/08/2026 — Commit 0.2:** se corrigieron cinco nombres de URL inexistentes
  en los decoradores de cuentas. Los accesos anónimos de profesionales,
  empresas y trabajadores ahora resuelven al login correspondiente, cerrando
  la causa raíz de la regresión N1.
- **02/08/2026 — Commit 0.3:** se restauró `@login_required` como capa exterior
  en once vistas de empresa y dos profesionales. Las ocho rutas anónimas
  verificadas redirigen con HTTP 302 y ninguna devuelve 500.
- **02/08/2026 — Commit 0.4:** se calificaron los settings profesionales de
  login y redirección con sus namespaces reales. Los cuatro settings de
  autenticación resuelven correctamente y el login profesional responde 200.
- **02/08/2026 — Commit 0.5:** se corrigió la ficha del trabajador para usar
  `QuizState.last_passed` y `Certificate.is_valid`, eliminando el atributo
  inexistente que causaba la regresión N2.
- **02/08/2026 — Commit 0.6:** se agregaron cuatro pruebas automáticas para N1
  y N2: diez rutas de backoffice anónimas, login resoluble y ficha del
  trabajador con y sin `QuizState`. La suite subió de 32 a 36 pruebas.
- **02/08/2026 — Commit 0.7:** se agregó `config/test_settings.py` con SQLite
  efímero, `LocMemCache`, hashing rápido, storage estático no manifestado y
  correo en memoria. Ejecutar: `.venv/bin/python manage.py test apps
  --settings=config.test_settings`.
- **02/08/2026 — Commit 0.8:** producción y desarrollo usan `DatabaseCache`
  sobre la tabla `ergosolutions_cache` para compartir cuotas y cerrojos entre
  workers. Tras migrar, ejecutar el paso idempotente
  `.venv/bin/python manage.py createcachetable`; la suite aislada conserva
  `LocMemCache`.
- **02/08/2026 — Commit 0.9:** se declararon `pypdf>=5,<7` para superposición
  sobre el PDF oficial (CF-6) y `pillow>=10,<14` para los `ImageField`; además
  se fijaron cotas superiores compatibles para Django, PostgreSQL, ReportLab,
  OpenAI, Agents y Uvicorn.
- **02/08/2026 — Commit 0.10:** `accounts`, `training`, `quiz`, `certificates`,
  `ergobot_ai` y el include público `training_public` ahora declaran
  `app_name`; todas las referencias internas quedaron calificadas sin cambiar
  ningún path público ni el endpoint JavaScript de Ergobot.
- **03/08/2026 — Fase 1:** el origen `ergonomia_srt` quedó preparado y
  publicado con siete commits secuenciales: aprobaciones profesionales,
  usuario swappable, namespaces propios, dependencias alineadas y locale
  `es-ar`; sus 160 pruebas continúan en verde y no se generaron migraciones.
- **03/08/2026 — Commit 2.1:** se creó `apps/ergonomia_886` como paquete
  contenedor desmontable. Su docstring identifica las cuatro apps y deja
  vinculadas las condiciones CF-1 a CF-6 antes del trasplante.
- **03/08/2026 — Commit 2.3:** se trasplantaron byte a byte `planillas`,
  `evaluaciones`, `exportaciones` y `help_ai`, con 10 migraciones, 24
  templates, 13 artefactos normativos y 12 mapas. El PDF oficial conserva el
  SHA-256 `bc0d0753943888779abd0936f6c4dc2e128766c7cf6370a4a2fb19073aad59f4`.
- **03/08/2026 — Commit 2.4:** los cuatro `AppConfig.name` apuntan a su ruta
  punteada bajo `apps.ergonomia_886`; se mantienen los labels finales
  `planillas`, `evaluaciones`, `exportaciones` y `help_ai` sin declararlos ni
  alterar las diez migraciones copiadas.
- **03/08/2026 — Commit 2.5:** se reescribieron los 101 imports absolutos de
  las cuatro apps trasplantadas bajo `apps.ergonomia_886` (el import 102 del
  inventario original pertenecía a `core`, descartado en 2.3). No se modificó
  ninguna migración y 87 sustituciones pertenecen a suites de prueba.
- **03/08/2026 — Commit 2.6:** la ayuda contextual resuelve sus 33 documentos
  Markdown desde `settings.BASE_DIR/static/ayuda/help_texts`, independizando
  la ruta de la profundidad del paquete y manteniendo el error estricto ante
  contenido ausente o inválido.
- **03/08/2026 — Commit 2.7:** se copiaron byte a byte los 44 estáticos del
  módulo: 33 documentos de ayuda, CSS/JS del widget, `planilla_logic.js` y
  dependencias vendor. Los 13 artefactos normativos cargan con SHA-256 y las
  siete aprobaciones profesionales permanecen en estado `approved`.
- **03/08/2026 — Commit 2.8:** Django registra las cuatro apps del módulo con
  sus labels históricos y 14 settings con defaults. `CHAT_AI_MODEL` deriva de
  `OPENAI_MODEL`; `help_ai` y `ergobot_ai` coexisten como apps separadas y las
  cuotas usan el cache compartido configurado en 0.8.
- **03/08/2026 — Commit 2.9:** el módulo se montó bajo
  `/evaluacion-ergonomica/` con namespaces planos para protocolo, factores,
  documentos y ayuda. `help_ai` queda separado del Ergobot docente, que
  conserva su prefijo `/ai/` conforme a CF-1.
- **03/08/2026 — Commit 2.10:** `base_886.html` integra visualmente el módulo
  con el dashboard y declara inline el bloque `help_slug`; nueve templates
  trasplantados cambiaron su herencia y el décimo (`core/dashboard.html`)
  permanece diferido a su reimplementación en 3.6.
- **03/08/2026 — Commit 2.11:** el cuerpo del offcanvas de ayuda contextual se
  extrajo a `_help_widget_body.html`, conservando el token CSRF del chat y los
  identificadores consumidos por `help_widget.js`; el widget sigue perteneciendo
  exclusivamente a `help_ai` conforme a CF-1.
- **03/08/2026 — Commit 2.12:** cuatro chequeos de arranque validan las 48 rutas
  declarativas, los 13 artefactos normativos (CF-3), el PDF oficial y su
  SHA-256 (CF-6), y la ausencia de imports cruzados entre `help_ai` y
  `ergobot_ai` (CF-1).
- **03/08/2026 — Commit 2.13:** se aplicaron las diez migraciones del módulo y
  la suite combinada cerró con 196 pruebas OK. El humo autenticado transaccional
  recorrió diez pantallas, calculó LMC, generó PDF/ZIP y verificó CF-1, CF-5 y
  CF-6 sin persistir datos. DA-2.13 adelantó el mínimo CSP requerido por la
  propia compuerta: vendor local, nonces, listeners y middleware bloqueante.
- **03/08/2026 — Commit 3.1:** `Evaluacion` se vinculó opcionalmente a
  `CompanyProfile` mediante `PROTECT`. Los campos documentales permanecen como
  snapshot histórico y se ampliaron a 300/20/400 caracteres para copiar sin
  truncamiento razón social, CUIT y domicilio.
- **03/08/2026 — Commit 3.2:** se amplió de forma únicamente aditiva la lista
  `CLAVES_PROHIBIDAS` para cubrir trabajadores, empresas, usuarios y datos de
  contacto introducidos por la integración. Una prueba de regresión verifica
  que no sobrevivan claves ni valores personales, mientras conserva el contexto
  mínimo y los datos técnicos requeridos por el informe (CF-4).
- **03/08/2026 — Commit 3.3:** la visibilidad de evaluaciones quedó centralizada
  por tipo de usuario: cada profesional ve sólo las que creó, cada empresa ve
  las vinculadas a su perfil y trainees/anónimos no ven ninguna. Los recursos
  ajenos continúan respondiendo 404 y sólo profesionales activos pueden editar.
  Cinco pruebas nuevas cubren directamente la decisión D-9.
- **03/08/2026 — Commit 3.4:** las vistas funcionales del módulo aplican
  `login_required` antes de `backoffice_required`; las vistas de clase ya
  heredan `LoginRequiredMixin`. Una regresión recorre doce rutas anónimas y
  descarta HTTP 500. El chat conserva su contrato 401 y separación CF-1.
- **03/08/2026 — Commit 3.5:** el alta incorpora un selector de empresas
  activas y snapshots documentales no destructivos. Los datos registrados sólo
  completan valores vacíos al crear; lo escrito por el profesional prevalece y
  futuras ediciones del perfil no alteran evaluaciones emitidas (CF-5).
- **03/08/2026 — Commit 3.6:** `/evaluacion-ergonomica/` es la pantalla de
  aterrizaje del módulo. Conserva búsqueda sobre seis campos, tres filtros,
  seis órdenes permitidos, paginación de veinte y precarga optimizada; aplica
  D-9 y oculta el alta a usuarios empresa.
- **03/08/2026 — Commit 3.7:** la eliminación exige POST y queda restringida
  al profesional autor. Empresas y otros profesionales reciben 404 para no
  confirmar la existencia del protocolo; GET nunca elimina.
- **03/08/2026 — Commit 3.8:** `Evaluacion` incorpora índices compuestos para
  listar por profesional o empresa y última modificación, más un índice por
  CUIT. La migración aditiva fue probada desde cero y aplicada en PostgreSQL.
- **03/08/2026 — Commit 3.9 / cierre de Fase 3:** una suite consolidada cubre
  propiedad mixta D-9, 404 contra enumeración, ausencia de HTTP 500 anónimo,
  edición profesional, saneamiento CF-4, snapshots CF-5 e índices. La fase
  cierra con 224 pruebas OK, checks limpios y smoke autenticado con rollback.
- **03/08/2026 — Commit 4.1:** la tarjeta «Evaluaciones» del dashboard está
  activa, indica «Disponible» y navega a `/evaluacion-ergonomica/`. Su texto
  describe exclusivamente Ergonomía SRT 886/15, sin prometer iluminación ni
  ruido; la tarjeta de Capacitaciones permanece intacta.
- **03/08/2026 — Commit 4.2:** el navbar compartido del backoffice incorpora
  «Evaluaciones» para profesionales y empresas. La entrada permanece activa en
  las pantallas HTML del módulo y el menú colapsable fue validado a 390 px sin
  desbordamiento horizontal.
- **03/08/2026 — Commit 4.3:** el dashboard profesional muestra una cuarta
  estadística con sus evaluaciones ergonómicas. El acceso al modelo es diferido
  y tolerante al desmontaje: sin las cuatro apps 886 el dashboard responde 200
  y omite la estadística.
- **03/08/2026 — Commit 4.4:** los 25 templates HTML del módulo fueron auditados
  para el tema oscuro y sus 30 pantallas quedaron cubiertas por un recorrido
  HTTP. Se verificaron los 23 bloques de ayuda, los cinco scripts interactivos,
  tablas densas y ausencia de overflow; la suite total alcanza 232 pruebas.
- **03/08/2026 — Commit 4.5 / cierre de Fase 4:** se habilitaron tres loggers
  jerárquicos sin payload, sin datos personales ni propagación duplicada. CF-1
  queda verificada por AST, 22 pruebas intactas de `help_ai`, URLs separadas y
  pruebas funcionales de ambos asistentes. La fase cierra con 234 pruebas OK.
- **03/08/2026 — Commit 5.1:** las fotos de montaje y certificados de
  calibración VCE se guardan fuera de `MEDIA_ROOT`, carecen de URL pública y
  sólo se descargan mediante autorización D-9. El ZIP incorpora la evidencia y
  el saneamiento CF-4 continúa excluyéndola; 239 pruebas pasan.

### Registro de cambios documentales

- **30/07/2026:** se creó `docs/`, se incorporó el informe técnico de auditoría
  de producción y se centralizaron los documentos Markdown de arquitectura,
  planificación, operación e inventario que estaban en la raíz. `README.md` y
  `AGENTS.md` permanecen en la raíz por su función operativa.
- **01/08/2026:** se incorporó el **Estado técnico consolidado**, que contrasta
  la auditoría de producción (`v0.1.3-beta`) con el código de desarrollo
  (`v0.1.7-beta`). Resultado del contraste: los 27 hallazgos de la auditoría
  siguen vigentes (4 agravados) y se documentaron 13 hallazgos nuevos de la
  Etapa 3, dos de ellos bloqueantes para el despliegue. El documento pasa a ser
  la referencia de estado del proyecto.

## Tests

```bash
python manage.py test apps.accounts apps.dashboard apps.presencial
```

## Autor

**Lic. Pablo Aguirre** — MN 10.027  
Kinesiólogo y Especialista en Ergonomía

## Roadmap técnico (beta)

- Etapa 3A — Commit 29 completado: soporte base de `user_type='company'` en `CustomUser`.
- Etapa 3A — Commit 30 completado: nueva app `apps.company` y modelo `CompanyProfile`.
- Etapa 3A — Commit 31 completado: decoradores y mixins backoffice multi-tipo (`professional` + `company`).
- Etapa 3A — Commit 32 completado: registro y login de empresa (`/empresa/auth/`) con namespace `accounts_company` para mantener coherencia de URLs.
- Etapa 3A — Commit 33 completado: dashboard refactorizado para backoffice multi-tipo con navbar condicional y context processor de empresa.
- Etapa 3A — Commit 34 completado: perfil de empresa (edición/vista) y despacho por tipo en `dashboard:profile`.
- Etapa 3B — Commit 35 completado: modelo `CompanyWorker` (relación formal empresa↔trabajador).
- Etapa 3B — Commit 36 completado: vista de nómina con búsqueda y filtros (`/dashboard/empresa/nomina/`).
- Etapa 3B — Commit 37 completado: alta manual de trabajadores en nómina (`/dashboard/empresa/nomina/agregar/`).
- Etapa 3B — Commit 38 completado: ficha individual del trabajador (`/dashboard/empresa/nomina/<id>/`).
- Etapa 3B — Commit 39 completado: edición de datos laborales (`/dashboard/empresa/nomina/<id>/editar/`).
- Etapa 3B — Commit 40 completado: exportación de nómina a CSV (`/dashboard/empresa/nomina/exportar/`).
- Etapa 3C — Commit 41 completado: incorporación de `AgendaEvent` para agenda y vencimientos de empresas.
- Etapa 3C — Commit 42 completado: vista de Agenda con filtros y métricas básicas (`/dashboard/empresa/agenda/`).
- Etapa 3C — Commit 43 completado: CRUD básico de eventos de agenda (alta, edición y marcado como completado).
- Etapa 3C — Commit 44 completado: management command `generate_cert_expiry_events` para auto-generar eventos por vencimientos próximos (`--days`, `--dry-run`).
- Etapa 3C — Commit 45 completado: home refactorizada por tipo y panel de vencimientos/agenda para empresa.
- Etapa 3D — Commit 46 completado: directorio básico de profesionales con flag de visibilidad y filtros.
- Etapa 3D — Commit 47 completado: solicitudes de contacto empresa-profesional (envío, listado y respuesta).
- Etapa 3D — Commit 48 completado: testing integral de Etapa 3 y validación de no-regresión de flujos company/professional/trainee.

---

*ErgoSolutions © 2026*
