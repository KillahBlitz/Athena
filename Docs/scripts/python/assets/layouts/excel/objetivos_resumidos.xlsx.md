# objetivos_resumidos.xlsx — objetivos, preguntas y habilidades

[Índice de documentación](../../../../../index.md) · [Abrir archivo original](../../../../../../Scripts/python/assets/layouts/excel/objetivos_resumidos.xlsx)

**Archivo documentado:** `Scripts/python/assets/layouts/excel/objetivos_resumidos.xlsx`  
**Revisión:** 2026-10-19. Descripción basada en el contenido local; no implica una ejecución del archivo.

Libro auxiliar de revisión de objetivos resumidos, preguntas e identificación de la habilidad central de cada carrera. Tiene tres hojas con 66 registros cada una. No se encontró una lectura directa de este archivo en los cinco notebooks; el generador SQL consume la versión integrada en [tablas_completas.xlsx](tablas_completas.xlsx.md).

## Hojas y estructura observadas

Los conteos excluyen encabezados y filas completamente vacías. No se encontraron celdas con fórmulas en las hojas inspeccionadas.

### `Objetivos y preguntas`

**Registros:** 66. **Columnas:** 6.

- `Área`
- `Carrera`
- `Objetivo resumido`
- `Pregunta`
- `Habilidad central`
- `preguntas`

### `Habilidades centrales`

**Registros:** 66. **Columnas:** 2.

- `Habilidad central`
- `Número de carreras`

### `Hoja1`

**Registros:** 66. **Columnas:** 3.

- `area`
- `objetivos `
- `preguntas `

## Interpretación y límites

`Objetivos y preguntas` agrupa área, carrera, objetivo, pregunta y habilidad central; contiene tanto `Pregunta` como `preguntas`, que son columnas distintas. `Habilidades centrales` relaciona textos de habilidad con `Número de carreras`. `Hoja1` conserva una estructura alternativa de área/objetivos/preguntas. Los encabezados `objetivos ` y `preguntas ` incluyen un espacio final: conservarlo o ajustar el consumidor cuando se normalicen.

No contiene IDs numéricos de carrera en todas sus hojas, por lo que no se debe unir por posición sin comprobar los nombres y la relación con el catálogo principal. No hay script de sincronización con `tablas_completas.xlsx` entre los archivos revisados.

## Archivos relacionados

- [02 — catálogos a SQL](../../../jupyter/02_generalte_construct_sql.ipynb.md)
- [03 — extracción de perfiles](../../../jupyter/03_extract_criteria_for_careers.ipynb.md)
- [04 — contrato de carga](../../../jupyter/04_submit_criteria_from_sql.ipynb.md)
