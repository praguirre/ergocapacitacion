# Guía: Evaluación de Estrés de Contacto

## Para qué sirve esta pantalla

Esta pantalla realiza un **cribado de estrés de contacto**: presión localizada del cuerpo contra bordes, superficies, apoyos, herramientas o piezas. Combina la frecuencia de exposición con factores agravantes y, cuando se dispone de ellos, datos de fuerza, área de contacto y percepción de esfuerzo.

Se accede desde **Planilla 2I: Estrés de contacto → Realizar Evaluación**. La Planilla 2I identifica cualitativamente el factor; este formulario documenta la situación y produce una clasificación interna `bajo`, `medio` o `alto`.

> El resultado no equivale automáticamente a los niveles `1`, `2` o `3` de la Planilla 1. Es un cribado parametrizado de ErgoApp y no reemplaza el análisis del puesto ni el criterio de un profesional competente.

## Qué situaciones deben observarse

Considere, entre otras:

- muñecas o antebrazos apoyados contra cantos;
- palmas o dedos en contacto con mangos, piezas o bordes duros;
- codos apoyados durante períodos prolongados;
- muslos o piernas contra bordes de mesas, asientos o estructuras;
- uso de la mano como herramienta de golpe;
- mangos que concentran fuerza en una superficie pequeña;
- contacto asociado con posturas forzadas; y
- marcas, dolor, hormigueo o adormecimiento relacionados con la tarea.

Observe ciclos completos y condiciones representativas. Identifique el segmento corporal, el objeto, la forma del borde, la duración continua y la proporción del ciclo en contacto.

## Campos del formulario

### General

| Campo | Cómo completarlo |
|---|---|
| Aplicable | Indica si el factor corresponde a la tarea. Consulte la advertencia de funcionamiento actual incluida más abajo. |
| Observaciones | Describa tarea, segmento, objeto, punto de contacto, frecuencia, condición operativa y cualquier evidencia necesaria para reconstruir el análisis. |

### Descripción de la exposición

| Campo | Qué representa |
|---|---|
| Segmento afectado | Muñeca, antebrazo, palma/dedos, codo, muslo/pierna u otro. |
| Objeto o superficie | Elemento que produce el contacto: canto de mesa, borde de bandeja, mango, pieza, apoyo, etc. |
| Tipo de borde | `Afilado/canto vivo`, `duro/recto` o `acolchado/redondeado`. |
| Duración continua | Minutos sin interrupción durante los cuales se mantiene el contacto. |
| Frecuencia de exposición | Proporción estimada del ciclo con contacto: baja (`<30 %`), moderada (`30–60 %`) o alta (`>60 %`). |

La aplicación representa internamente las tres opciones de frecuencia con `20 %`, `45 %` y `80 %`, respectivamente.

### Intensidad opcional

| Campo | Uso |
|---|---|
| Fuerza | Fuerza medida o estimada que se transmite en el contacto, en newtons. |
| Área de contacto | Superficie efectiva sobre la que actúa la fuerza, en cm². Debe ser mayor que cero para calcular presión. |
| Borg | Percepción de esfuerzo en escala `0–10`. |

Para estimar presión deben completarse **fuerza y área juntas**:

```text
presión (kPa) = fuerza (N) / área (cm²) × 10
```

Si falta uno de esos datos, el motor no calcula presión. Borg se usa en un índice auxiliar documental; no reemplaza una medición de fuerza o presión.

### Flags críticos

Los siguientes campos fuerzan inmediatamente un nivel **alto** en el motor actual:

- uso de la mano como martillo;
- mango inadecuado; o
- postura forzada asociada.

Márquelos solamente cuando la condición haya sido observada. Explique en Observaciones dónde, cuándo y con qué frecuencia ocurre.

## Procedimiento recomendado

1. Confirme que existe contacto localizado relevante.
2. Identifique el segmento y el objeto o superficie.
3. Seleccione el tipo de borde.
4. Estime la duración continua y la proporción del ciclo expuesto.
5. Si cuenta con datos confiables, ingrese fuerza y área; Borg es complementario.
6. Marque los flags críticos observados.
7. Registre en Observaciones síntomas informados, controles existentes, método de observación y evidencia.
8. Use **Guardar** para conservar datos sin ejecutar el motor.
9. Use **Guardar y calcular** para actualizar el nivel y `calc_data`.
10. Revise el badge de nivel, la matriz base, los agravantes, la presión y la trazabilidad.

**Guardar no recalcula.** Después de modificar una evaluación con resultado previo, utilice **Guardar y calcular** antes de interpretar el nivel.

## Cómo calcula ErgoApp

El motor utiliza:

```text
evaluaciones/data/estres_contacto_criterios.json
```

### 1. Frecuencia

La opción del formulario se convierte en un porcentaje representativo:

| Opción | Valor interno | Banda del motor |
|---|---:|---|
| Baja (`<30 %`) | 20 % | Bajo |
| Moderada (`30–60 %`) | 45 % | Medio |
| Alta (`>60 %`) | 80 % | Alto |

