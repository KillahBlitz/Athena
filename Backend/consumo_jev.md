# Jev, worker extractor y camino a la clasificación

Documento de trabajo. Separa lo que está **medido** de lo que es **proyección** o
**decisión pendiente**. Las mediciones se hicieron en local, con la BD en sesión de solo
lectura (`default_transaction_read_only = on`) y sin escribir nada en ella.

## 1. Estado actual

| Pieza | Estado |
|---|---|
| Extracción con Jev (state + preguntas tipadas, una sola llamada) | Funciona, probada con llamadas reales |
| Worker extractor (`src/tasks/extractor_event_handler.py`) | Arranca, consume Redis, llama a Jev y guarda el resultado en `Backend/logs/`. Verificado con un evento real |
| Persistencia en BD de lo extraído | No existe (`CommandHandler` está vacío) |
| Vectorización + clasificador | No existe (`ClassifierEventHandler.classifier_task` no hace nada con el modelo) |
| Generador de resultados (`generator_event_handler.py`) | Archivo vacío |
| Que el sitio se entere de que terminó | No existe (ver sección 6) |

Verificación del worker, en esta sesión:

- Antes de arrancarlo, Redis no tenía ningún grupo de consumo en `extractor_stream`: nunca había
  corrido un worker. Había 1 evento esperando, creado desde el sitio (área 1).
- Al arrancarlo consumió ese evento (usuario `USER-5914...`), armó **259 preguntas** (215 de
  coincidencia + 44 de repetición), hizo **una** llamada a Jev y escribió `logs/criteria/` y
  `logs/events/`. Terminó en menos de ~45 s contando el arranque. Pico de memoria: **116 MiB**
  (Working Set en Windows; en Linux puede variar).
- Estado final en Redis: grupo `extractor_group`, 1 consumidor, 0 pendientes.
- Para volver a procesar ese mismo evento: `XGROUP SETID extractor_stream extractor_group 0`.
- No se escribió nada en Postgres. El `usage` real de esa llamada no se imprimió (se agregó el
  `print` después); la próxima corrida lo mostrará.

### Cómo arrancar el worker

- Local (Mac, Linux o WSL), en paralelo a la API: `bash start_extractor.sh`. Usa rutas relativas,
  necesita `Backend/venv` y un `Backend/.env` propio (git lo ignora) con las variables de Redis, DB
  y `VERCEL_*`. Carga el `.env` y **después** exporta `PYTHONPATH`, porque el `.env` puede traer una
  ruta de otra máquina que pisaría el valor.
- Redis es compartido: el grupo `extractor_group` reparte los eventos entre los workers que lo
  consuman. Si dos personas corren el worker a la vez contra la misma Redis, cada una recibirá solo
  una parte de los eventos y se gastarán tokens de Jev en ambos lados.
- Kubernetes: `kubernetes/devel/athena-extractor/deployment.yaml` **sigue vacío**; por ahora no se
  despliega nada. Si se despliega más adelante: seguir el patrón del clasificador, crear un Secret
  `athena-extractor-env` con las variables de Redis, DB, `*_EXTRACTOR` y `VERCEL_*`, y tener en cuenta
  que `DeployToDevel.yml` solo valida la conexión y publica la librería: **ningún workflow construye la
  imagen ni aplica los manifiestos**.
- Si se construye la imagen, esta instala `kinasis-library==1.0.9` desde PyPI
  (`internal_requirements.txt`), que ya trae el `ExtractorEvent` nuevo. En local se usa la carpeta
  `library/` vía `PYTHONPATH`.

### Lo que endurecí en el worker

- Un evento inválido o un fallo de Jev ya no tumba el proceso: el evento y el motivo se guardan en
  `logs/errors/`. Motivo: `RedisConsumer` confirma (ack) el mensaje **al leerlo**, antes de
  procesarlo, así que Redis no lo reentrega si algo falla después (entrega "como máximo una vez").
