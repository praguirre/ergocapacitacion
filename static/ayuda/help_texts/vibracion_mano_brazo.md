# Guía: Evaluación de Vibración Mano-Brazo (VMB)

## Para qué sirve esta pantalla

Esta pantalla registra y calcula una **evaluación cuantitativa de vibración transmitida a manos y brazos**. Admite una exposición simple o varios tramos de exposición y conserva la trazabilidad del cálculo.

Se accede desde **Planilla 2G: Vibraciones → Realizar Evaluación → Vibración mano-brazo**. La Planilla 2G es el chequeo inicial cualitativo; este formulario es una evaluación cuantitativa posterior. No reemplaza la identificación de la tarea, la medición instrumental ni el criterio de un profesional competente.

> Los resultados `bajo`, `medio`, `alto` y `no aplicable` pertenecen al motor cuantitativo de ErgoApp. No equivalen automáticamente a los niveles `1`, `2` y `3` de la Planilla 1, y la aplicación no realiza esa conversión.

## Antes de completar

- Identifique la herramienta, pieza o mando que transmite la vibración.
- Utilice valores de aceleración ponderada obtenidos con instrumental y procedimiento de medición adecuados.
- Registre el **tiempo diario real de contacto o accionamiento**, no necesariamente toda la duración del turno.
- Elija **Exposición Simple** si las condiciones pueden representarse con una sola medición y duración.
- Elija **Exposición Múltiple** si durante la jornada cambian la herramienta, la intensidad o el tiempo de exposición.
- En exposición múltiple use un único criterio para todos los tramos: valores escalares `a_wi` o mediciones por ejes X/Y/Z.

## Campos del formulario

### Tipo de exposición

| Campo | Cómo completarlo |
|---|---|
| Tipo de exposición | Seleccione `Exposición Simple` o `Exposición Múltiple`. La pantalla muestra solamente el bloque correspondiente. |
| Aplicable | Déjelo marcado cuando el factor corresponda a la tarea. Si se desmarca, el cálculo devuelve `no aplicable`. |
| Observaciones | Identifique tarea, herramienta, mano evaluada, condiciones de operación, instrumento, fecha u otra información necesaria para interpretar la medición. |

### Exposición simple

| Campo | Qué representa | Unidad |
|---|---|---|
| `a_k` | Valor único de aceleración ponderada. Es la modalidad de compatibilidad denominada “legacy”. | m/s² |
| Duración | Tiempo diario real de exposición. Debe ser mayor que cero. | horas |
| `a_x` | Eje X, orientación dorso-palma. | m/s² |
| `a_y` | Eje Y, orientación lateral/pulgar. | m/s² |
| `a_z` | Eje Z, orientación longitudinal de la mano/brazo. | m/s² |

Puede ingresar **`a_k` o los tres ejes**. Si completa alguno de los ejes, debe completar X, Y y Z; en ese caso el motor usa el mayor de los tres y deja de usar `a_k` para el cálculo.

### Exposición múltiple

El constructor permite agregar tantos tramos como sean necesarios:

| Campo o control | Función |
|---|---|
| Cargar por ejes | Alterna entre un `a_wi` escalar por tramo y valores X/Y/Z. Cambiar de modo cuando ya hay tramos solicita confirmación y vacía la lista. |
| `a_wi` | Aceleración ponderada del tramo cuando se usa el modo escalar, en m/s². |
| `a_x`, `a_y`, `a_z` | Aceleraciones del tramo cuando se usa el modo por ejes, en m/s². Deben informarse las tres. |
| `T_i` | Duración del tramo, en horas; debe ser mayor que cero. |
| Agregar | Incorpora el tramo válido a la tabla. |
| Volcar al JSON | Sincroniza la tabla con `Ítems de Exposición`. La pantalla también sincroniza al agregar, quitar y enviar. |
| Vaciar | Elimina todos los tramos del constructor. |
| `exposiciones_json` | Vista de solo lectura de los tramos que se persistirán al guardar. |

El JSON normalizado usa una de estas dos estructuras:

```json
[
  {"awi_mps2": 4.2, "Ti_h": 1.5}
]
```

```json
[
  {"ax_mps2": 2.1, "ay_mps2": 3.0, "az_mps2": 2.6, "Ti_h": 1.5}
]
```

No mezcle ambos formatos en una misma evaluación.

## Procedimiento recomendado

1. Confirme que el factor corresponde a vibración mano-brazo y mantenga marcado **Aplicable**.
2. Seleccione el tipo de exposición.
3. Cargue la aceleración y la duración diaria real. En exposición múltiple, agregue cada tramo y revise la tabla.
4. Registre en observaciones las condiciones que permitan reconstruir la medición.
5. Use **Guardar** si desea conservar los datos sin ejecutar el motor.
6. Use **Guardar y calcular** para persistir los datos, ejecutar el cálculo y actualizar el nivel y la trazabilidad.
7. Revise el badge de nivel y despliegue **Ver trazabilidad (`calc_data`)**. Compruebe el método, el tiempo total, el eje dominante, los límites aplicados y la fuente.

