# Evaluación de Transporte Manual de Cargas

## Para qué sirve esta pantalla

Esta evaluación calcula la **masa acumulada transportada durante la jornada** y la compara con un límite dependiente de la distancia de cada traslado.

Se vincula con el factor C de la Planilla 1 y se utiliza después de la evaluación inicial de la **Planilla 2C — Transporte manual**, cuando corresponde profundizar el análisis. La Planilla 2C y esta calculadora son etapas relacionadas, pero no idénticas: el nivel cuantitativo no se copia automáticamente como nivel 1, 2 o 3 de la Planilla 1.

## Alcance del método

La comparación implementada corresponde al traslado manual horizontal de una carga:

- de **2 kg o más**;
- sostenida en vilo, sin soporte externo;
- sobre superficie plana y horizontal;
- a velocidad moderada de **0,5 a 1,0 m/s**;
- durante una jornada de **8 horas**.

Estas condiciones se muestran como casillas. Si alguna no se cumple, la calculadora devuelve `no aplicable`; eso no significa “sin riesgo”, sino que la tabla implementada no corresponde a la situación.

## Antes de completar

- Determiná la masa por ciclo con balanza o dato técnico verificable.
- Medí la distancia lineal recorrida con la carga en cada traslado.
- Contá el total de traslados con carga durante la jornada evaluada.
- Si existen masas o recorridos diferentes, separá escenarios o documentá claramente el criterio de agregación.
- Registrá carga, agarre, recorrido, pausas, variabilidad y fuente de datos en Observaciones.

## Campos de la pantalla

### Condiciones de aplicación

En la interfaz, una casilla **marcada significa “Sí”** y una casilla sin marcar se procesa como **“No”**:

- tarea en plano horizontal;
- jornada evaluada de 8 horas;
- velocidad de marcha entre 0,5 y 1,0 m/s;
- superficie plana.

Las cuatro deben estar marcadas para aplicar el cálculo.

### Parámetros de transporte

- **Masa kg:** masa transportada en cada ciclo, en kg. El mínimo evaluable validado por el formulario es 2,00 kg.
- **Distancia m:** metros recorridos por traslado. Debe ser al menos 1,0 m; admite una cifra decimal.
- **Frecuencia jornada:** cantidad total de traslados con carga en la jornada. Debe ser un entero positivo.

### Aplicabilidad y notas

- **Aplicable:** indica si el factor corresponde. Si se desmarca, el contrato común del motor devuelve `no aplicable`; además, las cuatro condiciones anteriores deben cumplirse para aplicar el método.
- **Observaciones:** documentá datos, mediciones, escenarios y cualquier condición no cubierta.

## Procedimiento

1. Confirmá el factor C y la necesidad de evaluación específica surgida de la Planilla 2C.
2. Marcá cada condición de aplicación que efectivamente se cumpla.
3. Ingresá masa, distancia por traslado y cantidad de traslados por jornada.
4. Completá Observaciones.
5. Usá **Guardar** para conservar un relevamiento parcial.
6. Usá **Guardar y calcular** para actualizar el nivel.
7. Revisá masa acumulada, límite, condiciones y trazabilidad.

## Cómo calcula la aplicación

### Masa acumulada

`Masa acumulada (kg/jornada) = masa por traslado (kg) × cantidad de traslados por jornada`

La aplicación no agrega automáticamente viajes de retorno ni combina diferentes cargas. La frecuencia ingresada debe representar el total que corresponda a la situación evaluada.

### Límites oficiales por distancia

La Resolución SRT 3345/2015 contiene cinco filas discretas, no bandas
extrapolables:

| Distancia de tabla | Frecuencia máxima | kg/min | kg/h | kg/8 h |
|---:|---:|---:|---:|---:|
| 1 m | 8/min | 120 | 7.200 | 10.000 |
| 2 m | 5/min | 75 | 4.500 | 10.000 |
| 4 m | 4/min | 60 | 3.000 | 10.000 |
| 10 m | 2/min | 30 | 1.500 | 10.000 |
| 20 m | 1/min | 15 | 750 | 6.000 |

Para una distancia intermedia, la aplicación selecciona conservadoramente la
primera fila cuya distancia sea mayor o igual que la medida. Por ejemplo, 3 m
usa la fila de 4 m y 12 m usa la de 20 m. Una distancia superior a 20 m queda
fuera de la tabla y no se extrapola.

La columna de frecuencia corresponde al máximo de referencia para una masa de
15 kg; no es un límite autónomo aplicable a cualquier peso. La evaluación compara
el producto masa × frecuencia real con los máximos de kg/min, kg/h y kg/8 h.
Por eso debés registrar el minuto y la hora de mayor exposición además del total
de la jornada. La aplicación usa esos máximos observados y no promedios, que
podrían ocultar picos de carga.

### Resultado

- **Bajo:** ninguna masa acumulada supera los límites por minuto, hora o jornada.
- **Alto:** al menos uno de los tres límites es superado.
- **No aplicable:** alguna condición de aplicación está sin marcar, masa <2 kg, distancia <1 m, frecuencia ≤0 o distancia superior a 20 m.

La calculadora es binaria y no produce nivel `medio`. La igualdad con el límite se clasifica como `bajo`.

## Validaciones y mensajes frecuentes

- **“Según Res. 3345/15, el peso mínimo evaluable es 2,00 kg”**: revisá la masa; una carga menor queda fuera de este método.
- **“La distancia por viaje debe ser ≥ 1,0 m”**: corregí la medición o tratá la situación con otro criterio.
- **“La frecuencia debe ser un entero positivo”**: ingresá el total de traslados de la jornada.
- **“Falta el máximo … observado”**: medí el minuto y la hora de mayor exposición; no uses el promedio de la jornada.
- **“Frecuencias incoherentes”**: verificá que máximo/minuto ≤ máximo/hora ≤ total/jornada.
- **“Una o más condiciones … no se cumplen”**: la tabla no aplica; revisá cuáles casillas quedaron sin marcar.
- **“No hay límite definido para el tramo de distancia”**: la tabla oficial termina en 20 m; no extrapoles un valor automáticamente.
- Un resultado `no aplicable` no equivale a riesgo bajo.

## Interpretación y acciones

El nivel bajo indica que la masa acumulada no supera el límite cargado para ese tramo y bajo las condiciones declaradas. No evalúa por sí solo agarre deficiente, carga inestable, posturas, obstáculos, síntomas ni otros factores de la Planilla 2C.

Ante un nivel alto, revisá primero los datos y luego analizá medidas como reducir masa o frecuencia, acortar recorridos, rediseñar el flujo, mejorar agarres o incorporar ayudas. La selección debe basarse en la tarea real y quedar documentada en las planillas de medidas y seguimiento.

## Referencias y advertencia profesional

- [Resolución SRT 3345/2015 — texto oficial y Anexo I](https://www.argentina.gob.ar/normativa/nacional/resoluci%C3%B3n-3345-2015-252684/texto)
- [Resolución SRT 886/2015 — Protocolo de Ergonomía](https://www.argentina.gob.ar/normativa/nacional/norma-246272/texto)
- [SRT — Protocolo de Ergonomía, guía y formularios](https://www.argentina.gob.ar/srt/prevencion/publicaciones/protocolos/ergonomia)

Los límites efectivos están versionados en `evaluaciones/data/transporte_limites.json` y fueron cotejados con la imagen oficial del Anexo I, Tabla 1. Esta ayuda describe el cálculo implementado y no reemplaza la evaluación integral, la interpretación normativa ni la firma de un profesional competente. El software no debe presentarse como homologado por la autoridad.
