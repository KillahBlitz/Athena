# Arquitectura y justificación tecnológica

**Estado:** especificación documental; no acredita implementación ni resultados.

**Fuente:** document.md · Arquitectura y justificación tecnológica; Objetivos Específicos.

El sistema se implementará mediante una arquitectura de microservicios con comunicación basada en eventos. Las responsabilidades se distribuirán entre el sitio web, la API, el homologador de habilidades, el clasificador y el constructor de resultados.

El sitio web recopilará la información y enviará las solicitudes a la API. Esta iniciará el procesamiento mediante los eventos correspondientes. El homologador analizará las respuestas y las relacionará con el catálogo; el clasificador procesará las habilidades obtenidas; y el constructor integrará los datos necesarios para presentar las recomendaciones. Los resultados se almacenarán para su consulta desde la plataforma.

Las tecnologías seleccionadas se vinculan con las necesidades de cada componente:

|  |  |
| --- | --- |
| **Tecnología** | **Aplicación y justificación dentro del proyecto** |
| Vue, Nuxt y TypeScript | Construcción de las pantallas y componentes de la plataforma, organización de la navegación y definición de los datos intercambiados con la API. |
| Python | Desarrollo de los servicios de procesamiento, preparación de datos e integración de los modelos de aprendizaje automático. |
| FastAPI y Pydantic | Construcción de la API y definición de estructuras de entrada y salida para mantener consistencia en la comunicación entre componentes. |
| PostgreSQL y pgvector | Almacenamiento de información académica y resultados, junto con las representaciones vectoriales y consultas requeridas por el mecanismo de recuperación. |
| Redis | Soporte para el intercambio de eventos y la distribución de tareas entre los servicios de procesamiento. |
| Docker | Empaquetado de cada servicio con sus dependencias y configuración para reproducir los entornos de ejecución. |
| GitHub | Administración del código mediante un mono repositorio con separación entre interfaz, servicios y base de datos. |
| GitHub Actions | Automatización de la construcción, las pruebas y las actividades de despliegue. |
| Google Cloud | Alojamiento de los componentes y recursos necesarios para la operación de la plataforma. |

## CI/CD, contenedores y despliegue

- Código en GitHub como monorepositorio, separando Frontend, Backend y Base de Datos.
- Estrategia de ramas para trabajo colaborativo.
- GitHub Actions para construcción, pruebas unitarias, integración y liberación.
- Contenedor independiente por servicio con Docker.
- Automatizar imágenes y despliegue a desarrollo, pruebas o producción en Google Cloud.
- Infraestructura como código para entornos reproducibles.
- Monitoreo y registros para detectar fallas.

Las fuentes no eligen productos concretos de Google Cloud, recursos ni objetivos de escalamiento. Este nodo expresa el alcance requerido, no el estado actual de los pipelines.

## Enlaces

- [[index-tesis|Volver al índice de tesis]]
