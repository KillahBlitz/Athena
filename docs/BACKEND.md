# Athena · Backend

Estado al 29-oct-2026, rama `devel` (commit `1e4645a`). Visión general del sistema en [`docs/PROYECTO.md`](../docs/PROYECTO.md); contrato visto desde el cliente en [`Frontend/FRONTEND.md`](../Frontend/FRONTEND.md).

El backend está formado por una API HTTP (FastAPI) y tres workers que se comunican por Redis Streams. Todos leen y escriben en PostgreSQL. La API recibe el cuestionario y responde de inmediato; los workers calculan el resultado en segundo plano y el cliente consulta el avance por polling.

```
Frontend ──HTTP──► API (main/endpoints.py)
                    │ INSERT usuarios (estatus 1)
                    └─► extractor_stream ─► Extractor ── JEV (/decisions)
                                              │ INSERT puntaje_objetivo, usuario_criterio (estatus 2)
                                              └─► classifier_stream ─► Classifier (RandomForest por área)
                                                                         │ (estatus 3)
                                                                         └─► constructor_stream ─► Constructor
                                                                                                     │ INSERT resultados top 3 (estatus 4)
Frontend ◄──HTTP── GET /get-results/{uuid} ◄────────────────────────────────────────────────────────┘
```

---

## 1. Estructura

| Ruta | Contenido |
|---|---|
| `src/main/endpoints.py` | App FastAPI `api`, CORS y las 4 rutas. |
| `src/handlers/api_handler.py` | Lógica de la API: arma el cuestionario, registra al usuario, publica el evento y construye resultados. |
| `src/handlers/query_handler.py` / `command_handler.py` | Fachadas de lectura / escritura sobre los repositorios (patrón CQRS ligero). Cada una crea su propio `Engine`. |
| `src/handlers/extraction_handler.py` | Construye el prompt para JEV, valida y normaliza su respuesta y la persiste. |
| `src/handlers/trainee_model_handler.py` | Carga datos sintéticos, vectoriza, entrena y valida un `RandomForestRegressor` por área. |
| `src/handlers/classification_handler.py` | Vectoriza a un usuario real con las mismas columnas del modelo y predice el ranking. |
| `src/tasks/*_event_handler.py` | Los tres workers (`extractor`, `classifier`, `constructor`). Cada uno es un `while True` que consume su stream. |
| `src/service/jev.py` | Cliente HTTP (`httpx2`) del servicio JEV. |
| `src/prompts/jev_prompt.json` | Las 3 plantillas de instrucción que se envían a JEV. |
| `src/models/tables/` | Mapeos SQLAlchemy 2 (una clase por tabla). |
| `src/models/repository/` | Consultas por tabla. Las lecturas para el modelo devuelven `pd.DataFrame`. |
| `src/models/request`, `response` | Esquemas Pydantic del contrato HTTP. |
| `src/models/trainee_data.py` | Contenedores Pydantic que validan columnas de los DataFrames (`Pieza`, `TraineeData`, `TrainedModel`). |
| `src/utils/set_envs.py` | Lee credenciales de DB y Redis desde variables de entorno. |
| `src/tests/` | Pruebas unitarias (pytest). |
| `../library/kinasis_library` | Paquete compartido: eventos Pydantic, `RedisConsumer`, `create_postgres_engine`, `ConfigManager`, `generate_uuid`. Se instala desde PyPI (`kinasis-library==1.1.0`). |

---

## 2. Contrato HTTP

Base: `http://127.0.0.1:8000` en local. CORS solo permite `http://localhost:3000` y `http://127.0.0.1:3000`. No hay autenticación.

### `GET /get_areas`
Devuelve `[{ "area_id": int, "nom_area": str }]`. 404 si la consulta devuelve `None` (con tabla vacía devuelve `[]`, no 404).

### `GET /{area_id}` → `QuestionaryResponse`
```json
{
  "area_id": 1, "nom_area": "…",
  "objetivos": [{ "id_carrera": 5, "id_objetivo": 5, "pregunta": "… | null" }],
  "preguntas": [{ "riasec_id": 1, "texto_pregunta": "…", "pregunta_abierta": "…",
                  "opciones": { "123": "resumen_criterio", "…": "…" } }]
}
```
- `objetivos`: una entrada por carrera del área, ordenada por `carrera_id`. `id_objetivo` es el mismo `carrera_id`; `pregunta` sale de `carreras.pregunta_objetivo` y puede ser `null`.
- `preguntas`: las de `cuestionarios` para el área, ordenadas por `pregunta_id`. `opciones` son los criterios de tipo PERFIL (`type_id = 1`) de todas las carreras del área con el mismo `riasec_id`, como `{criterio_id: resumen_criterio}`.
- 404 si el área no existe. La ruta es comodín, así que cualquier `GET /<texto>` no numérico responde 422.
- Ejemplo real versionado: `src/tests/fixtures/questionary_response.sample.json` (el frontend lo usa en su test de contrato).

