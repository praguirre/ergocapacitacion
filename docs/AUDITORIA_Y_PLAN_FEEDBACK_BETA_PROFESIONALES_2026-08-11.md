# Auditoría de viabilidad y plan de implementación — Canal de feedback para la beta profesional

**Proyecto:** ErgoSolutions / `ergocapacitacion`  
**Fecha de auditoría:** 11 de agosto de 2026  
**Estado del documento:** propuesta ejecutable; **no implementada**  
**Punto de partida auditado:** rama `codex/capacitaciones-firmas`, commit `f9ea7a0`  
**Destinatarios:** Pablo R. Aguirre, asistente IA de desarrollo y asistente IA de producción  

---

## 1. Resumen ejecutivo

La mejora es **técnicamente viable** con la arquitectura actual y no requiere
servicios externos nuevos, cambios de nginx, cambios de PostgreSQL ni tocar la
segunda aplicación del VPS (CriaApp).

La implementación recomendada agrega:

1. una tercera tarjeta, visible solamente para profesionales, en
   `/dashboard/`;
2. un formulario autenticado en `/dashboard/comentarios/`;
3. categorías de reporte, asunto, descripción, pasos para reproducir, resultado
   esperado, pantalla afectada y hasta cinco adjuntos;
4. un registro durable en PostgreSQL para que un fallo de SMTP no haga perder
   el reporte;
5. almacenamiento privado de adjuntos, sin URL pública y fuera de `/media/`;
6. envío inmediato a `consultaergosolutions@gmail.com`, usando la configuración
   SMTP ya existente;
7. trazabilidad del estado de entrega y reintento manual de correos fallidos;
8. una nueva guía y slug `feedback` para la Ayuda Contextual;
9. una instrucción general para que el Chat IA de la Resolución SRT 886/15 sepa
   guiar al usuario desde cualquiera de sus pantallas;
10. una excepción acotada en el asistente docente de capacitaciones para que no
    rechace una consulta sobre cómo informar un error de la plataforma.

### Dictamen

**APTO para implementar**, sujeto a las fronteras de seguridad y criterios de
aceptación de este documento.

### Estimación de alcance

La mejora es de alcance **medio**. No es sólo una tarjeta y un `send_mail`: los
adjuntos introducen riesgos de exposición, tamaño, archivos engañosos, pérdida
de información y bloqueo del SMTP. El plan los resuelve sin incorporar Celery,
Redis, S3 ni antivirus de servidor en esta primera beta.

### Resultado esperado para el profesional

El recorrido final será:

```text
Dashboard
  → tarjeta “Comentarios de la beta”
  → formulario protegido
  → adjuntar capturas/documentos opcionales
  → enviar
  → confirmación con código de seguimiento
  → email recibido en consultaergosolutions@gmail.com
```

---

## 2. Solicitud funcional interpretada

### 2.1. Requisitos expresos

| ID | Requisito | Interpretación verificable |
|---|---|---|
| RF-1 | Nueva tarjeta en el dashboard | La tarjeta aparece en el dashboard profesional y conduce al formulario |
| RF-2 | Enviar comentarios o errores | El formulario permite diferenciar error, mejora, consulta y otro |
| RF-3 | Adjuntar imágenes o archivos | Hasta cinco archivos, con validaciones de extensión, contenido y tamaño |
| RF-4 | Envío al correo de la aplicación | El único destinatario funcional es `consultaergosolutions@gmail.com` |
| RF-5 | El bot debe saber guiar | La ayuda general conoce el canal y el slug `feedback` explica el formulario |
| RF-6 | Preparado para beta real | Debe tolerar fallos de SMTP, limitar abuso y preservar evidencia útil |

### 2.2. Supuestos adoptados para evitar decisiones abiertas durante la ejecución

Estas decisiones forman parte del diseño recomendado y se deberán registrar en
el `README.md` como **Decisiones de Arquitectura de la beta** antes de escribir
el código funcional:

| ID | Decisión |
|---|---|
| DA-FB-1 | El canal estará disponible sólo para usuarios activos de tipo `professional`, no para trainees ni empresas |
| DA-FB-2 | Los reportes se guardarán en PostgreSQL antes de intentar el correo |
| DA-FB-3 | Los adjuntos se almacenarán fuera de `MEDIA_ROOT` y no tendrán URL pública |
| DA-FB-4 | El correo será inmediato y síncrono durante la beta; no se agregará Celery/Redis a ErgoSolutions |
| DA-FB-5 | Un fallo SMTP no borra el reporte: queda con estado `email_failed` y se puede reintentar |
| DA-FB-6 | Se aceptarán PNG, JPEG, WebP, PDF, DOCX, XLSX, CSV y TXT; se rechazan SVG, HTML, ejecutables, scripts, macros y archivos comprimidos genéricos |
| DA-FB-7 | Máximo 5 adjuntos, 5 MiB por archivo y 12 MiB acumulados |
| DA-FB-8 | Los adjuntos privados se conservarán 90 días y sólo se purgarán si el correo fue enviado correctamente |
| DA-FB-9 | No habrá descarga pública ni vista autenticada de adjuntos en esta versión; el destinatario los recibe por email |
| DA-FB-10 | Se conserva la separación CF-1 entre `help_ai` y `ergobot_ai`; sólo se agrega documentación coherente en ambos contextos |

### 2.3. Fuera de alcance de esta primera versión

- tablero público de incidencias;
- conversación o respuestas dentro de la aplicación;
- notificaciones al profesional cuando el reporte se cierre;
- integración con GitHub Issues, Jira, Trello o servicios externos;
- antivirus ClamAV en el VPS;
- subida directa a S3 u otro object storage;
- captura automática de pantalla;
- lectura de adjuntos por el modelo de IA;
- acceso de empresas o trainees al formulario;
- cambios en CriaApp;
- modificación del SMTP o de credenciales reales durante desarrollo.

---

## 3. Evidencia auditada en el código actual

### 3.1. Dashboard y autorización

| Componente | Evidencia actual | Consecuencia |
|---|---|---|
| `apps/dashboard/views.py` | `home()` despacha entre dashboard profesional y de empresa | La tarjeta puede agregarse sólo a `templates/dashboard/home.html` sin afectar empresas |
| `_professional_dashboard()` | Ya calcula estadísticas acotadas a `request.user` | El nuevo canal puede conservar el mismo límite por usuario |
| `apps/accounts/decorators.py` | Existe `professional_required` | Es el decorador correcto; `backoffice_required` sería demasiado amplio porque admite empresas |
| `apps/dashboard/urls.py` | Todo cuelga de `/dashboard/` | Se puede incluir `apps.feedback.urls` bajo `/dashboard/comentarios/` |
| `templates/dashboard/home.html` | Dos tarjetas activas en un grid Bootstrap | La tercera tarjeta requiere ajustar columnas, no una nueva dependencia visual |

### 3.2. Correo

`config/settings.py` ya define:

- `EMAIL_BACKEND`;
- `EMAIL_HOST` y `EMAIL_PORT`;
- TLS/SSL;
- `EMAIL_HOST_USER` y `EMAIL_HOST_PASSWORD`;
- `DEFAULT_FROM_EMAIL`;
- `ADMIN_EMAIL`;
- validación de credenciales SMTP cuando el backend es SMTP y `DEBUG=False`.

También existen envíos reales con `EmailMessage` y archivos adjuntos en
`apps/certificates/emailer.py`. Por lo tanto:

- no hace falta instalar una biblioteca de correo;
- no hace falta agregar un segundo proveedor;
- el remitente debe continuar siendo `DEFAULT_FROM_EMAIL`;
- el correo del profesional debe ir en `Reply-To`, no en `From`, para no
  quebrar SPF/DMARC del Gmail configurado;
- se debe usar `fail_silently=False` para conocer el resultado real.

