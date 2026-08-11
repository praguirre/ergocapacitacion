# Documentación de ErgoSolutions

Este directorio centraliza la documentación técnica, operativa e histórica del
proyecto. El `README.md` principal y `AGENTS.md` permanecen en la raíz por ser
puntos de entrada del repositorio y de los asistentes de desarrollo.

## Estado y auditoría

- [Auditoría de videos y firmantes documentales — 11/08/2026](AUDITORIA_CAPACITACIONES_VIDEOS_Y_FIRMANTES_2026-08-11.md):
  rastrea la regresión del reproductor, elimina el responsable fijo del
  certificado online y verifica las fuentes de identidad de documentos
  presenciales y planillas SRT 886/15.
- [**Estado técnico consolidado — 01/08/2026**](ESTADO_TECNICO_CONSOLIDADO_2026-08-01.md):
  **documento de referencia vigente y punto de partida para continuar el
  desarrollo.** Consolida la auditoría de producción con el estado real del
  código en `release/beta` (`v0.1.7-beta`), verifica los 27 hallazgos originales
  contra el código actual, documenta 13 hallazgos nuevos introducidos en la
  Etapa 3 y propone un plan de trabajo priorizado en 8 bloques.
- [Informe técnico de auditoría de producción — 30/07/2026](INFORME_TECNICO_AUDITORIA_PRODUCCION_2026-07-30.md):
  fotografía histórica del despliegue `v0.1.3-beta` auditado en esa fecha. No
  debe interpretarse como descripción automática del código local posterior.
- [Árbol del proyecto](project_tree.md): inventario de la estructura local al
  momento de su generación.

## Arquitectura y visión

- [Arquitectura y roadmap de escalamiento](ERGOSOLUTIONS_ARQUITECTURA_ROADMAP.md)
- [Mapa conceptual visual](MAPA_CONCEPTUAL_VISUAL.md)

## Planes de implementación

- [Plan maestro — Fases 1 y 2](PLAN_MAESTRO_COMMITS_GENERAL_FASES_1_2.md)
- [Plan maestro — Fases 3 a 6](PLAN_MAESTRO_COMMITS_FASES_3_4_5_6.md)
- [Plan maestro — Etapa 3: Perfil Empresa](PLAN_MAESTRO_ETAPA_3_PERFIL_EMPRESA.md)
- [Plan de capacitaciones personalizadas](PLAN_CAPACITACIONES_PERSONALIZADAS.md)

## Chat IA — contexto y datos

- [Propuesta técnica: contexto de pantalla y acceso a base de datos](PROPUESTA_CHAT_IA_CONTEXTO_Y_DATOS.md):
  diseño y auditoría de viabilidad. **Estado: borrador pendiente de aprobación.**
- [Roadmap de ejecución](ROADMAP_CHAT_IA_CONTEXTO_Y_DATOS.md): plan commit por commit.
- [Bitácora de ejecución](BITACORA_CHAT_IA_CONTEXTO_Y_DATOS.md): registro de trazabilidad.

## Operación y despliegue

- [Runbook de despliegue](DEPLOY_CLAUDE_RUNBOOK.md)
- [Plan de email de producción](PLAN_EMAIL_PRODUCCION.md): plan histórico ya
  ejecutado, conservado para trazabilidad.

## Criterio de organización

Los Markdown que forman parte del contenido funcional de una aplicación se
mantienen junto a su código:

- `apps/training/content/`
- `apps/ergobot_ai/prompts/`
