# Athena · Reporte del proyecto

Estado al 01-nov-2026, rama `devel`. Este documento une las piezas del sistema, su infraestructura y despliegue cloud. El detalle complementario está en:
- [`Backend/BACKEND.md`](../Backend/BACKEND.md): API, workers, modelo, base de datos, pruebas y riesgos del backend.
- [`Frontend/FRONTEND.md`](../Frontend/FRONTEND.md): cómo el cliente recibe, guarda y envía los datos.

## 1. Qué hace

Athena recomienda carreras del IPN a un aspirante dentro de un área académica (3 áreas, 66 carreras). El usuario valora con 1–5 un objetivo por carrera (justificando las valoraciones altas), elige habilidades y responde una pregunta abierta en cinco dimensiones RIASEC. Un servicio de evaluación semántica (JEV) puntúa cuánto coinciden esos textos con los criterios de cada carrera. Un `RandomForestRegressor`, entrenado con usuarios sintéticos, convierte esas señales en un porcentaje de afinidad por carrera, y se devuelven las 3 mejores con sus escuelas.

## 2. Componentes

| Carpeta | Rol | Estado |
|---|---|---|
| `Frontend/` | Nuxt 3 + Pinia + Tailwind. Flujo de 5 pasos: introducción, datos personales, objetivos, RIASEC, resultados (con pantalla de espera). | Funcional. Tests de contrato, sesión y polling pasando. |
| `Backend/` | API FastAPI + 3 workers (extractor, classifier, constructor) sobre Redis Streams y PostgreSQL. | Funcional. Tests unitarios pasando con mocks. |
| `library/kinasis_library` | Eventos Pydantic, cliente Redis Streams, engine de PostgreSQL y utilidades. Publicada en PyPI como `kinasis-library`. | En uso. |
| `DataBase/` | Esquema normalizado de 13 tablas, catálogos, datos de áreas/carreras/escuelas. `docker-compose` para desarrollo local y Cloud SQL (`athena-db`, PostgreSQL 15) para producción. | Desplegada y poblada en Cloud SQL. |
| `Scripts/python/jupyter` | Pipeline offline que construye el catálogo de criterios y el dataset sintético de entrenamiento. | Ver §4. |
| `Scripts/gcloud` | Encender y apagar la instancia Cloud SQL `athena-db` y clúster GKE `athena-cluster`. | Ver §6. |
| `.github/workflows` | CI/CD automatizado con pruebas unitarias, build de Docker y despliegue a GKE. | Ver §6. |

## 3. Flujo de punta a punta

| # | Paso | Dónde | Efecto en la base |
|---|---|---|---|
| 1 | Elegir área | `GET /get_areas` | — |
| 2 | Cargar cuestionario | `GET /{area_id}` → objetivos + preguntas RIASEC con opciones | — |
| 3 | Responder | Solo cliente; se guarda en `localStorage` | — |
| 4 | Enviar | `POST /save-user` → UUID; evento a `stream:extractor` | `usuarios` estatus 1 |
| 5 | Evaluar textos | Extractor → JEV `/decisions`; evento a `stream:classifier` | `puntaje_objetivo`, `usuario_criterio`, estatus 2 |
| 6 | Predecir afinidad | Classifier (modelo del área en memoria); evento a `stream:constructor` | estatus 3 |
| 7 | Guardar top 3 | Constructor guarda resultados finales | `resultados`, estatus 4 |
| 8 | Esperar y mostrar | El cliente consulta `GET /get-results/{uuid}` cada 5 s hasta estatus 4 | — |

## 4. Datos: del plan de estudios al modelo

El pipeline vive en notebooks y se ejecuta a mano, en orden:

1. **`01_normalize_pdf_to_md`**: convierte los PDF de los programas académicos a Markdown (markitdown) para reducir tokens.
2. **`02_generalte_construct_sql`**: genera `DataBase/scripts/insert_data.sql` (áreas, carreras, escuelas, `escuela_carrera`) a partir de `tablas_completas.xlsx`.
3. **`03_extract_criteria_for_careers`**: con Gemini y `assets/prompts/prompt.md`, extrae por carrera un criterio principal y criterios por dimensión RIASEC (jerarquía PERFIL → INTERNET → CONTINGENCIA) y produce `criterios.xlsx`.
4. **`04_submit_criteria_from_sql`**: carga 397 criterios (331 PERFIL + 66 PRINCIPAL, 66 carreras) a `public.criterios` en una transacción, con validación de llaves y re-ejecución idempotente.
5. **`05_generate_dataset_trainee`**: genera y sube usuarios sintéticos con sus `puntaje_objetivo`, `usuario_criterio` y `resultados`.

## 5. Base de datos

- **Esquema en producción (Cloud SQL - `athena-db`):** 13 tablas normalizadas en el esquema `public`:
  - Catálogos y estructura: `areas`, `tipos_riasec`, `pregunta_cuestionario`, `cuestionarios`, `carreras`, `escuelas`, `escuela_carrera`, `tipos_criterio`, `criterios`.
  - Usuarios y transaccional: `usuarios`, `resultados`, `usuario_criterio`, `puntaje_objetivo`.