**Guardar no recalcula.** Si ya existía un resultado y luego modifica entradas usando solamente Guardar, el nivel anterior puede continuar visible y quedar desactualizado. Para emitir una conclusión, vuelva a usar **Guardar y calcular**.

## Cómo calcula ErgoApp

### Exposición simple

- Con X/Y/Z, el valor de exposición es el mayor de los tres ejes; ese eje queda registrado como dominante.
- Sin ejes, utiliza el valor único `a_k`.
- La clasificación compara ese valor con la fila de tiempo diario configurada.

### Exposición múltiple

Para cada eje calcula el promedio energético:

```text
a_eq,eje = √[Σ(a_eje,i² × T_i) / ΣT_i]
```

Luego utiliza el mayor `a_eq` entre X, Y y Z. En modo escalar aplica la misma fórmula a los valores `a_wi`.

### Tabla y clasificación implementadas

El motor usa `evaluaciones/data/vibracion_mano_brazo_limites.json`:

| Duración total utilizada por el motor | Límite configurado | Nivel de acción interno |
|---|---:|---:|
| 0 h ≤ T < 1 h | 12,0 m/s² | 6,0 m/s² |
| 1 h ≤ T < 2 h | 8,0 m/s² | 4,0 m/s² |
| 2 h ≤ T < 4 h | 6,0 m/s² | 3,0 m/s² |
| 4 h ≤ T < 8 h | 4,0 m/s² | 2,0 m/s² |
| 8 h ≤ T < 24 h | 4,0 m/s² | 2,0 m/s² |

El “nivel de acción” es un umbral **interno** equivalente al 50 % del límite configurado. La regla implementada es:

- **Bajo:** valor menor que el nivel de acción.
- **Medio:** valor igual o superior al nivel de acción y menor o igual al límite.
- **Alto:** valor superior al límite.
- **No aplicable:** factor desmarcado o entradas que el motor no puede evaluar.

También calcula, solo con finalidad informativa:

```text
A(8) = valor de exposición × √(tiempo total / 8 h)
```

La clasificación actual se realiza contra la **tabla por duración**, no contra ese A(8) informativo.

## Interpretación y trazabilidad

- **Bajo** indica que el valor quedó por debajo del nivel de acción interno.
- **Medio** indica que alcanzó el nivel de acción pero no superó el límite configurado.
- **Alto** indica que superó el límite configurado.
- **No aplicable** no significa “riesgo bajo”: informa que el factor fue excluido o que no hubo datos evaluables.

En `calc_data` quedan, entre otros datos: eje dominante, valor final, tiempo total, A(8) informativo, fila temporal, nivel de acción, límite y método de integración. El profesional debe contrastar esa trazabilidad con la medición original antes de aceptar el resultado.

Los límites máximos por duración (`12`, `8`, `6` y `4 m/s²`) fueron cotejados
con la Tabla 1 de la Resolución 295/03. En cambio, el nivel de acción definido
como el 50 % de cada fila y la banda `medio` resultante son una extensión interna
pendiente de adopción profesional; la tabla oficial no prescribe esa fracción.

## Validaciones y errores frecuentes

- En exposición simple, la duración debe ser mayor que cero.
- Debe ingresar `a_k` o los tres ejes. Informar uno o dos ejes produce un error general.
- En exposición múltiple debe haber al menos un tramo.
- Cada `T_i` debe ser mayor que cero y las aceleraciones no pueden ser negativas.
- El JSON debe ser una lista de objetos con las claves exactas mostradas arriba.
- El formulario rechaza la mezcla de tramos escalares y triaxiales.
- Si **Agregar** no incorpora una fila, revise que todos los valores visibles sean numéricos y que `T_i` sea mayor que cero.
- La tabla interna no posee una fila específica para exposiciones de 24 horas o más; no extrapole resultados fuera del rango documentado.
- No use el campo **Payload JSON opcional** en la operatoria normal. Está destinado a parámetros avanzados y puede alterar las entradas conservadas en `calc_data`.

## Referencias y advertencia profesional

- [Resolución SRT 886/2015 — Protocolo de Ergonomía](https://www.argentina.gob.ar/normativa/nacional/norma-246272/texto), en especial la Planilla 2G.
- [Resolución MTEySS 295/2003](https://www.argentina.gob.ar/normativa/nacional/resoluci%C3%B3n-295-2003-90396/texto), Anexo V sobre vibraciones.
- [Portal oficial SRT — Protocolo, guía y formularios](https://www.argentina.gob.ar/srt/prevencion/publicaciones/protocolos/ergonomia).
- ISO 5349-1 e ISO 5349-2, como referencias técnicas para evaluación y medición de vibración transmitida a la mano.

Los umbrales, la banda “media” y las fórmulas aquí descriptas reflejan el **motor actualmente implementado en ErgoApp**. La aplicación no certifica por sí sola el cumplimiento legal ni reemplaza una evaluación instrumentada, la revisión de la normativa vigente, la vigilancia de la salud o la firma de los profesionales responsables.
