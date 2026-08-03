# Evaluación de Levantamiento Manual de Cargas (LMC)

## Para qué sirve esta pantalla

Esta evaluación cuantitativa compara el **peso real de la carga** con un límite de referencia seleccionado según:

- duración diaria de la tarea;
- frecuencia de levantamientos;
- altura vertical de las manos o de la carga (`V`);
- distancia horizontal de la carga al cuerpo (`H`);
- agravantes marcados.

Se accede a esta instancia después de la evaluación inicial de la **Planilla 2A — Levantamiento y/o descenso**, cuando corresponde profundizar el análisis. La comparación con la tabla oficial produce `tolerable` (`bajo`) o `no tolerable` (`alto`). Si hay agravantes, el profesional debe confirmar o modificar esa clasificación antes del cierre. El resultado no reemplaza automáticamente los niveles 1, 2 y 3 de la Planilla 1.

## Antes de completar

Observá un ciclo representativo y reuní datos verificables. Siempre que sea posible:

- determiná el peso con una balanza o una fuente técnica confiable;
- registrá la duración efectiva de la exposición, no solo la duración del turno;
- calculá levantamientos por hora sobre un período representativo;
- observá la posición más desfavorable que se repita en la tarea;
- documentá variaciones, picos y supuestos en **Observaciones**.

Si existen cargas, frecuencias o posturas claramente diferentes, evaluá escenarios separados; no promedies situaciones incompatibles sin justificarlo.

## Cómo completar los campos

### General

- **Aplicable:** indica si el método corresponde. Si se desmarca, el motor devuelve `no aplicable` sin ejecutar la fórmula específica; documentá el motivo en Observaciones.
- **Observaciones:** describí tarea, carga, fuente de los datos, variabilidad, lado corporal, condiciones ambientales y cualquier supuesto relevante.

### Parámetros del levantamiento

- **Peso kg (kg):** masa de una carga manipulada en cada levantamiento.
- **Duración h (h):** horas diarias efectivas durante las cuales se realizan los levantamientos.
- **Frecuencia h (lev/h):** cantidad de levantamientos por hora. El motor trabaja con un número entero.
- **V altura (V):** banda vertical en la que se encuentran las manos o la carga durante la condición evaluada:
  - `Suelo a mitad espinilla`;
  - `Mitad espinilla a nudillos`;
  - `Nudillos a codo/hombro`;
  - `Por encima del hombro`.
- **H dist (H):** alcance horizontal:
  - `Próximo (<30 cm)`;
  - `Intermedio (30–60 cm)`;
  - `Alejado (60–80 cm)`.

La calculadora consulta directamente las bandas seleccionadas en la tabla aplicable.

### Agravantes

Marcá únicamente los que estén presentes en la situación evaluada:

- giro mayor de 30°;
- levantamiento con una mano;
- postura agachada;
- carga inestable;
- entorno adverso;
- turnos largos.

Los campos no definen por sí solos todos los umbrales de observación. Cuando una condición requiera juicio profesional —por ejemplo, qué se considera “turno largo” o “entorno adverso”— justificá el criterio en Observaciones.

## Procedimiento recomendado

1. Confirmá que la tarea corresponde al factor A de la Planilla 1 y que la Planilla 2A requiere evaluación específica.
2. Ingresá peso, duración y frecuencia de una condición representativa.
3. Seleccioná las bandas `V` y `H` observadas.
4. Marcá todos los agravantes presentes.
5. Registrá método de medición, variaciones y supuestos.
6. Usá **Guardar** si querés conservar un relevamiento parcial sin calcular.
7. Usá **Guardar y calcular** solo cuando estén completos los datos necesarios.
8. Revisá el nivel, el límite base y la trazabilidad antes de emitir una conclusión. Si existen agravantes, completá desde el resumen la clasificación profesional final y justificá cualquier modificación.

## Cómo calcula la aplicación

### 1. Selección de tabla por exposición

| Tabla interna | Combinación de duración y frecuencia |
|---|---|
| Tabla 1 | duración ≤ 2 h y frecuencia ≤ 60 lev/h; o duración > 2 h y frecuencia ≤ 12 lev/h |
| Tabla 2 | duración > 2 h y frecuencia > 12 y ≤ 30 lev/h; o duración ≤ 2 h y frecuencia > 60 y ≤ 360 lev/h |
| Tabla 3 | duración > 2 h y frecuencia > 30 y ≤ 360 lev/h |

Una frecuencia nula no representa una tarea repetida y no debe utilizarse para obtener un resultado, aunque el control numérico admita `0`.

### 2. Límite base

El motor busca en `lmc_tablas.json` el límite en kilogramos correspondiente al cruce:

