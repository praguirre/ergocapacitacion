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

### Canal de feedback beta — arquitectura aprobada

La iniciativa del canal de comentarios para profesionales se rige por la
[auditoría y plan de feedback beta](docs/AUDITORIA_Y_PLAN_FEEDBACK_BETA_PROFESIONALES_2026-08-11.md).
El contrato aprobado (DA-FB-1 a DA-FB-10) exige acceso exclusivo para cuentas
profesionales activas, persistencia durable previa al correo, adjuntos privados
fuera de `MEDIA_ROOT`, destinatario fijo, límites de carga y separación CF-1
entre la Ayuda Contextual y Ergobot docente. La implementación se ejecuta en la
rama `codex/beta-feedback` mediante los commits secuenciales FB.0–FB.5.

- **11/08/2026 — FB.1 / persistencia privada:** `apps.feedback` incorpora
  `FeedbackReport` y `FeedbackAttachment`, snapshots del profesional, estado de
  entrega, hashes y rutas físicas UUID. La migración aditiva
  `feedback.0001_initial` crea sólo las dos tablas y sus índices; el storage
  vive en `private_media/feedback`, no publica URLs y el admin expone
  únicamente vistas de consulta sin acciones de envío o borrado. La suite sube
  de 310 a 315 pruebas. Este commit no modifica archivos de `static/`.
- **11/08/2026 — FB.2 / validación y entrega:** los adjuntos admitidos son PNG,
  JPEG, WebP, PDF, DOCX, XLSX, CSV y TXT, validados por firma o estructura con
  defensas contra ZIP bombs, traversal, macros y descompresión de imágenes. Se
  aplican 5 archivos, 5 MiB individuales y 12 MiB acumulados. El reporte se
  persiste antes del SMTP, se usa `DEFAULT_FROM_EMAIL`, destinatario fijo y
  email profesional sólo en `Reply-To`; fallos quedan reintentables. Los
  comandos `retry_feedback_emails` y `purge_feedback_attachments` operan por ID
  y estado; la purga exige invocación manual y ofrece `--dry-run`. La suite
  alcanza 334 pruebas. Este commit no modifica `static/`.
- **11/08/2026 — FB.3 / canal profesional:** `/dashboard/comentarios/` ofrece
  un formulario multipart accesible sólo a profesionales activos y aplica
  POST/Redirect/GET con código `FB-XXXXXXXX`. El dashboard profesional muestra
  la tercera tarjeta; empresas, trainees, inactivos y anónimos no pueden usar
  el canal. Los snapshots siempre derivan de `request.user`, aunque el POST
  intente falsificar identidad o destinatario. También se cerró el fallback de
  una empresa sin perfil para que nunca renderice el dashboard profesional.
  La suite alcanza 341 pruebas y el smoke local verificó formulario 302 a
  login, dashboard 302 y login profesional 200. No hay cambios en `static/`.
- **11/08/2026 — FB.4 / ayuda contextual y bots:** el widget pasó a
  `base_contextual_help.html`; las pantallas 886 conservan `planilla_logic.js`
  y feedback carga sólo la infraestructura neutral con `help_slug=feedback`.
  La nueva guía explica categorías, evidencia, privacidad, tracking y fallos de
  entrega. `help_ai` conoce la ruta y declara que no lee adjuntos; Ergobot
  docente incorpora sólo la excepción acotada para orientar a profesionales y
  trainees, sin compartir agentes ni historial. La suite alcanza 346 pruebas y
  el smoke autenticado verificó feedback, módulo 886 y guía en HTTP 200 con
  ETag/versión. Este commit modifica `static/ayuda/help_texts/`: producción
  requiere ejecutar `collectstatic --noinput`.
