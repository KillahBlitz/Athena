# 05_generate_dataset_trainee.ipynb — generación, validación y carga del dataset sintético

[Índice de documentación](../../../index.md) · [Abrir archivo original](../../../../Scripts/python/jupyter/05_generate_dataset_trainee.ipynb)

**Archivo documentado:** `Scripts/python/jupyter/05_generate_dataset_trainee.ipynb`  
**Revisión:** 2026-10-19. Descripción basada en el contenido local; no implica una ejecución del archivo.

Genera evaluaciones sintéticas para las tres áreas de Athena, calcula una etiqueta de coincidencia por pareja usuario–carrera, valida los datos y puede cargarlos en PostgreSQL. No entrena un modelo de aprendizaje automático: prepara las tablas que un entrenamiento posterior podría consumir.

Esta ficha describe las **13 celdas actuales** del notebook. No atribuye al código las exportaciones u otros pasos que puedan estar propuestos en estrategias externas.

## Configuración efectiva

| Constante | Valor actual | Efecto |
| --- | --- | --- |
| `LIST_AREAS` | `[3]` | La ejecución principal procesa solo el área 3; el comentario muestra la alternativa `[1, 2, 3]` |
| `AREAS_IMPLEMENTADAS` | `(1, 2, 3)` | El mismo generador admite las tres áreas |
| `SUBIR_DB` | **`True`** | La celda 11 confirma las cargas |
| `REEMPLAZAR_EXISTENTE` | `False` | Un rango ocupado detiene la carga |
| `CATALOGO` | `/Users/jmonroy/Downloads/PRUEBAS/catalogo_athena.json` | Archivo externo a `Scripts`; entrada obligatoria |
| `SEED` | `20261018` | Semilla maestra de los generadores NumPy |
| `ESTATUS_ID` | `4` | COMPLETED, según `STATUS_DIC` |
| `PARTICION_PCT` | `(70, 15, 15)` | Entrenamiento, validación y test por usuario |
| `BLOQUE_COBERTURA` | `20` | Mezcla las particiones de cobertura en bloques de hasta 20 |
| `CHUNK_CSV` | `100_000` | Tamaño máximo de los bloques de texto CSV para hash y COPY |

`type_user=4` identifica usuarios reales y no se genera. Las listas `NAMES` y `LAST_NAMES` tienen 50 valores cada una. Los nombres pueden repetirse; `usuario_id`, UUID5 y el sufijo de ID en el correo distinguen las evaluaciones.

## Dependencias y preparación

Resuelve la raíz del repositorio por `lib/set_envs.py` e importa `DB_CONFIG` desde [set_envs.py](lib/set_envs.py.md). Utiliza `numpy`, `pandas`, `matplotlib`, `pydantic`, `psycopg2` y `sklearn`; instalar `sklearn` mediante el paquete **`scikit-learn`**, no mediante el paquete PyPI del mismo nombre que el import. Consultar los faltantes de [requirements.txt](../assets/requirements.txt.md).

El catálogo debe existir, contener `areas`, `tipos_riasec`, `tipos_criterio`, `carreras`, `criterios` y `_meta`, y pasar la comparación SHA-256. No se reconstruye automáticamente desde los Excel del repositorio. La DB debe tener los mismos IDs, objetivos y descripciones evaluadas.

## Volumen y unidades

La unidad de evaluación es el usuario. Cada usuario responde sobre **todas** las carreras de su área. Por carrera se guarda un objetivo, un principal, cinco perfiles R/I/S/E/C y una etiqueta de resultado.

| Área | Carreras | Base | Presupuesto máximo de cobertura | Criterios evaluados por usuario |
| --- | ---: | ---: | ---: | ---: |
| 1 | 43 | 3,000 | 4,500 | 258 |
| 2 | 12 | 1,500 | 2,250 | 72 |
| 3 | 11 | 1,500 | 2,250 | 66 |

Con N usuarios y C carreras: `usuarios=N`, `puntaje_objetivo=N*C`, `usuario_criterio=6*N*C`, `resultados=N*C`. En el área 2, el criterio artístico 297 de Optometría se excluye de evaluación y similitud. Los demás criterios del catálogo siguen existiendo como referencia.

## Recorrido de las celdas

Las posiciones de esta tabla comienzan en 1; no son los números `In[...]` del historial de Jupyter.

