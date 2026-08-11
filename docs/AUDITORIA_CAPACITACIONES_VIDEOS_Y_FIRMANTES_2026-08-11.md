# Auditoría de videos embebidos y firmantes documentales

**Proyecto:** ErgoSolutions / ergocapacitación  
**Fecha:** 11/08/2026  
**Rama de trabajo:** `codex/capacitaciones-firmas`  
**Base auditada:** `930d7c3`  
**Estado de partida:** 290 tests `OK`, sin migraciones pendientes y `check` sin observaciones  
**Alcance:** capacitaciones online y presenciales, certificados de capacitación y planillas oficiales SRT 886/15

## 1. Objetivo y criterio de aceptación

Esta auditoría responde a tres observaciones detectadas durante el recorrido
funcional de producción:

1. El video de capacitación no se reproduce dentro de ErgoSolutions, ni en la
   modalidad online ni en la presencial.
2. El responsable impreso en los documentos de capacitación debe ser el
   profesional que impartió la capacitación presencial o creó el enlace de la
   capacitación online.
3. La aclaración sobre la firma de Higiene y Seguridad en las planillas SRT
   886/15 debe corresponder al profesional propietario de la evaluación.

Se considera resuelto cuando:

- las dos pantallas de capacitación muestran el reproductor dentro del sitio;
- la política CSP permite solamente el origen de frames necesario, sin abrir
  `https:` de manera general ni habilitar scripts remotos en el documento
  principal;
- toda nueva emisión online conserva la relación trazable
  enlace → intento → certificado → profesional responsable;
- el PDF online no contiene nombres, profesiones ni matrículas escritos en el
  código;
- la planilla presencial continúa tomando al usuario profesional autenticado;
- las planillas SRT continúan tomando a `Evaluacion.usuario`, aunque otra
  identidad autorizada sea quien descargue el documento;
- existen pruebas negativas con dos profesionales para impedir cruces de
  identidad.

## 2. Evidencia visual recibida

| Evidencia | Pantalla/documento | Observación |
|---|---|---|
| Captura 20:05 | Capacitación presencial | Tarjeta con icono de YouTube y botón externo; no existe reproductor |
| Captura 20:14 | Capacitación online | Mismo comportamiento; el trabajador debe abandonar la plataforma |
| Captura 20:08 | Planilla presencial | Imprime nombre, profesión y matrícula del profesional autenticado |
| Captura 20:18 | Certificado online | Imprime un responsable, pero la inspección de código demuestra que está fijado manualmente |
| Capturas 10:44, 10:46 y 11:40 | Planillas oficiales SRT | Imprimen la aclaración del profesional sobre el recuadro de Higiene y Seguridad |

Las capturas demuestran la salida visible, pero por sí solas no prueban el
origen del dato. Por eso se siguió cada valor desde la vista hasta el modelo y
el generador PDF.

## 3. Resumen ejecutivo de hallazgos

| ID | Hallazgo | Severidad | Estado antes de corregir |
|---|---|---:|---|
| H-V1 | Los dos reproductores fueron reemplazados deliberadamente por enlaces externos durante el endurecimiento CSP | Alta de UX | Confirmado |
| H-V2 | El video configurado existe y responde en las rutas `watch`, `embed` y oEmbed; no es un ID inválido | Informativo | Confirmado |
| H-V3 | La CSP no declara `frame-src`; por herencia de `default-src 'self'`, un iframe remoto sería bloqueado | Alta técnica | Confirmado |
| H-C1 | El certificado online tiene nombre, título y especialidad escritos literalmente en `apps/certificates/pdf.py` | Crítica documental | Confirmado |
| H-C2 | `CapacitacionLink.created_by` conserva al emisor, pero esa relación se pierde antes de `QuizAttempt` y `Certificate` | Crítica de trazabilidad | Confirmado |
| H-C3 | La sesión del navegador guarda `capacitacion_ref`, pero no la valida ni la materializa en el intento | Alta | Confirmado |
| H-C4 | Un `capacitacion_ref` anterior puede permanecer en sesión al navegar sin `ref` o con uno inválido | Alta | Confirmado |
| H-C5 | Los certificados ya emitidos son PDFs materializados; no existe evidencia suficiente para reasignarles un responsable retroactivamente | Alta histórica | Confirmado |
| H-P1 | La planilla presencial recibe `request.user` y registra la misma identidad en `PresencialSession.professional` | Correcto | Verificado |
| H-S1 | `Evaluacion.usuario` es la fuente del firmante de Higiene y Seguridad | Correcto | Verificado |
| H-S2 | El alta fija `Evaluacion.usuario` desde el usuario creador y las exportaciones no usan un nombre global | Correcto | Verificado |
| H-S3 | La línea aclaratoria SRT usa cuerpo 5 y ancho fijo; puede truncar visualmente perfiles largos aunque la identidad fuente sea correcta | Media visual | Confirmado |