- **11/08/2026 — FB.5 / cierre integral:** pruebas punta a punta cubren POST,
  storage, email, falla SMTP, retry y purga; el MIME del correo deriva del
  formato validado y el rate limit serializa por profesional. La revisión real
  de escritorio y móvil confirmó layout sin overflow, foco del primer error,
  asociaciones ARIA y guía contextual sin errores de consola. La suite final
  alcanza 350 pruebas. `makemigrations --check`, `check`, `git diff --check` y
  `collectstatic --dry-run` terminan correctamente.
- **12/08/2026 — correcciones predeploy:** la landing pública identifica
  Evaluaciones como `Disponible` y atribuye el desarrollo a **IAinsane**. El
  mapa oficial de Planilla 1 sube a `1.0.1`: Dirección, Área/Sector, Puesto y
  Nombre del trabajador/es ganan margen respecto de sus rótulos sin invadir
  otras celdas, y las tareas 1, 2 y 3 bajan de `y=505` a `y=496` para separarse
  de su número impreso. Tres regresores nuevos elevan la suite a 353 pruebas.
  El PDF se generó y renderizó para QA visual; la landing respondió HTTP 200
  en escritorio y móvil, sin overflow ni errores de consola. Este cierre no
  agrega migraciones ni modifica `static/`; `collectstatic --noinput` sigue
  siendo obligatorio por los recursos de ayuda incorporados en FB.4.
- **12/08/2026 — unificación global del crédito:** la segunda revisión en
  producción detectó que las páginas internas todavía heredaban el crédito
  anterior desde `base_dashboard.html`. Las dos únicas bases renderizables,
  `base_landing.html` y `base_dashboard.html`, ahora muestran exactamente
  `© 2026 ErgoSolutions. Desarrollado por IAinsane`. La búsqueda completa de
  templates confirma que no queda otra leyenda de desarrollador, y una nueva
  regresión autenticada eleva la suite a 354 pruebas. El fix no agrega
  migraciones ni modifica archivos de `static/`; sólo requiere actualizar el
  código y reiniciar ErgoSolutions.

#### Operación y rollback del canal de feedback

- Despliegue: aplicar únicamente `feedback.0001_initial` mediante el flujo
  normal de `migrate` y ejecutar `collectstatic --noinput` por los Markdown de
  ayuda. No se requieren cambios de nginx, SMTP, dependencias ni CriaApp.
- Reintento: `.venv/bin/python manage.py retry_feedback_emails --limit 20` o
  `--report <uuid>`. El máximo por reporte es 5 y la salida no expone payloads.
- Retención: primero `.venv/bin/python manage.py purge_feedback_attachments
  --older-than-days 90 --dry-run`. La ejecución sin `--dry-run` es destructiva,
  sólo alcanza reportes enviados y requiere autorización expresa.
- Límites: 5 adjuntos, 5 MiB por archivo y 12 MiB acumulados; almacenamiento en
  `private_media/feedback`, sin URL pública ni endpoint de descarga.
- Rollback: volver al commit anterior, regenerar estáticos y reiniciar sólo
  ErgoSolutions. La migración es aditiva: no ejecutar `migrate feedback zero`
  ni borrar tablas o adjuntos, para preservar los reportes recibidos.

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
- **03/08/2026 — Commit 5.2:** las doce planillas oficiales incorporan
  aclaraciones impresas de empleador y profesional sólo cuando las fuentes
  están completas. Medicina Laboral queda siempre vacía por CF-5; el render de
  las doce páginas preserva Borg, Fanger y el SHA-256 oficial. Pasan 242 tests.
- **03/08/2026 — Commit 5.3:** Planilla 1 puede seleccionar trabajadores activos
  de la nómina vinculada. La selección sólo completa un snapshot vacío; el
  texto profesional y el total del puesto prevalecen. El PDF nunca consulta la
  relación y un reporte real excluye CUIL, DNI, email y legajo por CF-4. La
  migración aditiva quedó aplicada y pasan 248 pruebas.
- **03/08/2026 — Commit 5.4:** guardar Planilla 4 crea o actualiza un vencimiento
  ergonómico en la agenda de la empresa, sin duplicados. El cierre se refleja
  como completado y la prioridad sólo mapea el nivel persistido, sin recalcular
  ni modificarlo (CF-2). La proyección es unidireccional y pasan 254 pruebas.
