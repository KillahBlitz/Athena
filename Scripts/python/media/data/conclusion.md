**Conclusión: las tres áreas tienen volumen para iniciar un experimento de Random Forest, pero el dataset actual todavía no permite demostrar que el modelo recomendará bien carreras a usuarios nuevos. La prioridad es mejorar la construcción y validación del dataset, no aumentar indiscriminadamente el número de filas.**

Consulta de PostgreSQL: **29 de septiembre de 2026, 06:48:58 UTC** (00:48:58 de Ciudad de México). Se usó una transacción `REPEATABLE READ` y `READ ONLY`. No se insertaron, actualizaron ni eliminaron registros. Estos resultados corresponden a esa consulta, no a los conteos de conversaciones anteriores.

**Cantidad y cobertura por área**

| Área | Usuarios distintos | Carreras | Usuarios con resultado por carrera: mínimo–máximo | Promedio por carrera | Habilidades del catálogo observadas | Evaluación del volumen |
|---|---:|---:|---:|---:|---:|---|
| 1. Ingeniería y Ciencias Físico Matemáticas | 3,225 | 43 | 54–93 | 75.0 | 166 de 166 | Permite un piloto; las 43 carreras distribuyen el volumen entre muchas categorías. |
| 2. Ciencias Médico Biológicas | 900 | 12 | 53–100 | 75.0 | 51 de 51 | Permite un piloto acotado; la evaluación por carrera tendrá pocas observaciones. |
| 3. Ciencias Sociales y Administrativas | 901 | 11 | 65–98 | 81.9 | 45 de 45 | Permite un piloto acotado; falta diversidad de perfiles y evaluación comparativa. |

Hay **5,026 usuarios y 5,026 resultados**. Cada usuario tiene exactamente un resultado, marcado `top = 1`. Las 77,012 filas de `usuario_habilidad` incluyen repeticiones: **no representan 77,012 usuarios independientes**. Tampoco puede asumirse independencia estadística solo por tener identificadores distintos.

