## PASO 5: Seguimiento de Medidas Preventivas (Planilla 4)

Esta última planilla es la herramienta para **controlar la implementación** de las medidas definidas en la Planilla 3. Funciona como una matriz de seguimiento general.

* **¿Cómo se completa?** Por cada medida listada en una Planilla 3, se crea una fila en la Planilla 4, donde se registra el puesto de trabajo, el nivel de riesgo original y las fechas clave.
* **Columnas de Fechas:**
    * **Fecha de implementación:** El día en que la medida administrativa o de ingeniería se puso en práctica.
    * **Fecha de Cierre:** **¡La más importante!** No es la fecha de implementación. Es la fecha en que se **verifica que la medida fue efectiva**.
        > Para ello, se debe realizar una **reevaluación** del puesto dentro de los **30 días** posteriores a la implementación, con el objetivo de confirmar que el riesgo ha bajado a **Nivel 1 (Tolerable)** [361].

Una vez que se completa el cierre de todas las medidas, el ciclo del protocolo para ese puesto de trabajo ha finalizado, a la espera de la siguiente revisión anual o de que ocurra un cambio que amerite iniciar el proceso nuevamente.

---

### Diagrama de Flujo del Ciclo Completo del Protocolo de Ergonomía (Resolución SRT 886/15)

Este diagrama muestra el recorrido completo, desde la identificación inicial del riesgo hasta la verificación de las medidas correctivas, destacando la naturaleza cíclica y continua del protocolo. El formato utilizado para el diagrama de flujo es `mermaid`, que permite una representación clara y estructurada del proceso.

```mermaid
graph TD
    subgraph "Ciclo Anual de Gestión Ergonómica"
    
    A[Inicio del Ciclo de Evaluación Ergonómica] --> B{¿Es la revisión anual O<br>hubo un cambio/incidente*?};
    B --> C[PASO 1: Llenar Planilla 1<br>Identificación de Factores de Riesgo];
    C --> D{¿Se identificaron Factores de Riesgo?<br>(¿Hay alguna 'X' en la planilla?)};
    
    D -- NO --> E[FIN del ciclo actual.<br>Archivar Planilla 1.];
    E --> F[Reevaluar en 1 año<br>o si ocurre un cambio*];
    F --> A;
    
    D -- SI --> G[PASO 2: Llenar Planillas 2A a 2I<br>Evaluación Inicial];
    G -- "Para cada riesgo identificado ('X')" --> H{¿El resultado de la Planilla 2 es<br>'No Tolerable'?};
    
    H -- NO (Riesgo Tolerable) --> I[Registrar 'Nivel 1' en Planilla 1.<br>FIN del análisis para este riesgo.];
    
    H -- SI (Riesgo No Tolerable) --> J[PASO 3: Realizar Evaluación de Riesgos<br>por un Profesional en Ergonomía];
    J --> K[El profesional determina un Nivel de Riesgo<br><b>2 (Moderado)</b> o <b>3 (No Tolerable)</b>];
    K --> L[Registrar el Nivel 2 o 3 final en Planilla 1];
    
    L --> M[PASO 4: Llenar Planilla 3<br>Identificación de Medidas Correctivas];
    M -- "Definir plan de acción<br>(Ingeniería y Administrativas)" --> N[PASO 5: Iniciar Planilla 4<br>Matriz de Seguimiento];
    
    N --> O[Implementar las Medidas Correctivas];
    O --> P[Registrar 'Fecha de Implementación'<br>en la Planilla 4];
    
    P --> Q{<p style='text-align:center;'><b>Reevaluación<br>(Dentro de los 30 días posteriores a la implementación)</b></p>};
    Q --> R[Realizar una nueva Evaluación de Riesgos<br>para verificar la efectividad de la medida];
    R --> S{¿Se logró un<br>Nivel de Riesgo 1 (Tolerable)?};
    
    S -- NO --> T[Revisar y definir NUEVAS Medidas.<br>Volver a PASO 4 (Planilla 3)];
    T --> M;
    
    S -- SI --> U[Registrar 'Fecha de Cierre'<br>en la Planilla 4];
    U --> V[FIN del ciclo de mejora para<br>esta medida en particular.];
    
    end
    
    subgraph "Notas"
        Note1("<b>*Cambio/incidente:</b><br>- Cambios en el proceso, máquinas, etc.<br>- Reporte de enfermedad profesional.<br>- Accidente de trabajo.")
        Note2("El ciclo de evaluación debe repetirse como mínimo <b>una vez al año</b>.")
    end

    style A fill:#c9ffc9,stroke:#333,stroke-width:2px
    style F fill:#c9ffc9,stroke:#333,stroke-width:2px
    style V fill:#c9ffc9,stroke:#333,stroke-width:2px
    style T fill:#ffb3b3,stroke:#333,stroke-width:2px
    style J fill:#f9f99f,stroke:#333,stroke-width:2px
    style Q fill:#f9f99f,stroke:#333,stroke-width:2px