### `POST /save-user` → `str` (UUID)
```json
{
  "username": "str", "email": "str", "age": 17, "area_id": 1,
  "objetives": [{ "id_objetive": 5, "id_carrera": 5, "puntuation": 1-5, "description": "str" }],
  "risec_questions": { "1": { "risec_id": 1, "criteria_list": [{ "123": "texto" }], "open_question": "str" } }
}
```
1. Inserta en `usuarios` con `uuid_usuario = "USER-<uuid4>"`, `estatus_id = 1`, `type_user = 4` (usuario real). `age` se valida pero **no se guarda**.
2. Convierte `puntuation` 1–5 a `porc_evaluation` 0, 0.25, 0.5, 0.75, 1.0.
3. Publica un `ExtractorEvent` en `extractor_stream` y responde el UUID como string JSON.

Validación: Pydantic devuelve 422 si `puntuation` está fuera de 1–5 o falta un campo. No hay validación de formato de correo, de pertenencia de `id_carrera` al área ni de límite de criterios seleccionados.

### `GET /get-results/{user_uuid}` → `ResultResponse`
```json
{ "user_uuid": "USER-…", "status_id": 1,
  "results": null | [{ "top": 1, "carrera_id": 5, "carrera": "…", "puntaje": 87.3, "escuelas": ["…"] }] }
```
`results` solo se llena con `status_id == 4`: top 3 de `resultados` ordenado por `porc_coincidencia` desc, `puntaje = round(porc*100, 1)`, escuelas por `escuela_carrera`. 404 si el UUID no existe.

### Estados del usuario (`usuarios.estatus_id`)

| id | Significado | Lo escribe |
|---|---|---|
| 1 | PENDING: registrado, evento publicado | API |
| 2 | EXTRACTED: respuestas evaluadas y guardadas | Extractor |
| 3 | CLASSIFIED: ranking calculado | Classifier |
| 4 | COMPLETED: top 3 en `resultados` | Constructor |

---

## 3. Pipeline asíncrono

### 3.1 Transporte (Redis Streams, `kinasis_library.services.redis_interface`)
- `event_producer` serializa el modelo Pydantic a JSON y hace `XADD stream {_kinasis_event_format: "json-v1", payload: "<json>"}`. Sigue aceptando el formato anterior (campos sueltos) al leer.
- `start_redis_consumer` crea el grupo si no existe (`XGROUP CREATE … MKSTREAM`), lee 1 mensaje con `XREADGROUP … >` y bloqueo de 2 s, y hace **`XACK` antes de devolver el evento**, es decir antes de procesarlo.
- Los consumidores leen el nombre de su stream de `STREAM_*`, pero los productores usan nombres fijos en el código: `extractor_stream`, `classifier_stream`, `constructor_stream`. Las variables `STREAM_*_SEND` se leen y no se usan.

### 3.2 Extractor (`tasks/extractor_event_handler.py` + `handlers/extraction_handler.py`)
Entrada: `ExtractorEvent {user_id, uuid_user, area_id, objetives[], questions{riasec_id: {criteria_list, open_question}}}`.

1. **Contexto** (`get_info_prompt`): carga todos los criterios del área ordenados por `riasec_id` y arma:
   - `part_0`: por cada objetivo con `description` no vacía, el criterio principal (`riasec_id = 0`) de su carrera → `{criteria_id, criteria, description}`.
   - `part_1, part_2, part_4, part_5, part_6`: por dimensión RIASEC (Artístico, `3`, se omite) → `{dimension, criteria: {id: resumen} de todas las carreras del área, priority_criteria: los que el usuario marcó, open_question}`.
