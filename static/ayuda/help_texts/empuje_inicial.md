# Evaluación de Empuje — Fuerza Inicial

## Para qué sirve esta pantalla

Esta evaluación compara la **fuerza inicial de empuje medida en Newtons** con el límite que la aplicación obtiene de la **Tabla 1 del Anexo II** configurada para:

- población de referencia;
- altura del agarre;
- distancia recorrida;
- frecuencia de la acción.

La fuerza inicial es la necesaria para **poner en movimiento o acelerar** el objeto. No es la fuerza requerida para mantenerlo desplazándose: esa condición se evalúa en **Empuje — Fuerza Sostenida**.

Esta pantalla profundiza el factor B identificado en la Planilla 1 y evaluado inicialmente mediante la **Planilla 2B — Empuje y arrastre**. Su resultado cuantitativo no sustituye automáticamente el nivel 1, 2 o 3 de la Planilla 1.

## Alcance del método

Los límites de empuje/tracción de la Resolución SRT 3345/15 contemplan acciones realizadas:

- por una sola persona;
- de pie;
- con ambas manos;
- sobre un objeto situado frente al operador.

La pantalla exige confirmar las cuatro condiciones antes de calcular y las conserva en la trazabilidad. Si la tarea se realiza sentado, con una sola mano, por varias personas o fuera de ese alcance, documentalo y seleccioná un método profesional adecuado.

## Antes de completar

- Medí la fuerza de arranque con un dinamómetro apto, calibrado y usado con un procedimiento reproducible.
- Registrá la fuerza en **Newtons (N)**. No ingreses un valor expresado en kgf como si fueran Newtons.
- Medí la altura real del punto de aplicación de la fuerza y la distancia de cada recorrido.
- Determiná la frecuencia sobre un período representativo.
- Si las condiciones cambian de forma relevante, realizá evaluaciones separadas.

## Campos de la pantalla

### General

- **Aplicable:** si se desmarca, el motor devuelve `no aplicable` sin ejecutar la tabla. Explicá el motivo en Observaciones.
- **Observaciones:** consigná objeto/equipo, instrumento, fecha o estado de calibración, superficie, ruedas, pendiente, técnica, variabilidad y cualquier supuesto.

### Parámetros del ensayo

- **Población:**
  - `Exclusivamente Masculina`;
  - `Femenina o Mixta`. Para una población mixta se usa la columna femenina configurada.
- **Altura de agarre:**
  - baja: aproximadamente 64 cm (nudillos/muslos);
  - media: aproximadamente 95 cm (cintura/codo);
  - alta: aproximadamente 144 cm (hombros/pecho).
- **Distancia:** la opción representa un rango y el motor guarda su límite superior:
  - hasta 2 m;
  - más de 2 y hasta 8 m;
  - más de 8 y hasta 15 m;
  - más de 15 y hasta 30 m;
  - más de 30 y hasta 45 m;
  - más de 45 y hasta 60 m.
- **Frecuencia:** elegí una de las opciones del selector según la exposición observada.
- **Fuerza n (N):** pico o fuerza representativa requerida para iniciar/acelerar el movimiento, medida con dinamómetro.

## Combinaciones de distancia y frecuencia disponibles

El selector filtra las frecuencias según la distancia. El servidor vuelve a validar la combinación contra el mismo archivo de la Tabla 1:

| Distancia seleccionada | Frecuencias admitidas por el motor |
|---|---|
| Hasta 2 m | 10/min; 5/min; 1/min; 1 cada 5 min; 1 cada 8 h |
| >2 a 8 m | 4/min; 1/min; 1 cada 5 min; 1 cada 8 h |
| >8 a 15 m | 2,5/min; 1/min; 1 cada 5 min; 1 cada 8 h |
| >15 a 30 m | 1/min; 1 cada 5 min; 1 cada 8 h |
| >30 a 45 m | 1/min; 1 cada 5 min; 1 cada 8 h |
| >45 a 60 m | 1 cada 2 min; 1 cada 5 min; 1 cada 8 h |

No selecciones una frecuencia distinta solo para obtener un resultado. Una combinación fuera de tabla no puede guardarse ni calcularse; si la exposición real no coincide, el método implementado no puede evaluarla directamente.

## Procedimiento

1. Marcá las cuatro condiciones de alcance únicamente si se cumplen.
2. Seleccioná población, altura, rango de distancia y frecuencia reales.
3. Ingresá la fuerza inicial en N.
4. Documentá medición y particularidades en Observaciones.
5. Usá **Guardar** para conservar datos sin recalcular.
6. Usá **Guardar y calcular** para buscar el límite y actualizar el nivel.
7. Revisá la fuerza medida, el límite y los parámetros guardados en la trazabilidad.

## Cálculo e interpretación

La aplicación consulta `empuje_inicial.json` siguiendo:

`distancia × frecuencia × altura × población → límite en N`

Luego compara:

- **Bajo:** fuerza medida ≤ límite.
- **Alto:** fuerza medida > límite.
- **No aplicable:** la combinación distancia/frecuencia no existe o no puede recuperarse un valor de tabla.

Esta calculadora es binaria: no genera nivel `medio`. La igualdad con el límite se clasifica como `bajo`.

Un nivel bajo solo indica cumplimiento de la comparación realizada. No elimina riesgos debidos a postura, agarre, aceleraciones bruscas, ruedas o superficie defectuosas, pendiente, ambiente u otras condiciones no capturadas por los campos.

## Validaciones y errores frecuentes

- Aunque el formulario permite guardar campos parciales, completá todos los parámetros antes de calcular.
- La fuerza debe ser un número no negativo expresado en N.
- Si aparece **“La combinación de … y frecuencia seleccionada no existe en la Tabla 1”**, revisá la tabla de combinaciones anterior.
- Si aparece un error de búsqueda, no cambies población o altura arbitrariamente; verificá los datos y reportá el problema.
- El resultado se actualiza con **Guardar y calcular**, no con un guardado simple.

## Referencias y advertencia profesional

- [Resolución SRT 3345/2015 — texto oficial y Anexo II](https://www.argentina.gob.ar/normativa/nacional/resoluci%C3%B3n-3345-2015-252684/texto)
- [Resolución SRT 886/2015 — Protocolo de Ergonomía](https://www.argentina.gob.ar/normativa/nacional/norma-246272/texto)
- [SRT — Protocolo de Ergonomía, guía y formularios](https://www.argentina.gob.ar/srt/prevencion/publicaciones/protocolos/ergonomia)

Los valores efectivos usados por ErgoApp están versionados en `evaluaciones/data/empuje_inicial.json`. Esta guía describe esa implementación; no constituye un dictamen profesional ni una certificación u homologación legal del motor.