## 4. Video de capacitación

### 4.1 Causa raíz

Los templates originales sí tenían un `<iframe>` de YouTube. El commit
`2d029ed` (`fix(security): resolver las violaciones detectadas en Report-Only`)
los reemplazó por tarjetas con enlaces porque la CSP restrictiva no admitía
orígenes remotos. La decisión quedó registrada en el README y en la bitácora
de integración.

Archivos actuales:

- `templates/training/training_page.html`: muestra el mensaje “El video de
  capacitación se abre en YouTube”.
- `templates/presencial/capacitacion.html`: implementa la misma salida.
- `config/middleware.py`: declara `default-src 'self'`, pero no `frame-src`.

Por lo tanto, no hay un error de red ni un rechazo actual del reproductor: el
sitio no intenta embeberlo.

### 4.2 Verificación externa del contenido configurado

Para el ID canónico `IIgZp_NbsAE` se verificó el 11/08/2026:

```text
watch code=200 type=text/html; charset=utf-8
embed code=200 type=text/html; charset=utf-8
oembed code=200 type=application/json
```

Esto confirma que el identificador es reconocido y que existe un documento de
reproductor. El enlace externo debe conservarse como contingencia por si el
propietario del video cambia posteriormente su política de inserción.

### 4.3 Solución de seguridad

No se debe usar `frame-src https:` ni agregar YouTube a `script-src`. La
excepción mínima es:

```text
frame-src https://www.youtube-nocookie.com
```

El documento principal de ErgoSolutions conserva:

- scripts propios y con nonce;
- `connect-src 'self'`;
- `object-src 'none'`;
- `frame-ancestors 'self'`;
- ausencia de CDN para CSS/JS.

El iframe debe usar el modo de privacidad mejorada:

```text
https://www.youtube-nocookie.com/embed/<youtube_id>
```

`frame-src` controla lo que ErgoSolutions puede cargar dentro de un frame;
`frame-ancestors` controla quién puede embeber ErgoSolutions. Son directivas
distintas y ambas deben permanecer explícitas.

### 4.4 Contratos automáticos requeridos

- Las dos vistas contienen exactamente la URL `youtube-nocookie.com/embed/…`.
- Las dos conservan el enlace `youtube.com/watch?v=…` con
  `target="_blank" rel="noopener"`.
- La CSP contiene el `frame-src` exacto.
- La CSP no contiene `frame-src https:` ni agrega YouTube a `script-src` o
  `connect-src`.
- El test anterior que prohibía cualquier cadena `https:` debe actualizarse:
  codificaba el comportamiento deliberadamente reemplazado por este cambio de
  producto. La condición CF-1 real —mantener separados `help_ai` y
  `ergobot_ai`— no se debilita.

## 5. Responsable de capacitación presencial

### 5.1 Cadena verificada

```text
usuario profesional autenticado
  → presencial.views.planilla_pdf(request.user)
  → PresencialSession.professional
  → build_planilla_presencial_pdf(professional=request.user)
  → display_name / profession / license_number
```

No se encontró un nombre fijo ni una consulta a “primer profesional”,
superusuario o dato global. La captura recibida coincide con esta cadena.

