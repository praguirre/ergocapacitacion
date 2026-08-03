# Ayuda — Resumen de la Evaluación Cuantitativa

Esta pantalla reúne las evaluaciones cuantitativas de la evaluación ergonómica
actual. Permite identificar obligaciones pendientes, revisar resultados
vigentes y conocer cómo se forma el resultado global.

El resumen complementa las Planillas 1–4. Los niveles cuantitativos `bajo`,
`medio`, `alto` y `no aplicable` no se convierten automáticamente en los
niveles 1, 2 y 3 de la Planilla 1.

## Factores requeridos

Un factor queda marcado como **Requerido** cuando ingresás mediante
**Realizar Evaluación** desde una Planilla 2. Solo esos factores intervienen en
el cierre y en el resultado global.

Si un factor requerido todavía no está vigente, la fila se destaca y el
resumen enumera qué bloquea el cierre. Los demás factores permanecen
disponibles, pero no alteran la conclusión global.

## Estados operativos

| Estado | Significado |
|---|---|
| **Sin iniciar** | El factor es requerido, pero todavía no posee registro. |
| **Borrador** | Existen datos guardados sin un cálculo vigente. |
| **Requiere recálculo** | Se modificaron entradas después del último cálculo. |
| **Calculado** | Existe un resultado vigente pendiente de revisión profesional. |
| **No aplicable** | El motor documentó que el método no corresponde o no puede emitir clasificación. También requiere revisión. |
| **Revisado** | El usuario autenticado confirmó el resultado vigente y quedaron registradas identidad y fecha. |

Guardar o recalcular reemplaza la evidencia de revisión anterior. Todo resultado
modificado debe revisarse nuevamente.

## Cómo revisar

1. Abrí **Editar** y verificá entradas, aplicabilidad, observaciones y
   trazabilidad.
2. Si modificás un dato, utilizá **Guardar y calcular**.
3. Volvé al resumen.
4. Presioná **Revisar** únicamente si el resultado vigente representa la tarea.

La revisión queda asociada al usuario autenticado. No reemplaza las firmas
profesionales exigibles en el protocolo o informe.

## Regla global

El resultado final es el nivel más alto entre los factores requeridos vigentes:
`alto` prevalece sobre `medio`, y `medio` sobre `bajo`.

- Un factor requerido sin iniciar, en borrador o desactualizado bloquea el
  cierre.
- Mientras existan resultados vigentes sin revisar, el nivel mostrado es
  **preliminar**.
- El resultado se vuelve **final** y la evaluación queda completada solo cuando
  todos los factores requeridos están revisados.
- Si todos los factores requeridos revisados son no aplicables, el resultado
  global es `no aplicable`.
- Si todavía no hay factores requeridos, no se calcula un resultado global.

La regla, los bloqueantes, la lista pendiente de revisión y los contadores se
guardan en `RiskEvaluation.resumen_json` para auditoría.

## PDF

**Generar PDF** crea una copia del estado actual. Antes de utilizarla:

- confirmá que no existan borradores o resultados desactualizados;
- verificá si el nivel es preliminar o final;
- revisá los factores no aplicables y sus motivos; y
- comprobá que la evaluación corresponda al establecimiento y puesto correctos.

El PDF es un documento de apoyo. La interpretación y firma corresponden a los
profesionales competentes.
