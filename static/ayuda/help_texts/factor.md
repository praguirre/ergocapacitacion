# Ayuda General — Evaluación Cuantitativa de un Factor

Esta es la guía de respaldo para los formularios de evaluación cuantitativa. Cada factor de ErgoApp debe mostrar una guía específica con sus campos, unidades y método de cálculo. Si aparece este texto en lugar de la guía del factor indicado en el título, puede existir una desalineación del contexto que conviene reportar.

La evaluación cuantitativa se realiza después de la identificación de la Planilla 1 y de la evaluación inicial de la Planilla 2 correspondiente. No reemplaza esas etapas ni convierte automáticamente su resultado en los niveles 1, 2 y 3 del protocolo.

---

## 1. Antes de cargar datos

1. Confirme la tarea y el factor que se están evaluando.
2. Seleccione una condición representativa o desfavorable conforme al método aplicable.
3. Reúna mediciones, tiempos, frecuencias, unidades y evidencia trazable.
4. Separe escenarios que tengan exposiciones sustancialmente diferentes.
5. Registre en **Observaciones** la fuente de cada dato y los supuestos utilizados.

No adapte datos reales para que encajen en una tabla. Si la situación queda fuera del alcance del método, documente la limitación y seleccione una metodología profesional apropiada.

## 2. Campos comunes

### Aplicable

Indica si el método corresponde a la situación evaluada. Cuando no aplique:

- desmarque la casilla;
- explique el motivo en Observaciones;
- prefiera **Guardar** para conservar el registro sin generar una comparación contradictoria.

La implementación actual no procesa esta casilla de manera uniforme en todas las calculadoras. Por eso, no interprete la marca por sí sola como una conclusión de “sin riesgo”.

### Observaciones

Incluya, como mínimo:

- tarea, fase, turno y población observada;
- fecha y duración del relevamiento;
- instrumentos, estado de calibración o técnica de observación;
- unidades y criterio de selección del escenario;
- variaciones, datos faltantes y supuestos;
- controles existentes y evidencia disponible.

### Payload JSON opcional

Algunos formularios muestran un campo avanzado en formato JSON. Utilícelo solo cuando la guía específica explique su estructura y exista un procedimiento técnico documentado. Un JSON mal formado impide guardar; en varios factores este payload queda registrado, pero no modifica el cálculo.

## 3. Guardar y calcular

- **Guardar:** conserva los datos sin ejecutar nuevamente la calculadora.
- **Guardar y calcular:** guarda las entradas, ejecuta el motor del factor y actualiza el nivel y `calc_data`.

Si modifica datos después de calcular y usa solamente **Guardar**, el nivel anterior puede seguir visible. Recalcule antes de utilizar el resultado en una conclusión o informe.

## 4. Nivel y trazabilidad

La insignia superior muestra el último `nivel_riesgo` guardado:

- **Bajo**
- **Medio**
- **Alto**
- **No aplicable**

No todos los métodos producen las cuatro categorías. Algunas calculadoras son binarias y otras incluyen una zona intermedia.

Abra **Ver trazabilidad (calc_data)** para revisar entradas procesadas, tabla o configuración utilizada, límites, cálculos intermedios, agravantes, advertencias y motivo de un resultado no aplicable.

Un nivel `no aplicable` significa que el método no pudo o no debía realizar la comparación. **No significa automáticamente riesgo bajo.**

Los niveles cuantitativos no se trasladan automáticamente a los niveles 1 —Tolerable—, 2 —Moderado— y 3 —No Tolerable— de la Planilla 1. Esa integración requiere revisión profesional.

## 5. Si aparece un error

- Revise los mensajes junto a cada campo.
- Confirme que los números sean finitos, no negativos cuando corresponda y estén expresados en la unidad indicada.
- Compruebe que selectores dependientes —por ejemplo distancia y frecuencia— formen una combinación admitida.
- No complete campos vacíos con cero salvo que cero sea una medición real y válida para el método.
- Si el formulario se guarda pero el nivel no cambia, confirme que utilizó **Guardar y calcular**.
- Si la trazabilidad contradice los datos visibles, no emita una conclusión: conserve evidencia y solicite revisión técnica.

## 6. Uso responsable del resultado

El motor evalúa únicamente los campos y reglas implementados para ese factor. No determina por sí solo:

- la representatividad del relevamiento;
- la validez del instrumento o método;
- la interacción con otros factores ergonómicos;
- el diagnóstico de síntomas;
- la suficiencia de las medidas de control;
- la clasificación documental final de la Planilla 1.

Los resultados deben integrarse con las Planillas 2, 3 y 4 y con la evaluación del puesto realizada por profesionales competentes.

## 7. Referencias y advertencia profesional

- [Resolución SRT 886/2015 — texto oficial](https://www.argentina.gob.ar/normativa/nacional/norma-246272/texto)
- [Resolución MTEySS 295/2003 — texto oficial](https://www.argentina.gob.ar/normativa/nacional/resoluci%C3%B3n-295-2003-90396/texto)
- [SRT — Protocolo de Ergonomía, guía y formularios](https://www.argentina.gob.ar/srt/prevencion/publicaciones/protocolos/ergonomia)

Esta ayuda describe el funcionamiento general de ErgoApp. No constituye un dictamen ergonómico, una certificación ni una homologación legal del software.
