# set_envs.py — configuración desde el entorno

[Índice de documentación](../../../../index.md) · [Abrir archivo original](../../../../../Scripts/python/jupyter/lib/set_envs.py)

**Archivo documentado:** `Scripts/python/jupyter/lib/set_envs.py`  
**Revisión:** 2026-10-19. Descripción basada en el contenido local; no implica una ejecución del archivo.

Centraliza los valores que usan los notebooks para Gemini y PostgreSQL. El módulo evalúa `os.getenv` al importarse y publica `GEMINI_API_KEY` y el diccionario `DB_CONFIG`. Importarlo no abre conexiones ni envía peticiones.

## Variables reconocidas

| Variable del entorno | Destino | Consideración |
| --- | --- | --- |
| `GEMINI_API_KEY` | Cliente de Gemini del notebook 03 | Tiene un valor de sustitución si falta; no equivale a una credencial funcional |
| `DB_HOST` | `DB_CONFIG['host']` | Servidor PostgreSQL; hay un valor local predeterminado |
| `DB_PORT` | `DB_CONFIG['port']` | Se convierte con `int`; predeterminado 5432 |
| `DB_USER` | `DB_CONFIG['user']` | Usuario de la conexión |
| `DB_PASSWORD` | `DB_CONFIG['password']` | Contraseña de la conexión |
| `DB_CONECTION` | `DB_CONFIG['dbname']` | Este es el nombre exacto, con esa ortografía |

No lee archivos `.env` ni llama a `load_dotenv`. Las variables deben estar presentes en el proceso que inicia el kernel. Un `DB_PORT` no numérico causa error durante el import. Si se cambia el entorno después del import, el diccionario ya creado no se actualiza automáticamente; hay que recargar el módulo o reiniciar el kernel.

## Relación con los notebooks

El 03 importa `GEMINI_API_KEY`. Los notebooks 04 y 05 importan `DB_CONFIG`; además resuelven la raíz y agregan la carpeta Jupyter a `sys.path`. Los valores de conexión predeterminados permanecen en el archivo original; esta ficha describe sus nombres sin duplicar credenciales.

## Archivos relacionados

- [03 — conexión a Gemini](../03_extract_criteria_for_careers.ipynb.md)
- [04 — carga de criterios](../04_submit_criteria_from_sql.ipynb.md)
- [05 — dataset sintético](../05_generate_dataset_trainee.ipynb.md)