2. **Prompt** (`generate_prompt_for_jev`): `input` es `prompt_info` en JSON y `questions` es una lista de decisiones:
   - `part_0:<id>:coincidence` y `part_k:<id>:coincidence`: tipo `score`, 6 niveles (`0,20,40,60,80,100`).
   - `part_k:<id>:repeat`: tipo `choice` `true/false`, solo para los criterios marcados.
   - Tamaño: `|part_0| + Σ criterios del área en las 5 dimensiones + criterios marcados`. Con ~5 criterios PERFIL por carrera, en el área 1 (43 carreras) son del orden de 300 preguntas en una sola llamada.
3. **JEV** (`service/jev.py`): `POST {VERCEL_API_URL}/decisions` con `{model, input, questions}`, `Authorization: Bearer VERCEL_API_KEY`, timeout 30 s, sin reintentos. Modelo por defecto `typesafe-ai/jev`.
4. **Normalización** (`format_jev_response`): el índice `score` 0–5 se convierte a `round(score/5*100)`. Un tipo distinto, `NaN`, valor fuera de rango o `choice` distinto de `"true"/"false"` lanza `ValueError` (no se convierte en 0).
5. **Persistencia** (`save_result_to_db`), en este orden:

   | Qué | Tabla | `porc_coincidencia` | `repeticiones` |
   |---|---|---|---|
   | Valoración de cada objetivo | `puntaje_objetivo.porc_objetivo` | 0–1 según `puntuation` | — |
   | Criterio principal de la carrera de cada objetivo | `usuario_criterio` | `part_0` / 100, o `0.0` si JEV no lo evaluó (sin justificación) | `1` si > 0, si no `0` |
   | Criterio marcado por el usuario | `usuario_criterio` | `1.0` siempre | `2` si JEV dice que la respuesta abierta lo menciona, si no `1` |
   | Criterio no marcado con puntaje ≥ 60 | `usuario_criterio` | puntaje / 100 | `1` |

   Los criterios no marcados con puntaje < 60 no se guardan. Cada inserción es su propia transacción. Al final cambia el estado a 2 y publica `ClassifierEvent {user_uuid, user_id, id_area}`.

### 3.3 Classifier (`tasks/classifier_event_handler.py`)
**Arranque.** Antes de consumir, `TraineeModelHandler.start_trainee_models()` entrena un modelo para cada área 1, 2 y 3 (fijas en código) con los usuarios sintéticos de la base (`type_user` 1 = entrenamiento, 2 = validación). Tarda ~1 min. Los modelos viven en memoria; no se serializan y se reentrenan en cada reinicio.

**Vector por pareja usuario × carrera** (mismo código conceptual en entrenamiento e inferencia):

| Columna | Origen |
|---|---|
| `carrera_<id>` | one-hot de la carrera (categorías = carreras del área) |
| `o` | `puntaje_objetivo.porc_objetivo` |
| `p` | `porc_coincidencia` del criterio principal (`type_id = 2`). Se fuerza a `0` cuando `o < 0.75`, porque con valoración < 4 la justificación es opcional y el modelo no debe confundir "no escribió" con "no coincide". |
| `{r,i,s,e,c}_coinc`, `{r,i,s,e,c}_rep` | `porc_coincidencia` y `repeticiones` del criterio PERFIL de esa carrera en cada dimensión (`riasec_id` 1, 2, 4, 5, 6). |

- Entrenamiento: exige que no falte ningún valor ni haya duplicados (los datos sintéticos traen las 6 filas por carrera) y que los porcentajes estén en [0, 1]. Etiqueta `y = resultados.porc_coincidencia` del usuario sintético.
- Inferencia (`UserClassificationHandler`): una fila por carrera del área; lo que el usuario no tiene se rellena con `0.0`; columnas reordenadas a `modelo.columnas`. Rechaza más de un registro por carrera y dimensión.
- Modelo: `RandomForestRegressor(n_estimators=300, min_samples_leaf=5, random_state=42, n_jobs=-1)`. Predicción recortada a [0, 1] y ordenada desc (orden estable).
- Validación: imprime `mae`, `rmse`, `r2`, `mae_y_alta` (solo `y ≥ 0.5`) y la carrera con mayor MAE. Las métricas solo se imprimen en consola; no hay umbral que impida arrancar con un modelo malo. Los usuarios `type_user = 3` (test) no se usan en el backend.

Por evento: clasifica, pone estado 3 y publica `ConstructorEvent {user_uuid, careers_list: [{career_id, score}]}` con **todas** las carreras del área.

### 3.4 Constructor (`tasks/constructor_event_handler.py`)
Ordena `careers_list` por `score`, toma 3, borra los `resultados` previos del usuario e inserta los nuevos en una transacción, y pone estado 4.