- Falla al arrancar, con un mensaje claro, si falta una variable obligatoria (imprime nombres, no valores).
- `VERCEL_MODEL` sin definir llegaba como `None` al payload; ahora cae a `typesafe-ai/jev`.
- La publicación hacia `classifier_stream` **sigue desactivada** a propósito: el resultado del
  extractor no tiene la forma de `ClassifierEvent` y rompería al clasificador.

## 2. Consumo y costo de Jev

Precio de Jev 1.14: **$42 por 10⁹ tokens de entrada**; la salida es gratis. Todas las preguntas
de un usuario van en una sola llamada (el `state` se paga una vez) y cada pregunta lleva una
instrucción corta que referencia por path el dato del `state` que juzga.

Medido con datos reales de BD (carreras y criterios) y respuestas de usuario **sintéticas**.
Caso típico: 3 criterios prioritarios por dimensión.

| Área | Carreras | Preguntas | Tokens de entrada | Tokens de salida | Costo |
|---|---|---|---|---|---|
| 1 | 43 | 273 | 50,122 | 6,634 | $0.002105 |
| 2 | 12 | 87 | 15,754 | 2,301 | $0.000662 |
| 3 | 11 | 81 | 14,565 | 2,157 | $0.000612 |

Proyección (no medida) con el tope de 11 criterios por dimensión que ya aplica el frontend.
Modelo lineal ajustado a esas 3 mediciones: `tokens ≈ -381 + 185 × preguntas`.

| Área | Preguntas (peor caso) | Tokens | Costo |
|---|---|---|---|
| 1 | 313 | ~57,500 | ~$0.0024 |
| 2 | 127 | ~23,100 | ~$0.00097 |
| 3 | 121 | ~22,000 | ~$0.00092 |

Sin el tope, el área 1 con los 43 criterios por dimensión marcados (473 preguntas) falló con
`max_tokens_exceeded`: el límite por request es de 64k tokens.

El evento real del área 1 (259 preguntas) se proyecta en ~47,500 tokens, unos $0.002.

## 3. Cómo se generaron los datos de entrenamiento

Salen de `Scripts/python/jupyter/05_generate_dataset_trainee.ipynb`, que fabrica usuarios
**sintéticos** y calcula la etiqueta `y` con una **fórmula determinista**:

```
adj_k = 0                                           si r_k = 0
adj_k = m_k + 0.15·(1 - m_k)·(1 - e^(-(r_k-1)/2))   si r_k ≥ 1
S = (Σ adj_k) / 5          B = 0.25·O + 0.30·P + 0.45·S
H = (0.30·P + 0.45·S) / 0.75
y = B · (1 - 0.20·|O - H|)
```

Consecuencia: el Random Forest aprende a **reproducir esa fórmula**. Por eso el R² es ≈ 0.998 en
validación y en test (`type_user = 3`). Esas métricas miden fidelidad a la fórmula sobre usuarios
sintéticos, no calidad de la recomendación con personas reales.

`type_user`: 1 entrenamiento, 2 validación, 3 test, 4 real. `estatus_id`: 1 PENDING, 2 EXTRACTED,
3 CLASSIFIED, 4 COMPLETED. El modelo solo entrena con 1 y 2, así que guardar usuarios reales
(`type_user = 4`) no contamina el entrenamiento.

## 4. Vectorización

### 4.1 Qué espera el modelo

Una fila por pareja **usuario × carrera**. Columnas, en el orden de `TrainedModel.columnas`:
primero el one-hot `carrera_<id>` (en el orden de `carrera_ids`) y luego
`FEATURES = [o, p, r_coinc, r_rep, i_coinc, i_rep, s_coinc, s_rep, e_coinc, e_rep, c_coinc, c_rep]`.
Son 55 columnas en el área 1, 24 en la 2 y 23 en la 3. La dimensión `riasec_id = 3` (Artística) no se
usa: solo el área 2 tiene un criterio con ese id y está excluido del entrenamiento.

| Feature | Qué es | En BD |
|---|---|---|
| `o` | Calificación del usuario a esa carrera | `puntaje_objetivo.porc_objetivo` |
| `p` | Coincidencia del criterio principal de esa carrera | `usuario_criterio.porc_coincidencia` con `criterios.type_id = 2` (`riasec_id = 0`) |
| `<letra>_coinc` | Coincidencia del criterio de perfil de esa carrera en esa dimensión | `porc_coincidencia` con `type_id = 1` |
| `<letra>_rep` | Repeticiones de ese criterio | `usuario_criterio.repeticiones` |