### 3.3. Archivos y almacenamiento

El servidor sirve públicamente `/media/` mediante nginx desde
`/srv/ergocapacitacion/app/media/`. Guardar ahí capturas de errores sería una
exposición innecesaria.

El módulo SRT 886/15 ya contiene un patrón correcto en
`apps/ergonomia_886/evaluaciones/storage.py`:

- `FileSystemStorage` con ubicación privada;
- `base_url=None`;
- `url()` falla deliberadamente;
- los archivos quedan fuera de `MEDIA_ROOT`.

Ese patrón puede replicarse para feedback, sin acoplar las dos aplicaciones.

### 3.4. Límites de infraestructura

La configuración de producción relevada durante la Fase B declara
`client_max_body_size 25M` en nginx. Para no rozar ese límite ni el máximo de
Gmail después de la codificación MIME/base64, el formulario aplicará:

- 5 MiB máximos por archivo;
- 12 MiB binarios máximos acumulados;
- 5 archivos como máximo.

Doce MiB binarios producen aproximadamente dieciséis MiB codificados, con
margen para cabeceras y cuerpo del mensaje por debajo del límite usual de
Gmail. La aplicación debe rechazar el exceso antes de intentar guardar o
enviar.

### 3.5. Ayuda contextual y los dos asistentes

El proyecto tiene dos asistentes separados por diseño:

1. `apps.ergonomia_886.help_ai`: ayuda contextual del protocolo SRT 886/15,
   con catálogo de slugs, guía Markdown y contexto general por pantalla.
2. `apps.ergobot_ai`: asistente docente de las capacitaciones, construido con
   `prompts/system_base.md` más el contenido del módulo.

La condición CF-1 prohíbe fusionarlos. La solución correcta es:

- registrar el slug `feedback` sólo en `help_ai`;
- agregar la instrucción transversal al documento general de `help_ai`;
- incorporar una excepción mínima en `ergobot_ai/prompts/system_base.md` para
  explicar dónde informa errores una cuenta profesional;
- no compartir clases, agentes, historial, tools ni datos entre asistentes.

### 3.6. Base de plantilla del widget

El widget de ayuda vive hoy en `templates/ergonomia_886/base_886.html`, que a
su vez extiende `base_dashboard.html`. Usar directamente `base_886.html` para
el formulario de feedback funcionaría, pero cargaría JavaScript específico de
planillas y mantendría una dependencia conceptual incorrecta.

Se recomienda extraer la infraestructura común a una base neutral:

```text
base_dashboard.html
  └── base_contextual_help.html
        ├── ergonomia_886/base_886.html
        └── feedback/create.html
```

Esta extracción debe conservar los bloques en la cadena de `{% extends %}`.
El `help_slug` **no puede trasladarse a un `{% include %}`**, porque los bloques
de Django no atraviesan includes y todas las pantallas terminarían usando el
slug de respaldo en silencio.

---

## 4. Riesgos técnicos y mitigaciones

| ID | Riesgo | Severidad | Mitigación obligatoria |
|---|---|---:|---|
| RT-1 | Archivo expuesto públicamente | Alta | Storage privado fuera de `MEDIA_ROOT`, sin URL y sin endpoint de descarga |
| RT-2 | Ejecutable renombrado como `.pdf` o `.jpg` | Alta | Validar extensión y firma/contenido; el `content_type` del navegador no es prueba |
| RT-3 | Email mayor que el límite de Gmail | Alta | 5 archivos, 5 MiB individual, 12 MiB total |
| RT-4 | SMTP falla y se pierde el comentario | Alta | Persistir reporte y adjuntos primero; estado de entrega y comando de reintento |
| RT-5 | El formulario se convierte en spam SMTP | Media | Sólo profesionales autenticados y límite de 5 reportes por hora por usuario |
| RT-6 | Datos personales en logs | Alta | Loguear únicamente UUID, user ID, estado, cantidad y bytes; nunca comentario ni nombres de archivo |
| RT-7 | Dirección de correo manipulada | Media | Destinatario desde settings, no desde POST; `Reply-To` desde el usuario autenticado |
| RT-8 | Path traversal por nombre de archivo | Alta | Nunca usar el nombre original como ruta; generar nombre UUID y guardar el original sólo como metadato saneado |
| RT-9 | Carga consume RAM del worker ASGI | Media | Django deriva archivos grandes a temporales; límites tempranos y procesamiento por chunks |
| RT-10 | Doble envío por recarga | Baja | Patrón POST/Redirect/GET, botón con texto claro y rate limit |
| RT-11 | Refactor del widget rompe los slugs existentes | Alta | Mantener `help_slug` como block heredable y ejecutar el barrido bidireccional existente |
| RT-12 | El bot docente rechaza la consulta por estar fuera de ergonomía | Media | Excepción literal y acotada en su prompt base |
| RT-13 | Adjuntos privados crecen indefinidamente | Media | Retención de 90 días y comando de purga sólo para reportes enviados |
| RT-14 | Archivo malicioso permitido pese a validaciones | Residual | No ejecutar ni renderizar en servidor; adjuntar como binario; Gmail agrega su análisis; ClamAV queda como mejora futura |
| RT-15 | El SMTP bloquea el request durante una caída | Media | Conexión con timeout específico de 20 segundos; estado fallido durable |
| RT-16 | Imagen o ZIP pequeño se expande de forma desproporcionada | Alta | Límite de píxeles para imágenes y límite de miembros/tamaño descomprimido para Office |

### Riesgo residual aceptado para la beta

Sin un antivirus dedicado no existe una garantía absoluta sobre documentos
Office o PDF. Para esta beta el riesgo se reduce mediante autenticación,
lista blanca, verificación estructural, límites, almacenamiento privado y
ausencia de ejecución/renderizado. Si el canal se abre a usuarios masivos, se
deberá reevaluar ClamAV o almacenamiento con análisis antimalware.

---

## 5. Diseño funcional definitivo

### 5.1. Tarjeta del dashboard

Texto recomendado:

- **Título:** `Comentarios de la beta`
- **Descripción:** `¿Encontraste un error o tenés una propuesta? Enviá el
  detalle y adjuntá capturas o documentos para ayudarnos a mejorar.`
- **Insignia:** `Enviar comentario`
- **Ícono:** `bi-chat-square-text`
- **Color:** warning o info, distinguible de Evaluaciones y Capacitaciones.

Al agregar la tercera tarjeta, cambiar las tres columnas a
`col-md-6 col-xl-4`. No mostrarla en `home_company.html`.

### 5.2. Formulario

Campos visibles:

| Campo | Tipo | Requerido | Límite |
|---|---|:---:|---:|
| Categoría | select | Sí | error / mejora / consulta / otro |
| Asunto | texto | Sí | 160 caracteres |
| Pantalla o sección afectada | texto | No | 300 caracteres |
| Descripción | textarea | Sí | 5.000 caracteres |
| Pasos para reproducir | textarea | No | 5.000 caracteres |
| Resultado esperado | textarea | No | 3.000 caracteres |
| Adjuntos | file multiple | No | 5 archivos / 12 MiB total |
| Confirmación de privacidad | checkbox | Sí | Acepta no incluir datos personales innecesarios |

El formulario debe mostrar:

- extensiones admitidas;
- límites individuales y acumulados;
- aviso de no adjuntar DNI, CUIL, historia clínica u otros datos de trabajadores
  salvo que sean imprescindibles y estén debidamente anonimizados;
- aclaración de que el reporte incluirá nombre, email profesional y datos
  técnicos del navegador para poder responder y reproducir el problema.

### 5.3. Datos capturados automáticamente

No se piden de nuevo en el formulario. Se toman de `request.user` y del request:

- ID del usuario;
- nombre visible;
- email;
- profesión;
- matrícula;
- `HTTP_USER_AGENT`, truncado a 500 caracteres;
- fecha y hora con zona del proyecto;
- UUID público del reporte.