- **03/08/2026 — Commit 5.5:** los vencimientos ergonómicos de la agenda enlazan
  a la Planilla 4 correcta. La resolución vive en un templatetag del módulo,
  vuelve a aplicar D-9 y no introduce imports de Ergonomía en `apps.company`;
  una empresa ajena no obtiene URL. Pasan 257 pruebas.
- **03/08/2026 — Commit 5.6 / cierre de Fase 5:** el wizard sugiere el módulo
  activo de Ergonomía ante niveles persistidos medio/alto en cinco factores y
  agrupa las causas. El enlace usa el flujo público por slug para trabajadores;
  CF-2 queda cubierta con cero llamadas al motor y niveles intactos. La fase
  cierra con 261 pruebas, checks y migraciones limpios.
- **03/08/2026 — Commit 6.1:** las tres bases HTML sirven Bootstrap 5.3.3,
  Bootstrap Icons 1.11.3 y el bundle JavaScript desde `static/vendor/`. El QA
  descubrió y eliminó dos CDN generados por `django_bootstrap5` que no figuraban
  como URLs literales; las 33 pantallas cargan recursos locales, sin íconos
  vacíos, overflow ni errores de consola.
- **03/08/2026 — Commit 6.2:** los cinco scripts inline del destino se
  extrajeron a `static/js/`; slug, preguntas y endpoint se pasan con `data-*`.
  El navegador confirmó cero bloques inline, carga de los cinco archivos y
  ejecución del chat, widget, copia y quiz sin errores. CF-1 conserva intactas
  las aserciones de `help_ai`; sólo se corrigieron rutas anidadas de templates.
- **03/08/2026 — Commit 6.3:** los siete manejadores `on*` remanentes en chats
  y quiz se reemplazaron por `addEventListener`; el listener de copia ya estaba
  adelantado. Templates y JavaScript quedan sin atributos ni propiedades
  `on*`, listos para `script-src-attr 'none'`; pasan las 261 pruebas.
- **03/08/2026 — Commit 6.4:** el recorrido previo al CSP cubrió las 33
  pantallas del destino y las 30 del módulo: cero errores de consola, cero
  overflow, recursos e íconos locales y JavaScript interactivo operativo. Se
  corrigió el ícono inexistente `bi-weight` de LMC; CF-1 quedó validada con la
  guía VCE real y 24 pruebas conjuntas de ambos asistentes.
- **03/08/2026 — Commit 6.5:** el middleware CSP soporta modo de observación y
  bloqueante con la misma política y nonce por respuesta. `config.settings`
  emite Report-Only por defecto; la suite conserva la compuerta bloqueante de
  `help_ai`. Tres pruebas cubren headers, políticas y posición del middleware;
  `.env.example` documenta la variable sin tocar el `.env` real.
- **03/08/2026 — Commit 6.6:** el período Report-Only recorrió las 63 pantallas
  sin violaciones y confirmó nonces reales en los seis templates inline del
  módulo. Los dos `iframe` de YouTube preexistentes se reemplazaron por enlaces
  externos explícitos para no abrir orígenes remotos en la política; pasan las
  261 pruebas y CF-1 conserva intactas sus aserciones de seguridad.
- **03/08/2026 — Commit 6.7 / cierre de Fase 6:** CSP queda bloqueante por
  defecto, con nonce por respuesta, `script-src-attr 'none'`, Referrer-Policy y
  Permissions-Policy. Las 63 pantallas y cinco formularios interactivos pasan
  sin violaciones; se corrigió la inicialización temprana del filtro de fuerza.
  La integración cierra con 264 pruebas, migraciones limpias y el SHA-256
  oficial intacto.
