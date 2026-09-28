# Estrategia de balanceo de la muestra de entrenamiento

## Objetivo

Reducir el sesgo residual hacia coincidencias bajas sin inventar targets ni volver a insertar usuarios en la base de datos. Esta estrategia opera sobre una muestra derivada para entrenamiento, no sobre las tablas `usuario` ni `resultado`.

La auditoria posterior al balanceo PERT reporta:

- 7,997 resultados.
- 71.95% en el decil 0.0.
- 599 casos PERT, con rango global 0.39-0.81.
- Desbalance entre areas: Area 1 tiene 6,163 resultados, Area 2 tiene 953 y Area 3 tiene 881.

## Opciones

### Opcion A: undersampling estratificado

Seleccionar como maximo `N` registros por combinacion `(id_area, decil)`. Es la opcion recomendada inicialmente porque es reversible, no cambia la base de datos y evita que Area 1 y el decil 0 dominen el entrenamiento.

Parametros iniciales:

- `N = 100` registros por area y decil.
- Diez estratos: `0.0`, `0.1`, ..., `0.9` y un estrato separado para `1.0`.
- Muestreo reproducible con seed `20260928`.
- Si un estrato tiene menos de `N`, se conservan todos sus registros y se informa la escasez.

### Opcion B: pesos de muestra

Conservar todos los registros y asignar un peso inversamente proporcional a la frecuencia de `(area, decil)`. Es preferible si se desea aprovechar todos los datos, pero depende de que el algoritmo de entrenamiento soporte `sample_weight`.

### Opcion C: modelos por area

Entrenar un modelo por area. Reduce el sesgo entre areas, pero disminuye el volumen disponible para cada modelo y no corrige por si solo el exceso de ceros dentro de cada area.

La implementacion debe iniciar con la Opcion A y dejar Opcion B como comparacion experimental. No se ejecuta Opcion C automaticamente.

## Procedimiento

1. Extraer desde PostgreSQL solamente `resultado`, `usuario` y `carrera` mediante `SELECT`.
2. Clasificar la estrategia por prefijo: `USER`, `CROSS`, `PERT`, `PERT-BAL` y `COMBO`.
3. Calcular `decil = floor(target * 10) / 10`, manteniendo `1.0` como estrato propio.
4. Construir `grupo_origen`:
   - usar `uuid_origen` del manifiesto para los casos `PERT-BAL`;
   - usar el UUID persistido para los casos sin manifiesto;
   - no mezclar grupos de origen entre train y test.
5. Muestrear por `(id_area, decil)` hasta `N` registros.
6. Dividir los grupos de origen en train/test con una particion 80/20 y seed fija.
7. Validar que la interseccion de grupos entre train y test sea cero.
8. Exportar la muestra, el resumen de estratos y el manifiesto de procedencia a `Docs/Reports/dataset_validation/`.

## Criterios de aceptacion

- El decil 0.0 no debe superar el 25% de la muestra balanceada, salvo que no existan suficientes casos en otros estratos.
- Ningun area debe aportar mas del 40% de la muestra balanceada.
- Deben conservarse casos USER, CROSS, PERT, PERT-BAL y COMBO cuando existan en el estrato seleccionado.
- `target_coincidencia` debe permanecer entre 0 y 1.
- La interseccion de `grupo_origen` entre train y test debe ser cero.
- El proceso no debe ejecutar `INSERT`, `UPDATE` ni `DELETE`.
- La muestra debe ser reproducible con el mismo seed.

## Riesgos y decisiones

- El undersampling elimina filas solo de la muestra de entrenamiento; no elimina datos de PostgreSQL.
- El balanceo no crea casos PERT nuevos. Las bandas PERT ausentes requieren una estrategia de generacion adicional basada en perfiles de carreras con mayor interseccion de habilidades.
- El manifiesto es una solucion temporal. La solucion definitiva es persistir `grupo_origen` en una tabla de procedencia o en `usuario`.
- No se mezclan directamente muestras de distintas areas si se entrenan modelos separados.

## Artefacto previsto

La estrategia debe implementarse en un notebook JSON valido:

`Scripts/python/dataset_balancing.ipynb`

El notebook tendra celdas de configuracion, consulta SQL, carga del manifiesto, estratificacion NumPy/Pandas, split por grupo, validaciones y exportacion de resultados. No debe modificar la base de datos.

## Estado

Este documento define la estrategia antes de crear o ejecutar el notebook. La siguiente ejecucion debe producir una muestra balanceada y sus metricas, sin alterar el dataset persistido.


