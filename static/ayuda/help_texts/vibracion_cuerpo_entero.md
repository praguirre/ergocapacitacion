# Guía: Evaluación de Vibración de Cuerpo Entero (VCE)

## Para qué sirve esta pantalla

Esta pantalla documenta la exposición a vibraciones transmitidas al cuerpo a través del asiento, respaldo, pies o superficie de apoyo. Permite registrar el contexto de medición, adjuntar evidencia y dividir la jornada en **tramos con condiciones constantes** —por ejemplo, circulación sobre asfalto y luego sobre terreno irregular—.

Se accede desde **Planilla 2G: Vibraciones → Realizar Evaluación → Vibración de cuerpo entero**. La Planilla 2G es el chequeo inicial cualitativo; este formulario es una evaluación cuantitativa posterior. No sustituye la identificación de fuentes, la medición instrumental ni el análisis de un profesional competente.

> Los resultados `bajo`, `medio`, `alto` y `no aplicable` pertenecen al motor cuantitativo de ErgoApp. No equivalen automáticamente a los niveles `1`, `2` y `3` de la Planilla 1, y la aplicación no realiza esa conversión.

## Modalidades disponibles

La pantalla ofrece dos caminos:

1. **Tramos de medición — modalidad prioritaria.** Permite integrar varias fuentes o condiciones a lo largo de la jornada.
2. **Modo Legacy / Carga Simple — compatibilidad.** Permite guardar una sola duración con aceleraciones ponderadas X/Y/Z o datos espectrales avanzados.

Si existe al menos un tramo guardado, el motor da prioridad a los **tramos** y no utiliza los valores del modo legacy para definir el resultado.

## 1. Contexto y montaje

| Campo | Cómo completarlo |
|---|---|
| Postura | Seleccione `Sentado`, `De pie` o `Recostado`. Es obligatorio. |
| Ubicación del sensor | Seleccione `Bajo isquiones (disco)`, `Respaldo` o `Pies`, de acuerdo con el montaje real. Es obligatorio. |
| Antecedentes de salud | Campo opcional para antecedentes de columna relevantes. Use información pertinente y respete las reglas aplicables a datos de salud. |
| Foto de montaje | Evidencia fotográfica opcional de la posición y orientación del sensor. |
| Certificado de calibración | Archivo opcional del instrumento utilizado. |

La postura, el montaje y los archivos quedan como contexto y evidencia; **no modifican por sí solos la fórmula numérica actual**.

## 2. Tramos de medición

Use un tramo por cada período en que la fuente, el terreno, la velocidad o las aceleraciones puedan considerarse estables.

| Campo | Qué representa | Unidad / opciones |
|---|---|---|
| Vehículo / Máquina | Identificación concreta de la fuente. | Texto; obligatorio |
| Tipo de asiento | Condición del asiento. | Fijo/sin suspensión, suspensión mecánica, neumática o deteriorado |
| Superficie / terreno | Condición de circulación o apoyo. | Liso, irregular, muy irregular/baches u off-road |
| Tiempo de exposición | Duración del tramo. | horas; obligatorio |
| Velocidad | Promedio del tramo. | km/h; opcional |
| Estado de neumáticos | Condición registrada. | Correcto, desinflado o macizo |
| Eje X — RMS | Aceleración ponderada informada por el equipo. | m/s²; obligatorio |
| Eje Y — RMS | Aceleración ponderada informada por el equipo. | m/s²; obligatorio |
| Eje Z — RMS | Aceleración ponderada informada por el equipo. | m/s²; obligatorio |
| CF X / Y / Z | Factores de cresta por eje. | adimensionales; opcionales |
| Pico espectral | Frecuencia dominante observada. | Hz; entero opcional |

Ingrese en X/Y/Z los valores ya ponderados `Wd/Wk` entregados por el equipo. La aplicación aplica internamente el factor `1,4` a X e Y y `1,0` a Z; no vuelva a multiplicarlos antes de cargarlos.

**Agregar otro tramo** crea una nueva tarjeta. Para eliminar un tramo ya mostrado, marque **Eliminar Tramo** antes de guardar. La actualización del padre y de todos sus tramos se intenta realizar en una transacción. Ante cualquier mensaje de error o navegación incompleta, verifique el registro antes de volver a enviarlo: no debe suponerse el estado final a partir de la pantalla solamente.

