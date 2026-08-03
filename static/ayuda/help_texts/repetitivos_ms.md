# Ayuda — Movimientos Repetitivos de Miembros Superiores (NAM)

Esta pantalla evalúa una tarea repetitiva de miembros superiores mediante el método **Nivel de Actividad Manual (NAM)** y la **Fuerza Pico Normalizada (FPN)**, representada en la interfaz por categorías de Borg CR-10.

Es la evaluación posterior vinculada a la **Planilla 2E**. Esa planilla identifica inicialmente tareas cíclicas de extremidades superiores y determina cuándo corresponde profundizar el análisis mediante **Realizar Evaluación**.

El cálculo posiciona el punto `(NAM, FPN)` respecto del **Límite de Acción (LA)** y del **Valor Límite Umbral (VLU)** definidos en el archivo de configuración del proyecto. El resultado debe ser revisado por un profesional competente y no reemplaza el protocolo completo.

---

## 1. Preparación de la observación

Antes de cargar datos:

1. Defina la tarea y el ciclo de trabajo que representa la exposición.
2. Observe varios ciclos y considere variaciones previsibles de ritmo, pausas y fuerza.
3. Determine si se cumplen las condiciones de aplicabilidad que el motor exige: **monotarea** y al menos **4 h/día**.
4. Asigne NAM mediante observación técnica de actividad y pausas.
5. Obtenga el esfuerzo pico con la escala Borg CR-10 y aplique la categoría conservadora prevista por el formulario.
6. Registre agravantes y describa el criterio en **Observaciones**.

Si existen exposiciones diferentes por mano, turno, producto o fase, no las mezcle sin justificar. Documente cuál fue la condición seleccionada.

---

## 2. Campos del formulario

### General

| Campo | Unidad / opción | Cómo completarlo |
|---|---|---|
| **Aplicable** | Sí/No | Manténgalo marcado cuando el método corresponda. Si no aplica, desmárquelo, justifique en **Observaciones** y use **Guardar**. Consulte la sección 7. |
| **Horas día** | h/día | Tiempo total diario dedicado a la tarea repetitiva. La interfaz admite incrementos de 0,25 h. |
| **Observaciones** | texto | Identifique tarea, ciclo, mano o lado evaluado, turno, pausas, fuente de los datos y criterio de selección de NAM/FPN. |

### Monotarea

El campo **Monotarea** es una condición de aplicabilidad obligatoria para el motor actual. Si no está marcado, el resultado será `no_aplicable`, aunque se hayan completado NAM y FPN.

Marque esta opción solo cuando la tarea observada reúna el criterio técnico que el evaluador utiliza para aplicar NAM. La aplicación no deduce esta condición automáticamente desde la Planilla 2E.

### Nivel de Actividad Manual — eje X

El formulario guarda valores canónicos pares. Seleccione la descripción que mejor represente la combinación observada de movimientos, esfuerzos y pausas:

| Valor guardado | Opción mostrada |
|---:|---|
| 0 | `0/1` — Sin manejo manual la mayor parte del tiempo; sin esfuerzos regulares |
| 2 | `2/3` — Pausas constantes, destacadas, largas o movimientos muy lentos |
| 4 | `4/5` — Movimientos/esfuerzos lentos o fijos; pausas breves frecuentes |
| 6 | `6/7` — Movimientos o esfuerzo fijo; pausas infrecuentes |
| 8 | `8/9` — Movimientos/esfuerzos rápidos y fijos, sin pausas regulares |
| 10 | `10` — Movimiento rápido y fijo, difícil de mantener, o esfuerzos continuos |

NAM es una tasación del observador. No lo confunda con cantidad de acciones por minuto ni con la duración diaria.

### Borg pico / FPN — eje Y

| Valor guardado | Opción mostrada |
|---:|---|
| 0 | Ausencia de esfuerzo |
| 1 | Esfuerzo muy débil |
| 2 | Esfuerzo débil / ligero |
| 3 | Esfuerzo moderado / regular |
| 4 | Esfuerzo algo fuerte |
| 6 | `5 o 6` — esfuerzo fuerte; la aplicación toma 6 |
| 9 | `7, 8 o 9` — esfuerzo muy fuerte; la aplicación toma 9 |
| 10 | Esfuerzo extremadamente fuerte |

Cuando la interfaz agrupa varios valores, guarda el mayor valor del rango como criterio conservador. La escala debe explicarse al trabajador y aplicarse al **pico de fuerza** correspondiente a la acción observada.

### Factores agravantes

Marque todos los presentes:

- **Posturas obligadas**
- **Estrés de contacto**
- **Bajas temperaturas**
- **Vibraciones mano-brazo**

La Resolución MTEySS 295/03 dispone que, si existe uno o más, debe aplicarse juicio profesional para reducir la exposición por debajo del LA. Como no prescribe un desplazamiento numérico de las líneas ni un nivel automático, el motor:

- conserva por separado la clasificación NAM base;
- marca `requiere_revision_profesional`;
- identifica el resultado como condicionado por agravantes; y
- agrega la recomendación normativa para cualquier nivel base, incluso `bajo`.

Los agravantes **no elevan automáticamente el nivel**: hacerlo sin una regla cuantitativa aprobada inventaría un umbral no contenido en la fuente.

---

## 3. Procedimiento recomendado

1. Confirme la relación con la tarea identificada en la Planilla 2E.
2. Complete las horas diarias y determine técnicamente si corresponde marcar **Monotarea**.
3. Seleccione una categoría NAM a partir de la observación de actividad y pausas.
4. Seleccione la categoría Borg/FPN correspondiente al pico de fuerza.
5. Marque los agravantes observados.
6. Explique en **Observaciones** cómo se obtuvieron los valores.
7. Pulse **Guardar y calcular**.
8. Revise el nivel y abra **Ver trazabilidad (calc_data)** para comprobar coordenadas, límites interpolados, zona, distancias y agravantes.

