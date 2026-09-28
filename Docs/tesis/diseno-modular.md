# Diseño modular

**Estado:** especificación documental; no acredita implementación ni resultados.

**Fuente:** document.md y powerpoint.md · arquitectura; diapositiva 11. Véase [[tesis/referencias#Fuentes, cobertura y decisiones pendientes|Fuentes y pendientes]].

| Módulo | Responsabilidad | Tecnología indicada |
| --- | --- | --- |
| Sitio web | Captura y presentación | Vue, Nuxt, TypeScript |
| API | Validar e iniciar solicitudes, consultar resultados | FastAPI, Pydantic, Python |
| Homologador | Interpretar STAR y vincular habilidades al catálogo | Python, ajuste fino y RAG |
| Clasificador | Inferir carreras compatibles | Python, modelo supervisado |
| Constructor | Integrar resultados, porcentajes y escuelas | Python |
| Persistencia | Catálogo, vectores y resultados | PostgreSQL y pgvector |
| Eventos | Distribuir tareas | Redis |

Cada servicio se empaqueta con Docker. La figura original queda pendiente de recuperar.

## Enlaces

- [[tesis/diseno-detallado|Diseño detallado y contratos]]
- [[tesis/base-de-datos|Base de datos y modelo entidad-relación]]
- [[tesis/arquitectura-y-justificacion-tecnologica#CI/CD, contenedores y despliegue|CI/CD, contenedores y despliegue]]
- [[index-tesis|Volver al índice de tesis]]