## 3. Modo Legacy / Carga Simple

El bloque se encuentra dentro de un acordeón opcional.

| Campo | Uso actual |
|---|---|
| Método | `Aceleraciones Ponderadas` selecciona el cálculo legacy por ejes; `Análisis Espectral` selecciona el screening espectral aproximado. |
| Duración | Tiempo diario, en horas. Para calcular en modo legacy debe ser finito y mayor que cero. |
| Factor de cresta mayor que 6 | Genera una advertencia de posible subestimación por RMS. No eleva automáticamente el nivel. |
| `a_wx`, `a_wy`, `a_wz` | Valores ponderados únicos por eje, en m/s². |
| Picos espectrales por eje | Objeto JSON con las seis claves obligatorias de frecuencia y aceleración. El motor espectral consume directamente este campo. |

El screening espectral legacy recibe este contrato exacto:

```json
{
  "pico_x_hz": 2,
  "pico_x_mps2": 0.25,
  "pico_y_hz": 2,
  "pico_y_mps2": 0.20,
  "pico_z_hz": 5,
  "pico_z_mps2": 0.35
}
```

No se admiten claves faltantes, adicionales, valores negativos ni valores no numéricos. La duración se carga en su campo propio. Este modo aproxima cada pico como si fuera un RMS ponderado: es un **screening aproximado**, no una evaluación espectral completa. Para la operatoria normal, prefiera tramos con aceleraciones ponderadas.

## Procedimiento recomendado

1. Confirme que la exposición corresponde a cuerpo entero y mantenga marcado **Aplicable**.
2. Registre postura, ubicación del sensor y antecedentes pertinentes.
3. Adjunte, si dispone de ellos, la foto de montaje y el certificado de calibración.
4. Divida la jornada en tramos homogéneos.
5. Para cada tramo identifique fuente y condiciones, cargue el tiempo y los tres valores RMS ponderados.
6. Agregue factores de cresta y pico espectral cuando la medición los proporcione.
7. Documente en observaciones cualquier cambio operativo, impacto, incertidumbre o limitación.
8. Use **Guardar** para conservar los datos sin ejecutar el motor.
9. Use **Guardar y calcular** para intentar guardar padre y tramos y ejecutar el cálculo.
10. Solo acepte el resultado si aparece la confirmación correspondiente y puede revisar el nivel y la trazabilidad. Si la pantalla informa un error inesperado, no suponga que el cálculo o el guardado finalizaron: conserve la evidencia y reporte el caso para revisión técnica.

Al guardar correctamente, el flujo vuelve al **resumen de factores** de la evaluación. Considere finalizada la operación únicamente cuando pueda volver a abrir el registro y confirmar los datos persistidos.

**Guardar no recalcula.** Si cambia datos después de un cálculo y usa solamente Guardar, un nivel previo puede quedar desactualizado. Para emitir una conclusión se necesita un cálculo confirmado con las entradas vigentes.

## Flujo de cálculo definido por la aplicación

### Modalidad por tramos

Para cada tramo `i`, el motor pondera:

```text
X_i = 1,4 × aw_x,i
Y_i = 1,4 × aw_y,i
Z_i = 1,0 × aw_z,i
```

Luego integra cada eje sobre una jornada de referencia de 8 horas:

```text
A8_X = √[Σ(X_i² × T_i) / 8]
A8_Y = √[Σ(Y_i² × T_i) / 8]
A8_Z = √[Σ(Z_i² × T_i) / 8]
```

El valor final es el mayor de `A8_X`, `A8_Y` y `A8_Z`; el eje correspondiente queda registrado como dominante.

### Modalidad legacy con aceleraciones ponderadas

Sin tramos, para una duración `T`:

```text
A8_X = |1,4 × a_wx| × √(T / 8)
A8_Y = |1,4 × a_wy| × √(T / 8)
A8_Z = |1,0 × a_wz| × √(T / 8)
```

También aquí se utiliza el máximo de los tres ejes.

### Modalidad espectral legacy

Normaliza los picos suministrados en el campo espectral modelado con la misma estructura por eje y duración. El resultado incluye una advertencia porque esta modalidad no implementa curvas espectrales numéricas completas.