---

## 4. Base de datos (usada por el backend)

Esquema completo en `DataBase/scripts/generate_tables.sql` (PostgreSQL ≥ 13). Catálogos en `insert_catalogs.sql`: `tipos_riasec` 0 Principal, 1 Realista, 2 Investigador, 3 Artística, 4 Social, 5 Emprendedor, 6 Convencional; `tipos_criterio` 1 PERFILES, 2 PRINCIPAL.

| Tabla | Clave | Uso en el backend |
|---|---|---|
| `areas`, `carreras`, `escuelas`, `escuela_carrera`, `pregunta_cuestionario`, `cuestionarios`, `criterios` | — | Solo lectura (catálogo). |
| `usuarios` | `usuario_id` identity, `uuid_usuario` UNIQUE | API inserta; workers actualizan `estatus_id`. `type_user`: 1 entrenamiento, 2 validación, 3 test, 4 real. |
| `puntaje_objetivo` | PK (`usuario_id`, `carrera_id`) | Extractor inserta. |
| `usuario_criterio` | PK (`usuario_id`, `criterio_id`, `repeticiones`) | Extractor inserta. |
| `resultados` | `id_resultado` identity | Constructor reemplaza (top 3). Los sintéticos traen una fila por carrera y sirven de etiqueta. |

Cada `QueryHandler` y `CommandHandler` crea un `Engine` con pool 5 + 5 overflow, `pool_pre_ping` y reciclado a 30 min. La API crea uno de cada uno; cada worker también.

---

## 5. Configuración

Variables (archivo `Backend/.env`, ignorado por git; en Kubernetes vienen de un `Secret` vía `envFrom`):

| Grupo | Variables |
|---|---|
| PostgreSQL | `DB_HOST`, `DB_PORT`, `DB_USER`, `DB_PASSWORD`, `DB_CONECTION` (nombre de la base) |
| Redis | `REDIS_HOST`, `REDIS_PORT`, `REDIS_PASSWORD` |
| JEV | `VERCEL_API_URL`, `VERCEL_API_KEY`, `VERCEL_MODEL` (opcional) |
| Streams | `STREAM_`, `GROUP_`, `CONSUMER_` + `EXTRACTOR` / `CLASSIFIER` / `CONSTRUCTOR`; `STREAM_EXTRACTOR_SEND`, `STREAM_CLASSIFIER_SEND` (sin uso) |
| Otros | `PYTHONPATH`, `ENVIRONMENT` (sin uso en el código) |

Dependencias (`assets/requirements.txt`): fastapi 0.150, uvicorn 0.54, pydantic 2.13, SQLAlchemy 2.1, psycopg 3.3, redis 8.1, pandas 3.0, numpy 2.5, scikit-learn 1.9, httpx2 2.16, pytest 9.1. Más `kinasis-library==1.1.0`.

---

## 6. Ejecución

Local (bash; en Windows usar WSL o Git Bash). Ambos scripts activan `Backend/venv`, cargan `.env` y fijan `PYTHONPATH=src:../library`:

```bash
./start.sh                       # API: uvicorn main.endpoints:api --reload en 127.0.0.1:8000
./start_workers.sh               # classifier + extractor + constructor, con prefijo [nombre] en el log
./start_workers.sh extractor     # solo algunos
```
`start_workers.sh` detiene a todos si uno termina, y devuelve el código de salida de ese worker.

Contenedor (`Dockerfile`): `python:3.14-slim`, una sola imagen para todos los workers; `ENTRYPOINT python`, `CMD src/tasks/classifier_event_handler.py`; cada Deployment cambia `args`. La imagen no trae comando para la API (uvicorn).

Kubernetes: solo existe `kubernetes/devel/athena-classifier/deployment.yaml` (namespace `dev-athena`, imagen `__IMAGE__` que reemplazaría el pipeline, límites 256 Mi / 250 m). El de extractor está vacío y no hay manifiestos para constructor ni API. `docker-compose.yml` del backend está vacío.

---

## 7. Pruebas

```powershell
# desde la raíz del repo
$env:PYTHONPATH = "$PWD\Backend\src;$PWD\library"
.\.venv\Scripts\python.exe -m pytest Backend\src\tests -q
```
Resultado el 29-oct-2026: **36 passed en ~10 s** (venv con Python 3.11.4, no 3.14 como la imagen). `conftest.py` fija credenciales falsas de DB/Redis con `setdefault`, así que las pruebas no tocan servicios reales: usan SQLite (archivo temporal o memoria) y `Mock`.