Cada carrera tiene exactamente un criterio principal y uno por dimensión (1, 2, 4, 5, 6). El
usuario ve en el frontend los criterios de **todas** las carreras del área para cada dimensión
(43 opciones por dimensión en el área 1).

**Recomendación:** no reescribir la vectorización. Convertir el resultado del extractor a los dos
DataFrames con la forma de BD (`puntaje_objetivo` y `usuario_criterio`) y pasarlos por
`TraineeModelHandler._build_features`. Así entrenamiento y servicio usan el mismo código, sin
desfase. Esa función ya valida NaN y rangos 0-1.

### 4.2 Distribución real del entrenamiento (consultas a la BD)

- `o` solo toma `{0, 0.25, 0.5, 0.75, 1.0}`. Está sesgado a valores bajos: en `type_user = 1`,
  90,484 en 0, 83,536 en 0.25, 25,102 en 0.5, 10,832 en 0.75 y 8,252 en 1.0.
- `p` depende mucho de `o` (mediana de `p` para `o` = 0 / .25 / .5 / .75 / 1: 0.13 / 0.235 / 0.46 /
  0.72 / 0.90). Existe para **todas** las parejas.
- `m` (coincidencia de perfil) es bimodal: `0`, o un valor en `[0.30, 0.90]`, o `1.0`. Nunca hay
  valores entre 0 y 0.30 (mínimo observado: 0.3001).
- `r` va de 0 a 4. **Regla dura:** `r = 0` si y solo si `m = 0` (0 filas incoherentes en el área 3).
  Entre los `r ≥ 1`: 71 % valen 1, 24 % valen 2, 5 % valen 3, 0.6 % valen 4.
- Por pareja usuario × carrera en el área 3: 36 % tienen 0 dimensiones con `m > 0`, 24 % una,
  13 % dos, 8 % tres, 9 % cuatro, 10 % las cinco.
- Por usuario en el área 3 (55 criterios de perfil posibles): el 94 % tiene entre 8 y 39 con `m > 0`.

### 4.3 Qué entrega hoy el sitio y Jev, y dónde no coincide

| # | Tema | Entrenamiento | Sitio / Jev hoy | Qué hacer |
|---|---|---|---|---|
| 1 | Escala de `o` | `{0, .25, .5, .75, 1}` | `porc_evaluation = puntuation / 5` → `{0.2, .4, .6, .8, 1.0}` | Convertir con `o = (puntuation - 1) / 4`, es decir `(porc_evaluation × 5 − 1) / 4` |
| 2 | `p` ausente | Siempre presente | La descripción solo es obligatoria con calificación 5. En el evento real, **43 de 43** objetivos llegaron sin descripción, así que `part_0` quedó vacío y no hay `p` para ninguna carrera | **Decisión de producto**, ver 4.4 |
| 3 | `m` de todos los criterios | Se necesita para todas las parejas | Jev califica los 215 criterios de perfil, pero `format_jev_response` solo devuelve los prioritarios y los de ≥ 60. Los demás se descartan | Devolver un mapa completo `criterio_id → coincidencia` |
| 4 | Valores de `m` | `0`, `[0.3, 0.9]` o `1.0` | Jev da un valor continuo 0-100 | Regla propuesta en 4.5 |
| 5 | `r` (repeticiones) | Entero 0-4 | Jev solo da un booleano `repeat`, y solo para los prioritarios | Regla propuesta en 4.5 |
| 6 | Dispersión | Casi todos los usuarios tienen muchas coincidencias | En el evento real, los 44 criterios prioritarios tuvieron coincidencias entre 6 y 62, con 1 solo `repeat = true` y 1 criterio ≥ 60. Solo 4 superan el piso de 0.30 (31, 42, 54 y 62) | Ver nota abajo |

