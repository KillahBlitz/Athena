# Requisitos de Implementación

**Estado:** especificación documental; no acredita implementación ni resultados.

**Fuente:** document.md · especificación de requerimientos. Véase [[tesis/referencias#Fuentes, cobertura y decisiones pendientes|Fuentes y pendientes]].

Se conservan los identificadores y el contenido de los requisitos originales.

## RIM A · Arquitectura de Software

La implementación de todos los módulos debe seguir una arquitectura basada en microservicios con un patrón de diseño event-driven.

**Relacionado:** [[tesis/diseno-modular|Diseño modular]]

## RIM B · Acceso a código

El código debe subirse a GitHub con una estructura Mono-repo separando el Frontend, Base de Datos y Backend.

**Relacionado:** [[tesis/arquitectura-y-justificacion-tecnologica#CI/CD, contenedores y despliegue|CI/CD, contenedores y despliegue]]

## RIM C · Tecnologías de Frontend

La plataforma web debe estar construida con vue.js usando nuxt para la comunicación con el Backend, usando módulos de TypeScript.

**Relacionado:** [[tesis/implementacion#Plataforma web y navegación|Plataforma web y navegación]]

## RIM D · Tecnologías de Base de datos

La base de datos debe estar construida con el Gestor de Base de Datos PostgreSQL y PGvector respetando el diseño de arquitectura Entidad Relación.

**Relacionado:** [[tesis/base-de-datos|Base de datos y modelo entidad-relación]]

## RIM E · Tecnología de Orquestación

La orquestación de eventos debe estar construida con REDIS.

**Relacionado:** [[tesis/diseno-detallado|Diseño detallado y contratos]]

## RIM F · Tecnología de Backend y API/REST

El API debe estar construida con FastAPI y Python, mientras que los microservicios deben respetar modelos con pydantic y construcción con Python.

**Relacionado:** [[tesis/diseno-detallado|Diseño detallado y contratos]]

## RIM G · Integración CI/CD

La construcción de CI/CD debe estar construido mediante GitHub Actions.

**Relacionado:** [[tesis/arquitectura-y-justificacion-tecnologica#CI/CD, contenedores y despliegue|CI/CD, contenedores y despliegue]]

## RIM H · Tecnologías de Nube

El despliegue del servicio debe ser mediante la plataforma de Google Cloud.

**Relacionado:** [[tesis/arquitectura-y-justificacion-tecnologica#CI/CD, contenedores y despliegue|CI/CD, contenedores y despliegue]]

## Enlaces

- [[tesis/requisitos-funcionales|Requisitos Funcionales]]
- [[tesis/requisitos-no-funcionales|Requisitos No Funcionales]]
- [[tesis/requisitos-interfaz|Requisitos de Interfaz]]
- [[index-tesis|Volver al índice de tesis]]