**Guardar** conserva la carga sin ejecutar nuevamente el motor. Si cambia NAM, FPN, horas o monotarea, use **Guardar y calcular** para evitar que quede visible un nivel anterior.

---

## 4. Aplicabilidad implementada

El motor calcula el punto NAM/FPN únicamente si se cumplen simultáneamente:

```text
Monotarea = marcada
Horas día >= 4,00
```

Si falta cualquiera de estas condiciones, devuelve:

```text
Nivel: No aplicable
Motivo: monotarea=False o menos de 4 h/día
```

El umbral de 4 horas coincide con el filtro temporal que la aplicación utiliza para este método, pero la decisión profesional debe considerar la exposición real y el alcance normativo de la Planilla 2E.

---

## 5. Cómo calcula la aplicación

### 5.1 Líneas de referencia

El archivo `repetitivos_ms_limites.json` define dos segmentos rectos entre NAM 0 y 10:

```text
VLU: desde (0; 7,0) hasta (10; 0,0)
LA:  desde (0; 4,8) hasta (10; 0,0)
```

Como la configuración contiene dos puntos por línea, la interpolación actual equivale a:

```text
FPN en VLU = 7,0 − 0,70 × NAM
FPN en LA  = 4,8 − 0,48 × NAM
```

Los valores se limitan internamente al rango de 0 a 10.

| NAM | FPN sobre LA | FPN sobre VLU |
|---:|---:|---:|
| 0 | 4,80 | 7,00 |
| 2 | 3,84 | 5,60 |
| 4 | 2,88 | 4,20 |
| 6 | 1,92 | 2,80 |
| 8 | 0,96 | 1,40 |
| 10 | 0,00 | 0,00 |

### 5.2 Clasificación del punto

Para el NAM seleccionado, el motor compara la FPN con ambas líneas:

| Condición | Zona | Nivel |
|---|---|---|
| `FPN >= VLU` | Peligro, sobre VLU | **Alto** |
| `LA <= FPN < VLU` | Control, entre LA y VLU | **Medio** |
| `FPN < LA` | Seguridad, bajo LA | **Bajo** |

Un punto situado exactamente sobre una línea se asigna a la categoría superior. Por ejemplo, sobre el LA se clasifica `medio` y sobre el VLU se clasifica `alto`.

La trazabilidad también informa:

- coordenadas NAM y FPN;
- valores interpolados de LA y VLU;
- distancia con respecto a ambas líneas;
- margen disponible hasta el LA cuando el punto queda por debajo;
- agravantes seleccionados y recomendaciones.
- condición de revisión profesional y regla aplicada a agravantes.

---

## 6. Interpretación del resultado

| Nivel de la aplicación | Lectura técnica orientativa |
|---|---|
| **Bajo** | El punto queda por debajo del LA configurado. Mantenga controles y confirme que los ciclos observados sean representativos. |
| **Medio** | El punto queda entre LA y VLU. Corresponde implementar o revisar controles y reducir la exposición. |
| **Alto** | El punto se ubica sobre o por encima del VLU. Requiere intervención prioritaria y evaluación profesional. |
| **No aplicable** | El motor no encontró cumplidas sus condiciones de monotarea y duración mínima, o no pudo obtener límites válidos. |

No convierta automáticamente `bajo`, `medio` o `alto` en los niveles 1, 2 o 3 de la Planilla 1. Esa integración requiere criterio profesional, consideración de todos los factores y trazabilidad documental.

---

## 7. Validaciones, errores y comportamiento actual

- NAM solo admite `0, 2, 4, 6, 8 o 10`.
- Borg/FPN solo admite `0, 1, 2, 3, 4, 6, 9 o 10`.
- En los rangos Borg `5–6` y `7–9`, el sistema guarda respectivamente `6` y `9`.
- Las horas pueden quedar vacías en el formulario; en ese caso el método devuelve `no_aplicable`. Para un análisis válido, consigne siempre la duración observada.
- Los agravantes no cambian el nivel base; siempre exigen revisión profesional y una exposición objetivo inferior al LA.
- Si desmarca **Aplicable**, el contrato común del motor devuelve `no aplicable` sin ejecutar la fórmula.
- Un guardado sin recalcular marca cualquier resultado anterior como desactualizado.
- En NAM 10, las dos líneas configuradas llegan a FPN 0; por la comparación inclusiva actual, cualquier FPN disponible queda en nivel alto. Verifique especialmente la correcta asignación de NAM 10.

Si la selección no representa adecuadamente la tarea, no fuerce una categoría para obtener un resultado: documente la limitación y utilice el método que corresponda.

---

## 8. Referencias y advertencia profesional

- [Resolución SRT 886/2015 — texto oficial](https://www.argentina.gob.ar/normativa/nacional/norma-246272/texto)
- [Resolución MTEySS 295/2003 — texto oficial](https://www.argentina.gob.ar/normativa/nacional/resoluci%C3%B3n-295-2003-90396/texto)
- [SRT — Protocolo de Ergonomía, guías y formularios](https://www.argentina.gob.ar/srt/prevencion/publicaciones/protocolos/ergonomia)
- Configuración interna consultada por la aplicación: `evaluaciones/data/repetitivos_ms_limites.json`.

La aplicación automatiza la ubicación de un punto sobre las líneas parametrizadas; no certifica la calidad de la observación, la correcta selección de NAM/FPN ni la suficiencia de las medidas. No debe afirmarse que el motor esté homologado o que su resultado constituya por sí solo un dictamen legal.