Nota sobre el punto 6: no se guardaron las coincidencias de los otros 171 criterios del evento, así
que la dispersión total no está medida. Aun así, 4 de 44 prioritarios con `m > 0` apunta a un vector
mucho más disperso que el de casi cualquier usuario de entrenamiento (en el área 3, solo el 6 % de los
usuarios tiene menos de 8 de 55 criterios con coincidencia). Sería una extrapolación para el modelo.
Conviene leer el resultado como un **ranking** de carreras y no como porcentajes absolutos, y revisar
casos reales antes de mostrarlos. Para medir la dispersión real hay que guardar el mapa completo de
coincidencias (punto 3).

### 4.4 Opciones para `p` cuando no hay descripción

1. **Imputar `p` desde `o`** con la mediana del entrenamiento (0.13, 0.235, 0.46, 0.72, 0.90 para
   `o` = 0 … 1). Mantiene al vector dentro de lo que el modelo conoce. Es una imputación y hay que
   documentarla así.
2. **`p = 0`** cuando no hay descripción. Es simple, pero genera parejas como `o = 1, p = 0` que casi
   no existen en el entrenamiento (con `o = 1` la mediana de `p` es 0.90).
3. **Pedir la justificación en el frontend para todas las calificaciones** (o desde 2). Es lo más
   consistente con el entrenamiento, pero cambia la experiencia y añade tokens por carrera.

Mi recomendación provisional es la opción 1 y evaluar la 3 con producto.

### 4.5 Reglas propuestas para `m` y `r` (hipótesis a validar)

```
c = coincidencia de Jev / 100
m = c   si c ≥ 0.30,   si no 0          # el entrenamiento nunca tiene 0 < m < 0.30
r = 0   si m = 0
r = 1 (+1 si Jev marcó repeat = true)    # asunción: 71 % de los r ≥ 1 valen 1
```

No hay etiquetas reales para validar estas reglas: `y` es una fórmula, no un juicio humano. Solo
se pueden validar con revisión de casos reales y con pruebas de sensatez (por ejemplo, subir la
calificación de una carrera no debería bajar su puntaje).

### 4.6 Esquema de la conversión

```python
# Ilustrativo: aún no existe en el repo.
puntaje_objetivo = DataFrame(columns=["usuario_id", "carrera_id", "porc_objetivo"])
usuario_criterio = DataFrame(columns=["usuario_id", "carrera_id", "type_id", "riasec_id",
                                      "repeticiones", "porc_coincidencia"])
# Una fila por carrera en puntaje_objetivo (o convertida, regla 1).
# Por carrera: 1 fila con type_id=2, riasec_id=0 (p) y 5 filas con type_id=1, riasec_id en
# {1,2,4,5,6} (m y r). Siempre las 6 filas, aunque sean ceros.
# El mapa criterio_id -> (carrera_id, riasec_id) sale de QueryHandler.get_criteria_order_by_id_riasec.
llaves, X = TraineeModelHandler._build_features(puntaje_objetivo, usuario_criterio, carrera_ids)
X = X.reindex(columns=trained_model.columnas)
y_hat = np.clip(trained_model.modelo.predict(X), 0, 1)
```

`usuario_criterio` en BD tiene como clave `(usuario_id, criterio_id, repeticiones)` y el
entrenamiento tiene siempre `6 × carreras` filas por usuario, ceros incluidos.

## 5. Clasificación y despliegue

### 5.1 Lo medido

| Área | Entrenar al arrancar | Modelo en disco (joblib) |
|---|---|---|
| 1 | 93 s | 174.5 MiB comprimido (`compress=3`), 551 MiB sin comprimir |
| 2 | 6 s | 27.3 MiB comprimido |
| 3 | 6 s | 24.3 MiB comprimido |

- Entrenar las 3 áreas llega a un pico de ~**1.1 GiB** de RAM.
- El modelo del área 1, ya cargado en un proceso nuevo, ocupa ~**665 MiB** de RAM (pico durante la
  carga: ~1.2 GiB); cargarlo tarda 3.2 s.
