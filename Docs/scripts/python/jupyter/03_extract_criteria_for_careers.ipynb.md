# 03_extract_criteria_for_careers.ipynb — extracción de perfiles RIASEC

[Índice de documentación](../../../index.md) · [Abrir archivo original](../../../../Scripts/python/jupyter/03_extract_criteria_for_careers.ipynb)

**Archivo documentado:** `Scripts/python/jupyter/03_extract_criteria_for_careers.ipynb`  
**Revisión:** 2026-10-19. Descripción basada en el contenido local; no implica una ejecución del archivo.

Procesa cada Markdown numérico de carrera mediante Gemini y construye un Excel de criterios de perfil. Aplica la jerarquía **PERFIL → INTERNET → CONTINGENCIA** definida en [prompt.md](../assets/prompts/prompt.md.md). No genera criterios principales (`type_id=2`) ni escribe en PostgreSQL.

## Configuración y archivos

| Elemento | Valor en el código |
| --- | --- |
| Modelo solicitado | `gemini-2.5-pro` |
| Credencial | `GEMINI_API_KEY`, importada desde `lib.set_envs` |
| Prompt | `../assets/prompts/prompt.md` |
| Entrada | `../assets/layouts/markdown/*.md` |
| Resultado | `../assets/media/extraction_result/resultado_criterios.xlsx` |
| Caché por carrera | `../assets/media/extraction_result/raw/<carrera_id>.json` |
| Fecha de fuentes | `date.today()` en cada ejecución |

Las rutas relativas y el import `lib.set_envs` requieren iniciar el kernel desde `Scripts/python/jupyter` o configurar su ruta de módulos. La carpeta `raw` no está presente en el inventario actual; el notebook la crea al ejecutar. Dependencias: `pandas`, `google-genai`, `pydantic`, `tqdm`, `openpyxl` y biblioteca estándar.

## Esquemas y funciones

`Criterio` exige `desc_criterio` y `resumen_criterio`. `Etapa1` contiene `nombre_carrera`, `area_disciplinar` y un campo opcional por dimensión R, I, A, S, E, C. Un campo por dimensión evita listas con varios criterios de la misma letra en esa respuesta.

| Función | Comportamiento |
| --- | --- |
| `call_with_retry` | Hasta tres llamadas; tras los fallos previos al último espera 10 y 20 segundos |
| `etapa1_perfil` | Envía el Markdown y el prompt; exige JSON mediante esquema pydantic y temperatura 0.2 |
| `etapa2_internet` | Activa Google Search solo para dimensiones obligatorias faltantes; extrae JSON de la respuesta textual |
| `process_career_markdown` | Obtiene el ID del nombre, reutiliza caché si existe o ejecuta ambas etapas y guarda JSON |

El lote se ordena por ID numérico, registra excepciones por archivo y espera un segundo entre carreras procesadas. Los nombres no numéricos se marcan como `NO PROCESADO`. La caché se acepta por existencia: no incorpora hash del prompt, del Markdown ni versión del modelo; una edición de entrada requiere revisar la caché de esa carrera.

## Construcción de los datos

Para cada carrera y dimensión, primero toma evidencia de `perfil`; después, evidencia de `internet` marcada como encontrada; finalmente, una plantilla de contingencia ligada al área disciplinar. Artística es opcional y solo puede provenir de PERFIL. Todos los criterios llevan `type_id=1`.

Los identificadores son R=1, I=2, A=3, S=4, E=5 y C=6. Las cinco plantillas de contingencia usan aplicar procedimientos, investigar, orientar, emprender y organizar información del área. `fuente_id` es un consecutivo global solo para INTERNET; las demás procedencias no lo llevan.

| Hoja de salida | Contenido |
| --- | --- |
| `criterios` | Carrera, tipo, dimensión, descripción, resumen, origen y fuente |
| `fuentes` | Evidencia externa: título, institución, URL, fecha y fragmento |
| `cobertura_riasec` | Una fila por carrera con procedencia por dimensión, estado y observaciones |

## Validación y efectos

Los `assert` revisan una R/I/S/E/C por carrera presente, a lo sumo una A, A solo desde PERFIL, tipos, correspondencia de fuentes y resumen más corto que descripción. El código captura errores por archivo y continúa: estos controles no garantizan por sí solos que las 66 carreras originales hayan terminado correctamente. Revisar también `errors` y los totales.

Ejecutarlo envía el texto de las carreras a la API, puede realizar búsquedas externas y reemplaza el Excel de salida. La comprobación de fuentes sigue dependiendo del contenido devuelto por el modelo; no se descarga cada URL para verificarla de forma independiente en Python. Las salidas guardadas no prueban que una llamada nueva tendrá el mismo resultado.

## Archivos relacionados

- [Resultado existente y sus conteos](../assets/media/extraction_result/resultado_criterios.xlsx.md)
- [Libro consolidado que utiliza el cargador 04](../assets/layouts/excel/criterios.xlsx.md)
- [01 — preparación de texto](01_normalize_pdf_to_md.ipynb.md)
- [Variables de entorno](lib/set_envs.py.md)
- [Dependencias](../assets/requirements.txt.md)
