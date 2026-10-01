# Base de datos y modelo entidad-relación

**Estado:** especificación documental; no acredita implementación ni resultados.

**Fuente:** document.md y powerpoint.md · objetivo específico 1 y preparación; diapositiva 13. Véase [[tesis/referencias#Fuentes, cobertura y decisiones pendientes|Fuentes y pendientes]].

## Entidades y relaciones requeridas

- Áreas académicas, carreras, escuelas y catálogo de habilidades.
- Relación entre habilidades de ingreso y carreras.
- Asociación entre carreras y escuelas que las ofertan.
- Datos de entrenamiento y resultados de evaluaciones.
- Representaciones vectoriales para recuperación.

Usar PostgreSQL y pgvector, normalizar el esquema y conservar relaciones consistentes.

El diagrama de la diapositiva está referenciado como imagen: las claves, cardinalidades y restricciones concretas deben documentarse cuando se recupere o se diseñe el esquema. No se infieren de la imagen ausente.

## Enlaces

- [[tesis/preparacion-de-la-informacion#ETL y catálogo del IPN|ETL y catálogo del IPN]]
- [[tesis/preparacion-de-la-informacion#Conjuntos de datos y etiquetado|Conjuntos de datos y etiquetado]]
- [[tesis/requisitos-implementacion#RIM D · Tecnologías de Base de datos|RIM D · Tecnologías de Base de datos]]
- [[index-tesis|Volver al índice de tesis]]
