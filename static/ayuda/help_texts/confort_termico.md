# Guía: Evaluación de Confort Térmico

## Para qué sirve esta pantalla

Esta pantalla realiza un **cribado de confort térmico** a partir de un punto definido por:

- la **temperatura operativa** (`To`), en °C; y
- la **humedad relativa** (`HR`), en %.

Se accede desde **Planilla 2H: Confort térmico → Realizar Evaluación**. La Planilla 2H identifica cualitativamente el factor; este formulario complementa ese análisis con una clasificación cuantitativa simplificada.

El motor ubica el punto `To–HR` en una de cinco zonas: `demasiado_frio`, `frio`, `confort`, `caliente` o `demasiado_caliente`. Luego informa un nivel interno `bajo`, `medio` o `alto`.

> Este cribado no es un cálculo completo de PMV/PPD ni una evaluación de estrés térmico. No contempla de manera explícita metabolismo, vestimenta, velocidad del aire, asimetría radiante ni características individuales. Tampoco convierte automáticamente el resultado en los niveles `1`, `2` o `3` de la Planilla 1.

## Antes de completar

- Defina la tarea, el puesto, la zona y el momento de la jornada que representa la medición.
- Espere la estabilización del instrumental y mida en una ubicación representativa de la permanencia del trabajador.
- Registre condiciones transitorias relevantes: apertura de portones, radiación solar, procesos calientes o fríos, ventilación, estacionalidad y carga de trabajo.
- Use **temperatura operativa**, no sustituya automáticamente este valor por la temperatura de aire. La temperatura operativa integra el efecto de la temperatura del aire y de la radiación térmica.
- Si existen condiciones diferentes durante la jornada, documente y evalúe por separado los escenarios representativos.
- Verifique la calibración, resolución y rango del instrumento utilizado.

## Campos del formulario

### General

| Campo | Cómo completarlo |
|---|---|
| Aplicable | Indica si el factor corresponde a la tarea analizada. Consulte la advertencia de funcionamiento actual incluida más abajo. |
| Observaciones | Identifique puesto, tarea, ubicación, horario, condición de operación, instrumento, fecha y cualquier circunstancia necesaria para interpretar la medición. |

### Parámetros

| Campo | Qué representa | Rango admitido |
|---|---|---:|
| Temperatura operativa | Temperatura equivalente resultante de los intercambios convectivo y radiante. | 15 a 40 °C |
| Humedad relativa | Relación porcentual entre el vapor de agua presente y el máximo posible para esa temperatura. | 0 a 90 % |

Aunque ambos campos se muestran como opcionales a nivel de formulario, **complete los dos antes de calcular**. Una evaluación térmica sin alguno de esos valores no es interpretable.

## Procedimiento recomendado

1. Confirme que el factor corresponde al puesto y a la tarea.
2. Identifique en **Observaciones** el escenario medido.
3. Ingrese la temperatura operativa y la humedad relativa.
4. Revise las unidades y los decimales.
5. Use **Guardar** si solamente desea conservar los datos.
6. Use **Guardar y calcular** para persistir los valores y ejecutar el motor.
7. Revise el nivel, la zona estimada y las recomendaciones.
8. Abra **Ver trazabilidad (`calc_data`)** y compruebe las entradas, los valores normalizados, las fronteras interpoladas y la fuente de configuración.

**Guardar no recalcula.** Si modifica las entradas de una evaluación que ya tenía resultado y utiliza solamente Guardar, el nivel anterior puede continuar visible. Antes de emitir una conclusión, vuelva a usar **Guardar y calcular**.

## Cómo calcula ErgoApp

El motor utiliza las polilíneas configuradas en:

```text
evaluaciones/data/confort_termico_umbrales.json
```

Cada polilínea relaciona temperatura operativa con un límite de humedad relativa. Para la `To` ingresada, el sistema interpola linealmente cuatro fronteras:

| Frontera | Puntos configurados `To °C, HR %` |
|---|---|
| Demasiado frío / frío | (15; 45) y (19; 0) |
| Frío / confort | (15; 60), (20; 30) y (22,5; 0) |
| Confort / caliente | (20; 90), (25; 50) y (33; 0) |
| Caliente / demasiado caliente | (26; 90), (30; 70), (35; 45) y (40; 20) |

Fuera del tramo propio de una polilínea se utiliza el valor de su extremo más cercano. Por eso la zona de confort **no es un rectángulo de temperatura y humedad**: el límite de HR cambia con la temperatura.

La clasificación implementada compara la HR con esas cuatro fronteras, en este orden:

1. hasta la primera frontera: `demasiado_frio`;
2. entre la primera y la segunda: `frio`;
3. entre la segunda y la tercera: `confort`;
4. entre la tercera y la cuarta: `caliente`;
5. por encima de la cuarta: `demasiado_caliente`.

El mapeo interno es:

| Zona calculada | Nivel informado |
|---|---|
| Demasiado frío | Alto |
| Frío | Medio |
| Confort | Bajo |
| Caliente | Medio |
| Demasiado caliente | Alto |

Los valores se limitan al dominio del gráfico (`15–40 °C` y `0–90 % HR`) antes de interpolar. El formulario normalmente rechaza valores externos, por lo que no deben utilizarse los extremos normalizados para extrapolar una medición fuera de rango.

## Cómo interpretar el resultado

- **Bajo / confort:** el punto quedó dentro de la zona de confort definida por las curvas simplificadas.
- **Medio / frío o caliente:** el punto quedó en una zona de disconfort que requiere revisar condiciones y controles.
- **Alto / demasiado frío o demasiado caliente:** el punto quedó en una zona extrema del cribado y requiere intervención prioritaria y una evaluación profesional específica.

El nivel describe únicamente el punto `To–HR` procesado. No demuestra por sí solo que toda la jornada, todas las personas o todos los sectores estén en la misma condición.

En `calc_data` quedan registrados:

- los valores originales;
- los valores limitados al dominio del gráfico;
- la humedad límite interpolada para cada frontera;
- la zona;
- las recomendaciones; y
- el archivo de configuración utilizado.

## Validaciones de funcionamiento

### No calcular con campos vacíos

**Guardar y calcular** exige `To` y `HR` y el motor vuelve a validar presencia,
finitud y dominio. Una entrada incompleta o fuera de rango queda como
`no aplicable`; no se normaliza hacia una zona de riesgo.

Por lo tanto:

- complete ambos parámetros para calcular;
- si falta una medición, use solamente **Guardar** y deje constancia en Observaciones; y
- no interprete un borrador incompleto como una evaluación vigente.

### Factor marcado como no aplicable

El contrato común del motor detiene el cálculo cuando se desmarca **Aplicable**
y devuelve `no aplicable`. Si el factor no corresponde:

1. desmarque Aplicable;
2. explique el motivo en Observaciones; y
3. guarde el registro para conservar la trazabilidad de la exclusión.

## Errores frecuentes

- Ingresar temperatura de aire como si fuera siempre temperatura operativa.
- Mezclar mediciones tomadas en lugares o momentos no comparables.
- Usar el resultado para valorar carga térmica sin considerar metabolismo, vestimenta y velocidad del aire.
- Omitir si el valor corresponde a invierno, verano, régimen normal o una condición excepcional.
- Interpretar `bajo`, `medio` o `alto` como equivalentes automáticos de la Planilla 1.
- Conservar un resultado anterior después de cambiar datos con la acción Guardar.
- Extrapolar el método fuera de `15–40 °C` o `0–90 % HR`.

## Medidas orientativas

Las recomendaciones que muestra el sistema son generales. Según el caso, la intervención profesional puede incluir:

- control de fuentes radiantes;
- aislamiento térmico;
- calefacción, refrigeración, ventilación o deshumidificación;
- reducción de corrientes de aire;
- adaptación de ropa o EPP;
- provisión de agua, pausas y recuperación térmica;
- cambios de organización o tiempos de exposición; y
- mediciones adicionales con un método específico para estrés térmico o confort.

La medida adecuada debe surgir de la evaluación integral y de la jerarquía de controles, no solamente de la etiqueta calculada.

## Referencias y advertencia profesional

- [Resolución SRT 886/2015 — Protocolo de Ergonomía](https://www.argentina.gob.ar/normativa/nacional/norma-246272/texto), especialmente la Planilla 2H.
- [Resolución MTEySS 295/2003](https://www.argentina.gob.ar/normativa/nacional/resoluci%C3%B3n-295-2003-90396/texto).
- [Portal oficial SRT — Protocolo, guía y formularios](https://www.argentina.gob.ar/srt/prevencion/publicaciones/protocolos/ergonomia).
- ISO 7730 e ISO 7726, como referencias técnicas para confort térmico e instrumentación.

Las curvas, zonas y recomendaciones aquí explicadas describen el **motor actualmente implementado en ErgoApp**. La aplicación es una herramienta de apoyo: no reemplaza el relevamiento del puesto, la selección del método legal y técnico aplicable, el juicio de un profesional competente ni la firma de los responsables exigidos por la normativa.
