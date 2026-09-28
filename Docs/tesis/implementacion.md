# Implementación

**Estado:** especificación documental; no acredita implementación ni resultados.

**Fuente:** document.md · Articulación de las etapas de desarrollo; desarrollo del capítulo de implementación.

## Implementación e integración

Documentar la construcción en este orden de dependencias:

1. Catálogo y base de datos.
2. Conjuntos de datos, ajuste fino y recuperación.
3. Ingeniería de características y entrenamiento del clasificador.
4. API, homologador, clasificador y constructor de resultados.
5. Pantallas y validaciones.
6. Integración de eventos, persistencia y consulta.
7. Contenedores y automatización de despliegue.

Por componente, registrar código, configuración, versión, evidencia de integración e incidencias. El capítulo queda preparado para completarse con evidencia del repositorio.

## Plataforma web y navegación

Recorrido secuencial:

1. Inicio e instrucciones.
2. Nombre, correo, aviso de uso estadístico y aceptación de términos.
3. Selección de una de las tres áreas IPN.
4. Selección de al menos una habilidad del área.
5. Cuatro situaciones STAR con navegación para corregir respuestas.
6. Resultados, ausencia de coincidencia o aviso de información insuficiente.
7. Reporte mediante diálogo de impresión del navegador.

Implementar con Vue, Nuxt y TypeScript. Los requisitos de cada pantalla se desglosan en [[index-tesis#Requerimientos del sistema|Requerimientos del sistema]].

## Cuestionario STAR

Cuatro situaciones: conflicto interpersonal, colaboración con alguien diferente, desacuerdo con el equipo y problema inesperado. Adaptar las preguntas al área seleccionada.

Cada situación recoge Situación (10 %), Tarea (10 %), Acción (60 %) y Resultado (20 %). Son proporciones sugeridas de desarrollo de la respuesta, no ponderaciones del modelo.

Permitir Siguiente y Volver; en la cuarta situación, Continuar. Evaluar suficiencia por contenido, no solo por longitud. Los textos completos de preguntas y mensajes se conservan en [[tesis/requisitos-funcionales#RF 5 · Cuestionario STAR|RF 5]] y [[tesis/requisitos-no-funcionales#RNF 5.1 · Restricciones de entradas de texto en cuestionario STAR|RNF 5.1]].

## Sistema visual e interfaz

- IBM Plex Sans; cuerpo 18 px, H1 32 px, H2 24 px y secundarios 16 px.
- Interlineado general 1.5 y campos abiertos 1.6; espaciado de títulos 0.01 em y margen inferior 1.25 rem.
- Fondo `#A8C1B6`, texto `#2E2E2E`, interacción `#53C9AF` y errores `#DB3539`.
- Glassmorfismo, pantallas secuenciales, progreso minimalista y animaciones mínimas.
- Resultados con gráficos y explicación textual; tarjetas de carreras y barra de coincidencia.
- Distribución adaptable y errores con texto junto al campo; no comunicar validación exclusivamente mediante color.

## Enlaces

- [[index-tesis|Volver al índice de tesis]]