| Celda | Contenido y efecto |
| ---: | --- |
| 1 | Imports, rutas, banderas, nombres, semillas, cuotas, columnas y colores |
| 2 | Modelos `Usuarios`, `PuntajeObjetivo`, `UsuarioCriterio`, `Resultado` |
| 3 | Funciones de muestreo, etiqueta, hash y ejecución de 12 casos de referencia |
| 4 | `CatalogoArea`: lectura, validación y similitud TF-IDF |
| 5 | `GeneratorData`: usuarios, escenarios, cobertura y construcción de tablas |
| 6 | `ValidatorData`: 14 controles sobre los datos generados |
| 7 | `UploaderData`: conexión, validación, carga, verificación, lectura y borrado |
| 8 | `GraphData`: cuatro gráficos de conteos y distribución |
| 9 | `GenerateDatasetTrainee`: coordinación por área |
| 10 | Crea `gdt`, genera cada área seleccionada, muestra reportes y consulta la DB con `confirmar=False` |
| 11 | Si `SUBIR_DB`, ejecuta `confirmar=True` para cada área seleccionada |
| 12 | Grafica desde DB si `SUBIR_DB=True`; en caso contrario usa los DataFrames de memoria |
| 13 | Ejemplo comentado de borrado del área 1 con `confirmar=False` |

**`SUBIR_DB=False` evita el commit de la celda 11, pero no evita la conexión de validación de la celda 10.** Para generar exclusivamente en memoria se puede invocar `gdt.generate_dataset(area)` sin llamar a `upload_dataset` ni ejecutar esa validación de DB. Cambiar una bandera no ejecuta ni revierte celdas ya ejecutadas.

## Modelos y funciones comunes

Los modelos pydantic validan longitudes, dominios y porcentajes declarados. La generación instancia `Usuarios`; las otras tres tablas se construyen mediante arrays/DataFrames y se validan posteriormente con `ValidatorData`.

| Función | Responsabilidad |
| --- | --- |
| `sin_acentos` | Normaliza texto a ASCII para el correo |
| `cuotas_particion` | Aritmética entera: 70 %, 15 % y resto a test |
| `csv_chunks` | Convierte segmentos de DataFrame a texto CSV, cuatro decimales y salto de línea fijo |
| `sha_tablas` | Calcula SHA-256 del CSV virtual de cada una de las cuatro tablas |
| `etiqueta` | Calcula el objetivo sintético de regresión |
| `banda` | Convierte una etiqueta redondeada en una de 12 bandas, con 0 y 1 separados |
| `generic` | Muestrea objetivo, principal y evidencias RISEC dada una afinidad |
| `completo` | Evidencia completa: coincidencia 1 y repeticiones positivas |
| `completos_en` | Elige k dimensiones completas; las demás quedan ausentes |
| `redondear` | Redondea P y coincidencias a cuatro decimales; ajusta repeticiones sin evidencia |
| `verificar_casos` | Comprueba los 12 casos de etiqueta; detiene la ejecución ante diferencias |

### Etiqueta de coincidencia

`O` es interés en el objetivo, en {0, 0.25, 0.5, 0.75, 1}. `P` es la probabilidad simulada de habilidad principal. Para cada dimensión, `m` es la coincidencia original y `r` el número de evidencias. La repetición refuerza parcialmente `m`, sin aumentar una coincidencia que ya vale 1.

```text
ajustada = 0 si r=0; en otro caso m + 0.15*(1-m)*(1-exp(-(r-1)/2))
S = promedio de las cinco coincidencias ajustadas
B = 0.25*O + 0.30*P + 0.45*S
H = (0.30*P + 0.45*S)/0.75
y = round(B * (1 - 0.20*abs(O-H)), 4)
```

Los valores ajustados son internos; `usuario_criterio` conserva las coincidencias originales. Las etiquetas no tienen ruido añadido. Una persona puede tener varias carreras con coincidencia alta; las etiquetas no deben sumar 1.

## `CatalogoArea`

`__init__` verifica el hash del JSON sin `_meta`, filtra carreras por área y las ordena por ID. Construye `crit[(carrera_id, riasec_id)] → criterio_id`, rechaza duplicados y exige principal más R/I/S/E/C por carrera. Comprueba las exclusiones esperadas, sin inferir pertenencia por rangos de criterios.

Concatena objetivo y seis descripciones evaluadas en orden 0,1,2,4,5,6. Utiliza TF-IDF con minúsculas, normalización de acentos y n-gramas de una y dos palabras, y calcula similitud coseno. `sim` correlaciona entradas entre carreras; no determina la etiqueta.

## `GeneratorData`