| Archivo | Tests | Qué cubre |
|---|---|---|
| `test_api_contract.py` | 7 | `GET /{area_id}` serializa igual que el fixture; 404 de área; `get_areas`; mapeo de `puntuation`→porcentaje sin mutar el request; no publica si falla el INSERT; `POST /save-user` responde 200 con el UUID. |
| `test_extraction_handler.py` | 5 | RAG de `part_0` solo con criterios del área; evento → prompt → request a JEV conserva criterios y salida; respuestas inválidas de JEV no se convierten en 0 (parametrizado). |
| `test_extraction_persistence.py` | 10 | Normalización y conteo de `repeticiones`; no marca estado 2 si falla una escritura; persistencia real con SQLite; criterio principal en 0.0 sin evaluación; rollback ante duplicados; `update_user_status` con UUID desconocido no afecta a otros. |
| `test_user_classification.py` | 10 | Forma y orden de columnas del vector; relleno de faltantes; rechazo de datos ambiguos; ranking ordenado y recortado; el classifier usa el modelo del área del evento; vector de inferencia idéntico al de entrenamiento; `p` oculto con `o < 0.75` en ambos. |
| `test_user_data_retrieval.py` | 3 | `get_user_data` filtra por usuario, devuelve las columnas que exigen las `Pieza` y DataFrames vacíos con columnas si no hay filas. |
| `test_setter_test.py` | 1 | Placeholder (`assert True`). |

Sin cobertura: el Constructor, el entrenamiento completo con datos de la base (`_train_area`, métricas), `RedisConsumer` contra un Redis real, el cliente JEV contra el servicio real, consultas específicas de PostgreSQL y una prueba de extremo a extremo de los cuatro estados. CI no ejecuta las pruebas.

---

## 8. Riesgos y pendientes conocidos

Ordenados por impacto en el flujo del usuario.

1. **Un fallo deja al usuario esperando para siempre.** El `XACK` ocurre antes de procesar y los bucles no tienen `try/except`: si JEV responde error o tarda más de 30 s, o falla una escritura, el worker termina y el evento se pierde. El usuario queda en estado 1, 2 o 3 y el frontend sigue consultando cada 5 s sin límite. No hay estado de error ni cola de reintentos.
2. **Sin idempotencia en el Extractor.** Si se reprocesara un evento, chocaría con las PK de `puntaje_objetivo` y `usuario_criterio`. Las escrituras van en transacciones separadas, así que un fallo a mitad deja datos parciales (el estado sí se queda en 1, lo cual está probado).
3. **Inserción y publicación no son atómicas en `/save-user`.** Si Redis falla después del INSERT, queda un usuario en estado 1 sin evento y la API responde 500.
4. **Una sola llamada a JEV con cientos de preguntas** y timeout de 30 s, sin reintento ni troceo.
5. **Supuestos rígidos sobre RIASEC.** `_obtain_context_dimention` accede a `event.questions[k]` para 1, 2, 4, 5 y 6; si el área no envía alguna de esas dimensiones lanza `KeyError`. La dimensión 3 se ignora aunque tenga criterios.
6. **Classifier sin modelo para áreas nuevas.** Las áreas 1–3 están fijas; para otra área `modelo` es `None` y la vectorización falla. El arranque depende de que existan datos sintéticos completos en la base, y el límite de 256 Mi del Deployment no se ha comprobado frente a 300 árboles por área.
7. **Nombres de stream duplicados**: fijos en los productores y configurables en los consumidores. Si se cambian las variables, el pipeline se desconecta sin error.
8. **API**: sin autenticación ni límite de peticiones; CORS solo para localhost; `GET /{area_id}` captura cualquier ruta de un segmento; la rama 404 de `/save-user` es inalcanzable (`generate_user_event` nunca devuelve `None`; los fallos salen como 500 genérico); `age` no se persiste.
9. **Código muerto o vacío**: `LOGS_DIR` y `traceback` sin uso en el extractor (la carpeta `Backend/logs/` es de una versión anterior y está en `.gitignore`); `google_cloud.py`, `error_event.py` vacíos y `response_event.py` sin uso en la librería; `setup.py` de la librería no declara dependencias (pydantic, redis, SQLAlchemy); `pytest` en las dependencias de producción.
