# criterios.xlsx — criterios consolidados para PostgreSQL

[Índice de documentación](../../../../../index.md) · [Abrir archivo original](../../../../../../Scripts/python/assets/layouts/excel/criterios.xlsx)

**Archivo documentado:** `Scripts/python/assets/layouts/excel/criterios.xlsx`  
**Revisión:** 2026-10-19. Descripción basada en el contenido local; no implica una ejecución del archivo.

Es la entrada directa de [04_submit_criteria_from_sql.ipynb](../../../jupyter/04_submit_criteria_from_sql.ipynb.md). La hoja `criterios_centrales` contiene 397 filas: 331 perfiles (`type_id=1`) y 66 principales (`type_id=2`, `riasec_id=0`). Las 66 carreras tienen principal y R/I/S/E/C; Optometría, carrera 50, tiene además Artística. Todos los registros del archivo inspeccionado declaran `origen=PERFIL`.

## Hojas y estructura observadas

Los conteos excluyen encabezados y filas completamente vacías. No se encontraron celdas con fórmulas en las hojas inspeccionadas.

### `catalogo_tipos`

**Registros:** 2. **Columnas:** 2.

- `id`
- `tipo`

### `criterios_centrales`

**Registros:** 397. **Columnas:** 6.

- `carrera_id`
- `type_id`
- `riasec_id`
- `desc_criterio`
- `resumen_criterio`
- `origen`

## Contrato con el cargador

El notebook 04 solo lee `criterios_centrales`; `catalogo_tipos` sirve de referencia. Requiere exactamente las seis columnas y su orden, 397 filas, origen PERFIL y resúmenes de hasta 100 caracteres. `origen` se guarda en `type_extraction`; no se debe añadir un `criterio_id` a la hoja de carga.

El Excel de extracción tiene 303 registros PERFIL, 26 INTERNET y 2 CONTINGENCIA, mientras este consolidado declara 397 PERFIL e incorpora los 66 principales. Los notebooks actuales no contienen la transformación que produce este consolidado a partir de aquel resultado. La diferencia de procedencia debe revisarse al actualizar el archivo; no atribuir esa conversión automáticamente al notebook 03.

## Archivos relacionados

- [02 — catálogos a SQL](../../../jupyter/02_generalte_construct_sql.ipynb.md)
- [03 — extracción de perfiles](../../../jupyter/03_extract_criteria_for_careers.ipynb.md)
- [04 — contrato de carga](../../../jupyter/04_submit_criteria_from_sql.ipynb.md)
