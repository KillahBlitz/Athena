# tablas_completas.xlsx — catálogo de áreas, carreras y escuelas

[Índice de documentación](../../../../../index.md) · [Abrir archivo original](../../../../../../Scripts/python/assets/layouts/excel/tablas_completas.xlsx)

**Archivo documentado:** `Scripts/python/assets/layouts/excel/tablas_completas.xlsx`  
**Revisión:** 2026-10-19. Descripción basada en el contenido local; no implica una ejecución del archivo.

Es el libro fuente de [02_generalte_construct_sql.ipynb](../../../jupyter/02_generalte_construct_sql.ipynb.md). Contiene la identificación estable de las 66 carreras y su relación con áreas y escuelas. También permite asociar los nombres numéricos de los PDF/Markdown con una carrera; la asociación documentada procede de `carreras.id_carrera`, no de suponer el orden alfabético.

## Hojas y estructura observadas

Los conteos excluyen encabezados y filas completamente vacías. No se encontraron celdas con fórmulas en las hojas inspeccionadas.

### `area`

**Registros:** 3. **Columnas:** 2.

- `id_area`
- `nombre_area`

### `carreras`

**Registros:** 66. **Columnas:** 7.

- `id_carrera`
- `nombre_carrera`
- `id_area`
- `objetivo_resumido`
- `pregunta`
- `habilidad_central`
- `objetivo`

### `escuelas`

**Registros:** 26. **Columnas:** 2.

- `id_escuela`
- `nombre_escuela`

### `carrera_escuelas`

**Registros:** 79. **Columnas:** 2.

- `id_carrera`
- `id_escuela`

## Relaciones y uso

`carreras.id_area` enlaza con `area.id_area`; `carrera_escuelas` une carreras y escuelas. Hay 43 carreras del área 1, 12 del área 2 y 11 del área 3. Los IDs de carrera 1–66 corresponden a los nombres de archivo PDF/Markdown.

El notebook 02 exporta los objetivos y preguntas, pero no `habilidad_central`. Las hojas actuales tienen orden `area`, `carreras`, `escuelas`, `carrera_escuelas`; la generación respeta ese orden. Agregar una hoja sin ampliar el selector provoca error.

Los textos originales y resumidos son distintos campos. No intercambiar `objetivo` y `objetivo_resumido` al actualizar el libro. Cambiar IDs afecta las relaciones, las fichas de programa y los catálogos usados por el generador sintético.

## Archivos relacionados

- [02 — catálogos a SQL](../../../jupyter/02_generalte_construct_sql.ipynb.md)
- [03 — extracción de perfiles](../../../jupyter/03_extract_criteria_for_careers.ipynb.md)
- [04 — contrato de carga](../../../jupyter/04_submit_criteria_from_sql.ipynb.md)