### Umbrales A(8) complementarios

El motor lee `evaluaciones/data/vibracion_cuerpo_entero_limites.json`:

- **Bajo:** A(8) final menor que `0,50 m/s²`.
- **Medio:** A(8) final igual o mayor que `0,50 m/s²` y menor o igual que `1,15 m/s²`.
- **Alto:** A(8) final mayor que `1,15 m/s²`.

Los valores `0,50` y `1,15 m/s²` provienen del artículo 3.2 de la Directiva
2002/44/CE. ErgoApp los usa como método internacional complementario A(8),
admisible bajo el criterio general de la Resolución SRT 886/15 cuando el
profesional lo adopta y registra. No deben presentarse como las curvas primarias
de límite de la Resolución 295/03 ni como una homologación automática del caso.

## Advertencias que genera el motor

- Si algún CF es mayor que `6`, registra que el RMS puede subestimar la exposición y recomienda considerar un método alternativo. **No cambia automáticamente el nivel.**
- Un pico entre `4 y 8 Hz` genera una advertencia de coincidencia con la banda de resonancia vertical configurada.
- Un pico entre `1 y 2 Hz` genera una advertencia de coincidencia con la banda de resonancia horizontal configurada.
- El tiempo total, las aceleraciones crudas, los valores ponderados, A(8) por eje, eje dominante, warnings y tramos se preparan para quedar disponibles en la trazabilidad.

## Aplicabilidad, validaciones y errores frecuentes

- Postura y ubicación del sensor son obligatorias.
- En cada tramo utilizado son obligatorios: vehículo/máquina, tipo de asiento, superficie, estado de neumáticos, tiempo y X/Y/Z.
- El formulario y el motor rechazan tiempos no positivos y mediciones negativas o no finitas.
- Si no queda ningún tramo temporalmente válido, no hay resultado evaluable.
- Los factores de cresta y el pico espectral son opcionales.
- El espectro debe contener exactamente sus seis claves y valores finitos no negativos.
- Si existen tramos guardados, los campos legacy no participan del resultado.
- Foto y certificado son opcionales en el formulario; su ausencia no bloquea el guardado.
- Si desmarca **Aplicable**, el contrato común del motor devuelve `no aplicable` sin ejecutar la fórmula específica.
- No deje una carga legacy sin duración o sin valores de medición: el motor la rechaza como incompleta.

## Interpretación y trazabilidad

- **Bajo** indica que el A(8) máximo quedó por debajo del umbral de acción interno.
- **Medio** indica que alcanzó el umbral de acción y no superó el límite configurado.
- **Alto** indica que superó el límite configurado.
- **No aplicable** no equivale a “bajo”; indica exclusión o ausencia de datos evaluables.

El profesional debe verificar que la suma de tiempos represente la jornada, que las ponderaciones del instrumento sean las declaradas, que la orientación de ejes sea correcta y que los warnings no invaliden el uso exclusivo de RMS.

## Referencias y advertencia profesional

- [Resolución SRT 886/2015 — Protocolo de Ergonomía](https://www.argentina.gob.ar/normativa/nacional/norma-246272/texto), en especial la Planilla 2G.
- [Resolución MTEySS 295/2003](https://www.argentina.gob.ar/normativa/nacional/resoluci%C3%B3n-295-2003-90396/texto), Anexo V sobre vibraciones.
- [Directiva 2002/44/CE](https://eur-lex.europa.eu/legal-content/ES/TXT/?uri=CELEX:32002L0044), artículo 3.2, valores A(8) de acción y límite para VCE.
- [Portal oficial SRT — Protocolo, guía y formularios](https://www.argentina.gob.ar/srt/prevencion/publicaciones/protocolos/ergonomia).
- ISO 2631-1, como referencia técnica general para evaluación de exposición humana a vibración de cuerpo entero.

Las ponderaciones, umbrales, warnings y aproximaciones descriptos reflejan el **motor actualmente definido en ErgoApp**. La aplicación no certifica por sí sola el cumplimiento legal ni reemplaza la medición con instrumental calibrado, la revisión de la normativa vigente, la evaluación de impactos o choques, la vigilancia de la salud o la firma de los profesionales responsables.
