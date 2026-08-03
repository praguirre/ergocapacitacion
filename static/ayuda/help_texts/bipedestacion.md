# Ayuda — Evaluación de Bipedestación

Esta pantalla permite realizar la evaluación posterior del factor **Bipedestación** para la tarea analizada. Complementa a la **Planilla 2D de la Resolución SRT 886/15**, que funciona como identificación inicial: cuando esa planilla indica que no puede presumirse un riesgo tolerable, el botón **Realizar Evaluación** conduce a este formulario.

El resultado se obtiene mediante el cribado parametrizado actualmente en la aplicación. Debe ser revisado por un profesional competente y no reemplaza el análisis integral del puesto, la valoración clínica ni las obligaciones documentales del protocolo.

---

## 1. Qué información conviene reunir

Antes de completar el formulario:

1. Identifique con precisión la tarea y el período representativo observado.
2. Mida las **horas totales de pie por día** y el **tramo continuo más representativo o desfavorable**, sin posibilidad efectiva de sentarse.
3. Estime la movilidad real en metros recorridos por hora.
4. Observe condiciones del piso, calzado, manipulación de cargas y posturas sostenidas.
5. Consulte y documente síntomas asociados, sin realizar diagnósticos médicos.
6. Verifique en el puesto los controles existentes; no registre como control una medida solamente prevista.

Use **Observaciones** para dejar constancia de la tarea, turno, fecha, fuente de los tiempos, criterio de medición y cualquier supuesto.

---

## 2. Campos del formulario

### General

| Campo | Cómo completarlo |
|---|---|
| **Aplicable** | Manténgalo marcado cuando esta evaluación corresponda a la tarea. Si el factor no aplica, desmárquelo, justifique el motivo en **Observaciones** y use **Guardar**. Consulte la advertencia de la sección 7. |
| **Observaciones** | Describa la tarea, trabajador o grupo observado, turno, pausas, alternancia postural, mediciones y particularidades relevantes. |

### Duración y movilidad

| Campo | Unidad / opción | Criterio de carga |
|---|---|---|
| **Horas de pie total** | horas/día | Suma diaria de los períodos en que la persona permanece de pie. Admite incrementos de 0,25 h. |
| **Tiempo continuo min** | minutos | Duración del período continuo de pie que se evalúa. Ingrese minutos enteros. |
| **Movilidad tipo** | `Estática/Restringida` o `Con deambulación` | Seleccione la condición que represente la tarea observada. |
| **Movilidad m por h** | m/h | Se muestra para tareas con deambulación. Registre la distancia recorrida durante una hora representativa. |

No confunda el **tiempo total diario** con el **tiempo continuo**. El primero interviene en una regla adicional de acumulación diaria; el segundo determina la fila principal de la matriz.

### Factores agravantes

Marque todos los que estén efectivamente presentes durante el período evaluado:

| Campo visible | Significado operativo en el cálculo |
|---|---|
| **Manipula cargas mayores 2 kg** | Manipulación de cargas de más de 2 kg durante la bipedestación. |
| **Ambiente caluroso** | Presencia de condición térmica desfavorable que corresponda documentar. |
| **Piso duro** | Superficie rígida durante la permanencia de pie. |
| **Superficie irregular** | Desniveles o irregularidades que afectan el apoyo. |
| **Piso resbaladizo** | Superficie con riesgo de deslizamiento. |
| **Calzado inadecuado** | Calzado que no brinda condiciones apropiadas de apoyo para la tarea. |
| **Tronco inclinado** | Inclinación sostenida o habitual del tronco. |
| **Brazos elevados** | Trabajo sostenido con brazos elevados. |
| **Cuello giro inclin** | Giro o inclinación sostenida del cuello. |

Cada agravante marcado suma una unidad al conteo bruto. La aplicación agrupa luego el conteo ajustado en **0**, **1** o **2 o más** agravantes.

### Síntomas

**Síntomas (JSON)** requiere una lista JSON válida. Escriba los elementos entre comillas y separados por comas, por ejemplo:

```json
["pesadez_piernas", "calambres", "dolor_lumbar"]
```

No escriba una lista en lenguaje natural ni omita las comillas. Si no se reportaron síntomas, use:

```json
[]
```

En **Síntomas frecuencia** seleccione `Diaria`, `Semanal` u `Ocasional`. Para el motor actual, una lista no vacía junto con frecuencia **diaria o semanal** fuerza el resultado a riesgo **alto**. La frecuencia ocasional queda registrada, pero no activa esa regla.

La carga de síntomas sirve para el cribado y la trazabilidad; no sustituye la intervención del Servicio de Medicina del Trabajo.

### Controles existentes

El formulario ofrece:

- **Alfombra antifatiga**
- **Banqueta/alternar sedente**
- **Apoyo pie (footrest)**
- **Rotación/micropausas**

En la configuración actual, cada control reconocido y efectivamente registrado resta una unidad al conteo de agravantes, sin permitir que el resultado sea menor que cero. Esta reducción es aritmética y no demuestra por sí sola la eficacia del control.

Después de calcular, abra **Ver trazabilidad (calc_data)** y confirme que las medidas aparezcan en `controles.aplicados`. Si una selección no figura allí, no presuma que produjo una reducción.

## 3. Procedimiento recomendado

1. Confirme que la evaluación corresponde al factor identificado en la Planilla 2D.
2. Complete ambos tiempos con mediciones representativas y coherentes entre sí.
3. Seleccione el tipo de movilidad y, si corresponde, mida los metros recorridos por hora.
4. Marque únicamente los agravantes observados y deje evidencia en **Observaciones**.
5. Registre síntomas en formato JSON y su frecuencia.
6. Marque solamente controles ya implementados y verificados.
7. Use **Guardar y calcular** para actualizar el nivel y la trazabilidad.
8. Revise el nivel mostrado, el detalle de cálculo y la coherencia con la observación del puesto.

