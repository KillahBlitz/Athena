# Preparación de la información y desarrollo de los modelos

**Estado:** especificación documental; no acredita implementación ni resultados.

**Fuente:** document.md · Preparación de la información y desarrollo de los modelos.

## ETL y catálogo del IPN

1. Recopilar los perfiles de ingreso oficiales incluidos en el alcance.
2. Extraer áreas, carreras, escuelas y habilidades.
3. Revisar duplicados y homologar términos equivalentes.
4. Conservar las relaciones habilidad–carrera y carrera–escuela.
5. Cargar información estructurada y limpia para entrenamiento y recuperación.
6. Documentar procedencia, estructura, preparación y criterios de revisión.

Las actualizaciones del catálogo son manuales; el flujo de evaluación usa datos previamente integrados.

## Conjuntos de datos y etiquetado

Mantener separados tres recursos:

| Conjunto | Uso | Documentación requerida |
| --- | --- | --- |
| Catálogo de habilidades | Contexto de RAG | Procedencia, términos y área |
| Ejemplos vocacionales | Ajuste fino | Experiencias, habilidades esperadas y revisión |
| Registros etiquetados | Entrenamiento y evaluación del clasificador | Características, carrera, asignación de etiqueta y consistencia |

Separar entrenamiento, validación y prueba; reservar prueba para evaluación final. Definir cómo combinar habilidades autodeclaradas y extraídas. Los tamaños, etiquetas definitivas y procedimiento de muestreo siguen pendientes.

## Enlaces

- [[index-tesis|Volver al índice de tesis]]
