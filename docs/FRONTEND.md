# Athena · Frontend (capa de datos)

Estado al 29-oct-2026, rama `devel` (commit `1e4645a`). Este documento cubre solo cómo el frontend obtiene, guarda y envía datos. Las pantallas y animaciones no se describen. El contrato del servidor está en [`Backend/BACKEND.md`](../Backend/BACKEND.md#2-contrato-http).

Stack: Nuxt 4.5 (Vue 3.5), Pinia 4, TypeScript; pruebas con Vitest 5 + happy-dom.

---

## 1. Configuración

- URL del backend: `runtimeConfig.public.apiBase`, que toma `NUXT_PUBLIC_API_BASE` (`Frontend/.env`). Todas las llamadas usan `$fetch` de Nuxt con `${apiBase}/…`.
- El backend solo acepta CORS desde `localhost:3000` / `127.0.0.1:3000`.
- En `Frontend/docker-compose.yml` el bloque `environment:` está al nivel raíz, no dentro del servicio, así que la variable no llega al contenedor.

---

## 2. Llamadas al backend

| Composable | Llamada | Cuándo | Validación en el cliente |
|---|---|---|---|
| `useAreasApi.fetchAreas` | `GET /get_areas` | Al montar `/datos-personales` | Error si la lista viene vacía. |
| `useAreasApi.fetchAreaData` | `GET /{area_id}` | Al enviar el formulario de datos personales | Error si `objetivos` no es arreglo o está vacío. |
| `useSaveUserApi.saveUser` | `POST /save-user` | "Finalizar" en `/riasec` | Exige string no vacío; un 422 de FastAPI se traduce a `campo: mensaje` legible. |
| `useResultsApi.fetchResults` | `GET /get-results/{uuid}` | Polling en `/espera` y carga de `/resultados` | Timeout 10 s, `retry: 0`, `AbortSignal`; exige `user_uuid` igual al pedido y `status_id` ∈ {1,2,3,4}. |

Los errores se normalizan con `utils/apiError.createApiError` a `{statusCode, message, details}`.

---

## 3. Del cuestionario recibido a lo que se envía

### 3.1 Lo que se recibe (`GET /{area_id}`)
`session.setAreaData` guarda la respuesta completa en el store y deriva:
- **Objetivos** (`normalizeObjectives`): descarta los que tienen `pregunta` nula o vacía o ids no enteros. Conserva `id_objetivo` e `id_carrera` tal como llegan, sin usar la posición como id. Se agrupan en bloques de 6.
- **Preguntas RIASEC**: `areaData.preguntas` tal cual; `opciones` (`{criterio_id: texto}`) se muestran como habilidades seleccionables.

### 3.2 Reglas que el cliente aplica antes de enviar
- Datos personales: nombre no vacío, correo con formato `x@y.z`, edad 12–100, avatar, área y términos aceptados.
- Objetivos: cada uno con valoración 1–5. La justificación es obligatoria con valoración ≥ 4 (`MIN_REQUIRED_JUSTIFICATION_RATING`). Coincide con el backend, que ignora `p` cuando `o < 0.75`.
- RIASEC: por dimensión, al menos 1 y como máximo 11 habilidades (`MAX_CRITERIOS_POR_DIMENSION`) y la respuesta abierta no vacía. El backend no impone el máximo.
- `findMissingData` revisa todo lo anterior otra vez sobre el payload final.

### 3.3 Lo que se envía (`session.saveUserPayload`)
```ts
{
  username: name, email, age: Number(age), area_id: selectedAreaId ?? 0,
  objetives: objectives.map(o => ({
    id_objetive: o.objectiveId, id_carrera: o.carreraId,
    puntuation: answers[o.carreraId]?.valoracion ?? 0,      // 0 provocaría 422; lo impide la validación previa
    description: answers[o.carreraId]?.justificacion.trim() ?? ''
  })),
  risec_questions: { [riasec_id]: {
    risec_id, open_question: respuestaAbierta.trim(),
    criteria_list: opcionIds.filter(id => id in q.opciones).map(id => ({ [id]: q.opciones[id] }))
  }}
}
```
Consecuencias para el backend:
- Solo se envían objetivos con `pregunta`; las carreras sin pregunta no reciben `puntaje_objetivo` y el classifier les asigna `o = 0`.
- Las respuestas se indexan por `carreraId`, no por `objectiveId` (hoy son el mismo valor).
- `risec_questions` contiene exactamente las dimensiones que trajo el área; el extractor espera las dimensiones 1, 2, 4, 5 y 6.

---

## 4. Persistencia local y ciclo de la evaluación

| Clave `localStorage` | Contenido |
|---|---|
| `athena_session_v2` | Snapshot completo del store (datos personales, avatar, `areaData`, respuestas, posición). Se escribe en cada acción y se restaura al montar cada página. |
| `athena_user_uuid` | UUID devuelto por `/save-user`. Marca que hay una evaluación enviada. |

Flujo:
1. `/riasec` → `saveUser` → guarda `athena_user_uuid` **antes** de navegar a `/espera`. Si ya existe un UUID, no reenvía y redirige.
2. Middleware global `pending-evaluation`: con UUID solo deja entrar a `/`, `/espera` y `/resultados`; sin UUID, `/espera` y `/resultados` redirigen a `/riasec`.
3. `/espera`: consulta `GET /get-results/{uuid}` al montar y luego cada **5 s**, sin solicitudes simultáneas. Muestra la etapa según `status_id` (1–3); con 4 navega a `/resultados`. Ante error muestra un aviso y sigue intentando. **No hay número máximo de intentos ni estado de fallo**, así que si el pipeline se cae la espera no termina. Si otra pestaña borra el UUID (evento `storage`), detiene el polling.
4. `/resultados`: vuelve a pedir el estado; si no es 4 regresa a `/espera`. `toCareerMatches` filtra resultados con nombre vacío o números inválidos, ordena por `top`, toma 3 y recorta `puntaje` a 0–100. Si la mejor coincidencia es < 60 % (`MIN_TOP_MATCH`) muestra el estado "baja coincidencia".
5. "Volver a hacer el test" → `session.startOver()` borra todas las claves `athena_*` y reinicia el store. `reset()` no borra nada mientras exista un UUID.

---

## 5. Pruebas

```powershell
cd Frontend; npx vitest run
```
Resultado el 29-oct-2026: **106 tests, 87 pasan y 19 fallan** (13 archivos, 5 con fallos).

| Archivo | Resultado | Relación con datos |
|---|---|---|
| `contract.spec.ts` | 5/5 | Lee `Backend/src/tests/fixtures/questionary_response.sample.json` y comprueba tipos, normalización de objetivos y bloques de 6. |
| `resultsPolling.spec.ts` | 12/12 | Polling de 5 s, transición 1→4, error y reintento, sin solicitudes simultáneas, cancelación, UUID borrado en otra pestaña. |
| `evaluationFlow.spec.ts` | 23/24 | Validaciones RIASEC, UUID guardado antes de `/espera`, sin doble envío, middleware. Falla "envía cada justificación… después de restaurar la sesión": no encuentra el botón `.block-nav-btn.is-next` (selector desactualizado tras el último cambio de UI). |
| `athenaSession.spec.ts` | 15/16 | Store y payload. Falla "un 4 sin justificación no bloquea el avance (es opcional)": la regla actual exige justificación con 4. Hay que decidir cuál es la regla correcta y alinear el test, la config y el comentario del backend. |
| `AvatarStoryCard`, `riasecStories`, `avatarCompanion` | 1/9, 2/9, 1/3 | Solo UI (historias y mensajes del avatar). Los tests esperan textos y constantes que cambiaron en `1e4645a`. |
| Resto (`AthenaStepper`, `avatarTheme`, `BaseButton`, `motion`, `RatingScale`, `useStoryPlayer`) | todos pasan | UI. |

No hay pruebas contra el backend real; todas las llamadas se simulan con `fetch` mockeado.