- Predecir un usuario del área 1 (43 filas) tarda **57 ms**.
- Los modelos de las áreas 2 y 3 son ~7 veces más pequeños en disco; su RAM no se midió por separado.
- El deployment del clasificador pide `limits.memory: 256Mi`: **no alcanza** ni para entrenar ni para
  servir. El proceso se mataría por falta de memoria (OOM) al arrancar.

### 5.2 Qué conviene

- No entrenar al arrancar el pod. Entrenar aparte, guardar con `joblib` y cargar al iniciar
  (o bajo demanda por área). Solo el área 1 ya pide ~0.7 GiB estables y ~1.2 GiB de pico al cargar,
  así que el límite debe ser bastante mayor que los 256Mi actuales. Dimensionarlo midiendo en
  Linux, con la imagen real.
- Si se reduce el tamaño del modelo (`n_estimators = 300`, `min_samples_leaf = 5`), re-validar
  contra `type_user = 3`.
- `n_jobs = -1` se guarda dentro del modelo: en un contenedor con 250m de CPU conviene fijar
  `modelo.n_jobs = 1` tras cargarlo.
- Salida: puntaje por carrera con `clip(0, 1)`, ordenar descendente, tomar el top N. Nombre de carrera
  en `carreras.nom_carrera`; las 66 carreras tienen escuela en `escuela_carrera` (79 relaciones, 26 escuelas).

## 6. Lo que falta para unir todo el flujo

Flujo implícito en los eventos de `kinasis_library`:
`API → extractor_stream → [extractor] → classifier_stream → [clasificador] → generator_stream → [generador] → ResponseEvent`.

1. **Insertar al usuario real.** En `ApiHandler._submit_user_in_db` la inserción está comentada y
   `ExtractorEvent.user_id` es un `random.randint(1, 1000)`. La secuencia `usuarios_usuario_id_seq`
   nunca se ha usado y los usuarios sintéticos empiezan en 1,000,001, así que un alta real recibiría
   1, 2, 3… y los ids simulados **chocarían**. El evento debe llevar el `usuario_id` real que devuelve la BD.
2. **Persistir lo extraído** (`puntaje_objetivo`, `usuario_criterio`) y pasar `estatus_id` a 2.
   Pendiente de decidir si escribe el extractor o el clasificador.
3. **Definir el traspaso al clasificador.** `ClassifierEvent` solo trae
   `user_uuid, id_area, [id_hablity, criteria_score, quantity_repeat]`; **no lleva `o`** (calificación por
   carrera). Opciones: (a) persistir en BD y que el clasificador lea por `user_uuid` con `QueryHandler`
   (recomendada), o (b) ampliar `ClassifierEvent`, lo que exige subir la versión de la librería y
   publicarla en PyPI.
4. **Implementar `ClassifierEventHandler.classifier_task`** (sección 4 y 5), guardar en `resultados`
   y pasar `estatus_id` a 3.
5. **Implementar `generator_event_handler.py`** (hoy vacío): armar `ConstructorEvent` /
   `ResponseEvent` con escuelas y `top`, y `estatus_id` a 4.
6. **Avisar al sitio.** `espera.vue` solo anima pasos con un temporizador. No hay endpoint para
   consultar el estado ni los resultados por `uuid` (`endpoints.py` solo tiene `/get_areas`,
   `/{area_id}` y `/save-user`).
7. **Desplegar.** Aplicar los manifiestos (ningún workflow lo hace), crear los Secrets y ajustar
   memoria del clasificador.

Otros puntos a tener presentes:

- `Backend/.env` contiene credenciales reales en texto plano. Git lo ignora (verificado), pero no
  conviene compartirlo ni pegarlo en chats o logs.
- Las respuestas libres de los usuarios se guardan en `logs/criteria/` y `logs/errors/`. Los logs
  están ignorados por git; aun así son datos personales y deberían tener una política de retención.
- La entrega "como máximo una vez" (ack antes de procesar) implica que, si el worker muere a mitad de
  un evento, ese usuario se queda sin resultado. Una cola de reintentos o un `XAUTOCLAIM` lo resolvería,
  pero exige cambiar `kinasis_library`.