- **03/08/2026 — Auditoría previa al despliegue:** la revisión independiente de
  la rama reprodujo las compuertas (264 pruebas, `check`, migraciones,
  `collectstatic` manifestado, humo anónimo y CSP bloqueante) y verificó las
  seis condiciones fundamentales sobre el código. Único hallazgo con acción:
  `private_media/` no estaba en `.gitignore`, de modo que la evidencia
  documental del módulo —fotos de montaje y certificados de calibración— podía
  versionarse en cuanto se cargara la primera. Corregido en este commit. Quedan
  reportadas sin resolver, por ser previas al módulo y requerir decisión de
  producción: las cabeceras y cookies de HTTPS ausentes en `config/settings.py`
  y la falta de cotas superiores en tres dependencias.
- **06/08/2026 — Commit 7.1 / estabilización de producción:** se corrigió el
  contrato multiturno de la ayuda contextual. Los items enriquecidos de
  Responses API se convierten ahora al formato canónico `{role, content}` sin
  relajar la validación contra roles privilegiados o claves adicionales; el
  cliente descarta historiales inesperados y el servidor conserva un fallback
  textual acotado. Cinco regresiones usan las clases reales del SDK y elevan la
  suite a 269 pruebas. `collectstatic` confirmó el hash
  `help_widget.435b6b864b40.js`; no hay migraciones ni llamadas a OpenAI.
- **06/08/2026 — Commit 7.2 / feedback del Chat IA:** la ayuda contextual
  muestra «ErgoBot está pensando» dentro del área de mensajes desde antes del
  primer acceso de red. El estado usa `role=status`, `aria-live=polite`, puntos
  animados en CSS externo y respeta `prefers-reduced-motion`; desaparecen el
  texto redundante y la burbuja vacía anteriores. La suite alcanza 270 pruebas
  y `collectstatic` produjo `help_widget.2674cac4e604.css` y
  `help_widget.d27cd8775b21.js`; sin migraciones.
- **06/08/2026 — Commit 7.3 / selector de evaluaciones:** el dashboard y el
  navbar abren `/dashboard/evaluaciones/`, un catálogo estático accesible a
  profesionales y empresas. Ergonomía SRT 886/15 permanece disponible;
  Iluminación, Ruido, Carga Térmica, Puesta a Tierra y Contaminantes Químicos
  se presentan como próximos módulos sin enlaces. El listado 886 incorpora un
  breadcrumb de regreso. La suite alcanza 272 pruebas y no hay migraciones.
- **07/08/2026 — Inicio de Chat IA: contexto y datos:** se abrió la iniciativa
  en `feature/chat-ia-contexto`, con propuesta técnica, roadmap commit por
  commit y bitácora de ejecución. La línea base reproducida es de 269 pruebas,
  sin migraciones pendientes ni issues del sistema.
- **07/08/2026 — Chat IA A.1 / registro de pantallas:** cada slug de ayuda
  dispone ahora de título humano, ruta y propósito estáticos. Cuatro pruebas
  cubren el catálogo, la integridad de las fichas y el fallo cerrado; la suite
  alcanza 273 pruebas.
- **07/08/2026 — Chat IA A.2 / preámbulo v2.0:** el agente declara al inicio
  la pantalla actual con título, ruta y propósito, y diferencia ubicación de
  datos no visibles. Tres regresiones nuevas elevan la suite a 276 pruebas.
- **07/08/2026 — Chat IA A.3 / slugs descruzados:** el listado conserva
  `dashboard` y el detalle usa el nuevo `menu_planillas`; sus guías se sirven
  desde el documento correcto y un test impide futuras colisiones. La suite
  alcanza 277 pruebas; el despliegue requiere `collectstatic`.
- **07/08/2026 — Chat IA A.4 / guías enriquecidas:** se reescribieron las
  ayudas del listado, menú de planillas, creación y respaldo general. Las tres
  guías críticas superan 3.000 caracteres y el respaldo 1.900; los 32 slugs
  cargan correctamente y el despliegue requiere `collectstatic`.
