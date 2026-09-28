# Procesamiento de lenguaje natural

**Estado:** especificación documental; no acredita implementación ni resultados.

**Fuente:** document.md · Procesamiento de lenguaje natural.

## PLN y homologación de habilidades

Analizar respuestas abiertas STAR para identificar evidencias de habilidades y asociarlas a entradas del catálogo. Integrar las habilidades extraídas como entrada del clasificador.

El flujo combina un modelo fundacional ajustado al dominio y recuperación RAG restringida al área elegida. Debe diferenciar información insuficiente de ausencia de habilidades.

Pendientes: modelo base, formato de salida, criterio de suficiencia y evaluación de la calidad de extracción.

## Ajuste fino del modelo de lenguaje

Preparar y revisar ejemplos del dominio vocacional que relacionen experiencias narradas con habilidades esperadas. Ajustar un modelo fundacional a la terminología y al contexto de las respuestas.

Documentar modelo base, versión del conjunto, configuración de entrenamiento y evaluación. Estos detalles aún no están especificados por las fuentes; no se presupone un proveedor ni un modelo concreto.

## RAG y recuperación por área

Consultar el catálogo de habilidades como conocimiento externo durante la interpretación de respuestas. La recuperación debe limitarse al área seleccionada y fundamentar la extracción en entradas existentes.

PostgreSQL y pgvector almacenan información y representaciones vectoriales.

Pendientes: modelo de embeddings, estrategia de indexación, cantidad de entradas recuperadas y criterio de relevancia; la fuente no fija esos valores.

## Enlaces

- [[index-tesis|Volver al índice de tesis]]
