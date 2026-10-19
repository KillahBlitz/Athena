# 04_submit_criteria_from_sql.ipynb — carga del Excel de criterios a PostgreSQL

[Índice de documentación](../../../index.md) · [Abrir archivo original](../../../../Scripts/python/jupyter/04_submit_criteria_from_sql.ipynb)

**Archivo documentado:** `Scripts/python/jupyter/04_submit_criteria_from_sql.ipynb`  
**Revisión:** 2026-10-19. Descripción basada en el contenido local; no implica una ejecución del archivo.

Carga [criterios.xlsx](../assets/layouts/excel/criterios.xlsx.md), hoja `criterios_centrales`, en `public.criterios`. A pesar de su nombre, lee un Excel y utiliza SQL parametrizado; no toma un archivo `.sql` como entrada. Espera **397 registros: 331 de perfil y 66 principales**, para las carreras 1–66.

## Configuración y columnas

Busca `ROOT` desde el directorio del kernel hacia sus padres usando la existencia de `Scripts/python/jupyter/lib/set_envs.py`. Añade la carpeta Jupyter a `sys.path` e importa `DB_CONFIG` desde [set_envs.py](lib/set_envs.py.md). Requiere `openpyxl` y `psycopg2-binary`.

| Excel | PostgreSQL |
| --- | --- |
| `carrera_id` | `carrera_id` |
| `type_id` | `type_id` |
| `riasec_id` | `riasec_id` |
| `desc_criterio` | `desc_criterio` |
| `resumen_criterio` | `resumen_criterio` |
| `origen` | `type_extraction` |

PostgreSQL asigna `criterio_id`. El archivo no se debe sustituir directamente por [resultado_criterios.xlsx](../assets/media/extraction_result/resultado_criterios.xlsx.md): ese resultado tiene otras hojas/columnas y solo contiene criterios de perfil, con procedencias adicionales.

## `leer_criterios(path=EXCEL_PATH)`

Abre el libro en modo de lectura con fórmulas visibles, exige el encabezado exacto y omite filas totalmente vacías. Rechaza IDs no enteros o negativos; textos vacíos, con inicio `=` o con carácter nulo; resúmenes mayores de 100 caracteres; origen distinto de `PERFIL`; y claves `(carrera_id, type_id, riasec_id)` repetidas.

Comprueba las 397 filas, las carreras 1–66, la distribución de tipos y un principal de dimensión 0 por carrera. Cada carrera debe incluir R/I/S/E/C y puede incluir A. No recorta las descripciones para hacerlas pasar.

## `cargar_criterios(records, confirmar=False)`

1. Construye el conjunto esperado y abre una conexión con timeout de diez segundos.
2. En validación usa una sesión de solo lectura; en escritura bloquea `criterios` con `SHARE ROW EXCLUSIVE`.
3. Comprueba las FK contra `carreras`, `tipos_criterio` y `tipos_riasec`, y consulta los límites del esquema real.
4. Omite una clave existente solo si todo el contenido coincide. Una clave duplicada o distinta produce error.
5. En `confirmar=False`, devuelve pendientes/existentes y revierte la transacción sin insertar.
6. En `confirmar=True`, inserta pendientes con `execute_values`, comprueba todas las filas y confirma. Ante excepciones hace rollback.

El resultado incluye `excel`, `existentes_identicos`, `pendientes`, `insertados` y `confirmado`. Los límites locales son diez segundos para bloqueo y sesenta para sentencias.

## Orden de uso y efectos

La celda 7 del archivo realiza la validación. La celda 9 vuelve a leer el Excel, ejecuta `confirmar=True` y comprueba que ya no existan pendientes. Por tanto, **ejecutar todas las celdas escribe en la DB**. Repetir la carga de contenido idéntico debe omitirlo; diferencias no se sobrescriben automáticamente. No altera catálogos, secuencias, usuarios o resultados.

## Archivos relacionados

- [Contrato del Excel de entrada](../assets/layouts/excel/criterios.xlsx.md)
- [03 — extracción previa](03_extract_criteria_for_careers.ipynb.md)
- [05 — uso del catálogo de criterios](05_generate_dataset_trainee.ipynb.md)
- [Configuración de conexión](lib/set_envs.py.md)
