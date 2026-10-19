# prompt.md — instrucciones para extraer criterios de perfil

[Índice de documentación](../../../../index.md) · [Abrir archivo original](../../../../../Scripts/python/assets/prompts/prompt.md)

**Archivo documentado:** `Scripts/python/assets/prompts/prompt.md`  
**Revisión:** 2026-10-19. Descripción basada en el contenido local; no implica una ejecución del archivo.

Es la especificación textual que [03_extract_criteria_for_careers.ipynb](../../jupyter/03_extract_criteria_for_careers.ipynb.md) envía como instrucción de sistema a Gemini. Define cómo transformar los perfiles de ingreso y egreso en criterios RIASEC y registrar su evidencia. No es un script ejecutable ni contiene los parámetros del dataset sintético del notebook 05.

## Contrato de entrada e identificación

El prompt describe PDF con nombre numérico, del que se obtiene `carrera_id`; el nombre de la carrera debe salir del contenido. En el flujo implementado, los PDF ya fueron convertidos a Markdown y el notebook pasa el mismo ID explícitamente. Sus ejemplos de IDs y carreras son ilustrativos: no sustituyen el catálogo real de [tablas_completas.xlsx](../layouts/excel/tablas_completas.xlsx.md).

## Reglas principales

- Por carrera: exactamente una R, I, S, E y C, y cero o una A. Todos los registros de este proceso llevan `type_id=1`.
- PERFIL combina evidencia de ingreso y egreso y selecciona la competencia más representativa de cada dimensión.
- INTERNET solo completa las dimensiones obligatorias ausentes; prioriza fuentes oficiales, institucionales, curriculares y académicas verificables.
- CONTINGENCIA construye una habilidad genérica del área cuando las dos etapas anteriores no bastan; registra la decisión en observaciones.
- Artística no se completa con Internet ni contingencia. No se inventa `criterio_id`; la DB lo asigna posteriormente.

## Normalización

La descripción se formula como verbo en infinitivo + objeto + contexto disciplinar. Se eliminan sujetos y adornos que no cambian el significado y se unifican equivalencias semánticas. Segmentar habilidades no autoriza producir varias filas finales de la misma dimensión: la selección debe conservar una sola por dimensión.

`resumen_criterio` deriva de la descripción, conserva su significado y debe ser más corto; se proponen 2–8 palabras y un máximo de 12. El archivo pide preservar trazabilidad para INTERNET mediante título, institución, URL, fecha y evidencia.

## Salidas y adaptación del consumidor

El prompt pide un Excel con `criterios`, `fuentes` y `cobertura_riasec`. En el notebook 03, las instrucciones de etapa reemplazan esa parte por JSON por carrera; Python arma el Excel. Las columnas y las relaciones se detallan en [resultado_criterios.xlsx](../media/extraction_result/resultado_criterios.xlsx.md).

La tabla de `cobertura_riasec` admite textualmente INTERNET para A, contradiciendo la prohibición general del propio prompt. El notebook aplica la restricción general: A únicamente de PERFIL, y un `assert` lo comprueba. Esta inconsistencia se documenta sin modificar el archivo.

## Reutilización

Un cambio del prompt no invalida automáticamente los JSON existentes en `raw/`. Revisar las cachés antes de volver a extraer. El prompt es una instrucción al modelo: la validación Python comprueba estructura y algunos invariantes, pero no certifica automáticamente cada evidencia ni la calidad semántica de todos los criterios.

## Archivos relacionados

- [03 — implementación del proceso](../../jupyter/03_extract_criteria_for_careers.ipynb.md)
- [Excel de resultados](../media/extraction_result/resultado_criterios.xlsx.md)
- [Consolidado utilizado para carga](../layouts/excel/criterios.xlsx.md)