### 5.2 Riesgo restante y prueba necesaria

El test actual sólo confirma que el endpoint devuelve un PDF. No inspecciona
su texto. Debe generarse el documento con dos profesionales de identidades
deliberadamente distintas y comprobar que contiene únicamente al usuario
autenticado.

La sesión se crea antes de generar el PDF y conserva también a ese usuario,
por lo que auditoría y documento quedan alineados.

## 6. Responsable del certificado online

### 6.1 Defecto documental crítico

`apps/certificates/pdf.py` contiene literalmente:

```text
Pablo Ricardo Aguirre
Licenciado en Kinesiología - MN 10.027
Especialista en Ergonomía
```

En consecuencia, cualquier trabajador, empresa, módulo o enlace produce el
mismo responsable. La captura luce correcta sólo porque el profesional usado
en la prueba coincide con el texto fijo. Con un segundo profesional el
certificado sería materialmente falso.

El archivo además contiene una segunda implementación encerrada en un string
triple y varios imports sin uso. Debe limpiarse para que exista una sola fuente
ejecutable del generador.

### 6.2 Información que ya existe pero se pierde

`CapacitacionLink.created_by` identifica al usuario que creó el link.
`public_landing()` almacena el UUID en `request.session["capacitacion_ref"]`.
Sin embargo:

- `training_home()` no valida ese UUID;
- `QuizAttempt` no tiene relación con el link;
- `_create_certificate()` recibe sólo trabajador, módulo e intento;
- `Certificate` no conserva responsable ni snapshot de sus datos;
- el PDF no recibe una identidad responsable.

La base conoce la respuesta en el momento de entrada, pero el dominio la
descarta antes de emitir el documento.

### 6.3 Modelo recomendado

Para nuevas emisiones:

1. Agregar a `QuizAttempt` un FK nullable `capacitacion_link` con
   `on_delete=SET_NULL`.
2. Al iniciar o rehacer un intento de trainee, resolver el UUID de sesión,
   exigir que pertenezca al mismo módulo y que el link sea utilizable, y fijar
   el FK en ese momento.
3. Limpiar `capacitacion_ref` al entrar sin referencia o con una referencia
   inválida, para impedir atribuciones por estado residual.
4. Agregar a `Certificate`:
   - FK nullable `responsible_professional` con `on_delete=SET_NULL`;
   - `responsible_name`;
   - `responsible_profession`;
   - `responsible_license_number`.
5. Al emitir, obtener el profesional desde
   `attempt.capacitacion_link.created_by`, validar que sea de tipo
   `professional` y copiar los tres campos al certificado.
6. Construir el PDF exclusivamente desde el snapshot del certificado.

El FK permite navegación y auditoría; el snapshot asegura que un cambio futuro
de perfil o la baja de la cuenta no altere un certificado ya emitido.

### 6.4 Enlaces creados por una cuenta empresa

El decorador actual permite a profesionales y empresas crear links. Una
empresa no puede figurar como “Responsable de Capacitación”. No existe hoy un
campo que permita elegir qué profesional aceptó esa responsabilidad.

Regla segura para esta corrección:

- los intentos que generen certificado deben proceder de un link creado por
  un profesional completo;
- nunca se debe sustituir silenciosamente por el primer profesional, un admin,
  el autor del módulo o un valor fijo;
- el flujo futuro de empresa requiere un campo explícito
  `responsible_professional` en el link y una selección limitada a una
  relación empresa-profesional aceptada.

Hasta diseñar esa selección, una cuenta empresa no debe poder originar un
certificado firmado de forma automática. Es preferible un error explícito a
emitir un documento con responsable falso.

### 6.5 Certificados existentes

No se deben regenerar masivamente ni completar por heurística. Los registros
actuales no guardan el link de origen y puede haber varios profesionales que
hayan compartido el mismo módulo. `LinkShareLog` tampoco enlaza al intento ni
demuestra qué URL usó finalmente el trabajador.

