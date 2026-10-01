# Reinicio y regeneracion de casos

## Resumen

La generacion anterior produjo casos mediante `caso_a`, `caso_b`, `caso_c` y `data_base_nonideal`. La auditoria mostro integridad referencial correcta, pero tambien sesgo fuerte hacia coincidencias bajas, cobertura PERT incompleta y trazabilidad insuficiente entre casos derivados y Happy Paths.

Esta propuesta plantea reiniciar la generacion de casos desde los Happy Paths, conservar el catalogo y el conocimiento metodologico, y reconstruir los casos no ideales con procedencia persistente y perfiles base seleccionados por similitud.

## Alcance del reinicio

Se consideran datos regenerables los usuarios y resultados creados por los prefijos:

- `CROSS-*`
- `PERT-*`
- `PERT-BAL-*`
- `COMBO-*`

Los Happy Paths `USER-*` deben conservarse como fuente principal de verdad. Tambien deben conservarse los catalogos y sus relaciones:

- `area`
- `carrera`
- `habilidad`
- `criterio`
- `carrera_habilidad`
- `carrera_escuela`
- `escuela`
- los usuarios `USER-*`
- sus habilidades y resultados originales

La limpieza de casos debe ejecutarse unicamente despues de realizar un respaldo y validar los conteos de Happy Paths.

## Limpieza controlada

La limpieza debe ejecutarse en una transaccion y en este orden:

1. Respaldar las tablas `usuario`, `usuario_habilidad` y `resultado`.
2. Seleccionar usuarios con los prefijos de casos regenerables.
3. Eliminar sus filas de `resultado`.
4. Eliminar sus filas de `usuario_habilidad`.
5. Eliminar sus filas de `usuario`.
6. Confirmar que permanecen todos los `USER-*` y los catalogos.
7. Confirmar que no quedan resultados sin usuario ni habilidades sin referencia.

No se debe ejecutar una limpieza basada solamente en `id_usuario`, porque las identidades son autoincrementales y pueden cambiar entre ejecuciones. La identificacion debe basarse en `uuid_usuario` y sus prefijos.

## Procedencia y `grupo_origen`

Los casos derivados deben conservar la relacion con el Happy Path del que provienen. El manifiesto CSV es una solucion temporal porque la relacion se pierde si el archivo se mueve o se elimina. La solucion definitiva es persistirla en PostgreSQL:

```sql
CREATE TABLE usuario_origen (
    uuid_usuario VARCHAR(50) PRIMARY KEY,
    uuid_origen VARCHAR(50) NOT NULL,
    estrategia VARCHAR(30) NOT NULL,
    similitud_base NUMERIC(6,4),
    creado_en TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_usuario_origen_usuario
        FOREIGN KEY (uuid_usuario) REFERENCES usuario(uuid_usuario),
    CONSTRAINT fk_usuario_origen_origen
        FOREIGN KEY (uuid_origen) REFERENCES usuario(uuid_usuario)
);
```

Para un Happy Path, `uuid_origen` puede ser el mismo UUID. Para un caso derivado, debe ser el UUID del Happy Path original. `grupo_origen` no es el target ni una feature del modelo; se utiliza para impedir data leakage.

El split train/test debe realizarse por `uuid_origen`, nunca por el `id_usuario` sintetico. Todas las variaciones de un mismo origen deben permanecer en un solo conjunto.

## Variacion del perfil base

El enfoque anterior perturbaba perfiles individuales sin controlar suficientemente la carrera contra la que se evaluaban. El nuevo enfoque debe seleccionar primero una pareja de carreras del mismo area:

- carrera de origen del Happy Path;
- carrera objetivo con interseccion suficiente de habilidades.

La similitud recomendada es Jaccard:

```text
similitud = habilidades_comunes / habilidades_union
```

Se pueden usar estos rangos:

- `0.00-0.20`: casos bajos CROSS.
- `0.20-0.40`: casos medios bajos.
- `0.40-0.60`: casos PERT medios.
- `0.60-1.00`: casos PERT altos.

