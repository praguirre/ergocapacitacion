# Evaluación de Tracción — Fuerza Sostenida

## Para qué sirve esta pantalla

Esta pantalla compara la **fuerza sostenida de tracción** con el límite de la **Tabla 4 del Anexo II** configurado para la población, altura del agarre, distancia y frecuencia seleccionadas.

La fuerza sostenida es la necesaria para **mantener el objeto en movimiento a velocidad aproximadamente constante**. El esfuerzo de arranque o aceleración corresponde a **Tracción — Fuerza Inicial**. Cuando una tarea contiene ambas fases, deben analizarse ambas.

La evaluación complementa la Planilla 2B. Sus niveles (`bajo`, `alto` o `no aplicable`) pertenecen al motor cuantitativo y no equivalen automáticamente a los niveles 1, 2 y 3 de la Planilla 1.

## Alcance

Las tablas implementadas contemplan una acción realizada por una sola persona de pie, con ambas manos y sobre un objeto situado frente al operador. La pantalla exige confirmar esas cuatro condiciones antes de calcular y las conserva en la trazabilidad.

## Antes de medir

- Usá un dinamómetro adecuado y un procedimiento reproducible.
- Medí durante el desplazamiento estable, no durante el arranque.
- Registrá la fuerza en **Newtons (N)**.
- Relevá altura, recorrido y frecuencia reales.
- Documentá superficie, pendiente, ruedas, atascamientos, velocidad y variaciones.

## Campos

### General

- **Aplicable:** en esta calculadora sí tiene efecto. Si se desmarca y se calcula, el resultado es `no aplicable` con el motivo correspondiente.
- **Observaciones:** detalle del objeto, instrumento, medición, condiciones y supuestos.

### Geometría de agarre y exposición

- **Población:** `Exclusivamente Masculina` o `Femenina o Mixta`; la opción mixta utiliza límites femeninos.
- **Altura de agarre:** baja ≈ 64 cm; media ≈ 95 cm; alta ≈ 144 cm.
- **Distancia:** hasta 2 m; >2–8 m; >8–15 m; >15–30 m; >30–45 m; >45–60 m. La clave guardada es el límite superior del rango.
- **Frecuencia:** repetición observada de la tracción.

### Fuerza sostenida

- **Fuerza n (N):** fuerza medida mientras el objeto se desplaza a velocidad aproximadamente constante.
- El texto de pantalla permite consignar una estimación en Observaciones si no hay medición. Una estimación no tiene la misma calidad que una medición instrumental; identificá método, fuente e incertidumbre y no la presentes como dato medido.

## Combinaciones disponibles

| Distancia seleccionada | Frecuencias admitidas por el motor |
|---|---|
| Hasta 2 m | 10/min; 5/min; 1/min; 1 cada 5 min; 1 cada 8 h |
| >2 a 8 m | 4/min; 1/min; 1 cada 5 min; 1 cada 8 h |
| >8 a 15 m | 2,5/min; 1/min; 1 cada 5 min; 1 cada 8 h |
| >15 a 30 m | 1/min; 1 cada 5 min; 1 cada 8 h |
| >30 a 45 m | 1/min; 1 cada 5 min; 1 cada 8 h |
| >45 a 60 m | 1 cada 2 min; 1 cada 5 min; 1 cada 8 h |

El selector filtra las frecuencias cuando cambia la distancia y el servidor vuelve a validar la combinación. Una fila fuera de tabla no puede guardarse ni calcularse.

## Procedimiento

1. Confirmá las cuatro condiciones de alcance y la aplicabilidad.
2. Seleccioná población, altura, distancia y frecuencia observadas.
3. Ingresá la fuerza sostenida en N.
4. Completá Observaciones.
5. Usá **Guardar y calcular**.
6. Revisá límite, resultado y trazabilidad.

## Cálculo e interpretación

El motor consulta `traccion_sostenida.json`:

`distancia × frecuencia × altura × población → límite en N`

- **Bajo / aceptable en la comparación:** fuerza medida ≤ límite.
- **Alto / riesgo ergonómico:** fuerza medida > límite.
- **No aplicable:** casilla Aplicable desmarcada, combinación distancia/frecuencia inexistente o error de tabla.

No existe una banda `medio` en esta calculadora. La igualdad se clasifica como `bajo`.

## Validaciones y errores

- Completá todos los parámetros cuando Aplicable esté marcado.
- La fuerza debe ser numérica, no negativa y expresarse en N.
- Si la frecuencia no corresponde al rango, el detalle enumera las claves válidas.
- No modifiques los datos reales para evitar `no aplicable`; elegí otro método o documentá la limitación.

## Referencias y advertencia profesional

- [Resolución SRT 3345/2015 — texto oficial y Anexo II](https://www.argentina.gob.ar/normativa/nacional/resoluci%C3%B3n-3345-2015-252684/texto)
- [Resolución SRT 886/2015 — Protocolo de Ergonomía](https://www.argentina.gob.ar/normativa/nacional/norma-246272/texto)
- [SRT — Protocolo de Ergonomía, guía y formularios](https://www.argentina.gob.ar/srt/prevencion/publicaciones/protocolos/ergonomia)

Los límites usados por ErgoApp están versionados en `evaluaciones/data/traccion_sostenida.json`. La conclusión y las medidas requieren revisión profesional; el resultado del software no implica homologación por la autoridad.