La migración debe dejar los nuevos campos vacíos en filas históricas. Los PDFs
ya guardados permanecen como artefactos históricos. Si se requiere corregir
uno concreto, debe hacerse con evidencia y un procedimiento de reemisión
individual auditable.

## 7. Firmante de las planillas SRT 886/15

### 7.1 Cadena verificada

```text
EvaluacionForm(user=request.user)
  → al crear: evaluacion.usuario = user
  → Evaluacion.usuario (FK “Profesional responsable”)
  → exportaciones.serializers.build_cabecera(evaluacion)
  → nombre/profesión/matrícula de evaluacion.usuario
  → aclaraciones_firma.higiene_seguridad
  → official.builders._aclaraciones_firma_ops()
  → overlay del PDF oficial
```

La fuente no es el usuario que descarga. Esto es correcto: una empresa
autorizada puede consultar una evaluación, pero no debe reemplazar al
profesional que la realizó.

Los accesos de edición/eliminación y los querysets de visibilidad también
parten de la propiedad de la evaluación; no se detectó una reasignación
implícita.

### 7.2 Cobertura existente

`AclaracionesFirmaCF5Tests` ya verifica:

- nombre, profesión y matrícula del profesional;
- recuadro de Medicina Laboral siempre vacío;
- aclaración vacía si falta matrícula;
- datos del empleador sólo cuando existe empresa vinculada.

Debe agregarse un contrato con dos profesionales para demostrar de forma
literal que el payload usa al propietario de la evaluación y no a otra
identidad activa.

### 7.3 Observación de maquetación

La captura muestra “Matri…” truncado. El builder usa:

- fuente Helvetica de 5 puntos;
- ancho máximo de 112 puntos;
- una línea para profesión y matrícula.

La fuente de identidad es correcta, pero perfiles extensos podían ocultar
parte de la matrícula. La implementación separa ahora nombre, profesión y
matrícula en tres líneas. Los builders conservan las coordenadas específicas
de las doce páginas y el test del payload exige las tres operaciones de texto.

## 8. Plan de implementación autónomo

### Paquete A — reproductor seguro

1. Agregar `frame-src https://www.youtube-nocookie.com` al middleware.
2. Crear un partial reutilizable del reproductor.
3. Incluirlo en online y presencial.
4. Conservar el enlace externo.
5. Actualizar contratos CSP y tests de ambas vistas.
6. Hacer smoke en navegador y confirmar ausencia de violaciones CSP.

### Paquete B — identidad presencial y SRT

1. Extraer texto del PDF presencial con `pypdf` y comprobar identidad.
2. Agregar segundo profesional adversarial.
3. Agregar test de propietario SRT adversarial.
4. No modificar la fuente de datos, porque ya es correcta.
5. Tratar el ajuste de truncamiento como cambio visual separado si la pasada
   sobre doce páginas no cabe en el mismo commit.

### Paquete C — trazabilidad online

1. Migración de `QuizAttempt.capacitacion_link`.
2. Migración de responsable y snapshots en `Certificate`.
3. Resolución estricta del link al crear intento.
4. Limpieza de sesión residual.
5. Emisión desde snapshot, sin constantes.
6. Admin de sólo lectura para inspeccionar responsable y link.
7. Tests de dos profesionales, link incorrecto, módulo incorrecto, link
   vencido/inactivo, sesión residual y cambio de perfil posterior.
8. Confirmar que los PDFs históricos no se reescriben.

## 9. Matriz mínima de pruebas

| Caso | Resultado exigido |
|---|---|
| Online con video válido | iframe `youtube-nocookie` visible y enlace externo disponible |
| Presencial con video válido | mismo reproductor compartido |
| CSP de cualquier respuesta | sólo el host exacto en `frame-src` |
| Link de profesional A + trainee + aprobado | certificado contiene A y no B |
| Link de profesional B + mismo módulo | certificado contiene B y no A |
| Perfil A cambia después de emitir | PDF y snapshot emitidos no cambian |
| Sesión con link de otro módulo | intento rechazado; no se atribuye responsable |
| Link inactivo o vencido | intento rechazado; no se emite certificado |
| Entrada posterior sin `ref` | la referencia anterior se elimina |
| Planilla presencial autenticada como A | contiene A y no B |
| Evaluación creada por A, descargada por actor autorizado B | planilla SRT contiene A y no B |
| Profesional SRT sin matrícula | aclaración vacía; no se inventa dato |