- **Scripts:** `generate_tables.sql` (13 tablas), `insert_catalogs.sql` (tipos RIASEC y criterios), `insert_data.sql` (carreras y áreas).
- **Entorno local:** `DataBase/deployment/docker-compose.yml` permite levantar un PostgreSQL local con proxy Nginx para desarrollo desconectado. No se usa en la nube (la nube usa Cloud SQL).

## 6. Infraestructura Cloud y CI/CD (Google Cloud Platform)

### 6.1 Arquitectura en GKE (`athena-cluster`, zona `us-central1-a`)
- **Namespace:** `dev-athena`.
- **Base de Datos:** Cloud SQL for PostgreSQL 15 (`athena-db`).
- **Broker / Colas:** Pod de Redis (`athena-redis` y `service/redis-service:6379`) dentro del namespace `dev-athena`.
- **Microservicios Backend (Imagen única `athena-backend`):**
  - `athena-api`: Endpoint REST FastAPI (puerto 8000).
  - `athena-classifier`: Worker ML (`src/tasks/classifier_event_handler.py`).
  - `athena-extractor`: Worker JEV (`src/tasks/extractor_event_handler.py`).
  - `athena-constructor`: Worker de persistencia final (`src/tasks/constructor_event_handler.py`).
- **Frontend (Imagen `athena-frontend`):** Pod Nuxt 3 (puerto 3000).
- **Ingress:** `athena-ingress` enrutando `/` hacia `athena-frontend-service:3000` y `/api/*` hacia `athena-api-service:8000`.

### 6.2 Variables de Configuración y Secretos
1. **ConfigMap (`Backend/kubernetes/devel/athena-config.yaml`):** Versionado en Git. Contiene nombres de streams, hosts y puertos públicos o internos no sensibles:
   - `DB_HOST`, `DB_PORT`, `DB_USER`, `DB_NAME`, `REDIS_HOST`, `STREAM_*`, `GROUP_*`, `CONSUMER_*`.
2. **Secret (`athena-secret`):** **NO** se sube a Git por seguridad. Se crea una única vez directamente en el clúster desde Cloud Shell:
   ```bash
   kubectl create secret generic athena-secret \
     --from-literal=DB_PASSWORD="TU_PASSWORD_POSTGRES" \
     --from-literal=VERCEL_API_URL="TU_URL_API_JEV" \
     --from-literal=VERCEL_API_KEY="TU_KEY_JEV" \
     --from-literal=VERCEL_MODEL="typesafe-ai/jev" \
     -n dev-athena
   ```

### 6.3 Pipeline CI/CD (`.github/workflows/DeployToDevel.yml`)
Automatizado para ejecutarse en cada push a la rama `devel`:
1. **Fase 1 (Quality Gate):**
   - Backend: corre `pytest Backend/src/tests/unit` con `PYTHONPATH=Backend/src`.
   - Frontend: corre Vitest unit tests.
   - *Si alguna prueba falla, el pipeline se detiene inmediatamente.*
2. **Fase 2 (Build & Push Docker):**
   - Autentica con `GCP_SA_KEY` en Artifact Registry (`us-central1-docker.pkg.dev`).
   - Construye `athena-backend` usando `Backend/Dockerfile`.
   - Construye `athena-frontend` usando `Frontend/Dockerfile`.
   - Sube ambas imágenes con tags `${{ github.sha }}` y `latest`.
3. **Fase 3 (Deploy a GKE):**
   - Conecta `kubectl` al clúster `athena-cluster` vía `get-gke-credentials`.
   - Reemplaza `__IMAGE__` en los manifiestos con el tag del commit.
   - Aplica `athena-config.yaml`, `redis.yaml`, los 4 deployments de backend, el de frontend y el `ingress.yaml` en `dev-athena`.

### 6.4 Control de Costos (Pausar y Reanudar el Laboratorio)
- **Pausar cuando no se use (\$0 en cómputo):**
  ```bash
  gcloud container clusters resize athena-cluster --num-nodes=0 --zone=us-central1-a --project=athena-509922 --quiet
  gcloud sql instances patch athena-db --activation-policy=NEVER --project=athena-509922 --quiet
  ```
- **Reanudar antes de hacer pruebas:**
  ```bash
  gcloud sql instances patch athena-db --activation-policy=ALWAYS --project=athena-509922 --quiet
  gcloud container clusters resize athena-cluster --num-nodes=2 --zone=us-central1-a --project=athena-509922 --quiet
  ```

## 7. Rol de los Archivos Docker

- **`Backend/Dockerfile`:** Indispensable. Genera la imagen genérica de Python con todas las dependencias compartidas para FastAPI y los tres workers.
- **`Frontend/Dockerfile`:** Indispensable. Genera el contenedor optimizado de producción de Nuxt 3 (Node 20 Alpine).
- **`DataBase/deployment/docker-compose.yml`:** Opcional para desarrollo local offline. No interviene en el despliegue a la nube.
