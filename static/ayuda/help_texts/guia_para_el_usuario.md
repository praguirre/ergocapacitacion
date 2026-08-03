# Guía Completa para el Usuario de ErgoApp SRT 886

## 🏁 1. Introducción

ErgoApp SRT 886 es una aplicación web pensada para profesionales en Higiene y Seguridad Laboral y empleadores, para facilitar el cumplimiento de la Resolución 886/15 de la Superintendencia de Riesgos del Trabajo (SRT). Su función principal es digitalizar el proceso de evaluación ergonómica a través de planillas oficiales y generar un reporte en PDF.

## 🔐 2. Registro e Inicio de Sesión

### 📝 Registro de Usuario

Accedé a la página principal (/).

Si no tenés cuenta, hacé clic en “Registrarse” (arriba a la derecha).

Completá el formulario con tus datos:

- Nombre de usuario
- Contraseña (y confirmación)
- Correo electrónico

Hacé clic en “Registrarse”.

📌 Al finalizar, serás redirigido al Dashboard.

### 🔑 Inicio de Sesión

Si ya tenés cuenta, hacé clic en “Iniciar Sesión”.

Ingresá tu usuario y contraseña.

Hacé clic en “Ingresar”.

💡 Al iniciar sesión correctamente, serás redirigido al Dashboard donde verás tus evaluaciones.

## 🧭 3. Dashboard: Panel Principal del Usuario

📌 **URL:** `/` (ruta raíz)

### ¿Qué podés hacer aquí?

- Ver un listado de todas tus evaluaciones creadas.
- Ver la fecha de última modificación.
- Acceder a cada evaluación para completarla.
- Crear una nueva evaluación.
- Eliminar una evaluación existente.

### Elementos principales:

- **Botón “Crear Nueva Evaluación”**: inicia el proceso desde la Planilla 1.
- **Tabla de Evaluaciones**:
  - Columna “Razón Social”
  - “CUIT”
  - “Última Modificación”
  - Botones: Ver/Editar y Eliminar

## 🏢 4. Crear una Evaluación Nueva

Desde el Dashboard:

Hacé clic en el botón “Crear Nueva Evaluación”.

Completá los datos iniciales de la empresa:

- Razón social
- CUIT
- CIIU
- Dirección
- Nombre de trabajadores
- Puesto
- Procedimiento escrito, capacitación, etc.

📄 Esta pantalla corresponde a la **Planilla 1** del protocolo oficial.

Guardá el formulario → serás redirigido automáticamente a la vista de Detalle de Evaluación.

## 📂 5. Vista de Detalle de Evaluación

📌 Aquí se muestra el progreso y acceso directo a cada planilla asociada a una evaluación.

### Planillas disponibles (por ahora):

- ✅ Planilla 1: Identificación de factores de riesgo
- ✅ Planilla 2A–2I: Evaluación Inicial según factor (levantamiento, empuje, bipedestación, etc.)
- 🛠️ Planilla 3: Medidas Correctivas (en desarrollo o implementada según versión)
- 🛠️ Planilla 4: Matriz de Seguimiento (en desarrollo o implementada según versión)

Cada sección incluye:

- Un botón “Completar” o “Editar”.
- Validaciones automáticas para campos requeridos.
- Formularios individuales y reutilizables con Bootstrap para facilitar la navegación.

## 📄 6. Llenado de Planillas

### 🔹 Planilla 1 (Evaluación general del puesto):

Relevás los factores de riesgo (levantamiento, empuje, postura, etc.)

Para cada factor presente, deberás avanzar a la Planilla 2 correspondiente.

### 🔹 Planillas 2 (A a I):

Cada planilla es específica para un factor de riesgo.

Se presentan preguntas con respuestas **SI / NO** que determinan si el riesgo es tolerable o no.

Si hay factores de riesgo presentes → se propone continuar con **Medidas Correctivas (Planilla 3)**.

🧠 El formulario tiene validaciones que impiden enviar si hay errores u omisiones.

## 🔧 7. Planillas 3 y 4 (Etapa Correctiva y Seguimiento)