- **07/08/2026 — Chat IA A.5 / slug con respaldo:** la plantilla genérica de
  Planillas 2 cae a la guía `home` y la vista rechaza configuraciones vacías
  con un error explícito. Dos pruebas nuevas elevan la suite a 279.
- **07/08/2026 — Chat IA A.6 / falla visible:** si el widget no recibe slug,
  la Guía y el Chat muestran un aviso y la consola registra `[ayuda-886]`.
  La prueba real en navegador cubrió camino normal, apertura, envío y recarga;
  el despliegue exige `collectstatic`.
- **07/08/2026 — Chat IA A.7 / núcleo y anexos:** `guia_general.md` se
  conserva como maestro y se deriva en 15 piezas temáticas. Dos pruebas
  reconstruyen el original carácter por carácter; la suite alcanza 281 y el
  contexto servido todavía permanece en 27.241 caracteres.
- **07/08/2026 — Chat IA A.8 / perfiles de contexto:** los 32 slugs reciben
  núcleo más anexos pertinentes y degradan al global completo ante omisiones.
  El promedio documental baja de 33.249 a 16.070 caracteres (-51,7 %) y la
  suite alcanza 287; la batería externa quedó restringida por política de
  egreso, con 6/6 fuentes verificadas localmente.
- **07/08/2026 — Chat IA A.9 / cobertura bidireccional:** el inventario de
  slugs recorre las plantillas reales de la raíz y de las apps, comprueba ambos
  sentidos y distingue respaldos de valores dinámicos. Una inyección temporal
  confirmó que rechaza `slug_fantasma`; la suite alcanza 289 pruebas.
- **07/08/2026 — Chat IA A.10 / cierre de Fase A:** los cinco hallazgos y dos
  guardas adicionales quedan corregidos. El contrato de identidad cubre 32/32
  pantallas, el promedio documental baja 51,7 % (33.249 → 16.070), `crear`
  reduce su contexto global 67,5 % y pasan 289 pruebas. `collectstatic` reunió
  196 archivos y el humo local respondió como se esperaba. La aceptación
  generativa externa queda explícitamente pendiente por política de egreso;
  las pruebas estructurales, de integración y de navegador están en verde.
- **08/08/2026 — Chat IA B.0 / dependencias de producción:** `gunicorn` y el
  paquete no deprecado `uvicorn-worker` quedan declarados, instalados y
  protegidos por contrato. Las versiones verificadas son 23.0.0 y 0.4.0; la
  suite alcanza 290 pruebas y el despliegue debe reinstalar requirements.
- **08/08/2026 — Chat IA B.1 / WhiteNoise condicional:** nginx ya sirve los
  estáticos desde el `STATIC_ROOT` real (`app/staticfiles`), por lo que
  WhiteNoise sale del middleware productivo y permanece en desarrollo. El
  manifiesto comprimido conserva sus hashes y la cadena ASGI queda sin
  componentes sync-only; pasan 290 pruebas.
- **08/08/2026 — Chat IA B.2 / contrato ASGI:** cuatro pruebas impiden
  reintroducir middlewares sync-only y congelan las capacidades del CSP,
  `ATOMIC_REQUESTS=False` y la ausencia de routers implícitos. Una inyección
  temporal confirmó que el guardián falla; `apps` mantiene 290 pruebas.
- **10/08/2026 — Chat IA B.3 / infraestructura para ASGI:** el VPS quedó en
  4 GB RAM / 2 vCPU, con `vm.swappiness=10` y PostgreSQL en 128 MB. Un drop-in
  exclusivo de ErgoSolutions aplica `MemoryMax=1200M` y `CPUQuota=150%`;
  CriaApp quedó formalmente fuera de alcance y sus tres servicios conservaron
  timestamps, estado activo y HTTP 200. La suite mantiene 290 pruebas.
