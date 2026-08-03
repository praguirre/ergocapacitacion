# Evaluación de Tracción — Fuerza Inicial

## Para qué sirve esta pantalla

Esta evaluación compara la **fuerza inicial de tracción** con el límite que la aplicación obtiene de la **Tabla 3 del Anexo II** para la población, altura, distancia y frecuencia seleccionadas.

La tracción o acción de tirar orienta la fuerza hacia el cuerpo del operador. La fuerza inicial es la requerida para **poner el objeto en movimiento o acelerarlo**. La fuerza necesaria para mantener el desplazamiento se evalúa por separado en **Tracción — Fuerza Sostenida**.

Esta instancia cuantitativa complementa el factor B de la Planilla 1 y la evaluación inicial de la **Planilla 2B — Empuje y arrastre**. No convierte automáticamente su nivel `bajo` o `alto` en los niveles 1, 2 o 3 de la Planilla 1.

## Alcance

El método normativo de empuje/tracción considerado por las tablas se limita a una acción:

- realizada por una sola persona;
- de pie;
- con ambas manos;
- sobre un objeto frente al operador.

La pantalla exige confirmar esas cuatro condiciones antes de calcular y las conserva en la trazabilidad. Si no se cumplen, documentá el caso y no interpretes la tabla como directamente aplicable.

## Preparación

- Medí la fuerza de arranque con dinamómetro y un protocolo reproducible.
- Ingresá la medición en **Newtons (N)**.
- Relevá la altura efectiva del agarre, la distancia por recorrido y la frecuencia.
- Separá escenarios con diferencias relevantes de carga, recorrido o condiciones.

## Campos

### General

- **Aplicable:** si se desmarca, el motor devuelve `no aplicable` sin ejecutar la tabla. Explicá el motivo en Observaciones.
- **Observaciones:** describí objeto, equipo, dinamómetro, superficie, pendiente, estado de ruedas, técnica, variabilidad y supuestos.

### Parámetros del ensayo

- **Población:** `Exclusivamente Masculina` o `Femenina o Mixta`; la población mixta utiliza la columna femenina.
- **Altura de agarre:** baja ≈ 64 cm; media ≈ 95 cm; alta ≈ 144 cm.
- **Distancia:** hasta 2 m; >2–8 m; >8–15 m; >15–30 m; >30–45 m; >45–60 m. El rango se guarda mediante su límite superior.
- **Frecuencia:** repetición de la acción, seleccionada entre las opciones visibles.
- **Fuerza n (N):** fuerza inicial medida para comenzar o acelerar la tracción.

## Combinaciones distancia/frecuencia válidas

| Distancia seleccionada | Frecuencias admitidas por el motor |
|---|---|
| Hasta 2 m | 10/min; 5/min; 1/min; 1 cada 5 min; 1 cada 8 h |
| >2 a 8 m | 4/min; 1/min; 1 cada 5 min; 1 cada 8 h |
| >8 a 15 m | 2,5/min; 1/min; 1 cada 5 min; 1 cada 8 h |
| >15 a 30 m | 1/min; 1 cada 5 min; 1 cada 8 h |
| >30 a 45 m | 1/min; 1 cada 5 min; 1 cada 8 h |
| >45 a 60 m | 1 cada 2 min; 1 cada 5 min; 1 cada 8 h |

La interfaz filtra las frecuencias según la distancia y el servidor revalida la combinación con la Tabla 3. Una fila inexistente no puede guardarse ni calcularse.

## Procedimiento

1. Marcá las cuatro condiciones de alcance si se cumplen y confirmá que la medición corresponde a tracción inicial.
2. Seleccioná población, altura, rango de distancia y frecuencia.
3. Ingresá la fuerza en N.
4. Documentá el relevamiento.
5. Usá **Guardar** para conservar datos parciales o **Guardar y calcular** para actualizar el resultado.
6. Verificá límite, nivel y parámetros usados en la trazabilidad.

## Cálculo e interpretación

La búsqueda en `traccion_inicial.json` sigue:

`distancia × frecuencia × altura × población → límite en N`

- **Bajo / aceptable en la comparación:** fuerza medida ≤ límite.
- **Alto / riesgo ergonómico:** fuerza medida > límite.
- **No aplicable:** frecuencia no válida para la distancia o error al recuperar el límite.

La calculadora no produce nivel `medio`. Un resultado bajo no descarta condiciones adversas no representadas por los campos ni reemplaza la evaluación profesional.

### Celda 60 m / una vez cada 8 h / agarre alto / población femenina

La imagen oficial publicada muestra `1460 N`, valor discordante con las celdas
vecinas. ErgoApp conserva una corrección interna conservadora a `140 N`; no se
localizó una fe de erratas oficial. Hasta que el profesional responsable apruebe
expresamente esa sustitución, todo caso que use esa celda debe quedar señalado
para revisión y no debe atribuirse `140 N` literalmente a la resolución.

## Validaciones y errores

- Completá todos los parámetros antes de calcular, aunque el modelo admita guardarlos vacíos.
- La fuerza debe ser no negativa y estar expresada en N.
- Ante el mensaje de frecuencia no válida, elegí otra opción únicamente si representa la exposición real.
- Un error técnico de búsqueda debe reportarse; no debe resolverse alterando los datos observados.
- El nivel solo se renueva con **Guardar y calcular**.

## Referencias y advertencia profesional

- [Resolución SRT 3345/2015 — texto oficial y Anexo II](https://www.argentina.gob.ar/normativa/nacional/resoluci%C3%B3n-3345-2015-252684/texto)
- [Resolución SRT 886/2015 — Protocolo de Ergonomía](https://www.argentina.gob.ar/normativa/nacional/norma-246272/texto)
- [SRT — Protocolo de Ergonomía, guía y formularios](https://www.argentina.gob.ar/srt/prevencion/publicaciones/protocolos/ergonomia)

ErgoApp toma los valores de `evaluaciones/data/traccion_inicial.json`. La herramienta asiste el análisis, pero no constituye por sí sola un dictamen ni acredita homologación legal.