No almacenar la contraseña, cookies, token CSRF, contenido de sesión ni IP en
texto plano. La IP no es necesaria para este caso autenticado y queda fuera.

### 5.4. Confirmación

Después de un envío exitoso:

```text
Recibimos tu comentario. Código: FB-<8 caracteres del UUID>.
Gracias por ayudarnos a mejorar la beta de ErgoSolutions.
```

Si el registro se guardó pero el SMTP falló:

```text
Tu comentario quedó guardado con el código FB-XXXXXXXX, pero el correo no pudo
enviarse en este momento. No hace falta que lo cargues de nuevo; el equipo puede
reintentar el envío.
```

Nunca mostrar el texto técnico de la excepción SMTP al profesional.

---

## 6. Modelo de datos propuesto

Crear una app independiente `apps.feedback`. No reutilizar `ContactRequest`:
esa entidad representa solicitudes empresa → profesional, tiene otro ciclo de
vida y otra autorización.

### 6.1. `FeedbackReport`

| Campo | Tipo sugerido | Regla |
|---|---|---|
| `id` | `UUIDField(primary_key=True, default=uuid.uuid4)` | Código no secuencial |
| `professional` | FK a user, `SET_NULL`, nullable | Sólo professional al crear; SET_NULL preserva auditoría |
| `reporter_name` | `CharField(200)` | Snapshot |
| `reporter_email` | `EmailField()` | Snapshot y Reply-To |
| `reporter_profession` | `CharField(100, blank=True)` | Snapshot |
| `reporter_license_number` | `CharField(50, blank=True)` | Snapshot |
| `category` | `CharField` con choices | `bug`, `improvement`, `question`, `other` |
| `subject` | `CharField(160)` | Sin saltos de línea |
| `affected_screen` | `CharField(300, blank=True)` | Texto o ruta informada |
| `description` | `TextField` | Máximo validado por form |
| `reproduction_steps` | `TextField(blank=True)` | Opcional |
| `expected_result` | `TextField(blank=True)` | Opcional |
| `user_agent` | `CharField(500, blank=True)` | Snapshot técnico |
| `email_status` | choices | `pending`, `sent`, `failed` |
| `email_attempts` | `PositiveSmallIntegerField(default=0)` | Trazabilidad |
| `email_error_code` | `CharField(120, blank=True)` | Clase/código, nunca payload completo |
| `last_email_attempt_at` | `DateTimeField(null=True)` | Trazabilidad |
| `emailed_at` | `DateTimeField(null=True)` | Confirmación |
| `created_at` | `DateTimeField(auto_now_add=True)` | Orden |
| `updated_at` | `DateTimeField(auto_now=True)` | Orden |

Índices:

- `professional, -created_at`;
- `email_status, created_at`;
- `category, -created_at`.

Propiedad:

```python
tracking_code = f"FB-{str(self.pk).split('-')[0].upper()}"
```

### 6.2. `FeedbackAttachment`

| Campo | Tipo sugerido | Regla |
|---|---|---|
| `id` | `UUIDField` | Identificador no predecible |
| `report` | FK CASCADE | El archivo no existe sin reporte |
| `file` | `FileField(storage=private_feedback_storage)` | Sin URL pública |
| `original_name` | `CharField(255)` | Sólo basename saneado |
| `content_type` | `CharField(120)` | Informativo, no criterio de confianza |
| `size_bytes` | `PositiveBigIntegerField` | Auditoría y correo |
| `sha256` | `CharField(64)` | Integridad y diagnóstico sin leer contenido |
| `created_at` | `DateTimeField(auto_now_add=True)` | Retención |

Restricciones:

- ordenar por `created_at`;
- no exponer `file.url`;
- evitar que `__str__` imprima el nombre del archivo en logs inesperados;
- el `upload_to` debe generar
  `feedback/<report_uuid>/<attachment_uuid>.<extensión_validada>`.

### 6.3. Migración

Una única migración inicial de la app. Debe contener sólo `CreateModel`,
índices y constraints. No requiere `RunPython`, backfill ni cambios de datos
existentes.

---

## 7. Contrato de validación de adjuntos

### 7.1. Límites

Constantes centralizadas en `apps/feedback/validators.py`:

```python
MAX_ATTACHMENTS = 5
MAX_ATTACHMENT_BYTES = 5 * 1024 * 1024
MAX_TOTAL_ATTACHMENT_BYTES = 12 * 1024 * 1024
```

No dispersar números mágicos entre form, template y servicio.

### 7.2. Formatos admitidos

| Extensión | Validación mínima de contenido |
|---|---|
| `.png` | firma PNG y `Pillow.Image.verify()` |
| `.jpg`, `.jpeg` | firma JPEG y `Pillow.Image.verify()` |
| `.webp` | contenedor RIFF/WEBP y `Pillow.Image.verify()` |
| `.pdf` | comienza con `%PDF-` y `pypdf.PdfReader` puede abrir estructura |
| `.docx` | ZIP válido con `[Content_Types].xml` y directorio `word/` |
| `.xlsx` | ZIP válido con `[Content_Types].xml` y directorio `xl/` |
| `.txt` | decodifica UTF-8, sin bytes NUL |
| `.csv` | decodifica UTF-8, sin bytes NUL |

Reglas adicionales:

1. Convertir la extensión a minúscula.
2. Rechazar doble extensión peligrosa (`captura.pdf.exe`).
3. Usar `Path(upload.name).name`, nunca rutas aportadas por el cliente.
4. Rechazar nombres vacíos o con caracteres de control.
5. Leer por chunks cuando sea posible.
6. Restaurar el cursor con `seek(0)` después de validar/calcular hash.
7. El MIME declarado sólo acompaña la decisión; no la determina.
8. Rechazar archivos cifrados que no puedan inspeccionarse.
9. No aceptar `.svg`, porque puede contener script.
10. No aceptar `.zip`, `.rar`, `.7z`, `.docm`, `.xlsm`, `.html` ni `.htm`.
11. Rechazar imágenes que excedan 25 millones de píxeles y tratar
    `DecompressionBombWarning` de Pillow como error.
12. Para DOCX/XLSX, limitar a 2.000 miembros y 50 MiB descomprimidos acumulados;
    rechazar nombres internos absolutos o con `..` para evitar ZIP bombs y path
    traversal, aunque el ZIP nunca se extraiga.

### 7.3. Formulario múltiple en Django 5.2

Implementar explícitamente:

- `MultipleFileInput(ClearableFileInput)` con
  `allow_multiple_selected = True`;
- `MultipleFileField(FileField)` cuyo `clean()` devuelve una lista validada;
- validación acumulada en `FeedbackForm.clean_attachments()`.

No confiar en agregar únicamente `multiple` al HTML: el contrato de Django
debe validar cada elemento.

---

## 8. Contrato de correo

### 8.1. Settings nuevas

Agregar a `config/settings.py`:

```python
FEEDBACK_RECIPIENT_EMAIL = env(
    "FEEDBACK_RECIPIENT_EMAIL",
    default="consultaergosolutions@gmail.com",
)
FEEDBACK_EMAIL_TIMEOUT_SECONDS = env.int(
    "FEEDBACK_EMAIL_TIMEOUT_SECONDS",
    default=20,
)
FEEDBACK_RATE_LIMIT = env.int("FEEDBACK_RATE_LIMIT", default=5)
FEEDBACK_RATE_WINDOW_SECONDS = env.int(
    "FEEDBACK_RATE_WINDOW_SECONDS",
    default=3600,
)
FEEDBACK_ATTACHMENT_RETENTION_DAYS = env.int(
    "FEEDBACK_ATTACHMENT_RETENTION_DAYS",
    default=90,
)
PRIVATE_FEEDBACK_ROOT = BASE_DIR / "private_media" / "feedback"
```