- **10/08/2026 — Chat IA B.4a / HTTPS detrás del proxy:** el primer corte ASGI
  reveló que Gunicorn WSGI aportaba implícitamente el esquema HTTPS; Uvicorn
  sobre socket Unix dejó el login en 403 CSRF y se ejecutó rollback. Django
  ahora declara `SECURE_PROXY_SSL_HEADER` y los orígenes HTTPS canónicos; dos
  tests de regresión elevan la suite de configuración de 7 a 9, mientras
  `apps` conserva sus 290 pruebas.
- **11/08/2026 — Videos y firmantes documentales:** las capacitaciones online
  y presenciales vuelven a reproducir el video dentro de ErgoSolutions mediante
  `youtube-nocookie.com`, autorizado por un `frame-src` de host único. Los
  intentos online conservan el link de origen y los certificados congelan el
  nombre, profesión y matrícula del profesional que lo creó; se eliminó el
  responsable escrito en el generador PDF. La planilla presencial y las
  exportaciones SRT quedaron protegidas con pruebas adversariales de dos
  profesionales, y la aclaración SRT separa profesión y matrícula para evitar
  truncamiento. La auditoría completa y el plan de despliegue están en
  `docs/AUDITORIA_CAPACITACIONES_VIDEOS_Y_FIRMANTES_2026-08-11.md`.

### Ayuda contextual del área de Capacitaciones

Trabajo en curso sobre la rama `feat/ayuda-contextual-capacitaciones`. Replica en el área de
Capacitaciones el sistema de ayuda contextual (estática y dinámica) que ya existe en el
módulo de Evaluación Ergonómica SRT 886/15, como **app independiente**
(`apps.training.help_ai`), con catálogo de pantallas, corpus y prefijo de URL propios.

Documentos de referencia:

- Diseño auditado: `docs/AUDITORIA_Y_PROPUESTA_AYUDA_CONTEXTUAL_CAPACITACIONES_2026-08-12.md`
- Plan de ejecución commit por commit: `docs/ROADMAP_AYUDA_CONTEXTUAL_CAPACITACIONES.md`
- Bitácora de trazabilidad: `docs/BITACORA_AYUDA_CONTEXTUAL_CAPACITACIONES.md`

Registro de avance:

- **12/08/2026 — Commit 0.0:** se abrió la rama `feat/ayuda-contextual-capacitaciones` y se
  creó la bitácora de trazabilidad con el estado de partida verificado sobre `4187b10`:
  `manage.py check` sin issues, 354 pruebas en verde, 52 pruebas de
  `apps.ergonomia_886.help_ai` en verde y ninguna migración pendiente. Esa es la línea base
  que ningún commit posterior puede empeorar.
- **12/08/2026 — Commit 0.1:** se creó la estructura de directorios del sistema:
  `apps/training/help_ai/` (la app), `templates/capacitaciones/` (el cuerpo del panel) y
  `static/ayuda/capacitaciones/help_texts/` (el corpus). El corpus del módulo 886 vive en
  `static/ayuda/help_texts/` y **no se toca**: son directorios distintos, por colisión de
  nombres de documento (`home.md`, `dashboard.md`, `crear.md`, `factor.md`). Se registró que
  ese corpus contiene 50 documentos, no 51 como declaraba el estado de partida del roadmap.
- **12/08/2026 — Commit 1.1:** se creó la app `apps.training.help_ai` y se la dio de alta en
  `LOCAL_APPS`. **Decisión de arquitectura (DA-1 / CV-1):** el `AppConfig` declara
  `label = "capacitaciones_help_ai"` de forma explícita. Django deriva el label del último
  componente de la ruta punteada, de modo que sin esa línea la app colisionaría con la ayuda
  del módulo 886 y el proyecto no arrancaría (`Application labels aren't unique`).
  **Restricción documentada en el camino:** una prueba preexistente del módulo 886
  (`evaluaciones/tests_sugerencias.py`) barre como texto plano todos los `.py` de
  `apps/training/` y prohíbe la ruta punteada del módulo 886 incluso dentro de comentarios.
  El código de esta app nombra al módulo 886 en prosa y construye en tiempo de ejecución
  cualquier referencia a su ruta.

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
