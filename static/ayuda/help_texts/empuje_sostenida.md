# Evaluación de Empuje — Fuerza Sostenida

## Para qué sirve esta pantalla

Esta evaluación compara la **fuerza sostenida de empuje** con el límite que la aplicación obtiene de la **Tabla 2 del Anexo II** según población, altura de agarre, distancia y frecuencia.

La fuerza sostenida es la necesaria para **mantener el objeto en movimiento a una velocidad aproximadamente constante**. No es el pico requerido para arrancarlo o acelerarlo; ese valor debe registrarse en **Empuje — Fuerza Inicial**. En una misma tarea puede ser necesario completar ambas evaluaciones.

La pantalla complementa la evaluación inicial de la **Planilla 2B — Empuje y arrastre**. El nivel cuantitativo de esta pantalla no se traslada automáticamente a los niveles 1, 2 y 3 de la Planilla 1.

## Alcance del método

Los límites implementados corresponden a una acción realizada por una persona de pie, con ambas manos, sobre un objeto situado frente al operador. La pantalla exige confirmar esas cuatro condiciones antes de calcular y las conserva en la trazabilidad.

Si se empuja sentado, con una mano, entre varias personas o en otra condición fuera del alcance, documentá la situación y aplicá un método profesional apropiado.

## Preparación de la medición

- Utilizá un dinamómetro apto y un procedimiento reproducible.
- Medí la fuerza mientras el objeto ya se desplaza en régimen estable.
- Registrá el valor en **Newtons (N)**; no cargues kgf como si fueran N.
- Relevá altura, recorrido y frecuencia reales.
- Describí superficie, pendiente, ruedas, atascamientos, velocidad y variabilidad en Observaciones.

## Campos de la pantalla

### General

- **Aplicable:** si se desmarca, el motor devuelve `no aplicable` sin ejecutar la tabla. Dejá trazado el motivo.
- **Observaciones:** fuente de datos, instrumento, condiciones de ensayo, variaciones y supuestos.

### Parámetros del ensayo

- **Población:** `Exclusivamente Masculina` o `Femenina o Mixta`. La opción mixta usa los límites femeninos configurados.
- **Altura de agarre:** baja ≈ 64 cm, media ≈ 95 cm o alta ≈ 144 cm.
- **Distancia:** hasta 2 m; >2–8 m; >8–15 m; >15–30 m; >30–45 m; >45–60 m. El motor usa el límite superior del rango como clave.
- **Frecuencia:** repetición observada de la acción.
- **Fuerza n (N):** fuerza sostenida medida durante el desplazamiento a velocidad aproximadamente constante.

## Combinaciones disponibles

| Distancia seleccionada | Frecuencias admitidas por el motor |
|---|---|
| Hasta 2 m | 10/min; 5/min; 1/min; 1 cada 5 min; 1 cada 8 h |
| >2 a 8 m | 4/min; 1/min; 1 cada 5 min; 1 cada 8 h |
| >8 a 15 m | 2,5/min; 1/min; 1 cada 5 min; 1 cada 8 h |
| >15 a 30 m | 1/min; 1 cada 5 min; 1 cada 8 h |
| >30 a 45 m | 1/min; 1 cada 5 min; 1 cada 8 h |
| >45 a 60 m | 1 cada 2 min; 1 cada 5 min; 1 cada 8 h |

El selector filtra las frecuencias al cambiar la distancia. El servidor valida nuevamente la combinación contra la tabla e impide guardar o calcular una fila inexistente.

## Procedimiento

1. Confirmá las cuatro condiciones de alcance y que estás midiendo fuerza sostenida, no inicial.
2. Seleccioná población, altura, rango de distancia y frecuencia.
3. Ingresá la fuerza sostenida en N.
4. Documentá el método de medición.
5. Presioná **Guardar y calcular**.
6. Revisá el valor medido, el límite aplicable, el nivel y la trazabilidad.

## Cálculo e interpretación

El motor consulta `empuje_sostenida.json`:

`distancia × frecuencia × altura × población → límite en N`

- **Bajo / Aceptable en la comparación:** fuerza medida ≤ límite.
- **Alto / Riesgo ergonómico:** fuerza medida > límite.
- **No aplicable:** no existe la combinación distancia/frecuencia o se produce un error de recuperación de tabla.

No se genera nivel `medio`. La igualdad con el límite se clasifica como `bajo`.

La evaluación no calcula por sí sola el efecto de pendientes, aceleraciones, impactos, agarre unilateral, mala condición de ruedas u otros factores. Esos aspectos deben integrar la conclusión profesional.

## Validaciones y mensajes frecuentes

- Completá todos los parámetros antes de calcular; el formulario admite guardado parcial.
- La fuerza debe ser numérica, no negativa y estar expresada en N.
- Si la frecuencia no aplica a la distancia, el detalle informa las claves válidas para ese rango.
- **Guardar** conserva los datos; **Guardar y calcular** actualiza el nivel.

## Referencias y advertencia profesional

- [Resolución SRT 3345/2015 — texto oficial y Anexo II](https://www.argentina.gob.ar/normativa/nacional/resoluci%C3%B3n-3345-2015-252684/texto)
- [Resolución SRT 886/2015 — Protocolo de Ergonomía](https://www.argentina.gob.ar/normativa/nacional/norma-246272/texto)
- [SRT — Protocolo de Ergonomía, guía y formularios](https://www.argentina.gob.ar/srt/prevencion/publicaciones/protocolos/ergonomia)

Los límites que usa la aplicación están versionados en `evaluaciones/data/empuje_sostenida.json`. La clasificación debe ser revisada por un profesional competente y no implica homologación del software por la autoridad.