El destinatario solicitado no es un secreto y el default permite desplegar
sin modificar el `.env`. Si Pablo decide configurarlo en `.env`, esa carga es
una operación P-1 del despliegue y no debe imprimirse ni ser ejecutada por el
asistente sin autorización.

### 8.2. Encabezados

- `From`: `settings.DEFAULT_FROM_EMAIL`;
- `To`: lista de un único elemento, `settings.FEEDBACK_RECIPIENT_EMAIL`;
- `Reply-To`: snapshot de `reporter_email`;
- no usar CC/BCC;
- subject construido sólo con categoría y código:
  `[ErgoSolutions Beta][ERROR][FB-1234ABCD] <asunto saneado>`.

Eliminar `\r` y `\n` del asunto antes de construir el email.

### 8.3. Cuerpo

Texto plano, en este orden:

1. código de seguimiento;
2. categoría;
3. fecha/hora;
4. datos del profesional;
5. pantalla afectada;
6. asunto;
7. descripción;
8. pasos de reproducción;
9. resultado esperado;
10. user agent;
11. resumen de adjuntos: cantidad y bytes.

No generar HTML en la primera versión. El texto plano reduce superficie de
inyección y mantiene el mensaje legible en cualquier cliente.

### 8.4. Flujo de persistencia y envío

1. Validar todo el formulario y todos los archivos.
2. Comprobar rate limit.
3. Crear `FeedbackReport` en estado `pending` con snapshots.
4. Crear adjuntos privados, calculando hash y metadatos.
5. Construir `EmailMessage`.
6. Leer cada archivo desde el storage privado y adjuntarlo.
7. Enviar con `fail_silently=False` y timeout.
8. Si `send()` devuelve `1`, marcar `sent`, incrementar intentos y guardar
   `emailed_at`.
9. Ante excepción o retorno `0`, marcar `failed`, incrementar intentos y guardar
   sólo la clase/código seguro del error.
10. Redirigir siempre mediante PRG a la misma pantalla con mensaje de éxito o
    de envío pendiente.

No envolver el envío SMTP dentro de una transacción de base de datos larga.
La red no debe mantener locks abiertos.

### 8.5. Reintento

Agregar:

```text
python manage.py retry_feedback_emails --limit 20
python manage.py retry_feedback_emails --report <uuid>
```

El comando sólo toma estados `failed` o `pending`, respeta un máximo de
intentos configurable (recomendado: 5), reutiliza el mismo servicio y muestra
únicamente IDs y estados. No imprime comentarios, emails ni nombres de archivo.

### 8.6. Purga

Agregar:

```text
python manage.py purge_feedback_attachments --older-than-days 90 --dry-run
python manage.py purge_feedback_attachments --older-than-days 90
```

Condiciones:

- sólo reportes `sent`;
- conservar filas y metadatos;
- borrar físicamente el archivo y dejar una marca `purged_at` en el adjunto;
- `--dry-run` obligatorio en el runbook antes de una purga real;
- una purga real es destructiva y requiere autorización expresa.

---

## 9. Ayuda Contextual y contexto de los bots

### 9.1. Base neutral del widget

Crear `templates/base_contextual_help.html` con:

- extensión de `base_dashboard.html`;
- CSS actual de `help_widget.css`;
- botón y offcanvas actuales;
- `{% block help_slug %}home{% endblock %}` en el atributo
  `data-page-slug`;
- librerías locales marked/DOMPurify;
- `help_widget.js`;
- bloques neutrales:
  - `content_with_help`;
  - `extra_css_with_help`;
  - `extra_js_with_help`.

Refactorizar `templates/ergonomia_886/base_886.html` para extender esa base y
conservar:

- `content_886`;
- `extra_css_886`;
- `extra_js_886`;
- `planilla_logic.js` sólo en las pantallas 886.

Crear `templates/feedback/create.html` extendiendo la base neutral y declarando:

```django
{% block help_slug %}feedback{% endblock %}
```

### 9.2. Catálogo `help_ai`

Modificar:

- `apps/ergonomia_886/help_ai/catalog.py`: agregar `feedback` a
  `PAGE_HELP_SLUGS`;
- `apps/ergonomia_886/help_ai/pages.py`: agregar ficha con:
  - título: `Enviar comentarios de la beta`;
  - ruta: `/dashboard/comentarios/`;
  - propósito: informar errores o mejoras y adjuntar evidencia;
- `apps/ergonomia_886/help_ai/profiles.py`: declarar `"feedback": ()`, de
  modo que use sólo el núcleo y no cargue anexos normativos irrelevantes;
- `static/ayuda/help_texts/feedback.md`: guía específica.

### 9.3. Contenido mínimo de `feedback.md`

Debe explicar:

1. diferencia entre error, mejora, consulta y otro;
2. cómo describir el problema;
3. cómo informar la pantalla;
4. cómo escribir pasos reproducibles;
5. formatos y límites de archivos;
6. cómo anonimizar capturas;
7. qué sucede después de enviar;
8. qué significa el código `FB-XXXXXXXX`;
9. qué hacer si el correo queda pendiente;
10. que el bot no recibe ni puede leer los archivos adjuntos.

### 9.4. Contexto general de `help_ai`

Agregar una sección breve y factual a
`static/ayuda/help_texts/guia_para_el_usuario.md`, que ya forma parte del
contexto global de todas las pantallas:

```markdown
## Enviar errores o sugerencias de la beta

Una cuenta profesional puede abrir Dashboard → Comentarios de la beta, o ir a
/dashboard/comentarios/. Allí puede describir un error o mejora y adjuntar
capturas o documentos. El canal no reemplaza la carga de la evaluación y no se
deben incluir datos personales de trabajadores que no sean necesarios.
```

No agregar esta información a todos los anexos: una única fuente general evita
duplicaciones y aumenta muy poco el prompt.

### 9.5. Preámbulo de `help_ai`

El preámbulo actual dice que el asistente es experto en la Resolución y que
debe rechazar lo que exceda ese módulo. Al habilitar una pantalla de aplicación
general, ajustar sólo el rol, conservando intactas las fronteras de privacidad:

- ErgoBot es asistente de uso de ErgoSolutions y especialista en el módulo SRT
  886/15;
- puede responder sobre la pantalla `feedback` y sobre cómo enviar sugerencias;
- no puede afirmar que recibió, abrió o leyó un adjunto;
- no debe pedir contraseñas, DNI, CUIL ni datos de salud;
- `normalize_thread()` y `to_wire_thread()` no se tocan.

### 9.6. Asistente docente `ergobot_ai`

Agregar una excepción acotada en
`apps/ergobot_ai/prompts/system_base.md`:

- aunque normalmente responde sólo sobre la capacitación, sí puede explicar
  el canal de feedback de la aplicación;
- una cuenta profesional usa Dashboard → Comentarios de la beta;
- un trainee debe informar el problema al profesional responsable, porque no
  accede al dashboard profesional;
- no debe pedir ni aceptar información sensible en el chat.

No agregar un slug de feedback a `ergobot_ai`: ese asistente trabaja por módulo
de capacitación, no por pantalla.

---

## 10. Inventario previsto de archivos

### Archivos nuevos

```text
apps/feedback/__init__.py
apps/feedback/apps.py
apps/feedback/admin.py
apps/feedback/forms.py
apps/feedback/models.py
apps/feedback/services.py
apps/feedback/storage.py
apps/feedback/urls.py
apps/feedback/validators.py
apps/feedback/views.py
apps/feedback/migrations/__init__.py
apps/feedback/migrations/0001_initial.py
apps/feedback/management/__init__.py
apps/feedback/management/commands/__init__.py
apps/feedback/management/commands/retry_feedback_emails.py
apps/feedback/management/commands/purge_feedback_attachments.py
apps/feedback/tests/__init__.py
apps/feedback/tests/test_access.py
apps/feedback/tests/test_forms.py
apps/feedback/tests/test_mail.py
apps/feedback/tests/test_storage.py
apps/feedback/tests/test_commands.py
templates/base_contextual_help.html
templates/feedback/create.html
static/ayuda/help_texts/feedback.md
```