## 10. Despliegue y rollback

### Despliegue

1. Aplicar migraciones antes de habilitar nuevas emisiones.
2. Ejecutar `collectstatic` sólo si se agrega CSS/JS estático; un cambio de
   template y middleware por sí solo no lo requiere.
3. Reiniciar exclusivamente `ergocapacitacion.service` para cargar el código.
4. No tocar nginx, PostgreSQL global ni servicios de CriaApp.
5. Validar:
   - login profesional y trainee;
   - reproductor online y presencial;
   - un intento sintético originado por link;
   - texto del certificado;
   - planilla presencial;
   - una exportación SRT;
   - consola sin violaciones CSP;
   - CriaApp `active` y HTTP 200.

### Rollback

- El código puede volver al commit anterior.
- Las columnas nuevas son aditivas y nullable, por lo que pueden permanecer
  durante un rollback de aplicación sin afectar lecturas antiguas.
- No borrar migraciones aplicadas ni columnas en una ventana de rollback.
- Los certificados emitidos con snapshots siguen siendo válidos aunque se
  revierta temporalmente la interfaz.
- No regenerar ni borrar PDFs históricos durante rollback.

## 11. Conclusión

El problema del video es una regresión funcional introducida conscientemente
para satisfacer una CSP que no contemplaba el caso de negocio. Se puede
restaurar sin abandonar la política restrictiva mediante un único origen de
frames y el dominio de privacidad mejorada de YouTube.

La modalidad presencial y las planillas SRT ya toman la identidad correcta,
pero necesitan pruebas adversariales que congelen ese contrato. El certificado
online, en cambio, no está vinculado al profesional real: hoy produce un dato
correcto sólo por coincidencia con el nombre codificado. La solución correcta
requiere persistir procedencia y snapshot; reemplazar el texto fijo por
`request.user`, por el primer profesional o por el autor del módulo sería una
corrección aparente y documentalmente insegura.

## 12. Resultado de implementación en esta rama

La implementación se completó después de redactar y revisar el diagnóstico:

- reproductor compartido con `youtube-nocookie.com` en ambas modalidades;
- `frame-src` reducido al host exacto y contratos CSP actualizados;
- `QuizAttempt.capacitacion_link` como procedencia persistente;
- responsable y snapshot documental en `Certificate`;
- generador PDF único, sin identidad escrita en el código;
- rechazo explícito de enlaces sin profesional completo, incluidos enlaces
  creados por cuentas empresa mientras no exista selección nominal;
- limpieza de referencias de sesión inválidas, inactivas o de otro módulo;
- pruebas adversariales con dos profesionales para certificado online,
  planilla presencial y planillas SRT;
- profesión y matrícula SRT separadas para evitar la truncación observada.

Los certificados históricos no se modifican ni se infieren. Las nuevas
columnas son aditivas y nullable precisamente para permitir una migración y un
rollback seguros.

### QA visual de PDFs

Se generaron y renderizaron a PNG tres artefactos sintéticos con identidades
largas: certificado online, planilla de asistencia presencial y Planilla 1 SRT.
La inspección visual confirmó:

- certificado en una página, sin solapamientos ni texto cortado;
- nombre, profesión y matrícula del responsable claramente separados;
- encabezado presencial legible con profesión extensa;
- aclaración SRT en tres líneas, centrada sobre el recuadro correcto y sin
  invadir el rótulo ni las firmas contiguas;
- ausencia de cuadrados negros, glifos rotos o desbordes.

Los PDFs y PNGs de QA fueron temporales y no forman parte del repositorio.
