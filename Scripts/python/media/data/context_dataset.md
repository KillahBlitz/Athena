# Contexto del dataset y criterios de entrenamiento

Modelo objetivo: **RandomForest de clasificacion** que, dadas las habilidades del usuario, estima la coincidencia por carrera y devuelve el **top-3** (via `predict_proba` sobre `id_carrera`).

Un modelo independiente por area (el `id_area` cierra el universo de carreras y habilidades).


## Resumen por area

| Area | Usuarios | Carreras (clases) | Features (hab. distintas) | Muestras/clase (min/avg/max) | Ratio muestras/feature | Media coincidencia | Cruce carreras/usuario (avg) |
|------|----------|-------------------|---------------------------|------------------------------|------------------------|--------------------|------------------------------|
| 1 - Ingenieria y Ciencias Fisico Matematicas | 6450 | 43 | 166 | 115/150.0/210 | 38.9 | 53.4% | 11.35 |
| 2 - Ciencias Medico Biologicas | 1800 | 12 | 51 | 128/150.0/188 | 35.3 | 53.2% | 6.81 |
| 3 - Ciencias Sociales y Administrativas | 1802 | 11 | 45 | 132/163.8/196 | 40.0 | 52.4% | 7.07 |

## Criterios evaluados

### Area 1 - Ingenieria y Ciencias Fisico Matematicas

- Muestras por clase >= 100: **CUMPLE** (minimo real = 115).
- Ratio muestras/feature >= 10: **CUMPLE** (ratio real = 38.9).
- Todas las carreras representadas como top-1: **CUMPLE** (43/43).
- Perfiles realistas (habilidades cruzan >1 carrera): **CUMPLE** (promedio = 11.35 carreras/usuario; sin leakage de carrera unica).
- >=1 usuario 100% por carrera (ejemplar perfecto): **CUMPLE** (usuarios al 100% = 122).

**Veredicto area 1: APTA para entrenar**

### Area 2 - Ciencias Medico Biologicas

- Muestras por clase >= 100: **CUMPLE** (minimo real = 128).
- Ratio muestras/feature >= 10: **CUMPLE** (ratio real = 35.3).
- Todas las carreras representadas como top-1: **CUMPLE** (12/12).
- Perfiles realistas (habilidades cruzan >1 carrera): **CUMPLE** (promedio = 6.81 carreras/usuario; sin leakage de carrera unica).
- >=1 usuario 100% por carrera (ejemplar perfecto): **CUMPLE** (usuarios al 100% = 34).

**Veredicto area 2: APTA para entrenar**

### Area 3 - Ciencias Sociales y Administrativas

- Muestras por clase >= 100: **CUMPLE** (minimo real = 132).
- Ratio muestras/feature >= 10: **CUMPLE** (ratio real = 40.0).
- Todas las carreras representadas como top-1: **CUMPLE** (11/11).
- Perfiles realistas (habilidades cruzan >1 carrera): **CUMPLE** (promedio = 7.07 carreras/usuario; sin leakage de carrera unica).
- >=1 usuario 100% por carrera (ejemplar perfecto): **CUMPLE** (usuarios al 100% = 34).

**Veredicto area 3: APTA para entrenar**


## Conclusion

Las 3 areas **cumplen los criterios** de cantidad, balance, dimensionalidad y realismo para entrenar un RandomForest de clasificacion con salida top-3.


### Recomendaciones de entrenamiento

- Features: vector multi-hot de las habilidades del area ponderado por `cumplimiento_criterio` consolidado (max entre formularios).
- Label: carrera con `top=1` en `resultado`. Top-3 en inferencia con `predict_proba` -> 3 clases de mayor probabilidad.
- Split estratificado por carrera; reportar accuracy top-1 y top-3, y metricas por clase (no solo el promedio global).
- Usar `class_weight="balanced"` por robustez ante clases menores.
- Un modelo por area (3 modelos independientes).