Solo deben compararse carreras de la misma area. La similitud sirve para seleccionar perfiles plausibles; no sustituye el calculo del target.

## Generacion nueva

### Caso A: Cross-Matching

Cruzar Happy Paths contra carreras del mismo area, priorizando carreras con similitud baja o media. Persistir un caso solo si el target se calcula desde las habilidades reales y si la cuota del estrato aun no esta cubierta.

### Caso B: PERT dirigido

Usar perfiles base seleccionados por similitud y generar candidatos por bandas:

- `0.50-0.60`: dropout de 1-2 habilidades y cumplimiento perturbado entre `0.40-0.70`.
- `0.60-0.70`: dropout de 0-1 habilidades y cumplimiento entre `0.55-0.80`.
- `0.70-0.80`: dropout de 0-1 habilidades y cumplimiento entre `0.70-0.90`.
- `0.80-0.90`: sin dropout y degradacion ligera entre `0.75-0.95`.

Si una banda no es alcanzable con un perfil, se descarta el candidato y se selecciona otro perfil o carrera. Nunca se fuerza el target.

### Caso C: Combo

Aplicar ruido moderado al perfil y cruzarlo contra carreras del mismo area. Limitar la cuota de carreras con interseccion cero para evitar que COMBO vuelva a dominar el decil `0.0`.

## Regla unica del target

El target persistido siempre debe calcularse asi:

```text
suma_cumplimiento = SUM(cumplimiento_criterio de habilidades comunes)
target = suma_cumplimiento / total_habilidades_requeridas
```

La precision debe alinearse con `NUMERIC(5,2)` en `resultado`. La formula no debe recibir porcentajes predefinidos ni valores inventados.

## Balanceo y cuotas

La generacion debe controlar simultaneamente:

- area;
- decil del target;
- estrategia;
- similitud entre carreras;
- grupo de origen.

El dataset persistido puede conservar todos los casos validos, pero la muestra de entrenamiento debe aplicar undersampling estratificado o pesos de muestra. Como punto inicial, limitar a 100 registros por combinacion `(id_area, decil)` y dividir train/test por `uuid_origen`.

No se busca una distribucion perfectamente uniforme si los datos reales no la soportan. Se busca evitar que un area o el decil cero dominen el modelo.

## Validacion

Antes de aceptar la nueva generacion se debe comprobar:

- cero referencias rotas;
- cero duplicados de usuario-habilidad;
- cumplimientos en `[0,1]`;
- targets iguales al recalculo dentro de la precision de la columna;
- carreras y usuarios dentro de la misma area;
- procedencia completa para todo caso derivado;
- interseccion cero entre grupos de origen de train y test;
- distribucion por area, estrategia, similitud y decil;
- ausencia de inserciones duplicadas al reejecutar el proceso.

## Orden de ejecucion

1. Respaldar y validar Happy Paths.
2. Crear la tabla de procedencia.
3. Limpiar unicamente los prefijos regenerables.
4. Regenerar similitudes de carreras y perfiles candidatos.
5. Ejecutar un dry-run por cuotas y bandas.
6. Revisar la factibilidad de las bandas PERT.
7. Persistir en lotes transaccionales con procedencia.
8. Ejecutar la auditoria SQL y la preparacion de features.
9. Construir muestras balanceadas y hacer el split por `uuid_origen`.

## Documentacion conservada

- `index.md`: punto de entrada documental.
- `NLP_research_to_standardize.md`: investigacion NLP y homologacion de habilidades.
- `dataset_generation_strategy.md`: reglas y blueprint historico de generacion.
- `dataset_balancing_strategy.md`: estrategia actual de balanceo para entrenamiento.

Los planes historicos y los CSV/PNG derivados de ejecuciones anteriores no son fuente normativa; sus hallazgos relevantes quedan resumidos en este documento.

## Estado

Esta es una propuesta de reinicio. La limpieza de PostgreSQL y la regeneracion deben ejecutarse como una fase independiente, con respaldo verificable y confirmacion de los conteos de Happy Paths.
