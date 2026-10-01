# Mejora Integral de Generación PERT: Procedencia, Cobertura y Prevención de Fuga de Datos

## Contexto

Actualmente cada usuario generado mediante la estrategia PERT-BAL se almacena como un usuario independiente.

Ejemplo:

```text
Usuario original: USER-abc
Usuario generado: PERT-BAL-123
```

La única relación entre ambos existe en el archivo:

```text
pert_balance_manifest.csv
```

con una estructura similar a:

```csv
uuid_nuevo,uuid_origen
PERT-BAL-123,USER-abc
```

El problema es que `dataset_generator.ipynb` consulta directamente PostgreSQL. Si el manifiesto se pierde, se mueve o no se carga correctamente, la relación entre el usuario generado y su usuario de origen desaparece, imposibilitando reconstruir la genealogía de los datos y aumentando el riesgo de fuga de información entre entrenamiento y prueba.

---

## Persistencia de procedencia en base de datos

Como solución permanente se propone almacenar explícitamente la procedencia en la base de datos mediante una nueva tabla:

```sql
CREATE TABLE usuario_origen (
    uuid_usuario VARCHAR(50) PRIMARY KEY,
    uuid_origen VARCHAR(50) NOT NULL,
    estrategia VARCHAR(30) NOT NULL,

    FOREIGN KEY (uuid_usuario)
        REFERENCES usuario(uuid_usuario),

    FOREIGN KEY (uuid_origen)
        REFERENCES usuario(uuid_usuario)
);
```

Ejemplo:

| uuid_usuario | uuid_origen | estrategia |
|-------------|-------------|------------|
| PERT-BAL-123 | USER-abc | PERT-BAL |

Esta tabla permite mantener la trazabilidad completa de cada usuario generado independientemente de archivos externos.

---

## Prevención de fuga de datos (Data Leakage)

El particionado train/test no debe realizarse utilizando directamente `uuid_usuario`, sino el identificador de origen.

```python
grupos = df["uuid_origen"].unique()
```

De esta forma:

- todas las variantes derivadas del mismo usuario permanecen juntas;
- el perfil original y sus perturbaciones nunca quedan repartidos entre train y test;
- la evaluación refleja mejor la capacidad real de generalización del modelo.

Ejemplo incorrecto:

```text
TRAIN
USER-abc

TEST
PERT-BAL-123
```

Ejemplo correcto:

```text
TRAIN
USER-abc
PERT-BAL-123
PERT-BAL-124

TEST
USER-xyz
PERT-BAL-500
```

La incorporación de `uuid_origen` no altera ni el target ni las métricas; únicamente preserva la genealogía de los datos y garantiza un split correcto.

---

## Problema actual de cobertura PERT

Actualmente los casos PERT se generan mediante el siguiente proceso:

1. Seleccionar un perfil happy path.
2. Degradar habilidades.
3. Eliminar habilidades.
4. Compararlo contra su carrera original.

Sin embargo, algunos perfiles poseen pocas habilidades o pertenecen a carreras con escasa flexibilidad curricular. Como consecuencia, tras aplicar dropout, el target puede caer rápidamente a valores bajos como:

```text
0.39
```

y resulta difícil generar observaciones en rangos altos:

```text
0.80 - 0.90
```

sin conservar casi intacto el perfil original.

---

## Variación del perfil base

Para mejorar la cobertura del espacio de targets se recomienda no depender siempre del mismo perfil happy path.

Posibles estrategias:

### 1. Combinar habilidades de perfiles afines

Generar perfiles derivados mezclando competencias de usuarios pertenecientes a una misma área de conocimiento.

### 2. Utilizar carreras relacionadas

Seleccionar perfiles de carreras que compartan una proporción significativa de habilidades.

### 3. Aplicar perturbaciones suaves para targets altos

Cuando se deseen casos en el rango:

```text
0.80 - 0.90
```

realizar reducciones mínimas en lugar de degradaciones agresivas.

### 4. Permitir casos sin eliminación de habilidades

Generar algunas muestras con:

```text
dropout = 0
```

manteniendo únicamente ligeras variaciones de nivel.

### 5. Reducir menos intensidad

Por ejemplo:

```text
0.90 → 0.80
```

en lugar de:

```text
0.90 → 0.30
```

---

## Cálculo correcto del target

El target nunca debe asignarse artificialmente.

Siempre debe recalcularse a partir de las habilidades efectivamente presentes en el perfil generado.

```math
target =
\frac{
\sum cumplimiento\_criterio\_habilidades\_comunes
}{
total\_habilidades\_requeridas
}
```

Por lo tanto, cualquier estrategia de generación modifica las habilidades, pero no modifica directamente el valor objetivo.

---

## Selección de carreras mediante similitud

Antes de generar un caso PERT es recomendable identificar carreras que compartan una cantidad significativa de habilidades.

Se propone utilizar el índice de Jaccard:

```math
similitud(A,B)=
\frac{
|habilidades_A \cap habilidades_B|
}{
|habilidades_A \cup habilidades_B|
}
```

### Ejemplo

Carrera A:

```text
{1, 2, 3, 4, 5, 6}
```

Carrera B:

```text
{1, 2, 3, 4, 7, 8}
```

Intersección:

```text
{1, 2, 3, 4}
```

La existencia de una base común de habilidades incrementa la posibilidad de producir targets intermedios o altos aun después de aplicar perturbaciones.

---

## Selección de candidatos PERT

Una regla simple sería:

```python
if similitud >= 0.40:
    usar_como_candidato_pert()
```

De este modo las carreras poco relacionadas quedan excluidas del proceso de generación.

---

## Generación por bandas de similitud

También puede establecerse una distribución deseada según el nivel de similitud:

| Rango de similitud | Banda objetivo esperada |
|-------------------|------------------------|
| Baja | 0.50 - 0.60 |
| Media | 0.60 - 0.75 |
| Alta | 0.75 - 0.90 |

Esto ayuda a poblar regiones del espacio de targets que actualmente se encuentran subrepresentadas.

---

## Diferencia entre las propuestas

### Procedencia mediante `uuid_origen`

Resuelve principalmente:

```text
Data Leakage
```

evitando que perfiles derivados del mismo usuario contaminen la evaluación.

### Variación de perfiles y carreras similares

Resuelve principalmente:

```text
Cobertura de casos PERT
```

permitiendo generar ejemplos útiles en bandas donde actualmente existe poca representación.

### Lo que ninguna resuelve por sí sola

Ninguna de estas medidas elimina automáticamente la concentración excesiva de muestras en el decil:

```text
0.0
```

Para ello sigue siendo necesario aplicar balanceo o muestreo estratificado durante la construcción del conjunto de entrenamiento.

---

## Estrategia recomendada

1. Persistir la procedencia en la base de datos mediante `usuario_origen`.
2. Seleccionar perfiles y carreras con suficiente similitud.
3. Generar muestras PERT por bandas objetivo.
4. Recalcular siempre el target desde las habilidades reales.
5. Balancear el conjunto de entrenamiento por área y decil.
6. Realizar el split train/test utilizando `uuid_origen`.

---

## Resultado esperado

La adopción conjunta de estas medidas proporciona:

- trazabilidad permanente de todos los usuarios generados;
- independencia de archivos auxiliares como `pert_balance_manifest.csv`;
- eliminación de fugas de información entre entrenamiento y evaluación;
- mejor representación de targets medios y altos;
- mayor diversidad de casos PERT;
- datasets más reproducibles y auditables;
- una evaluación más realista de la capacidad de generalización del modelo.