### 2. Presión

Cuando hay fuerza y área válidas:

| Presión calculada | Banda |
|---|---|
| Hasta 100 kPa inclusive | Baja |
| Más de 100 y hasta 150 kPa inclusive | Media |
| Más de 150 kPa | Alta |

Una presión alta cuenta como agravante y, después de la matriz, eleva un nivel adicional. Debido a esa combinación, **no debe asumirse que toda presión mayor que 150 kPa produce por sí sola un resultado alto**; depende también del nivel base.

### 3. Agravantes

El cálculo suma:

- borde afilado: `+1`;
- presión alta: `+1`; y
- frecuencia alta: `+1`.

Los agravantes se agrupan como `0`, `1` o `2 o más`.

### 4. Matriz base

| Frecuencia | 0 agravantes | 1 agravante | 2 o más |
|---|---|---|---|
| Baja | Bajo | Bajo | Medio |
| Media | Bajo | Medio | Alto |
| Alta | Medio | Alto | Alto |

Después de la matriz se aplica, si corresponde, el aumento por presión alta. Los flags críticos se procesan antes y fuerzan nivel alto.

### 5. Duración y Borg

La duración continua se agrupa de esta manera:

| Duración | Banda |
|---|---|
| Menos de 5 min | Baja |
| Desde 5 hasta 15 min inclusive | Media |
| Más de 15 min | Alta |

El motor asigna a esas bandas `20 %`, `45 %` u `80 %` y calcula:

```text
índice auxiliar = duración % estimada × frecuencia % × Borg / 100
```

Este índice se conserva con finalidad documental. **No determina el nivel principal** en la implementación actual.

## Cómo interpretar el resultado

- **Bajo:** combinación de frecuencia y agravantes baja en la matriz actual.
- **Medio:** condición intermedia que requiere revisar exposición y medidas preventivas.
- **Alto:** condición prioritaria por matriz, escalado o flag crítico.

En `calc_data` pueden quedar registrados:

- entradas usadas;
- presión y banda de presión;
- bandas de frecuencia y duración;
- cantidad de agravantes;
- nivel base de la matriz;
- flags críticos;
- índice auxiliar;
- reglas aplicadas; y
- fuente de configuración.

La clasificación debe contrastarse con la observación, síntomas, controles, evidencia fotográfica o instrumental y el resto del protocolo.

## Síntomas, controles y aplicabilidad

La pantalla ofrece selecciones controladas para síntomas y controles. Al guardar, esas selecciones se persisten y se incorporan a la trazabilidad:

- cualquier síntoma eleva el resultado al menos a `medio`;
- `adormecimiento` o `marcas` lo elevan a `alto`;
- tres o más controles reconocidos pueden reducir un nivel, salvo que el resultado ya sea `alto`.

Verifique siempre que los controles estén efectivamente implementados y que las selecciones aparezcan en `calc_data`. Si desmarca **Aplicable**, el contrato común del motor devuelve `no aplicable` sin ejecutar la fórmula. Un cálculo nuevo reemplaza el detalle obsoleto del cálculo anterior.

## Errores frecuentes

- Confundir duración continua con duración total del turno.
- Elegir la frecuencia sin observar un ciclo completo.
- Informar área cero o completar fuerza sin área.
- Usar Borg como si fuera presión.
- Marcar un flag crítico sin describir la condición.
- Asumir que tres controles son eficaces sin verificar su implementación y trazabilidad.
- Interpretar el índice auxiliar como la clasificación principal.
- Considerar `bajo`, `medio` o `alto` equivalentes automáticos a la Planilla 1.
- Modificar datos con Guardar y conservar un resultado desactualizado.

## Medidas orientativas

Según el caso, priorice:

- eliminar el contacto contra cantos;
- redondear, cubrir o acolchar bordes;
- rediseñar mangos, apoyos y superficies;
- distribuir la fuerza sobre un área mayor;
- ajustar alturas, alcances y postura;
- usar dispositivos de sujeción en lugar de la mano;
- reducir la duración y frecuencia mediante organización, rotación y micropausas; y
- verificar que la medida controle efectivamente la exposición.

Los guantes u otros EPP son complementarios y no sustituyen el control de la fuente o el rediseño.

## Referencias y advertencia profesional

- [Resolución SRT 886/2015 — Protocolo de Ergonomía](https://www.argentina.gob.ar/normativa/nacional/norma-246272/texto), especialmente la Planilla 2I.
- [Resolución MTEySS 295/2003](https://www.argentina.gob.ar/normativa/nacional/resoluci%C3%B3n-295-2003-90396/texto).
- [Portal oficial SRT — Protocolo, guía y formularios](https://www.argentina.gob.ar/srt/prevencion/publicaciones/protocolos/ergonomia).

La matriz y los umbrales aquí explicados describen el **motor actualmente implementado en ErgoApp**. No constituyen por sí solos un límite legal de presión de contacto ni reemplazan la evaluación integral, la vigilancia de la salud, la revisión de la normativa vigente o la intervención y firma de los profesionales responsables.