No existe un mínimo universal de usuarios que garantice un Random Forest adecuado. La suficiencia depende de la diversidad de entradas, las etiquetas, la complejidad de la tarea y el error aceptable. Debe comprobarse con usuarios reservados para evaluación y curvas de aprendizaje; estas permiten observar si añadir usuarios sigue reduciendo el error. [Documentación oficial sobre curvas de aprendizaje](https://scikit-learn.org/stable/modules/learning_curve.html).

**Calidad e integridad observadas**

En las tres áreas, todos los usuarios tienen habilidades y resultado. No se encontraron habilidades o carreras asignadas fuera del área del usuario, cumplimientos nulos o fuera de `[0,1]`, resultados fuera de esa escala, habilidades del catálogo sin criterios ni pares usuario–habilidad con más de cinco repeticiones. Los cumplimientos son compatibles con fracciones del número de criterios, considerando su redondeo. Tampoco se encontraron usuarios sin área válida ni filas huérfanas en las relaciones auditadas.

Estas comprobaciones validan consistencia interna. No prueban que las repeticiones procedan de cinco formularios independientes: `usuario_habilidad` no identifica el formulario ni conserva las respuestas individuales a criterios.

| Área | Media del resultado almacenado | Usuarios con 0 % | Con 20 % | Con 100 % | Carreras con al menos un usuario al 100 % |
|---|---:|---:|---:|---:|---:|
| 1 | 56.25 % | 26 (0.81 %) | 15 (0.47 %) | 119 | 43 de 43 |
| 2 | 56.30 % | 14 (1.56 %) | 5 (0.56 %) | 28 | 12 de 12 |
| 3 | 56.23 % | 8 (0.89 %) | 9 (1.00 %) | 32 | 11 de 11 |

Los picos masivos de 0 % y 20 % descritos anteriormente no aparecen en esta consulta. Los diez intervalos de 10 puntos porcentuales contienen observaciones en cada área. Hay entre 98 y 99 valores distintos de resultado por área. Los casos perfectos cumplen la condición de cobertura solicitada, pero por sí solos no acreditan la calidad de una recomendación.

Una distribución de aspecto suave no es un requisito de Random Forest ni demuestra que el entrenamiento será bueno. Tampoco conviene alterar resultados reales solamente para obtener una campana.

**La etiqueta actual usa el máximo por habilidad, no la media de sus repeticiones**

El recálculo desde la DB confirma esta regla en los 5,026 resultados, dentro de una tolerancia de 0.0051 en escala `[0,1]` por el almacenamiento con dos decimales:

```text
frecuencia(u,h) = COUNT de registros de esa habilidad para el usuario
cumplimiento(u,h) = MAX(cumplimiento_criterio)
coincidencia(u,c) = SUM(frecuencia × cumplimiento) / SUM(frecuencia)
```

Las sumas se restringen a las habilidades de la carrera. En los resultados auditados no faltan habilidades requeridas; por ello, estos datos no permiten validar cómo debería tratarse una habilidad ausente.

Si se sustituye `MAX` por `AVG` de las repeticiones, cambian sustancialmente las etiquetas:

| Área | Resultados que difieren de AVG ponderado, más allá del redondeo | Diferencia absoluta media |
|---|---:|---:|
| 1 | 3,071 de 3,225 | 17.76 puntos porcentuales |
| 2 | 860 de 900 | 18.09 puntos porcentuales |
| 3 | 866 de 901 | 18.15 puntos porcentuales |

**Antes de entrenar debe fijarse cuál es la regla de negocio.** Si se conserva el mayor cumplimiento y la frecuencia como peso, la DB es coherente con esa decisión. Si se quiere promediar primero todas las repeticiones, habrá que recalcular las etiquetas. Este análisis no cambió ninguna.

**El problema principal: los perfiles ya contienen la estructura de la carrera asignada**

Los 5,026 usuarios tienen exactamente el conjunto de habilidades requeridas por su única carrera registrada: no hay habilidades faltantes ni adicionales respecto de esa carrera. Aunque sus frecuencias y cumplimientos producen perfiles numéricos distintos, solo hay **43, 12 y 11 combinaciones de identificadores de habilidad**, respectivamente: una por carrera en cada área.

Esto coincide con la estructura de los generadores locales `data_set_area_1.py`, `data_set_area_2.py` y `data_set_area_3.py`: seleccionan una carrera y construyen un usuario a partir de todas sus habilidades. La DB no incluye una marca de procedencia que permita distinguir de forma concluyente registros reales de sintéticos.

La consecuencia es que un clasificador podría reconocer la carrera por el conjunto de habilidades usado para crear el registro, incluso cuando el cumplimiento es bajo. Una exactitud alta en otra muestra del mismo generador demostraría principalmente que aprendió esa construcción. No demostraría que puede orientar perfiles mixtos, incompletos o distintos a las plantillas.

**Faltan comparaciones entre carreras del mismo universo**

| Área | Pares usuario–carrera almacenados | Pares posibles dentro del área | Cobertura |
|---|---:|---:|---:|
| 1 | 3,225 | 138,675 | 2.33 % |
| 2 | 900 | 10,800 | 8.33 % |
| 3 | 901 | 9,911 | 9.09 % |

El `top = 1` actual es una asignación, no evidencia de una comparación con las demás carreras. Incluso los usuarios con 0 % tienen una carrera etiquetada como primera. La gráfica adjunta representa el máximo **almacenado** por usuario; al existir un solo resultado, no representa el máximo calculado entre todas las carreras del área.

Para aprender a puntuar candidatos y ordenarlos, conviene construir ejemplos usuario–carrera con alternativas del mismo `id_area`, incluidos casos de cumplimiento bajo, parcial y alto. Se pueden evaluar todas las carreras o muestrear alternativas con un criterio documentado. Los pares no registrados son desconocidos, no etiquetas de cero automáticas. Expandirlos tampoco aumenta el número de personas independientes: seguirán siendo 5,026 usuarios.

**Qué hacer antes del primer entrenamiento útil**

1. **Definir el objetivo y la etiqueta.** Para predecir el porcentaje se plantea una regresión. Si el porcentaje se determina completamente por una fórmula y todas sus entradas están disponibles, usar la fórmula directamente como referencia: un bosque solo la aproximaría. Para medir adecuación vocacional se requieren etiquetas independientes, por ejemplo evaluaciones profesionales o resultados posteriores; una coincidencia calculada no equivale a éxito o satisfacción académica.
2. **Mantener cerrado el universo por `id_area`.** Preparar y evaluar datos por área, con candidatos y habilidades válidos para ella. No confiar únicamente en que el modelo aprenda a respetar esa restricción.
3. **Ampliar la diversidad de perfiles.** Añadir usuarios con mezclas de habilidades de varias carreras de su área, cobertura parcial, intereses compartidos, distintas frecuencias y casos ambiguos. Distinguir habilidad no evaluada de incumplimiento confirmado. Generar más copias de las mismas combinaciones actuales no resuelve esta limitación.
4. **Construir comparaciones dentro del área.** Incluir para cada usuario varias carreras candidatas y sus etiquetas según la regla acordada. Reservar una evaluación separada de perfiles reales; documentar qué filas son sintéticas, su generador y versión, y las variantes que comparten un perfil de origen.
5. **Separar entrenamiento y evaluación por usuario, nunca por fila de habilidad o par usuario–carrera.** Si hay variantes de un mismo perfil base, mantener también ese origen en un único grupo. Ajustar transformaciones y seleccionar parámetros usando solo entrenamiento y validación. [GroupShuffleSplit](https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.GroupShuffleSplit.html) y [prevención de fuga de información](https://scikit-learn.org/stable/common_pitfalls.html).
6. **Medir el resultado y decidir si hacen falta más usuarios.** Comparar con una predicción constante y con la fórmula vigente; medir MAE en puntos porcentuales por área, carrera e intervalos de cumplimiento. Para recomendaciones, evaluar la ordenación de carreras con referencias independientes y métricas como acierto entre las primeras opciones o NDCG. Usar curvas de aprendizaje y variabilidad entre particiones agrupadas. Recoger más usuarios diferentes donde el error sea alto o la incertidumbre amplia; no fijar una cuota universal sin evidencia.

Una separación ilustrativa de aproximadamente 80/20 dejaría 645 usuarios de evaluación en el área 1, 180 en la 2 y 181 en la 3. Al distribuirlos entre carreras habría, en promedio, apenas 15–16 usuarios por carrera. Es útil para un piloto, pero puede producir métricas por carrera muy variables. Esos tamaños son ilustrativos: no se realizó una partición ni se entrenó un modelo durante esta auditoría.

**Decisión por área:** área 1 tiene mayor volumen total, pero una cobertura por carrera parecida a las otras dos; áreas 2 y 3 permiten empezar pruebas pequeñas. **Ninguna queda validada todavía para una recomendación vocacional confiable.** Resolver la definición de etiqueta, los perfiles de plantilla y las comparaciones entre carreras es más urgente que ampliar el total. La cantidad adicional necesaria debe determinarse con evaluación independiente, no a partir de la forma del histograma.

**Evidencia y reproducción**

- [Resumen por área](resumen_por_area.csv): cantidades y verificaciones de calidad.
- [Cobertura por carrera](cobertura_por_carrera.csv): usuarios, casos perfectos y medias por carrera.
- [Distribuciones por área](distribuciones_por_area.csv): intervalos `[0,10)`, …, `[90,100]`.
- [Gráfica de distribuciones](distribuciones_por_area.png): porcentajes almacenados por usuario.
- [Auditoría completa en JSON](analisis_datos.json): fecha de consulta y métricas.
- [Script de solo lectura](../../get_distribution_data.py): ejecutar desde la raíz del proyecto con `python Scripts/python/get_distribution_data.py`.

El script actualiza los agregados y la gráfica; esta conclusión documenta la consulta indicada al inicio y debe revisarse si cambian los datos. Los archivos exportados contienen estadísticas agregadas, sin nombres, correos ni credenciales.
