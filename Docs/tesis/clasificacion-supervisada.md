# Clasificación supervisada

**Estado:** especificación documental; no acredita implementación ni resultados.

**Fuente:** document.md · Clasificación supervisada.

## Clasificador supervisado

1. Construir registros etiquetados que relacionen perfiles de habilidades y carreras.
2. Transformar respuestas y habilidades en variables numéricas o categóricas.
3. Definir la combinación de habilidades seleccionadas y extraídas.
4. Comparar algoritmos candidatos mediante entrenamiento, validación y prueba.
5. Aplicar validación cruzada y búsqueda de hiperparámetros con los datos de desarrollo.
6. Elegir un modelo por desempeño, generalización y viabilidad de integración.
7. Evaluar con exactitud, precisión, exhaustividad, F1 y matriz de confusión.

La predicción operativa se restringe al área seleccionada. Algoritmo final y representación de características están pendientes.

## Afinidad y construcción de recomendaciones

Ordenar las carreras por coincidencia y presentar tres opciones con nombre, posición, porcentaje y escuelas.

Debe definirse y justificarse la transformación de la salida del modelo a porcentaje y el umbral mínimo para recomendar. La afinidad representa la correspondencia calculada por el método.

Si no se alcanza coincidencia suficiente, ofrecer reintento o cambio de área. Falta definir qué hacer si solo una o dos carreras cumplen el umbral y cómo resolver empates.

## Enlaces

- [[index-tesis|Volver al índice de tesis]]
