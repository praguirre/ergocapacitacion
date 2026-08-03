# Contrato de fuentes de cálculo

Cada archivo JSON de este directorio es una fuente versionada declarada en
`evaluaciones.catalog.FACTOR_DEFINITIONS`.

## Metadatos obligatorios

La clave raíz `meta` contiene:

| Campo | Uso |
|---|---|
| `schema_version` | Versión semántica del contrato estructural del JSON. |
| `data_version` | Versión semántica de los valores contenidos. |
| `artifact_effective_date` | Fecha ISO desde la que la aplicación utiliza esta revisión. No declara por sí sola vigencia normativa. |
| `source` | Documento, método o criterio del que proceden los valores. |
| `source_url` | URL primaria cuando existe; `null` si no se identificó una publicación verificable. |
| `provenance_status` | Explicación explícita de si se trata de transcripción, aproximación o criterio interno. |
| `professional_approval` | Estado, responsable y fecha de la aprobación profesional registrada. |

Los estados de aprobación admitidos son:

- `approved`: requiere `approved_by` y `approved_at`;
- `pending`: la revisión fue identificada como necesaria y aún no consta; y
- `not_recorded`: el artefacto existe, pero el proyecto no posee evidencia
  nominal y fechada de una aprobación anterior.

No debe cambiarse un estado a `approved` sin conservar responsable y fecha.

## Trazabilidad del resultado

El SHA-256 no se guarda dentro del propio JSON porque eso generaría una
referencia circular. `data_source_info()` lo calcula sobre los bytes exactos
del archivo desplegado.

`run_for_instance()` y `apply_result()` incorporan en cada resultado:

```text
calculation_trace.schema_version
calculation_trace.engine_version
calculation_trace.factor_slug
calculation_trace.sources[].archivo
calculation_trace.sources[].data_version
calculation_trace.sources[].sha256
```

De esta forma un registro histórico permite identificar el motor y todos los
artefactos que participaron, incluso si el método devolvió `no_aplicable`.

## Cambio controlado

Al modificar estructura o valores:

1. actualizar `schema_version` o `data_version` según corresponda;
2. mantener fuente, procedencia y aprobación honestas;
3. ejecutar la suite `evaluaciones` y `help_ai`;
4. revisar el diff de los valores, no solo el formato JSON; y
5. registrar el cambio y su justificación en la documentación de mejoras.