**Guardar** conserva datos sin ejecutar nuevamente el motor. Si modifica entradas que afectan el resultado, use **Guardar y calcular**; de lo contrario puede permanecer visible un resultado anterior.

---

## 4. Cómo calcula la aplicación

### 4.1 Duración continua efectiva

Por defecto:

```text
tiempo continuo efectivo = tiempo continuo ingresado
```

Si se selecciona **Con deambulación** y la movilidad es **mayor que 100 m/h**, el motor aplica:

```text
tiempo continuo efectivo = tiempo continuo ingresado × 0,7
```

La reducción puede desplazar el caso a una banda de duración menor. Es una regla interna parametrizada del cribado, no una exención normativa.

### 4.2 Bandas usadas por el código actual

| Tiempo continuo efectivo | Fila de matriz |
|---:|---|
| desde 0 y menos de 120 min | `< 2 h` |
| desde 120 y menos de 240 min | `2 a < 4 h` |
| 240 min o más | `≥ 4 h` |

Los intervalos son semiabiertos (`[mínimo, máximo)`), por lo que cada valor de frontera pertenece a una sola banda.

### 4.3 Conteo ajustado de agravantes

El motor:

1. cuenta los agravantes marcados;
2. resta una unidad por cada control reconocido que esté persistido;
3. limita el conteo mínimo a cero;
4. ubica el resultado en la columna `0`, `1` o `2 o más`.

### 4.4 Matriz de clasificación

| Duración efectiva | 0 agravantes | 1 agravante | 2 o más agravantes |
|---|---|---|---|
| menos de 120 min | Bajo | Bajo | Medio |
| desde 120 y menos de 240 min | Bajo | Medio | Alto |
| 240 min o más | Medio | Alto | Alto |

Luego se aplican dos reglas:

- si las **horas totales de pie son 4 h/día o más** y la matriz dio `bajo`, el resultado sube al menos a `medio`;
- si existen síntomas con frecuencia **diaria o semanal**, el resultado es `alto`, con prioridad sobre la matriz.

La trazabilidad conserva duración bruta y efectiva, movilidad, agravantes, controles, banda aplicada, reglas adicionales y sugerencias de controles aún no registrados.

---

## 5. Interpretación del resultado

| Nivel de la aplicación | Lectura técnica orientativa |
|---|---|
| **Bajo** | La combinación cargada queda en la zona inferior del cribado actual. Mantenga controles y verifique que los datos sean representativos. |
| **Medio** | Se requiere revisión profesional, mejora o seguimiento según la exposición y el contexto del puesto. |
| **Alto** | Requiere atención prioritaria, evaluación profesional y definición documentada de medidas de control. |
| **No aplicable** | Debe utilizarse solo cuando el método no corresponda y la razón esté justificada. |

Estos niveles no se deben trasladar automáticamente a los niveles 1, 2 o 3 de la Planilla 1 sin la validación del profesional responsable y la integración con el protocolo completo.

---

## 6. Comprobaciones antes de aceptar el resultado

- Los tiempos son no negativos y pertenecen al mismo escenario observado.
- El tiempo continuo no supera las horas totales convertidas a minutos, salvo que exista una explicación documentada.
- Los metros por hora provienen de una medición o estimación trazable.
- Los síntomas forman una lista JSON válida y tienen frecuencia consignada.
- Los controles marcados existen en el puesto y aparecen en la trazabilidad.
- La evaluación fue recalculada después del último cambio.
- El resultado es consistente con la tarea y con la Planilla 2D.

---

## 7. Validaciones, errores y comportamiento actual

- Los campos numéricos aceptan valores no negativos en la interfaz, pero no existe una validación cruzada automática entre horas totales y tiempo continuo.
- Los borradores pueden quedar incompletos, pero **Guardar y calcular** exige duración total, duración continua y movilidad; si corresponde deambulación, también exige metros por hora.
- `Síntomas (JSON)` debe contener JSON válido; el formulario informa error si la sintaxis no puede analizarse.
- Si desmarca **Aplicable**, el contrato común del motor devuelve `no aplicable` sin ejecutar la fórmula específica.
- La Planilla 2D describe como deambulación escasa una distancia de hasta 100 m/h. Por eso el motor no atenúa en 100 m/h exactos y comienza la reducción únicamente por encima de ese valor.
- Si la selección de controles no aparece en `controles.aplicados`, el motor no la tuvo en cuenta.

Ante un dato faltante, una combinación incoherente o una trazabilidad inesperada, no use el nivel como conclusión final: corrija la carga o solicite revisión técnica.

---

## 8. Referencias y advertencia profesional

- [Resolución SRT 886/2015 — texto oficial](https://www.argentina.gob.ar/normativa/nacional/norma-246272/texto)
- [Resolución MTEySS 295/2003 — texto oficial](https://www.argentina.gob.ar/normativa/nacional/resoluci%C3%B3n-295-2003-90396/texto)
- [SRT — Protocolo de Ergonomía, guías y formularios](https://www.argentina.gob.ar/srt/prevencion/publicaciones/protocolos/ergonomia)
- Configuración interna consultada por la aplicación: `evaluaciones/data/bipedestacion_limites.json`.

La matriz y sus reducciones constituyen un **cribado v1 implementado en la aplicación**. No debe afirmarse que el motor esté homologado, certificado o que reproduzca por sí solo una determinación legal. La evaluación final, la selección de medidas y la firma del protocolo corresponden a profesionales competentes dentro de sus incumbencias.
