# resultado_criterios.xlsx — resultado de extracción RIASEC

[Índice de documentación](../../../../../index.md) · [Abrir archivo original](../../../../../../Scripts/python/assets/media/extraction_result/resultado_criterios.xlsx)

**Archivo documentado:** `Scripts/python/assets/media/extraction_result/resultado_criterios.xlsx`  
**Revisión:** 2026-10-19. Descripción basada en el contenido local; no implica una ejecución del archivo.

Es la salida local existente de [03_extract_criteria_for_careers.ipynb](../../../jupyter/03_extract_criteria_for_careers.ipynb.md): 331 criterios de perfil, 26 fuentes externas y 66 filas de cobertura. No incluye criterios principales ni las columnas de porcentajes y repeticiones de usuarios. No equivale al libro que carga el notebook 04.

## Hojas y estructura observadas

Los conteos excluyen encabezados y filas completamente vacías. No se encontraron celdas con fórmulas en las hojas inspeccionadas.

### `criterios`

**Registros:** 331. **Columnas:** 7.

- `carrera_id`
- `type_id`
- `riasec_id`
- `desc_criterio`
- `resumen_criterio`
- `origen`
- `fuente_id`

### `fuentes`

**Registros:** 26. **Columnas:** 9.

- `fuente_id`
- `carrera_id`
- `riasec_id`
- `type_id`
- `titulo_fuente`
- `institucion`
- `url`
- `fecha_consulta`
- `evidencia_utilizada`

### `cobertura_riasec`

**Registros:** 66. **Columnas:** 12.

- `carrera_id`
- `nombre_carrera`
- `R`
- `I`
- `A`
- `S`
- `E`
- `C`
- `dimensiones_completadas_por_contingencia`
- `dimensiones_faltantes`
- `estado`
- `observaciones`

## Distribución y trazabilidad

Hay 303 criterios de origen PERFIL, 26 INTERNET y 2 CONTINGENCIA. Las dimensiones R/I/S/E/C tienen 66 filas cada una; A tiene una. Las 26 filas de `fuentes` respaldan las extracciones externas mediante `fuente_id`. La cobertura indica 64 carreras completas con evidencia y dos completas con contingencia.

`criterios.fuente_id` debe apuntar a `fuentes.fuente_id` solo para INTERNET. `cobertura_riasec` registra una fila por carrera. `type_id=1` en todas las filas de criterios: este archivo por sí solo no aporta la habilidad principal requerida por el dataset sintético.

El notebook 03 sobrescribe el archivo al terminar; cambiar solo este Excel no cambia su caché JSON ni los Markdown fuente. El notebook 04 no lo carga directamente: espera otra hoja, seis columnas y los 66 principales adicionales en `criterios.xlsx`.

## Archivos relacionados

- [02 — catálogos a SQL](../../../jupyter/02_generalte_construct_sql.ipynb.md)
- [03 — extracción de perfiles](../../../jupyter/03_extract_criteria_for_careers.ipynb.md)
- [04 — contrato de carga](../../../jupyter/04_submit_criteria_from_sql.ipynb.md)
