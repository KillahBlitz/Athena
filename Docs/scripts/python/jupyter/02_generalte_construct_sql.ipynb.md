# 02_generalte_construct_sql.ipynb — generación del SQL de catálogos

[Índice de documentación](../../../index.md) · [Abrir archivo original](../../../../Scripts/python/jupyter/02_generalte_construct_sql.ipynb)

**Archivo documentado:** `Scripts/python/jupyter/02_generalte_construct_sql.ipynb`  
**Revisión:** 2026-10-19. Descripción basada en el contenido local; no implica una ejecución del archivo.

Lee [tablas_completas.xlsx](../assets/layouts/excel/tablas_completas.xlsx.md) y construye `DataBase/scripts/insert_data.sql`. Genera SQL en disco; no abre una conexión ni ejecuta las inserciones. Se conserva el nombre original `generalte` del notebook.

## Entradas, salidas y dependencias

`RUTA_EXCEL` vale `../assets/layouts/excel/tablas_completas.xlsx`, relativo al directorio de trabajo del kernel. `RUTA_SQL_OUTPUT` es una ruta absoluta del equipo a `DataBase/scripts`; la celda de ejecución crea esa carpeta si falta. Requiere `pandas` y el motor Excel `openpyxl`.

## Transformación por hoja

| Hoja | Tabla destino | Mapeo principal |
| --- | --- | --- |
| `area` | `public.areas` | `id_area → area_id`, `nombre_area → nom_area` |
| `escuelas` | `public.escuelas` | `id_escuela → escuela_id`, `nombre_escuela → nom_escuela` |
| `carreras` | `public.carreras` | `id_carrera → carrera_id`, `id_area → area_id`, `nombre_carrera → nom_carrera` |
| `carrera_escuelas` | `public.escuela_carrera` | `id_escuela`, `id_carrera` |

En carreras, `objetivo` del Excel se guarda en `origina_objetivo`, `objetivo_resumido` en `objetivo` y `pregunta` en `pregunta_objetivo`. `habilidad_central` no se exporta. El nombre `origina_objetivo` se conserva porque así lo espera el SQL.

## Clase `Extractor`

| Método | Responsabilidad |
| --- | --- |
| `__init__` | Convierte rutas a `Path` y lee todas las hojas con `pd.read_excel(..., sheet_name=None)` |
| `extract` | Recorre las hojas, selecciona un extractor y entrega el contenido a `_save_sql` |
| `_extract_areas` | Inserciones de áreas con IDs explícitos |
| `_extract_escuelas` | Inserciones de escuelas |
| `_extract_carreras` | Inserciones de carreras y sus tres textos de objetivo/pregunta |
| `_extract_escuela_carrera` | Inserciones de relaciones escuela-carrera |
| `_save_sql` | Une las secciones y sobrescribe `insert_data.sql` en UTF-8 |

Cada extractor devuelve un `INSERT` con múltiples tuplas, rodeado por su propio `BEGIN`/`COMMIT`. Las comillas simples del texto se duplican. `extract()` escribe el archivo y no devuelve el SQL, aunque su anotación sea `-> str`.

## Orden y controles reales

El libro inspeccionado tiene 3 áreas, 66 carreras, 26 escuelas y 79 relaciones. Sus hojas están en orden `area`, `carreras`, `escuelas`, `carrera_escuelas`; el script respeta ese orden. Carrera depende de área; la relación se inserta después de escuelas y carreras.

Una hoja desconocida produce `ValueError`. El código espera exactamente los nombres de hoja en minúsculas al acceder a `self.data`, aunque el selector utilice `sheet_name.lower()`. No valida exhaustivamente nulos, duplicados o existencia de IDs en PostgreSQL y no implementa `ON CONFLICT`.

Las transacciones son por sección, no una transacción para todo el archivo: si posteriormente se ejecuta el SQL y falla una sección, las anteriores pueden estar confirmadas. Revisar el SQL antes de cargarlo. La celda de ejemplo que muestra `psql` es texto explicativo, no una ejecución automática.

## Archivos relacionados

- [Libro fuente](../assets/layouts/excel/tablas_completas.xlsx.md)
- [04 — carga separada de criterios](04_submit_criteria_from_sql.ipynb.md)
- [Dependencias](../assets/requirements.txt.md)
