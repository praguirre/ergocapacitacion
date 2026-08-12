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
