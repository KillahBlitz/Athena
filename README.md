# Athena

Sistema inteligente de recomendación académica basado en perfiles de habilidades y análisis de afinidad con carreras profesionales. Athena utiliza técnicas de procesamiento de lenguaje natural (NLP), clasificación supervisada y generación sintética de datos para evaluar la compatibilidad entre estudiantes y programas educativos.

---

## 📋 Tabla de Contenidos

- [Visión General](#visión-general)
- [Estructura del Repositorio](#estructura-del-repositorio)
- [Tecnologías](#tecnologías)
- [Instalación y Despliegue](#instalación-y-despliegue)
- [Documentación](#documentación)
- [CI/CD](#cicd)
- [Contribución](#contribución)

---

## 🎯 Visión General

Athena es un proyecto académico desarrollado como tesis de grado que implementa un sistema de recomendación para orientación vocacional. El sistema evalúa perfiles de estudiantes basándose en sus habilidades y los compara con los requisitos de diferentes carreras profesionales, proporcionando métricas de compatibilidad y recomendaciones personalizadas.

### Características Principales

- **Análisis de Habilidades:** Procesamiento y evaluación de competencias académicas
- **Clasificación Supervisada:** Modelos de ML para predicción de afinidad
- **Generación Sintética:** Creación de datasets mediante estrategia PERT-BAL
- **Prevención de Data Leakage:** Trazabilidad completa mediante `uuid_origen`
- **API REST:** Backend escalable con FastAPI
- **Interfaz Web:** Frontend responsive con Nuxt 3
- **Despliegue Cloud-Native:** Kubernetes en GKE y K3s local

---

## 📁 Estructura del Repositorio

```
Athena/
├── Backend/           # Servicios backend y API REST
├── Frontend/          # Interfaz de usuario web
├── DataBase/          # Esquemas y scripts SQL
├── Docs/              # Documentación académica y técnica
├── Scripts/           # Automatización y utilidades
├── library/           # Biblioteca compartida (kinasis_library)
├── .github/           # Workflows de CI/CD
└── catalogo_habilidades_ipn.xlsx  # Catálogo de competencias
```

### 🔧 Backend

Contiene la lógica de negocio, endpoints REST y tareas asíncronas del sistema.

**Contenido:**
- `src/main/` - Endpoints principales de la API
- `src/tasks/` - Event handlers para procesamiento asíncrono:
  - `classifier_event_handler.py` - Clasificación de perfiles
  - `extractor_event_handler.py` - Extracción de características
  - `generator_event_handler.py` - Generación de datos sintéticos
- `src/handlers/` - Lógica de negocio
- `src/models/` - Modelos de datos
- `src/tests/` - Tests unitarios
- `kubernetes/` - Manifiestos de deployment para devel y prod
- `assets/requirements.txt` - Dependencias Python (pydantic, redis, pytest)

**Tecnologías:**
- Python 3.14
- FastAPI
- Redis (caché y cola de eventos)
- PostgreSQL (persistencia)

### 🎨 Frontend

Interfaz web moderna y responsive construida con Nuxt 3.

**Contenido:**
- `app/` - Componentes, páginas y layouts
- `public/` - Recursos estáticos
- `config/` - Configuración de la aplicación
- `kubernetes/` - Manifiestos de deployment
- `nuxt.config.ts` - Configuración de Nuxt

**Tecnologías:**
- Nuxt 3 (Vue.js)
- TypeScript
- Docker

### 🗄️ DataBase

Scripts de creación y configuración de la base de datos relacional.

**Contenido:**
- `scripts/db_creator.sql` - Creación de base de datos
- `scripts/generate_tables.sql` - Definición de esquemas, incluyendo:
  - Tabla `usuario` - Perfiles de estudiantes
  - Tabla `usuario_origen` - Trazabilidad de datos sintéticos (prevención de data leakage)
  - Tabla `carrera` - Catálogo de programas educativos
  - Tabla `habilidad` - Competencias y habilidades
  - Relaciones entre usuarios, carreras y habilidades
- `deployment/` - Configuración Docker Compose y nginx

**Características:**
- PostgreSQL con modelado normalizado
- Índices de Jaccard para similitud entre carreras
- Sistema de procedencia para datos generados (uuid_origen)

### 📚 Docs

Documentación académica y técnica organizada como base de conocimiento en Obsidian.

**Contenido:**
- `main.md` - Nodo principal de documentación
- **`index-project.md`** - Implementación técnica del proyecto
- **`index-tesis.md`** - Sustento académico y metodológico
- **`index-prouporse.md`** - Propuestas de integración y análisis
- `tesis/` - Documentos formales:
  - Arquitectura y justificación tecnológica
  - Estado del arte
  - Diseño conceptual y detallado
  - Implementación
  - Conclusiones y trabajo futuro
- `analisis/` - Investigación técnica:
  - Estrategias de generación de datasets
  - Configuración de clusters (GKE, K3s)
  - Investigación NLP para estandarización
- `resume.md` - Propuesta de mejora integral de generación PERT
- `dataset_balancing_strategy.md` - Estrategia de balanceo de datasets

**Organización:**
Base de conocimiento interconectada diseñada para navegación en Obsidian, con enlaces bidireccionales entre conceptos técnicos y académicos.

### 🛠️ Scripts

Automatizaciones y utilidades para gestión de datos y despliegue.

**Contenido:**
- `python/` - Scripts de Python:
  - `subir_catalogo_normalizado.py` - Carga de catálogo de habilidades
  - `generar_excel_por_areas.py` - Exportación de datos por área
  - `recuperation_data.py` - Recuperación de datos
  - `save_relations.py` - Persistencia de relaciones
  - `CONTEXT.md` - Contexto de los scripts
  - `assets/`, `layouts/`, `media/` - Recursos auxiliares
- `gcloud/` - Scripts para Google Cloud Platform

**Uso:**
Herramientas para carga inicial de datos, migraciones y operaciones de mantenimiento.

### 📦 library

Biblioteca compartida `kinasis_library` que encapsula servicios y utilidades comunes.

**Contenido:**
- `kinasis_library/` - Código base reutilizable:
  - Servicios de conexión (Redis, PostgreSQL, Google Cloud)
  - Manejo de eventos
  - Utilidades compartidas
- `setup.py` - Configuración de empaquetado

**Distribución:**
Publicada en PyPI mediante workflow de CI/CD cuando se detectan cambios en `setup.py`.

### ⚙️ .github

Configuración de CI/CD con GitHub Actions.

**Workflows:**

**`DeployToDevel.yml`** - Pipeline de desarrollo:
1. **ValidateConection** - Valida conectividad con K3s local y GCP
2. **publish-library** - Publica `kinasis_library` en PyPI si hay cambios

**`DeployToProd.yml`** - Pipeline de producción (rama main)

**Características:**
- Self-hosted runner en K3s local para desarrollo
- Autenticación automática con GCP Artifact Registry
- Despliegue automático en namespace `dev-athena`
- Validación de permisos y estado del cluster

### 📊 Archivos Raíz

- **`catalogo_habilidades_ipn.xlsx`** - Catálogo oficial de habilidades del IPN
- **`estrategia.md`** - Documento de estrategia del proyecto
- **`.gitignore`** - Exclusiones de Git

---

## 🚀 Tecnologías

### Backend
- **Python 3.14** - Lenguaje principal
- **FastAPI** - Framework web asíncrono
- **Pydantic** - Validación de datos
- **Redis** - Caché y cola de eventos
- **PostgreSQL** - Base de datos relacional

### Frontend
- **Nuxt 3** - Framework Vue.js
- **TypeScript** - Tipado estático
- **Vue.js** - Framework reactivo

### Infraestructura
- **Docker** - Contenedorización
- **Kubernetes** - Orquestación (GKE + K3s)
- **GitHub Actions** - CI/CD
- **Google Cloud Platform** - Artifact Registry, servicios cloud

### Machine Learning
- **Scikit-learn** - Modelos de clasificación
- **Pandas** - Procesamiento de datos
- **NumPy** - Computación numérica

---

## 🔧 Instalación y Despliegue

### Prerrequisitos

- Python 3.14+
- Node.js 18+
- Docker y Docker Compose
- kubectl (para despliegue en Kubernetes)
- Acceso a PostgreSQL y Redis

### Desarrollo Local

#### Backend

```bash
cd Backend
python -m venv .venv
source .venv/bin/activate  # En Windows: .venv\Scripts\activate
pip install -r assets/requirements.txt
# Configurar variables de entorno en .env
# Iniciar servidor de desarrollo
```

#### Frontend

```bash
cd Frontend
npm install
npm run dev
```

#### Base de Datos

```bash
cd DataBase/deployment
docker-compose up -d
# Ejecutar scripts de inicialización
psql -h localhost -U usuario -d athena < ../scripts/db_creator.sql
psql -h localhost -U usuario -d athena < ../scripts/generate_tables.sql
```

### Despliegue en Kubernetes

#### Desarrollo (K3s local)

```bash
# Aplicar manifiestos
kubectl apply -f Backend/kubernetes/devel/athena-classifier/deployment.yaml
kubectl apply -f Backend/kubernetes/devel/athena-extractor/deployment.yaml
kubectl apply -f Frontend/kubernetes/devel/
```

#### Producción (GKE)

El despliegue en producción se realiza automáticamente mediante el workflow `DeployToProd.yml` al hacer merge a la rama `main`.

---

## 📖 Documentación

La documentación completa está organizada en la carpeta `Docs/` como una base de conocimiento en Obsidian.

### Acceso Rápido

- **[main.md](Docs/main.md)** - Centro de control de documentación
- **[index-project.md](Docs/index-project.md)** - Documentación técnica de implementación
- **[index-tesis.md](Docs/index-tesis.md)** - Documentación académica
- **[resume.md](Docs/resume.md)** - Propuesta de mejora integral (PERT, data leakage, cobertura)
- **[dataset_balancing_strategy.md](Docs/dataset_balancing_strategy.md)** - Estrategia de balanceo

### Visualización Recomendada

Para una experiencia óptima, abre la carpeta `Docs/` en [Obsidian](https://obsidian.md/), que permite navegación mediante enlaces bidireccionales y visualización de grafo de conocimiento.

---

## 🔄 CI/CD

### Pipeline de Desarrollo (rama `devel`)

1. **Validación de Conexión**
   - Verifica conectividad con K3s local
   - Valida autenticación en GCP
   - Confirma acceso a Artifact Registry

2. **Publicación de Biblioteca**
   - Detecta cambios en `library/setup.py`
   - Construye paquete Python
   - Publica `kinasis_library` en PyPI

3. **Despliegue Automático**
   - Actualiza deployments en namespace `dev-athena`
   - Verifica estado de pods

### Pipeline de Producción (rama `main`)

Similar al de desarrollo, pero despliega en el cluster de GKE en producción.

---

## 🤝 Contribución

Este es un proyecto académico de tesis. Para consultas o colaboraciones:

1. Revisa la documentación en `Docs/`
2. Consulta los issues abiertos
3. Sigue las convenciones de código del proyecto
4. Asegúrate de que los tests pasen antes de crear un PR

### Estructura de Branches

- `main` - Producción
- `devel` - Desarrollo activo
- `feature/*` - Nuevas características
- `fix/*` - Correcciones de bugs

---

## 📄 Licencia

Este proyecto es parte de un trabajo académico de tesis. Consulta con el autor para términos de uso y distribución.

---

## 👤 Autor

Proyecto desarrollado como tesis de grado en el Instituto Politécnico Nacional (IPN).

---

## 🔗 Enlaces Relacionados

- **Documentación Técnica:** [Docs/index-project.md](Docs/index-project.md)
- **Documentación Académica:** [Docs/index-tesis.md](Docs/index-tesis.md)
- **Propuestas de Mejora:** [Docs/index-prouporse.md](Docs/index-prouporse.md)
- **Biblioteca kinasis_library:** [PyPI](https://pypi.org/) (publicada automáticamente)

---

## 🎓 Contexto Académico

### Problemática

La orientación vocacional tradicional carece de herramientas cuantitativas para evaluar la compatibilidad entre estudiantes y carreras. Athena aborda este problema mediante:

1. **Modelado de Competencias:** Representación estructurada de habilidades
2. **Métricas de Afinidad:** Cálculo objetivo de compatibilidad
3. **Generación Sintética:** Ampliación de datasets mediante PERT-BAL
4. **Prevención de Sesgos:** Sistema de trazabilidad `uuid_origen` para evitar data leakage

### Metodología

- **Clasificación Supervisada:** Modelos entrenados en perfiles reales
- **Similitud de Jaccard:** Medición de cercanía entre carreras
- **Estrategia PERT:** Perturbación de perfiles para generar casos sintéticos
- **Balanceo por Deciles:** Distribución uniforme de targets (0.0 - 1.0)

### Resultados Esperados

- Sistema funcional de recomendación académica
- Dataset balanceado y trazable
- Modelos con capacidad de generalización validada
- Documentación completa para reproducibilidad

---

**Última actualización:** Octubre 2026