### Archivos a modificar

```text
config/settings.py
apps/dashboard/urls.py
templates/dashboard/home.html
templates/ergonomia_886/base_886.html
apps/ergonomia_886/help_ai/catalog.py
apps/ergonomia_886/help_ai/pages.py
apps/ergonomia_886/help_ai/profiles.py
apps/ergonomia_886/help_ai/preamble.py
apps/ergonomia_886/help_ai/tests.py
apps/ergobot_ai/prompts/system_base.md
apps/ergobot_ai/tests.py
apps/dashboard/tests.py
README.md
docs/README.md
este documento
```

Si durante la implementación aparece otro archivo, justificarlo en la bitácora
del commit. No aprovechar esta iniciativa para refactors ajenos.

---

## 11. Plan de implementación commit por commit

> Este trabajo está fuera de `PLAN_MAESTRO_ETAPA_3_PERFIL_EMPRESA.md`. Antes de
> implementarlo debe registrarse en el `README.md` como Decisión de
> Arquitectura. Las reglas de `AGENTS.md` sobre aprobación y un commit por vez
> continúan vigentes salvo que Pablo las suspenda expresamente para esta rama.

### Regla de cierre de cada commit

En cada commit, en este orden:

1. **VALIDAR** la suite específica y la suite completa.
2. **DOCUMENTAR** en este archivo el resultado literal relevante y actualizar
   `README.md`.
3. **PEDIR APROBACIÓN** según `AGENTS.md`.
4. **COMMITEAR** con el mensaje literal indicado.

La línea de base al crear este documento es de **310 tests** en
`apps + config`. El total nunca debe bajar.

### FB.0 — Crear rama y congelar contrato

**Mensaje:**

```text
docs(feedback): documentar la arquitectura del canal beta
```

Pasos:

1. Verificar que `f9ea7a0` está pusheado y el árbol sólo contiene este
   documento sin commitear.
2. Crear `codex/beta-feedback` desde `f9ea7a0`.
3. Revisar y, si Pablo lo solicita, incorporar decisiones adicionales.
4. Agregar a `README.md` una entrada “Canal de feedback beta — arquitectura
   aprobada” enlazando este documento.
5. Agregar el documento al índice `docs/README.md`.
6. Ejecutar validación base.
7. Commit sólo documental.

Validación:

```bash
.venv/bin/python manage.py test apps config --settings=config.test_settings
.venv/bin/python manage.py makemigrations --check --dry-run --settings=config.test_settings
.venv/bin/python manage.py check --settings=config.test_settings
git diff --check
```

### FB.1 — Modelo, storage privado y administración

**Mensaje:**

```text
feat(feedback): registrar reportes y adjuntos privados
```

Pasos:

1. Crear la app `apps.feedback` con docstrings de módulo.
2. Añadirla a `LOCAL_APPS`.
3. Declarar settings y constantes.
4. Implementar `PrivateFeedbackStorage` sin URL pública.
5. Implementar modelos y snapshots.
6. Generar migración `0001_initial` usando siempre `.venv/bin/python`.
7. Registrar los modelos en admin:
   - reportes en sólo lectura para contenido y snapshots;
   - filtros por categoría, estado y fecha;
   - inline de adjuntos mostrando metadatos, no links públicos;
   - acciones administrativas no deben enviar ni borrar por defecto.
8. Implementar tests de modelos, storage, ruta generada, índices y migración.
9. Actualizar README y este documento.

Validación específica:

```bash
.venv/bin/python manage.py test apps.feedback --settings=config.test_settings
.venv/bin/python manage.py makemigrations --check --dry-run --settings=config.test_settings
.venv/bin/python manage.py check --settings=config.test_settings
```

Prueba negativa obligatoria:

- `attachment.file.url` debe lanzar error;
- el path físico debe comenzar en `PRIVATE_FEEDBACK_ROOT` y no en `MEDIA_ROOT`.

### FB.2 — Validadores, email, reintento y purga

**Mensaje:**

```text
feat(feedback): validar adjuntos y entregar reportes por email
```

Pasos:

1. Implementar validadores por firma y estructura.
2. Implementar `MultipleFileInput` y `MultipleFileField`.
3. Implementar `FeedbackForm` con todos los límites.
4. Implementar el servicio de creación/persistencia sin mezclarlo con la vista.
5. Implementar el servicio idempotente de envío de un reporte.
6. Configurar destinatario fijo, Reply-To y timeout.
7. Implementar manejo de éxito/falla sin filtrar excepciones al usuario.
8. Implementar rate limit consultando reportes recientes en la base.
9. Implementar comando de reintento.
10. Implementar comando de purga con `--dry-run`.
11. Escribir tests de todos los formatos admitidos y rechazados.
12. Usar archivos mínimos generados dentro del test; no incorporar binarios
    grandes al repositorio.

Pruebas negativas obligatorias:

- `.exe` renombrado a `.pdf`;
- SVG;
- archivo ZIP genérico;
- DOCX sin estructura `word/`;
- XLSX sin estructura `xl/`;
- más de cinco archivos;
- archivo de más de 5 MiB;
- total de más de 12 MiB;
- asunto con CR/LF;
- backend de correo que lanza excepción;
- `send()` que devuelve cero;
- sexto reporte dentro de una hora.

Assertions de correo:

- un único destinatario exacto;
- `From` correcto;
- `Reply-To` correcto;
- cuerpo con tracking y campos;
- archivos binariamente iguales;
- el email no incluye contraseñas, cookies ni token CSRF;
- estado `sent` sólo después de `send()==1`.

### FB.3 — Formulario, URL y tarjeta profesional

**Mensaje:**

```text
feat(dashboard): habilitar el canal de feedback de la beta
```

Pasos:

1. Crear URL namespaced bajo `/dashboard/comentarios/`.
2. Crear vista sync con `login_required` y `professional_required`.
3. En GET, mostrar formulario vacío.
4. En POST, pasar `request.POST` y `request.FILES`.
5. Crear snapshots desde `request.user`, nunca desde campos ocultos.
6. Ejecutar servicio y aplicar PRG.
7. Crear template multipart con errores por campo y no-field.
8. Añadir tarjeta sólo a `dashboard/home.html`.
9. Ajustar grid responsive a tres tarjetas.
10. Mantener `home_company.html` intacto.
11. Agregar tests de acceso y rendering.

Matriz de permisos:

| Actor | GET | POST |
|---|---:|---:|
| Anónimo | redirect a login | redirect a login |
| Trainee | 403 | 403 |
| Company | 403 | 403 |
| Professional inactivo | 403/redirect según decorador | 403/redirect |
| Professional activo | 200 | 302 PRG |

Tests de propiedad:

- el FK y snapshots pertenecen al usuario autenticado aunque el POST intente
  enviar otro `user_id` o email;
- el destinatario no puede cambiarse desde el formulario;
- no existe una URL para descargar adjuntos;
- el dashboard empresa no contiene la tarjeta.

### FB.4 — Slug, base contextual y conocimiento de los bots

**Mensaje:**

```text
feat(help-ai): guiar el envio de comentarios de la beta
```

Pasos:

1. Extraer `base_contextual_help.html` preservando todos los bloques.
2. Adaptar `base_886.html` sin alterar su resultado HTML efectivo salvo la
   herencia.