`tabla seleccionada × banda V × banda H`

Algunas celdas tienen valor `0`. Para esas zonas, la aplicación informa que **no se conoce un límite seguro para levantamientos repetidos** y clasifica el resultado como `alto`.

### 3. Tratamiento profesional de los agravantes

La fuente normativa indica que, cuando están presentes determinados factores,
deben considerarse valores inferiores a los recomendados. Sin embargo, no se
identificaron en esa fuente coeficientes numéricos que respalden los
multiplicadores históricos configurados por la aplicación.

La decisión profesional vigente del proyecto establece que esos coeficientes no
se utilizarán. Por seguridad y trazabilidad:

- los coeficientes históricos se conservan únicamente como evidencia rechazada y
  nunca intervienen en el cálculo;
- si no hay agravantes, el motor compara el peso con el límite base;
- si hay al menos un agravante, el motor igualmente informa la clasificación
  tolerable/no tolerable obtenida con el límite base;
- la pantalla enumera los agravantes presentes y marca
  `requiere_revision_profesional`; y
- desde el resumen, el profesional puede confirmar la clasificación de tabla o
  elegir una final diferente. Si la modifica, debe registrar la justificación.

No utilices los coeficientes inactivos como si fueran una transcripción de la
Resolución 295/03.

### 4. Comparación con la tabla oficial

La aplicación calcula la relación:

`peso real / límite de comparación`

- **Tolerable / Bajo:** peso real ≤ límite oficial.
- **No tolerable / Alto:** peso real > límite oficial.
- **Alto conservador:** combinación de duración/frecuencia fuera de las Tablas 1–3, por ejemplo más de 360 lev/h.
- **No aplicable:** el factor fue desmarcado o no puede obtenerse un dato técnico válido.

Cuando existen agravantes, `calc_data.clasificacion_base_nivel` conserva el
resultado de tabla y `revision_profesional` conserva la clasificación final,
responsable, fecha, justificación y agravantes considerados.

## Validaciones y mensajes frecuentes

- Completá los cinco parámetros principales antes de calcular. Los campos del modelo admiten guardado parcial, pero la calculadora necesita valores numéricos y bandas válidas.
- No ingreses valores negativos o no finitos. El formulario y el motor aplican validaciones de dominio antes de calcular.
- La frecuencia debe ser entera. Valores superiores a 360 lev/h producen nivel `alto` por quedar fuera de las tablas implementadas.
- Si aparece **“Combinación V/H no encontrada”**, no reemplaces la selección al azar: revisá los datos y reportá un posible problema de configuración.
- Si el límite es `0`, no lo interpretes como “cero riesgo”; significa que la tabla no reconoce un límite seguro para esa combinación.
- Si existen agravantes, revisá la lista informada por el sistema y documentá en el resumen si confirmás o modificás la clasificación de tabla.
- Si solo querés corregir o completar datos, podés usar **Guardar**. El nivel se actualiza únicamente con **Guardar y calcular**.

## Interpretación y acciones

Un resultado bajo significa que el peso no supera el límite oficial de comparación. Si existen agravantes, ese resultado queda condicionado hasta que el profesional los valore; no descarta otros factores no modelados ni reemplaza la observación ergonómica integral.

Cada cálculo registra el archivo, la versión de datos, la fuente normativa y el
checksum SHA-256 exacto de la tabla utilizada. Esa evidencia permite reproducir
qué artefacto intervino aunque el archivo cambie en una versión posterior.

Un resultado alto, o una modificación profesional motivada por agravantes, requiere revisar la calidad de los datos, analizar controles y documentar la decisión. Considerá, entre otras medidas, reducir peso, frecuencia, duración o alcance; mejorar altura, agarre y estabilidad; evitar giros y posturas desfavorables; o incorporar ayudas mecánicas. La selección definitiva de medidas debe adecuarse a la tarea real.

## Referencias y advertencia profesional

- [Resolución SRT 886/2015 — texto oficial](https://www.argentina.gob.ar/normativa/nacional/norma-246272/texto)
- [Resolución MTEySS 295/2003 — texto oficial](https://www.argentina.gob.ar/normativa/nacional/resoluci%C3%B3n-295-2003-90396/texto)
- [SRT — Protocolo de Ergonomía, guía y formularios](https://www.argentina.gob.ar/srt/prevencion/publicaciones/protocolos/ergonomia)

Esta guía explica el comportamiento actual de ErgoApp. No constituye por sí sola un dictamen ergonómico ni acredita que el motor haya sido homologado por la autoridad. La medición, la elección del escenario, la interpretación normativa y la firma del informe corresponden a profesionales competentes.
