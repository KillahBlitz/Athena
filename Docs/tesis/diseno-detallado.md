# Diseño detallado y contratos

**Estado:** especificación documental; no acredita implementación ni resultados.

**Fuente:** document.md y powerpoint.md · objetivos y arquitectura; diapositiva 12. Véase [[tesis/referencias#Fuentes, cobertura y decisiones pendientes|Fuentes y pendientes]].

## Definido por las fuentes

- API REST con FastAPI; entradas y salidas validadas con Pydantic.
- Intercambio JSON y procesamiento basado en eventos con Redis.
- Errores y reintentos entre componentes.
- Persistencia de resultados para su consulta.

## Especificación pendiente

- Rutas, métodos, campos obligatorios y esquemas completos de eventos.
- Estados del procesamiento, correlación de solicitudes, límites de reintentos y tratamiento de duplicados.
- Versionado de contratos y asociación entre evaluación y resultado.

Los puntos pendientes son decisiones de diseño propuestas para completar los contratos; no se presentan como exigencias textuales. La diapositiva contiene solo una referencia a una imagen.

## Enlaces

- [[index-tesis|Volver al índice de tesis]]