3. Hacer que `feedback/create.html` extienda la base neutral.
4. Registrar `feedback` en catálogo, páginas y perfiles.
5. Crear `feedback.md`.
6. Agregar la sección transversal a `guia_para_el_usuario.md`.
7. Ajustar el rol del preámbulo sin tocar privacidad ni normalización.
8. Agregar la excepción en el prompt base de `ergobot_ai`.
9. Actualizar tests de cobertura bidireccional de slugs.
10. Agregar tests que inspeccionen las instrucciones finales de ambos agentes.

Pruebas obligatorias:

- todos los slugs anteriores siguen devolviendo guía 200;
- `feedback` devuelve guía 200, versión y ETag;
- la ruta del chat se construye para `feedback`;
- el agente conoce `/dashboard/comentarios/`;
- el agente afirma que no puede ver adjuntos;
- una pregunta “¿Cómo informo un error?” se responde con el canal correcto en
  los tests de prompt, sin llamar a API real;
- `normalize_thread()` y `to_wire_thread()` permanecen sin diff;
- el barrido de templates no detecta slugs huérfanos;
- `planilla_logic.js` no se carga en la página de feedback;
- las páginas 886 siguen cargándolo;
- ningún CDN o handler inline aparece.

Como este commit toca `static/`, el deploy requerirá `collectstatic` y se debe
documentar explícitamente.

### FB.5 — Verificación integral y cierre

**Mensaje:**

```text
test(feedback): cerrar el flujo beta de punta a punta
```

Pasos:

1. Agregar prueba de integración completa profesional → POST → storage → email.
2. Agregar prueba de fallo SMTP → registro durable → comando retry → enviado.
3. Agregar prueba de purga dry-run y purga autorizada sobre storage temporal.
4. Revisar accesibilidad: labels, ayuda, foco, errores y contraste.
5. Ejecutar suite completa tres veces si hubo flakiness; no ocultarla.
6. Verificar migraciones y `git diff --check`.
7. Actualizar README con arquitectura, límites, seguridad, operación y rollback.
8. Completar en este documento la sección “Resultado de ejecución”, incluyendo
   hashes y salida literal relevante.
9. Push de `codex/beta-feedback`.

Validación final:

```bash
.venv/bin/python manage.py test apps config --settings=config.test_settings
.venv/bin/python manage.py makemigrations --check --dry-run --settings=config.test_settings
.venv/bin/python manage.py check --settings=config.test_settings
.venv/bin/python manage.py check --deploy --settings=config.settings
git diff --check
git status --short
```

`check --deploy` puede conservar warnings preexistentes documentados, pero no
puede introducir uno nuevo.

Push:

```bash
git push -u origin codex/beta-feedback
git rev-parse HEAD
git status --short --branch
```

---

## 12. Matriz mínima de tests

| Área | Caso | Resultado esperado |
|---|---|---|
| Dashboard | Profesional abre home | Ve tres tarjetas |
| Dashboard | Empresa abre home | No ve feedback |
| Auth | Trainee abre formulario | 403 |
| Auth | Anónimo abre formulario | Redirect login |
| Form | Datos válidos sin adjuntos | Reporte + email |
| Form | Datos válidos con 5 adjuntos | Reporte + 5 attachments + email |
| Form | Sexto adjunto | Error, cero escrituras |
| Form | Archivo demasiado grande | Error, cero escrituras |
| Form | Total demasiado grande | Error, cero escrituras |
| Archivo | PNG/JPEG/WebP genuino | Aceptado |
| Archivo | PDF genuino | Aceptado |
| Archivo | DOCX/XLSX estructural | Aceptado |
| Archivo | Texto UTF-8 | Aceptado |
| Archivo | Ejecutable renombrado | Rechazado |
| Archivo | SVG/HTML/script | Rechazado |
| Storage | `.url` | Falla cerrado |
| Storage | ubicación | Fuera de MEDIA_ROOT |
| Email | SMTP exitoso | `sent`, una entrega |
| Email | SMTP excepción | `failed`, reporte preservado |
| Retry | reporte failed | pasa a sent |
| Rate | 5 dentro de una hora | permitidos |
| Rate | sexto dentro de una hora | bloqueado |
| Identidad | POST falsifica email/user | se ignora y usa request.user |
| Ayuda | slug feedback | Guía y chat registrados |
| Ayuda | todos los slugs previos | Sin regresión |
| ErgoBot docente | pregunta por feedback | indica dashboard profesional |
| Privacidad | logs | sólo IDs y métricas |
| Retención | dry-run | no borra |
| Retención | reporte no enviado | nunca borra |

---

## 13. QA manual local

Antes del push:

1. Crear dos profesionales de prueba locales.
2. Entrar con el profesional A.
3. Confirmar que la tarjeta se ve y la de empresa no se alteró.
4. Abrir el formulario en escritorio y viewport móvil.
5. Enviar mejora sin adjunto.
6. Revisar `mail.outbox` o backend de consola.
7. Enviar error con PNG, PDF y DOCX mínimos.
8. Confirmar código y destinatario.
9. Intentar SVG, ejecutable renombrado y exceso de tamaño.
10. Confirmar que no quedan archivos huérfanos después de una validación fallida.
11. Abrir Ayuda Contextual en el formulario:
    - Guía describe la pantalla;
    - Chat IA sabe la ruta;
    - Chat IA no dice que puede leer adjuntos.
12. Abrir una Planilla 1 y preguntar cómo informar una mejora.
13. Abrir la capacitación y verificar que Ergobot indica el canal profesional.
14. Confirmar que el profesional B no aparece en snapshots ni email del A.
15. Revisar HTML: no hay valores de rutas físicas, secrets o destinatarios
    editables.

---

## 14. Runbook previsto de deploy para el asistente de producción

Este capítulo no autoriza un deploy. El prompt final se debe generar después
de que desarrollo complete y pushee la rama.

### 14.1. Precondiciones

- árbol de producción limpio y detached en el commit vigente;
- ErgoSolutions active bajo ASGI con dos workers;
- CriaApp: tres unidades active y timestamps capturados;
- PostgreSQL active;
- nginx válido, sin necesidad de modificarlo;
- espacio libre suficiente;
- backup de unidad, drop-in, nginx, commit y dump de `ergocapacitacion_db`;
- no mostrar `.env` ni credenciales.

### 14.2. Alcance permitido

- fetch de la rama exacta;
- checkout detached del hash autorizado;
- `pip install -r requirements.txt` sólo si el diff realmente cambia
  requirements (el diseño actual no lo requiere);
- `manage.py check`;
- `migrate --plan` y `migrate`;
- `collectstatic --noinput` por los Markdown bajo `static/`;
- reinicio exclusivo de `ergocapacitacion.service`;
- smoke HTTP/CSRF y verificación de cabeceras;
- prueba funcional realizada por Pablo con una cuenta profesional autorizada.

### 14.3. Prohibiciones

- no correr tests en producción;
- no tocar `.env` salvo detención P-1 y acción de Pablo;
- no tocar ni consultar la base `criaapp`;
- no reiniciar PostgreSQL;
- no modificar/reload/restart nginx;
- no tocar unidades de CriaApp;
- no ejecutar purga real;
- no exponer contenido de reportes o adjuntos en la respuesta;
- no pushear desde producción.

### 14.4. Verificaciones post-deploy

1. migración de `feedback` aplicada;
2. directorio privado accesible por `deploy` y fuera de alias nginx;
3. servicio ASGI active, dos workers, `NRestarts=0`;
4. `/` y `/auth/login/` devuelven 200;
5. `/dashboard/comentarios/` redirige sin sesión;
6. CSP, unidad, drop-in y nginx sin cambios inesperados;
7. CriaApp conserva timestamps y HTTP 200;
8. Pablo envía un reporte sintético con captura sin datos reales;
9. mailbox `consultaergosolutions@gmail.com` recibe asunto, cuerpo y archivo;
10. admin muestra estado `sent` sin exponer URL pública.

### 14.5. Rollback

El rollback de aplicación consiste en:

1. checkout detached al commit anterior;
2. `collectstatic --noinput` con el código anterior;
3. restart exclusivo de ErgoSolutions;
4. verificar HTTP y CriaApp.

La migración es aditiva. En un rollback de emergencia no se debe revertir ni
borrar sus tablas: el código anterior las ignora y se preservan los reportes.
Un `migrate feedback zero` borraría datos y adjuntos relacionados; es una
operación destructiva y queda prohibida sin autorización expresa y backup.

---

## 15. Observabilidad y operación

Agregar logger `apps.feedback` con nivel INFO. Eventos permitidos:

```text
feedback_created report_id=<uuid> user_id=<id> attachments=<n> bytes=<n>
feedback_email_sent report_id=<uuid> attempts=<n>
feedback_email_failed report_id=<uuid> attempts=<n> error_class=<clase>
feedback_attachment_purged attachment_id=<uuid> report_id=<uuid>
```

Nunca loguear:

- asunto;
- descripción;
- pasos;
- nombre original;
- dirección de email;
- contenido binario;
- user agent completo;
- excepción SMTP completa si pudiera contener datos de conexión.

Métricas operativas iniciales, consultables desde admin:

- total de reportes;
- reportes por categoría;
- enviados/fallidos/pendientes;
- cantidad y tamaño de adjuntos;
- antigüedad del pendiente más antiguo.

No agregar un dashboard de métricas en esta primera versión.

---

## 16. Checklist de aceptación de producto

- [ ] La tarjeta se ve sólo para profesionales.
- [ ] La tarjeta es clara en desktop y móvil.
- [ ] El formulario permite informar error y mejora.
- [ ] El formulario acepta adjuntos permitidos.
- [ ] Los límites se explican antes de enviar.
- [ ] Los errores de validación son comprensibles.
- [ ] El reporte muestra código de seguimiento.
- [ ] El email llega a `consultaergosolutions@gmail.com`.
- [ ] Reply responde al email del profesional.
- [ ] Los adjuntos del email abren correctamente.
- [ ] Un error SMTP no pierde el reporte.
- [ ] No existe URL pública del adjunto.
- [ ] Empresa, trainee y anónimo no acceden.
- [ ] El Chat IA 886 sabe guiar desde cualquier pantalla.
- [ ] La guía específica del slug `feedback` es correcta.
- [ ] Ergobot de capacitaciones conoce la excepción de feedback.
- [ ] Ningún bot afirma poder leer adjuntos.
- [ ] La suite supera o iguala los 310 tests de partida.
- [ ] No hay migraciones pendientes.
- [ ] README y este documento reflejan lo ejecutado.
- [ ] La rama se pusheó sin reescribir historia.
- [ ] CriaApp quedó intacta.

---

## 17. Condiciones de detención durante la implementación

El asistente de desarrollo debe detenerse únicamente si aparece alguno de
estos casos:

1. hace falta conocer, leer o modificar una contraseña SMTP real;
2. se decide cambiar el destinatario y requiere un valor secreto/no confirmado;
3. hay que borrar reportes o adjuntos reales;
4. se necesita operar el servidor de producción;
5. la realidad contradice una decisión de producto central de este documento;
6. el árbol contiene cambios ajenos que se superponen con estos archivos;
7. los tests revelan que preservar CF-1 exige una decisión de arquitectura
   distinta.

Un fallo de test, una migración mal generada o un error de implementación no
son detenciones: se corrigen, documentan y vuelven a validar.

---

## 18. Plantilla de reporte de avance para el asistente de desarrollo

```yaml
✅ Commit FB.N — <título> — <hash>

Qué hice:      <resumen concreto>
Validación:    tests <antes> → <después> OK · migraciones OK · check OK
               <validación específica>
Documentado:   auditoría/plan ✓ · README ✓
Desvíos:       <ninguno o explicación>
Siguiente:     FB.N+1 — <título>
```

Al terminar FB.5:

```yaml
✅ CANAL DE FEEDBACK BETA LISTO PARA DEPLOY

Rama:          codex/beta-feedback
Commit final:  <hash completo>
Tests:         <total> — OK
Migraciones:   feedback.0001 — creada y validada
Static:        modificado — collectstatic requerido
SMTP:          validado con backend de test; prueba real pendiente de deploy
CriaApp:       sin cambios
```

---

## 19. Resultado de ejecución

### FB.0 — Contrato congelado

```yaml
Estado:        COMMIT a17e9dc5c36cd5d500669febe6a70fdbccfc2069
Rama:          codex/beta-feedback
Rama base:     codex/capacitaciones-firmas
Commit base:   f9ea7a044233ce1e630f976500efe73221e912f3
Árbol inicial: únicamente este documento sin seguimiento
Tests base:    Ran 310 tests in 4.269s — OK
Tests FB.0:    Ran 310 tests in 5.927s — OK
Migraciones:   No changes detected
System check:  System check identified no issues (0 silenced)
Diff check:    OK
Código nuevo:  ninguno; FB.0 es exclusivamente documental
Desvíos:       ninguno
```

### FB.1 — Modelo, storage privado y administración

```yaml
Estado:              COMMIT c14afee281a6c545a20bc26dab290e531a6c198e
App:                 apps.feedback registrada en LOCAL_APPS
Modelos:             FeedbackReport y FeedbackAttachment
Migración:           feedback.0001_initial (CreateModel + 3 índices)
Tests específicos:  Ran 5 tests in 0.006s — OK
Suite completa:      Ran 315 tests in 6.031s — OK
Migraciones check:   No changes detected
System check:        System check identified no issues (0 silenced)
Pruebas negativas:  file.url falla cerrado; path privado fuera de MEDIA_ROOT
Static:              sin cambios; collectstatic no requerido por FB.1
Desvíos:             purged_at se incluyó en 0001 porque DA-FB-8 y la única
                     migración prevista lo requieren para el comando de FB.2
```

### FB.2 — Validadores, email, reintento y purga

```yaml
Estado:              COMMIT 6703e735a3973fa41c03d0df63cfa6ad009af4b3
Tests específicos:  Ran 24 tests in 0.226s — OK
Suite completa:      Ran 334 tests in 5.690s — OK
Migraciones check:   No changes detected
System check:        System check identified no issues (0 silenced)
Formatos aceptados:  PNG, JPEG, WebP, PDF, DOCX, XLSX, CSV y TXT genuinos
Pruebas negativas:  ejecutable renombrado, SVG, ZIP, Office falso, traversal,
                     ZIP bomb, exceso de miembros/píxeles, 6 archivos,
                     5 MiB individual, 12 MiB total, CR/LF, SMTP excepción,
                     retorno 0 y sexto reporte por hora
Correo:              To fijo; From settings; Reply-To del snapshot; LocMem/mocks
Operación:           retry con máximo 5; purga sent-only y --dry-run
Static:              sin cambios; collectstatic no requerido por FB.2
Desvíos:             ninguno
```

### FB.3 — Formulario, URL y tarjeta profesional

```yaml
Estado:              COMMIT d6b8d096075b0417cf7286ee59fa01d2c97b6202
Tests específicos:  Ran 31 tests in 0.487s — OK
Suite completa:      Ran 341 tests in 6.044s — OK
Migraciones check:   No changes detected
System check:        System check identified no issues (0 silenced)
Permisos:            anónimo 302; trainee/company/inactivo 403; profesional 200/302
Identidad:           request.user prevalece sobre user_id/email/recipient del POST
PRG:                 confirmado con redirect y mensaje con tracking code
Smoke local:         /dashboard/comentarios/ 302 a /auth/login/;
                     /dashboard/ 302; /auth/login/ 200; servidor detenido
Static:              sin cambios; collectstatic no requerido por FB.3
Desvíos:             se modificó apps/dashboard/views.py, no previsto en el
                     inventario: una company sin CompanyProfile caía en
                     home.html profesional. El fallback ahora usa
                     home_company.html y preserva la regla de visibilidad.
```

