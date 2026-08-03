"""Módulo de Evaluación Ergonómica — Protocolo SRT 886/15.

Digitaliza de punta a punta el Protocolo de Ergonomía de la Resolución SRT
N° 886/15 de Argentina.

Contiene cuatro aplicaciones Django:

    planillas      Protocolo documental. Modelo raíz: Evaluacion.
                   Planilla 1 (matriz A-I), Planillas 2A-2I, Planilla 3
                   (medidas) y Planilla 4 (seguimiento).

    evaluaciones   13 factores cuantitativos con motor de cálculo
                   determinístico y trazabilidad normativa con SHA-256.

    exportaciones  Planillas en el formulario oficial de la SRT por
                   superposición, detalle técnico por factor, informes
                   profesionales con modelo de lenguaje y paquete ZIP.

    help_ai        Ayuda contextual estática (33 documentos Markdown) y
                   chat con streaming SSE.

--------------------------------------------------------------------------
CONDICIONES VINCULANTES — leer antes de modificar cualquier cosa acá dentro
--------------------------------------------------------------------------

CF-1  `help_ai` y `apps.ergobot_ai` NO se fusionan. Son productos distintos
      que comparten proveedor. Ninguna importa código de la otra.

CF-2  `evaluaciones/calculators.py` es la ÚNICA autoridad sobre niveles de
      riesgo. Ninguna vista, plantilla ni modelo de lenguaje puede calcular
      o sobrescribir un nivel. La única excepción es la revisión profesional
      registrada.

CF-3  `calc_data` se persiste íntegro, con `calculation_trace` y el SHA-256
      de cada artefacto normativo aplicado. Ninguna capa puede filtrarlo,
      truncarlo ni normalizarlo.

CF-4  Los datos personales no salen hacia el proveedor del modelo.
      `sanitize_payload()` y `CLAVES_PROHIBIDAS` se conservan sin excepciones.

CF-5  Un documento oficial nunca afirma lo que el profesional no respondió.
      Planilla no completada -> se descarga en blanco.

CF-6  Los documentos oficiales se producen exclusivamente por superposición
      sobre `res_srt_886_15-formulario.pdf`, con verificación de SHA-256.
      Está prohibido generarlos rellenando el `.xls` oficial.

Referencias:
    docs/INTEGRACION_MODULO_ERGONOMIA_886_PROPUESTA_TECNICA.md
    docs/ROADMAP_INTEGRACION_ERGONOMIA_886.md
"""
