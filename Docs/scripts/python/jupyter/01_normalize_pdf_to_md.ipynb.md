# 01_normalize_pdf_to_md.ipynb — extracción de PDF a texto

[Índice de documentación](../../../index.md) · [Abrir archivo original](../../../../Scripts/python/jupyter/01_normalize_pdf_to_md.ipynb)

**Archivo documentado:** `Scripts/python/jupyter/01_normalize_pdf_to_md.ipynb`  
**Revisión:** 2026-10-19. Descripción basada en el contenido local; no implica una ejecución del archivo.

Convierte los PDF de programas académicos a archivos Markdown mediante la herramienta de línea de comandos `markitdown`. Conserva el identificador del archivo: `1.pdf` produce `1.md`.

## Entradas y salidas

| Elemento | Configuración actual |
| --- | --- |
| Entrada | Ruta absoluta a `Scripts/python/assets/layouts/pdf` |
| Selección | Todos los nombres terminados exactamente en `.pdf`; no recorre subcarpetas |
| Salida configurada | Ruta absoluta a `Scripts/python/assets/layouts/test` |
| Archivos de texto que hoy consume el flujo | `Scripts/python/assets/layouts/markdown/1.md` a `66.md` |

La carpeta `test` no existe en el inventario revisado. El código no la crea. Para que su salida alimente al notebook 03, se debe configurar una carpeta existente y usar `layouts/markdown`, o trasladar los resultados después. El estado actual no conecta automáticamente ambas rutas.

## Código y ejecución

El notebook tiene cuatro celdas: explicación, clase, ejecución y una celda vacía. `ExtractorPDF.__init__` guarda `route_pdfs` y `route_md`. `run_command_bash` lista los PDF, cambia la extensión y ejecuta `markitdown 'entrada.pdf' > 'salida.md'` con `os.system`.

La tercera celda instancia la clase dentro de `if __name__ == "__main__"`; esa condición también se cumple normalmente en Jupyter. La redirección `>` reemplaza un Markdown existente. El orden de procesamiento depende de `os.listdir`; no se ordena por ID.

## Dependencias y uso

Instalar [requirements.txt](../assets/requirements.txt.md) en el entorno del kernel y comprobar que el ejecutable `markitdown` esté en el `PATH`. La conversión utiliza el extra `markitdown[pdf]`. Ajustar las dos rutas antes de ejecutar las celdas en orden.

## Comprobaciones y límites

El mensaje `Extracted text...` se imprime aunque el comando falle: no se comprueba el código de salida. Hay que verificar que cada Markdown exista y contenga texto, y contrastarlo con su PDF. No hay OCR adicional, validación de perfiles, conexión a PostgreSQL ni asignación de criterios RIASEC en este notebook. Los Markdown existentes tienen normalizaciones de texto; este código solo convierte, sin aplicar reglas explícitas de minúsculas o eliminación de acentos.

## Archivos relacionados

- [03 — consumidor de los Markdown](03_extract_criteria_for_careers.ipynb.md)
- [PDF de ejemplo](../assets/layouts/pdf/1.pdf.md)
- [Markdown de ejemplo](../assets/layouts/markdown/1.md.md)