📌 Estas planillas están interconectadas.

### 🧩 Planilla 3 – Medidas Correctivas

Cargás una o más medidas para cada riesgo identificado.

Cada medida tiene:

- Descripción
- Plazo de implementación
- Responsable asignado

### 🔁 Planilla 4 – Matriz de Seguimiento

Lista automáticamente todas las medidas de la Planilla 3.

Debés registrar:

- Estado de avance (implementada / en proceso / pendiente)
- Observaciones
- Fecha de revisión

📝 Al actualizar el estado de medidas, podés generar un historial de control.

## 🧾 8. Eliminación de Evaluaciones

Desde el Dashboard:

Hacé clic en “Eliminar” al lado de la evaluación.

Confirmá en el cuadro emergente (confirmación mediante JavaScript).

La evaluación y todas sus planillas se eliminan definitivamente.

## 📥 9. Exportación de documentación

Desde el detalle de una evaluación, el botón **Exportar documentación** abre el
panel de descargas. Desde ahí podés obtener:

- **Cada planilla por separado**, en el formulario oficial de la Resolución
  SRT N° 886/15, completado con los datos que cargaste.
- **El protocolo completo**, con las Planillas 1, 2A a 2I, 3 y 4 en un único
  archivo PDF.

Detalles a tener en cuenta:

- Las planillas que todavía no completaste se descargan **en blanco**, listas
  para llenar a mano.
- Una respuesta se marca como «NO» sólo si guardaste esa planilla. Si nunca la
  completaste, la página sale vacía en lugar de marcar «NO» por vos.
- Los recuadros de firma quedan **libres**, para la firma de los responsables.
- El tamaño de página es **Carta**, porque así publicó la SRT el formulario
  oficial. Al imprimir en A4, usá la opción «ajustar a página».
- El documento es un **insumo de apoyo**: no constituye una homologación ni
  reemplaza la firma profesional.

## 📝 10. Informe profesional por factor

En cada una de las 13 páginas de evaluación cuantitativa vas a encontrar el
botón **Generar informe profesional**. Esta opción crea un borrador técnico en
PDF a partir de los datos guardados y del resultado calculado para ese factor.

Tené en cuenta:

- La aplicación calcula los niveles de riesgo, límites y clasificaciones con
  su motor determinístico. El modelo de lenguaje sólo redacta la explicación.
- El botón permanece deshabilitado mientras el resultado esté en borrador o
  desactualizado. Usá **Guardar y calcular** o recalculá el factor primero.
- El PDF incluye la redacción asistida y un anexo de respaldo armado
  directamente con los datos y la trazabilidad del cálculo.
- El informe no sustituye el criterio profesional: revisalo, corregilo y
  firmalo antes de presentarlo.
- Si cambiás un dato del factor, generá nuevamente el informe. La aplicación
  conserva la trazabilidad y marca como obsoleta la versión anterior.

## 👤 11. Cierre de Sesión

Desde cualquier página:

En la barra superior, hacé clic en “Cerrar Sesión”.

Serás redirigido automáticamente a la pantalla de inicio de sesión.

## ⚙️ 12. Seguridad y Acceso

- Solo podés acceder a tus evaluaciones personales.
- Todos los formularios están protegidos con token **CSRF**.
- Las rutas están protegidas por login:
  - Si intentás entrar sin iniciar sesión, serás redirigido automáticamente a `/login`.

## 💡 13. Consejos para una buena experiencia de uso

- Usá navegadores modernos (Chrome, Firefox, Edge).
- Completá los formularios de manera secuencial.
- Guardá frecuentemente.
- Revisá los mensajes de validación antes de enviar.
- Recordá que los campos con **SI** implican continuidad con más planillas.

## 📌 Conclusión

ErgoApp SRT 886 es una herramienta pensada para guiarte paso a paso a través del Protocolo de Evaluación Ergonómica exigido por la legislación argentina. Su diseño modular, intuitivo y seguro permite gestionar, registrar y controlar el estado de las evaluaciones desde una única plataforma.
