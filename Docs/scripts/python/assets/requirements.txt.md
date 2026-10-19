# requirements.txt — dependencias del entorno Python

[Índice de documentación](../../../index.md) · [Abrir archivo original](../../../../Scripts/python/assets/requirements.txt)

**Archivo documentado:** `Scripts/python/assets/requirements.txt`  
**Revisión:** 2026-10-19. Descripción basada en el contenido local; no implica una ejecución del archivo.

Lista doce paquetes, uno por línea, sin versiones fijadas. Sirve para preparar el entorno que ejecuta los notebooks; no instala por sí mismo PostgreSQL, Google Cloud CLI ni una instancia de base de datos.

| Dependencia | Función en este directorio |
| --- | --- |
| `openpyxl` | Lectura/escritura de libros Excel en los notebooks 02–04 |
| `pandas` | Tablas, transformación, Excel y construcción del dataset |
| `polars` | Disponible para manipulación de datos; no se importa en los cinco notebooks actuales |
| `fastexcel` | Motor de lectura Excel disponible; no se importa directamente en los notebooks actuales |
| `pydantic` | Esquemas de respuesta de Gemini y modelos de tablas |
| `sqlalchemy` | Disponible en el entorno; la carga actual utiliza psycopg2 directamente |
| `psycopg2-binary` | Conexión, transacciones, inserción y COPY en PostgreSQL |
| `markitdown[pdf]` | Conversión de PDF a texto Markdown |
| `google-genai` | Cliente Gemini y herramientas de búsqueda |
| `tqdm` | Progreso de la extracción por carreras |
| `ipykernel` | Kernel Python para Jupyter |
| `jupyterlab` | Interfaz para ejecutar los notebooks |

## Instalación

Desde la raíz del repositorio, en el entorno elegido:

```bash
python -m pip install -r Scripts/python/assets/requirements.txt
```

El notebook 05 también importa directamente `numpy`, `matplotlib` y `sklearn`, que **no están declarados** en este archivo. Para instalar esos paquetes en el kernel activo:

```python
%pip install numpy matplotlib scikit-learn
```

El nombre de instalación es `scikit-learn`; los imports del código siguen siendo `from sklearn...`. No usar `pip install sklearn`. Algunas dependencias pueden llegar transitivamente, pero este archivo no fija sus versiones ni declara todo el conjunto del notebook 05.

No se modificó la lista durante esta documentación. Para reproducibilidad del dataset también importa conservar las versiones del entorno, no solo la semilla del generador.

## Archivos relacionados

- [01 — markitdown](../jupyter/01_normalize_pdf_to_md.ipynb.md)
- [03 — Gemini](../jupyter/03_extract_criteria_for_careers.ipynb.md)
- [05 — dependencias adicionales](../jupyter/05_generate_dataset_trainee.ipynb.md)