### FB.4 — Slug, base contextual y conocimiento de los bots

```yaml
Estado:              COMMIT 490441033e3cd4a49c081ce176698a249c7d2c51
Tests específicos:  Ran 87 tests in 0.847s — OK
Suite completa:      Ran 346 tests in 6.357s — OK
Migraciones check:   No changes detected
System check:        System check identified no issues (0 silenced)
Herencia:            base_dashboard → base_contextual_help → base_886/feedback
Slug feedback:       guía 200; ETag y X-Help-Content-Version coincidentes
Assets:              feedback sin planilla_logic.js; páginas 886 con script
CF-1:                apps help_ai y ergobot_ai separadas; sin cambios en
                     normalize_thread() ni to_wire_thread(); sin API OpenAI
Smoke autenticado:   login 302; feedback 200; listado 886 200; guía 200;
                     servidor detenido y archivos temporales eliminados
Static:              feedback.md y guia_para_el_usuario.md modificados;
                     collectstatic requerido en producción
Desvíos:             _help_widget_body.html recibió sólo la corrección del
                     comentario que identifica su nueva base neutral
```

### FB.5 — Verificación integral y cierre

```yaml
Estado:              VALIDADO, corresponde al propio commit FB.5
Tests específicos:  Ran 36 tests in 0.518s — OK
Suite completa:      Ran 350 tests in 6.649s — OK
Migraciones check:   No changes detected
System check:        System check identified no issues (0 silenced)
Deploy check:        6 warnings preexistentes (W004, W008, W009, W012,
                     W016 y W018); FB.0–FB.5 no agrega warnings de deploy
Diff check:          OK
Collectstatic:       --dry-run OK; producción requiere --noinput real
Integración:         profesional → POST → storage privado → LocMem email OK
Recuperación:        SMTP falla → reporte durable → retry → sent OK
Retención:           dry-run preserva; purga temporal borra binario y conserva metadata
Accesibilidad:       labels, privacidad, errores ARIA y foco inicial verificados
QA visual:           1440x1000 y 390x844; sin overflow horizontal ni consola
Procesos/temporales: servidor detenido; SQLite/cookies/capturas temporales eliminados
Static modificado:   feedback.md y guia_para_el_usuario.md
CriaApp:             fuera de alcance y sin cambios
Desvíos:             MIME de adjuntos se normaliza desde la extensión validada
                     y el rate limit bloquea la fila del profesional; ambas
                     defensas conservan y refuerzan DA-FB-6 y RT-5/RT-7
```

### Correcciones predeploy — 12/08/2026

Después de cerrar FB.5, la revisión manual previa al despliegue detectó tres
detalles de presentación. Pablo autorizó expresamente corregirlos, validar,
documentar, crear un commit adicional y actualizar el prompt de producción.
Este cierre no rediseña el canal de feedback ni altera DA-FB-1 a DA-FB-10.

```yaml
Estado:              VALIDADO, corresponde al propio commit predeploy
Base del ajuste:     aaed0c5aa0beaad995362f7ad6c022cce5d47657
Landing:             Evaluaciones = Disponible; desarrollo = IAinsane
Mapa Planilla 1:     schema 1.0.1; cuatro campos con margen horizontal
Tareas 1/2/3:        línea base y=505 → y=496
Tests específicos:  Ran 31 tests in 0.248s — OK (28 → 31)
Suite completa:      Ran 353 tests in 5.091s — OK (350 → 353)
Migraciones check:   No changes detected
System check:        System check identified no issues (0 silenced)
Deploy check:        6 warnings preexistentes (W004, W008, W009, W012,
                     W016 y W018); el ajuste no agrega warnings
Diff check:          OK
QA PDF:              Planilla 1 generada y renderizada a 180 dpi; Dirección,
                     Área/Sector, Puesto, trabajadores y tareas 1/2/3 sin solapes
Smoke local:         landing HTTP 200 en 1440x1000 y 390x844; badge y footer
                     verificados; sin overflow horizontal ni errores de consola
Procesos/temporales: servidor detenido; SQLite, PDF y PNG temporales eliminados
Static del ajuste:   sin cambios; collectstatic continúa requerido por FB.4
Migraciones nuevas:  ninguna; producción aplica sólo feedback.0001_initial
CriaApp:             fuera de alcance y sin cambios
Desvíos:             el primer smoke con SQLite :memory: no conservó las tablas
                     entre procesos; se repitió correctamente con una base
                     temporal aislada dentro de /private/tmp
```

### Corrección predeploy 2 — crédito global — 12/08/2026

Después del despliegue de `2100a3c`, la inspección funcional verificó que la
landing ya mostraba IAinsane pero las páginas internas conservaban el crédito
anterior. La causa fue de alcance: el primer ajuste modificó
`base_landing.html`, mientras que todo el backoffice hereda
`base_dashboard.html`, directamente o mediante `base_contextual_help.html`.

```yaml
Estado:              VALIDADO, corresponde al propio commit predeploy 2
Base en producción:  2100a3cd05f9bbb87608416aa2dcd6753ca00edf
Fuente pública:      base_landing.html — ya correcta y preservada
Fuente interna:      base_dashboard.html — unificada a IAinsane
Texto canónico:      © 2026 ErgoSolutions. Desarrollado por IAinsane
Cobertura:           profesional, empresa, feedback, capacitaciones,
                     evaluaciones y pantallas 886 por herencia de templates
Búsqueda global:     sólo dos leyendas de desarrollador en templates;
                     ambas contienen el texto canónico y ninguna el anterior
Tests específicos:  Ran 24 tests in 0.500s — OK
Suite completa:      Ran 354 tests in 4.881s — OK (353 → 354)
Migraciones nuevas:  ninguna
Static:              sin cambios; collectstatic no requerido por este fix
CriaApp:             fuera de alcance y sin cambios
Desvíos:             ninguno
```

### Cadena de commits de la iniciativa

```text
FB.0 a17e9dc5c36cd5d500669febe6a70fdbccfc2069
FB.1 c14afee281a6c545a20bc26dab290e531a6c198e
FB.2 6703e735a3973fa41c03d0df63cfa6ad009af4b3
FB.3 d6b8d096075b0417cf7286ee59fa01d2c97b6202
FB.4 490441033e3cd4a49c081ce176698a249c7d2c51
FB.5 aaed0c5aa0beaad995362f7ad6c022cce5d47657
PREDEPLOY 2100a3cd05f9bbb87608416aa2dcd6753ca00edf
PREDEPLOY-2 este mismo commit; su hash exacto se informa tras crearlo porque un
            commit no puede contener criptográficamente su propio hash.
```

FB.0–FB.5 permanecen intactos y en el orden aprobado. El commit PREDEPLOY fue
solicitado después de esa cadena para corregir la landing y la geometría de la
Planilla 1 antes de desplegar. PREDEPLOY-2 unifica el mismo crédito en todas las
páginas internas después de la revisión funcional. La confirmación remota y el
hash completo final se consignan en la entrega del asistente.

---

## 20. Conclusión

El canal es viable y conveniente para la beta. La arquitectura recomendada
prioriza cuatro propiedades:

1. **facilidad para el profesional**, con un único formulario desde el
   dashboard;
2. **entrega directa**, mediante el SMTP ya operativo;
3. **durabilidad**, para no perder reportes cuando el correo falla;
4. **privacidad**, manteniendo adjuntos fuera de las rutas públicas y evitando
   que bots o logs consuman su contenido.

La implementación puede realizarse íntegramente en una rama de desarrollo y
desplegarse de forma aditiva. No requiere downtime de base, cambios de nginx ni
operaciones sobre CriaApp. La única migración crea tablas nuevas, por lo que el
rollback de código es seguro sin destruir datos.