| Método | Qué produce o comprueba |
| --- | --- |
| `__init__` | Conserva catálogo, área, número de carreras, RNG de nombres y contadores |
| `generate_users` | Nombre aleatorio, correo sin acentos con ID y UUID5 determinista `USER-...` |
| `nueva_evaluacion` | Contenedor de usuario/lote/escenario/partición y una posición por carrera |
| `fila` | Redondea entradas, calcula etiqueta y conserva afinidad para auditoría |
| `entradas_foco` | Entradas específicas de los escenarios A1–A6 |
| `afinidad_no_foco` | Combina afinidad base, similitud al foco y variación aleatoria |
| `completar` | Llena todas las carreras no dirigidas; A7 explora y A8 queda en cero |
| `generate_base` | Recorre usuarios por ID, rota focos y genera el lote base |
| `deficit` | Ordena faltantes por cantidad, banda y carrera |
| `dirigida` | Intenta hasta 200 muestras de entrada para una banda; falla si ninguna sirve |
| `generate_cobertura` | Añade usuarios completos con hasta cuatro carreras objetivo hasta cubrir mínimos o presupuesto |
| `build_tables` | Convierte evaluaciones a las cuatro tablas con arrays NumPy y DataFrames |
| `audit` | Genera el DataFrame de auditoría: lote, escenario, focos, objetivos dirigidos, partición y afinidades |

### Escenarios del lote base

| Escenario | Proporción | Área 1 | Áreas 2/3 | Comportamiento |
| --- | ---: | ---: | ---: | --- |
| A1 Ideal | 10 % | 300 | 150 | Objetivo, principal y cinco perfiles completos |
| A2 Casi ideal | 15 % | 450 | 225 | Interés alto, principal alto, cuatro perfiles completos |
| A3 Parcial | 15 % | 450 | 225 | Evidencia textual parcial en cinco dimensiones |
| A4 Interés sin evidencia | 8 % | 240 | 120 | Interés alto y poca evidencia |
| A5 Habilidad sin interés | 8 % | 240 | 120 | Principal/perfiles altos e interés bajo |
| A6 Multicarrera | 15 % | 450 | 225 | Dos o tres focos; alterna vecinos similares y selección aleatoria |
| A7 Explorador | 24 % | 720 | 360 | Sin foco y afinidad Beta(2,4) por carrera |
| A8 Ausencia completa | 5 % | 150 | 75 | Cero en todas las carreras |

La cobertura busca al menos 100 filas por carrera en cada banda de [0.2,0.3) hasta [0.9,1.0), y 20 unos exactos. También se validan 20 ceros por carrera. Todas las carreras de un usuario permanecen juntas aunque solo cuatro se dirijan a bandas deficitarias.

## Particiones e identificadores

Los RNG separan etapas 0 base, 1 cobertura, 2 partición, 3 nombres y 4 monotonicidad. En la base, la partición se calcula dentro de cada escenario. En cobertura, `particion_cobertura` mezcla bloques de 20 posiciones: 14 entrenamiento, 3 validación y 3 test por bloque completo. El último bloque usa la misma regla entera. No es una única permutación global del presupuesto.

Para área A: usuarios base desde `A*1_000_000+1`; cobertura desde `A*1_000_000+500_001`; resultados desde `A*1_000_000+1` en orden de usuario/carrera. Cada tabla tiene su propio espacio de claves. El UUID usa `uuid5(NAMESPACE_URL, f'athena/{usuario_id}')`, con prefijo `USER-`.

## `ValidatorData`

`control` agrega resultados estructurados; `validate` ejecuta los controles; `recalcular` reconstruye las entradas mediante los criterios; `monotonicidad` prueba 10,000 perfiles aleatorios; `minimos` calcula déficits por carrera y banda. `__init__` conserva el catálogo y la lista de resultados.

Los **14 controles implementados** son: catálogo; 12 casos de etiqueta; PK/UUID únicos; ausencia de huérfanos; filas por usuario; escalas y ausencia de nulos; recálculo de etiquetas; monotonicidad; cuotas/focos; partición 70/15/15; mínimos por carrera; dominios de estado/tipo/área; rangos de IDs; y reproducibilidad SHA-256.

El control 7 recalcula desde DataFrames, no desde CSV exportados. El control 14 compara dos generaciones serializadas en memoria. No hay un control 15 de reapertura de Excel porque este notebook no crea ese libro. Los controles validan el dataset generado; no certifican todos los aspectos de los detectores reales ni el contenido de usuarios reales.

## `UploaderData`

