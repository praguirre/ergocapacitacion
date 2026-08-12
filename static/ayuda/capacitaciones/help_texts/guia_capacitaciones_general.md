# Conceptos del área de Capacitaciones

Estos son los términos que usa la aplicación. Conocerlos alcanza para interpretar
cualquier pantalla del área.

## Módulo de capacitación

Un contenido de formación completo. Tiene un título, una descripción, un video, material
de lectura, una transcripción y un cuestionario. Se identifica con un nombre corto en la
dirección de la página; por ejemplo, la capacitación de ergonomía aparece como
`/dashboard/capacitaciones/ergonomia/`.

Un módulo puede estar activo o inactivo. Los inactivos se muestran con la etiqueta
**Próximamente** y no se pueden abrir.

## Modalidad

La forma de dictar el módulo. Hay dos y son excluyentes por sesión:

- **Presencial:** el profesional está con el grupo y proyecta el contenido.
- **Online:** cada trabajador realiza la capacitación por su cuenta desde un link.

Elegir una modalidad no bloquea la otra: el mismo módulo puede dictarse presencialmente
hoy y compartirse por link mañana.

## Link de capacitación

Una dirección única que habilita el acceso de un trabajador a un módulo. Tiene:

- una **etiqueta** opcional, para reconocerlo internamente;
- una **fecha de creación**;
- un **estado**: activo, inactivo o expirado;
- un **contador de accesos**, que se incrementa cada vez que alguien entra por él.

El link no es personal: el mismo enlace puede compartirse con varias personas. Quien lo
usa se registra al ingresar.

## Quiz

El cuestionario de evaluación del módulo. Su comportamiento depende de la modalidad:

- **Online:** hasta 3 intentos, se aprueba con 8 respuestas correctas sobre 10 y emite
  certificado al aprobar.
- **Presencial:** sin límite de intentos, muestra el resultado en pantalla y **no** guarda
  intentos individuales ni emite certificados.

## Planilla de asistencia

Un PDF que genera la aplicación al terminar una capacitación presencial. Trae los datos
del módulo y del profesional, y deja los renglones libres para que los asistentes firmen a
mano. Generarla registra la sesión en el historial.

## Certificado

Un PDF individual que emite la aplicación cuando un trabajador aprueba el quiz en modo
online. El trabajador lo descarga desde su propio circuito; no se emite desde el panel
profesional.

## Historial presencial

El registro de las sesiones presenciales realizadas por el profesional: fecha, módulo,
ubicación, cantidad de participantes y resultado del quiz cuando fue tomado.
# Elegir entre presencial y online

La pantalla de modalidad presenta dos tarjetas. La decisión depende de si el profesional
va a estar presente con el grupo o no.

## Modo presencial

Conviene cuando hay un grupo reunido y alguien conduce la capacitación.

- Proyecta el video de la capacitación desde la misma pantalla.
- Ofrece un chat con **Ergobot**, el asistente docente, para responder las consultas que
  surgen durante la charla.
- Permite tomar un quiz grupal cuyo resultado se ve en el momento.
- Genera una planilla PDF de asistencia para que el grupo firme.
- **No** registra a cada trabajador de forma individual y **no** emite certificados.

## Modo online

Conviene cuando cada trabajador va a capacitarse por su cuenta.

- Genera un link compartible por correo o por mensajería.
- Cada trabajador se registra al ingresar, con lo cual queda identificado.
- El quiz aplica las reglas completas: hasta 3 intentos y aprobación con 8 sobre 10.
- Al aprobar, la aplicación emite un certificado individual en PDF.

## Cómo decidir

| Situación | Modalidad recomendada |
|---|---|
| Charla en planta con el grupo reunido | Presencial |
| Personal en turnos distintos o en varias sedes | Online |
| Se necesita constancia individual por trabajador | Online |
| Se necesita una planilla firmada de la jornada | Presencial |
| Se quiere dejar ambas constancias | Presencial primero, y después compartir el link |
# El circuito online en detalle

## Generar un link

Desde la pantalla de links, el campo **Etiqueta** es opcional y sirve sólo para reconocer
el link más tarde; por ejemplo «Planta Norte — Turno Mañana». Al presionar **Generar
Link**, la aplicación crea el enlace y lo muestra en la lista de abajo.

Se pueden generar tantos links como haga falta para el mismo módulo. Usar un link distinto
por grupo, sede o turno permite después distinguir cuántos accesos tuvo cada uno.

## Compartir el link

Hay dos caminos, y son equivalentes para el trabajador:

1. **Copiar y pegar:** el botón con el ícono de portapapeles copia la dirección completa,
   lista para enviar por WhatsApp, Teams o el canal que se use.
2. **Enviar por correo desde la aplicación:** el botón del sobre abre un formulario donde
   se cargan una o más direcciones y, opcionalmente, un mensaje. La aplicación envía el
   correo y registra cada envío.

## Qué ve el trabajador

Al abrir el link, el trabajador llega a una pantalla de acceso donde se registra o inicia
sesión. Después ve el video del módulo, puede consultar con Ergobot y rendir el
cuestionario. Si aprueba, obtiene su certificado.

El trabajador **no** entra al panel profesional en ningún momento y no ve los links, ni el
historial, ni las demás capacitaciones.

## Seguimiento

La lista de links muestra, por cada uno:

- la etiqueta o un identificador abreviado;
- la fecha de creación;
- el estado: **Activo**, **Inactivo** o **Expirado**;
- la cantidad de accesos registrados.

El contador de accesos cuenta ingresos por el link, no personas distintas ni aprobaciones.
Un trabajador que entra dos veces suma dos accesos.
# El circuito presencial en detalle

## Durante la capacitación

La pantalla de dictado presencial está pensada para proyectarse. Tiene dos áreas:

- **Video de capacitación:** el reproductor del módulo. Conviene ponerlo en pantalla
  completa durante la proyección.
- **Chat con Ergobot:** el asistente docente. Responde consultas sobre el contenido de la
  capacitación —qué es una postura forzada, cómo levantar una carga— y sirve para resolver
  dudas del grupo en el momento.

Debajo del video está el botón **Iniciar Quiz de Evaluación**, que lleva al cuestionario
grupal.

## El quiz presencial

Se responde una pregunta por vez, con botones para avanzar y retroceder. Al terminar,
**Finalizar Quiz** muestra el resultado inmediatamente: puntaje sobre el total y si el
grupo alcanzó el mínimo de 8 respuestas correctas.

Diferencias con el quiz online, que conviene tener claras:

- no hay límite de intentos y el botón **Repetir Quiz** permite volver a empezar;
- no se guarda un intento por persona;
- no se emite certificado.

## La planilla de asistencia

Desde la pantalla de resultado, el botón **Generar Planilla de Asistencia** descarga un
PDF con los datos del módulo y del profesional y renglones libres para las firmas.

Generar la planilla **registra la sesión** en el historial presencial. Si se genera dos
veces, quedan dos sesiones registradas.

## El historial

La pantalla de historial lista las sesiones presenciales del profesional con su fecha,
módulo, ubicación, cantidad de participantes y resultado del quiz. Es el respaldo de lo
actuado y sirve para reconstruir qué se dictó y cuándo.