| Método | Responsabilidad |
| --- | --- |
| `__init__` | Define área y rango alto reservado |
| `connect` | Abre conexión de solo lectura cuando `confirmar=False` |
| `validate_catalog_db` | Compara carreras, objetivos, criterios e identidades/textos contra JSON |
| `validate_identity` | Exige identidad `BY DEFAULT` y que las secuencias no hayan alcanzado el rango reservado |
| `validate_uuid` | Detecta UUID del lote utilizados fuera de su rango |
| `occupied` | Cuenta ocupación de IDs de usuarios y resultados en el rango |
| `manifest` | Obtiene pares de usuario y UUID del lote |
| `candidates` | Comprueba propiedad del lote y arma selección por manifiesto, área, rango y tipo sintético |
| `delete_rows` | Borra resultados, criterios, objetivos y usuarios de los candidatos |
| `validate_counts` | Verifica N usuarios y las cardinalidades N*C y 6*N*C |
| `copy_table` | Serializa y carga bloques de hasta 100,000 filas con `COPY FROM STDIN` |
| `upload` | Valida y carga en una transacción; opcionalmente reemplaza el mismo lote |
| `verify_db` | Relee los datos y compara conteos y particiones con los esperados |
| `delete` | Cuenta candidatos en modo consulta o borra y confirma cuando se solicita |
| `read_db` | Lee usuarios, resultados y conteos del área/rango para verificación y gráficos |

En `upload(confirmar=True)`, bloquea escrituras de `usuarios`, verifica catálogo/secuencias/UUID y comprueba el rango. Sin reemplazo, una ocupación produce error. Con reemplazo, elimina solo coincidencias del manifiesto y exige que no queden filas ajenas antes de recargar. Los cuatro COPY y la comprobación de conteos comparten una transacción. Errores revierten todo; no utiliza `setval` ni modifica catálogos.

El modo `confirmar=False` consulta y hace rollback sin cargar. Cuando `reemplazar=True`, ese modo no ejecuta ni prueba el borrado: la validación detallada de candidatos ocurre al reemplazar. `verify_db` comprueba conteos y particiones, no una igualdad completa de cada valor cargado.

## Coordinación y gráficos

`GenerateDatasetTrainee.__init__` mantiene `datasets` y `reportes`. `generate_dataset` selecciona `generate_dataset_area_1`, `generate_dataset_area_2` o `generate_dataset_area_3`; cada método delega en `build_dataset` con su área. Este último genera dos veces, calcula hashes, valida, construye el reporte y conserva el dataset solo si no hay controles fallidos.

`generate` prepara cuotas, escenarios, particiones y ambos lotes, crea usuarios y tablas y devuelve sus metadatos. `particion_cobertura` arma los bloques de partición. `report` resume usuarios por tipo, conteos, cobertura, presupuesto, déficit y controles. `resumen` presenta los controles en un DataFrame. `upload_dataset` delega en `UploaderData` y verifica después del commit.

`GraphData.style` aplica formato; `lote` distingue base/cobertura por el resto del ID; `plot` organiza cuatro paneles. `plot_tablas` muestra filas por tabla, `plot_particion` usuarios por tipo y lote, `plot_bandas` etiquetas por banda con mínimos y `plot_carreras` un mapa de conteos por carrera/banda. El título dice «en la base de datos» incluso cuando `SUBIR_DB=False` y se muestran datos de memoria; comprobar la bandera al interpretar la figura.

## Salidas reales y límites

Los datasets y reportes quedan en `gdt.datasets` y `gdt.reportes`. Las figuras se muestran con `plt.show()`. `csv_chunks` produce texto temporal para hash/COPY: **no guarda archivos CSV**. El código actual tampoco escribe Excel, JSON de reporte/configuración, scripts de carga/borrado ni un generador independiente.

Aunque el COPY se divide en bloques, la construcción conserva evaluaciones, arrays y DataFrames completos en memoria; no es un flujo de generación totalmente incremental. El área 1 alcanza hasta 1,935,000 filas de criterios. La doble generación y las validaciones añaden trabajo y memoria temporal.

El catálogo externo y una DB accesible siguen siendo necesarios para ejecutar el recorrido principal actual. La generación no llama a Gemini: P, perfiles y etiquetas se simulan. La utilidad del dataset es reproducir la función de etiqueta; no constituye evidencia de precisión vocacional con personas reales.

## Archivos relacionados

- [Configuración PostgreSQL](lib/set_envs.py.md)
- [Dependencias e instalación](../assets/requirements.txt.md)
- [04 — carga previa de criterios](04_submit_criteria_from_sql.ipynb.md)
- [Criterios consolidados](../assets/layouts/excel/criterios.xlsx.md)
- [Catálogo académico](../assets/layouts/excel/tablas_completas.xlsx.md)
