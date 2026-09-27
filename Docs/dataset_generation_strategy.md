# Estrategia de Generación de Dataset para Modelo Random Forest

Este documento presenta una propuesta técnica fundamentada en el análisis de la estructura actual de la base de datos y los scripts del proyecto. El objetivo es generar datos adicionales para entrenar un modelo Random Forest capaz de predecir el **porcentaje de coincidencia** (nivel de compatibilidad) de un usuario respecto a distintas carreras.

---

## 1. Análisis de la Arquitectura y Datos Reales

Tras analizar el esquema de base de datos (`generate_tables.sql`) y los scripts de inserción (`data_base_generator.ipynb`, `data_base_happypath.ipynb`), se identifican las siguientes realidades sobre las que debe basarse el modelo:

1. **Construcción Actual de los Happy Paths:**
   - Se selecciona una carrera y se extraen todas sus habilidades asociadas (`carrera_habilidad`).
   - Se crea un usuario sintético (`usuario`).
   - Se le asignan **todas** esas habilidades con un `cumplimiento_criterio = 1.0` en la tabla `usuario_habilidad`.
   - Se registra en `resultado` un `porcentaje_coincidencia = 1.0`.

2. **Realidad Estructural (Esquema BD):**
   - La relación entre Carrera y Habilidad es M:N (`carrera_habilidad`).
   - El cumplimiento del usuario se evalúa por **habilidad** (`cumplimiento_criterio` en `usuario_habilidad`), no por criterio individual.
   - La tabla `criterio` relaciona múltiples subhabilidades o descriptores hacia un único `id_habilidad`. Por tanto, la "repetición" o "peso" de una habilidad está intrínsecamente ligada a la cantidad de registros que tiene en la tabla `criterio`.
   - No existen campos de "peso" o "porcentaje" preasignados en `carrera_habilidad` ni en `criterio`. El único valor flotante es el puntaje que obtiene el usuario (`cumplimiento_criterio`).

3. **Restricción de Área:**
   - El cruce vocacional debe hacerse siempre dentro de la misma Área (`id_area`), lo cual está fuertemente tipificado en las tablas `carrera` y `usuario`.

---

## 2. Estrategia de Generación de Datos (Data Augmentation)

Para evitar la creación de datos irreales o distribuciones arbitrarias, se propone una estrategia de doble vía utilizando **únicamente las relaciones existentes en la base de datos**:

### A. Generación de Casos Parciales y Bajos por Cruce Cruzado (Cross-Matching)
La mejor manera de generar niveles de compatibilidad naturales (bajos y medios) es tomar los "Happy Paths" existentes de un área y enfrentarlos contra **otras carreras de su misma área**.

* **Lógica:** Si el usuario ideal de *Ingeniería en Sistemas* se compara con *Ingeniería Biomédica*, compartirá habilidades de tronco común (matemáticas, análisis), pero fallará en las habilidades de especialidad.
* **Resultado:** Esto genera automáticamente casos con compatibilidades distribuidas naturalmente (ej. casos con 10%, 35%, 60% de coincidencia) basadas estrictamente en la intersección real de habilidades (Data-driven), eliminando la necesidad de inventar porcentajes arbitrarios.

### B. Generación de Casos con Ruido Natural (Perturbación)
Para los casos de alta compatibilidad que no son perfectos (simular humanos reales), se tomarán copias de los Happy Paths y se aplicarán dos perturbaciones estocásticas:
1. **Reducción del Cumplimiento:** Disminuir aleatoriamente el `cumplimiento_criterio` de algunas habilidades (ej. de 1.0 a valores entre 0.4 y 0.9).
2. **Omisión de Habilidades (Dropout):** Eliminar del perfil del usuario 1 o 2 habilidades que la carrera requiere.

---

## 3. Resolución de la Regla de "Repeticiones y Criterios"

El análisis identificó que la "repetición" a la que se hace referencia está en la tabla `criterio` (varios criterios apuntan al mismo `id_habilidad`) y en la tabla `carrera_habilidad` (una habilidad es compartida por varias carreras del área). 

* **Solución de Agrupación:** Para determinar la "relevancia" de una habilidad, en lugar de usar un peso quemado en BD, se calculará dinámicamente un **Score de Complejidad de la Habilidad**. 
* Si un usuario tiene varios registros provenientes de evaluaciones, el agrupamiento en la base de datos debe aplicar `MAX(cumplimiento_criterio)` para evitar que una habilidad evaluada múltiples veces supere el valor lógico de 1.0.

---

## 4. Ingeniería de Variables (Feature Engineering) para el Random Forest

Para que el modelo aprenda patrones más allá de un simple promedio, se deben construir variables estructuradas a partir de la BD:

| Variable | Tipo | Origen de Datos (SQL) | Justificación |
| :--- | :--- | :--- | :--- |
| `habilidades_requeridas` | Numérica | `COUNT(id_habilidad) FROM carrera_habilidad` | Define la longitud del perfil esperado. |
| `habilidades_cumplidas` | Numérica | Intersección `carrera_habilidad` y `usuario_habilidad` | Cuántas habilidades de la carrera posee el usuario. |
| `suma_cumplimiento` | Numérica | `SUM(cumplimiento_criterio)` del usuario | Suma bruta del nivel de desempeño del usuario en las habilidades requeridas. |
| `peso_criterios_habilidad` | Numérica | `COUNT(id_criterio) FROM criterio GROUP BY id_habilidad` | Refleja la "importancia" o complejidad de la habilidad mediante sus repeticiones. |
| `frecuencia_area` | Numérica | `COUNT(id_carrera) FROM carrera_habilidad` | Identifica si la habilidad es de tronco común o de alta especialidad. |
| **`target_coincidencia`** | Continua (0 a 1) | `suma_cumplimiento / habilidades_requeridas` | Etiqueta objetivo (Target) a predecir por el modelo. |

---

## 5. Prevención de Sesgos, Data Leakage y Muestreo

### Prevención de Datos Irreales
* No se crearán usuarios que tengan combinaciones de habilidades que jamás se dan juntas en la realidad. Todos los perfiles base serán los Happy Paths (que representan perfiles reales/lógicos), y de ahí se degradarán.

### Riesgo de Sesgos
* **Sesgo por Volumen de Habilidades:** Áreas como "Ingeniería" (Área 1) tienen 166 habilidades, mientras que "Administrativas" (Área 3) tienen 45. Si se entrena todo junto, el modelo penalizará injustamente al Área 3. 
* **Solución:** Introducir la variable del "Total de habilidades del área" en el entrenamiento, o entrenar modelos / árboles separados por `id_area`.

### Riesgo de Data Leakage
* **Data Leakage:** Generar datos sintéticos a partir de un usuario y que las variaciones de este terminen en el set de Train y en el de Test simultáneamente.
* **Solución:** Realizar el *Train/Test Split* basado en el `id_usuario` original, asegurando que todas las variaciones sintéticas de un mismo "Happy Path" se mantengan exclusivamente en el conjunto de entrenamiento.

### Estrategia de Muestreo
Al hacer el cruce de todos contra todos (Cross-Matching) dentro de un área, la distribución se sesgará hacia compatibilidades bajas (0% - 30%), ya que la mayoría de las carreras no se parecen.
* **Recomendación:** Utilizar un **Muestreo Estratificado (Stratified Sampling)** dividiendo el `target_coincidencia` en deciles (0.0-0.1, 0.1-0.2...). Posteriormente, aplicar **Undersampling** a los deciles más bajos para balancear el dataset antes de alimentar al Random Forest.

---

## 6. Consulta SQL de Base para la Generación de Datos

La siguiente consulta extrae la base real calculada para generar el dataset de entrenamiento, aplicando las reglas descubiertas en el modelo relacional:

```sql
WITH requerimientos AS (
    -- Extrae las habilidades requeridas por carrera y su peso basado en criterios
    SELECT 
        ch.id_carrera, 
        c.id_area,
        ch.id_habilidad,
        COUNT(cr.id_criterio) AS complejidad_habilidad -- Repeticiones de la habilidad
    FROM carrera_habilidad ch
    JOIN carrera c ON ch.id_carrera = c.id_carrera
    LEFT JOIN criterio cr ON ch.id_habilidad = cr.id_habilidad
    GROUP BY ch.id_carrera, c.id_area, ch.id_habilidad
),
usuarios_perfil AS (
    -- Extrae los usuarios (Happy paths) y su cumplimiento (evitando duplicados)
    SELECT 
        uh.id_usuario, 
        u.id_area,
        uh.id_habilidad,
        MAX(uh.cumplimiento_criterio) AS cumplimiento_criterio -- Regla: Conservar el más relevante
    FROM usuario_habilidad uh
    JOIN usuario u ON uh.id_usuario = u.id_usuario
    GROUP BY uh.id_usuario, u.id_area, uh.id_habilidad
)
-- Cruce de usuarios con TODAS las carreras de SU MISMA área
SELECT 
    up.id_usuario,
    req.id_carrera,
    req.id_area,
    -- Variables para el modelo
    COUNT(req.id_habilidad) AS total_habilidades_requeridas,
    COUNT(up_match.id_habilidad) AS habilidades_cumplidas,
    COALESCE(SUM(up_match.cumplimiento_criterio), 0) AS suma_cumplimiento,
    -- Calculo dinámico del Target (Porcentaje de coincidencia)
    COALESCE(SUM(up_match.cumplimiento_criterio), 0) / NULLIF(COUNT(req.id_habilidad), 0) AS target_coincidencia
FROM requerimientos req
JOIN usuarios_perfil up 
    ON req.id_area = up.id_area -- REGLA: Restricción estricta por área
LEFT JOIN usuarios_perfil up_match 
    ON up_match.id_usuario = up.id_usuario 
    AND up_match.id_habilidad = req.id_habilidad
GROUP BY 
    up.id_usuario, 
    req.id_carrera, 
    req.id_area;
```

---

## 7. Blueprint del Notebook `data_base_nonideal.ipynb`

Este documento describe **cómo construir** el script Jupyter para inyectar los casos no ideales en la base de datos. El archivo debe crearse en `Scripts/data_base_nonideal.ipynb` y reutiliza las funciones del happy path como base.

> **Regla general:** Nunca se inventa un porcentaje. El `porcentaje_coincidencia` que se persiste en la tabla `resultado` **siempre se calcula** como `suma_cumplimiento / total_habilidades_requeridas` a partir de las habilidades reales asignadas al usuario.

---

### Distribución por Área

La imagen de referencia muestra la distribución de habilidades únicas por área:

| id_area | nombre_area | total_habilidades_unicas |
| :---: | :--- | :---: |
| 1 | Ingeniería y Ciencias Físico Matemáticas | 166 |
| 2 | Ciencias Médico Biológicas | 51 |
| 3 | Ciencias Sociales y Administrativas | 45 |

Esto impacta directamente en el volumen de casos cruzados que se generarán por área y en la variedad de valores de `target_coincidencia` posibles. El Área 1 produce la mayor variedad de combinaciones; el Área 3, la menor.

---

### Estructura de Celdas del Notebook

#### **Celda 1 — Imports y Configuración de Conexión**

Reutilizar exactamente la misma configuración de `data_base_happypath.ipynb`:

```python
import polars as pl
import sqlalchemy as sa
from pydantic import BaseModel
from IPython.display import display
import uuid, random
from typing import Optional

DB_HOST = '100.95.220.1'
DB_PORT = 5432
DB_USER = 'admin'
DB_PASSWORD = "password"
DB_CONECTION = "athena"

connection_url = (
    f'postgresql://{DB_USER}:{DB_PASSWORD}'
    f'@{DB_HOST}:{DB_PORT}/{DB_CONECTION}'
)
engine = sa.create_engine(connection_url)
```

---

#### **Celda 2 — Modelos Pydantic (reutilizados del happy path)**

Copiar exactamente los modelos `Area`, `Carrera`, `Habilidad`, `Usuario`, `Resultado` del happy path. No modificar.

---

#### **Celda 3 — Helpers de Consulta a BD**

Copiar las funciones `get_all_areas()`, `get_careers_by_area_select()`, `get_habilities_by_career()`, `generate_name_and_email()`, `submit_user()`, `submit_user_habilities()` y `construct_result()` del happy path.

Agregar adicionalmente la siguiente función para obtener todos los usuarios happy-path agrupados por área:

```python
def get_happy_path_users_by_area(id_area: int) -> list[dict]:
    """
    Retorna los usuarios ya insertados (happy paths) de un área,
    junto con sus habilidades y cumplimiento.
    """
    query = """
        SELECT
            u.id_usuario,
            u.uuid_usuario,
            u.nombre,
            u.correo,
            u.id_area,
            uh.id_habilidad,
            MAX(uh.cumplimiento_criterio) AS cumplimiento_criterio
        FROM usuario u
        JOIN usuario_habilidad uh ON uh.id_usuario = u.id_usuario
        WHERE u.id_area = :id_area
        GROUP BY u.id_usuario, u.uuid_usuario, u.nombre, u.correo, u.id_area, uh.id_habilidad
        ORDER BY u.id_usuario, uh.id_habilidad;
    """
    with engine.begin() as conn:
        rows = conn.execute(sa.text(query), {"id_area": id_area}).mappings().all()
    # Agrupar por usuario -> {id_usuario: {meta, habilidades: {id_habilidad: cumplimiento}}}
    usuarios = {}
    for row in rows:
        uid = row["id_usuario"]
        if uid not in usuarios:
            usuarios[uid] = {
                "id_usuario": uid,
                "uuid_usuario": row["uuid_usuario"],
                "nombre": row["nombre"],
                "correo": row["correo"],
                "id_area": row["id_area"],
                "habilidades": {}
            }
        usuarios[uid]["habilidades"][row["id_habilidad"]] = float(row["cumplimiento_criterio"])
    return list(usuarios.values())
```

---

#### **Celda 4 — Estrategia A: Cross-Matching (casos bajos y medios naturales)**

**Lógica:**
- Tomar cada usuario happy-path de un área.
- Cruzarlo con **todas las otras carreras** de su misma área (no con su carrera original).
- Calcular `porcentaje_coincidencia` = intersección real de habilidades / habilidades requeridas por esa carrera.
- Insertar un nuevo usuario sintético con exactamente las habilidades que posee (que pueden coincidir parcialmente con la nueva carrera) y registrar el resultado calculado.

```python
def run_cross_matching() -> list[dict]:
    """
    Genera casos no ideales cruzando usuarios happy-path contra
    otras carreras de su misma área.
    Retorna lista de dicts con el resumen de cada caso insertado.
    """
    resumen = []
    areas = get_all_areas()

    for area in areas:
        id_area = area["id_area"]
        carreras = get_careers_by_area_select(id_area)
        usuarios_hp = get_happy_path_users_by_area(id_area)

        for usuario_hp in usuarios_hp:
            habilidades_usuario = usuario_hp["habilidades"]  # {id_habilidad: cumplimiento}

            for carrera in carreras:
                habilidades_carrera = get_habilities_by_career(carrera.id_carrera)
                ids_carrera = {h.id_habilidad for h in habilidades_carrera}
                total_requeridas = len(ids_carrera)

                # Intersección: habilidades que el usuario tiene Y la carrera requiere
                ids_comunes = ids_carrera.intersection(set(habilidades_usuario.keys()))
                suma_cumplimiento = sum(habilidades_usuario[h_id] for h_id in ids_comunes)
                porcentaje = round(suma_cumplimiento / total_requeridas, 4) if total_requeridas > 0 else 0.0

                # Omitir el caso perfecto (ya existe en happy path)
                if porcentaje >= 1.0:
                    continue

                # Crear nuevo usuario sintético con el mismo perfil de habilidades
                nombre, correo = generate_name_and_email()
                nuevo_usuario = Usuario(
                    uuid_usuario=f"CROSS-{uuid.uuid4()}",
                    nombre=nombre,
                    correo=correo,
                    id_area=id_area
                )
                user_db = submit_user(nuevo_usuario)

                # Insertar con cumplimiento variable (NO la función del happy path que fija 1.0)
                habilidades_a_insertar = [
                    {"id_usuario": user_db.id_usuario,
                     "id_habilidad": h_id,
                     "cumplimiento_criterio": cumpl}
                    for h_id, cumpl in habilidades_usuario.items()
                ]
                with engine.begin() as conn:
                    conn.execute(sa.text("""
                        INSERT INTO usuario_habilidad (id_usuario, id_habilidad, cumplimiento_criterio)
                        VALUES (:id_usuario, :id_habilidad, :cumplimiento_criterio)
                    """), habilidades_a_insertar)

                construct_result(user_db.uuid_usuario, carrera.id_carrera, porcentaje)

                resumen.append({
                    "id_usuario": user_db.id_usuario,
                    "id_area": id_area,
                    "id_carrera": carrera.id_carrera,
                    "total_requeridas": total_requeridas,
                    "habilidades_comunes": len(ids_comunes),
                    "suma_cumplimiento": suma_cumplimiento,
                    "porcentaje_coincidencia": porcentaje
                })

    return resumen

# Ejecutar y mostrar resumen
resumen_cross = run_cross_matching()
df_cross = pl.DataFrame(resumen_cross)
print(f"Casos cross-matching generados: {len(resumen_cross)}")
display(df_cross.describe())
display(df_cross.sort("porcentaje_coincidencia"))
```

**Valores esperados de `porcentaje_coincidencia`:** Distribuidos naturalmente entre ~0.0 y ~0.85. El Área 1 (166 habilidades) producirá la mayor variedad de rangos intermedios.

---

#### **Celda 5 — Estrategia B: Perturbación con Ruido (casos altos imperfectos)**

**Lógica:**
- Tomar cada usuario happy-path.
- Crear `N_VARIACIONES` copias del mismo.
- En cada copia, aplicar dos perturbaciones estocásticas:
  1. **Reducción de cumplimiento:** A un porcentaje aleatorio de habilidades (`PCTG_REDUCCION`), bajar su `cumplimiento_criterio` a un valor entre `MIN_CUMPL` y `MAX_CUMPL`.
  2. **Dropout:** Eliminar aleatoriamente entre `MIN_DROPOUT` y `MAX_DROPOUT` habilidades del perfil.
- Calcular el porcentaje resultante y persistir.

```python
# ── Parámetros ajustables ──────────────────────────────────────────────
N_VARIACIONES   = 3      # Copias perturbadas por cada happy path
PCTG_REDUCCION  = 0.40   # Fracción de habilidades a las que se reduce el cumplimiento
MIN_CUMPL       = 0.40   # Valor mínimo de cumplimiento al perturbar
MAX_CUMPL       = 0.90   # Valor máximo de cumplimiento al perturbar
MIN_DROPOUT     = 1      # Habilidades mínimas a eliminar del perfil
MAX_DROPOUT     = 3      # Habilidades máximas a eliminar del perfil
# ──────────────────────────────────────────────────────────────────────

def run_perturbation() -> list[dict]:
    """
    Genera variaciones ruidosas de los happy paths para simular
    usuarios reales con alta (pero imperfecta) compatibilidad.
    """
    resumen = []
    areas = get_all_areas()

    for area in areas:
        id_area = area["id_area"]
        usuarios_hp = get_happy_path_users_by_area(id_area)

        for usuario_hp in usuarios_hp:
            habilidades_originales = dict(usuario_hp["habilidades"])

            # Obtener la carrera del happy path original desde resultado
            with engine.begin() as conn:
                row = conn.execute(sa.text("""
                    SELECT id_carrera FROM resultado
                    WHERE uuid_usuario = :uuid
                    LIMIT 1;
                """), {"uuid": usuario_hp["uuid_usuario"]}).mappings().fetchone()
            if row is None:
                continue
            id_carrera_original = row["id_carrera"]
            habilidades_carrera = get_habilities_by_career(id_carrera_original)
            total_requeridas = len(habilidades_carrera)

            for variacion in range(N_VARIACIONES):
                habs_variadas = dict(habilidades_originales)

                # Perturbación 1: Reducir cumplimiento
                ids_a_reducir = random.sample(
                    list(habs_variadas.keys()),
                    k=max(1, int(len(habs_variadas) * PCTG_REDUCCION))
                )
                for h_id in ids_a_reducir:
                    habs_variadas[h_id] = round(random.uniform(MIN_CUMPL, MAX_CUMPL), 2)

                # Perturbación 2: Dropout
                n_dropout = random.randint(MIN_DROPOUT, min(MAX_DROPOUT, len(habs_variadas) - 1))
                for h_id in random.sample(list(habs_variadas.keys()), k=n_dropout):
                    del habs_variadas[h_id]

                # Calcular porcentaje real resultante
                ids_carrera_set = {h.id_habilidad for h in habilidades_carrera}
                ids_comunes = ids_carrera_set.intersection(set(habs_variadas.keys()))
                suma_cumplimiento = sum(habs_variadas[h_id] for h_id in ids_comunes)
                porcentaje = round(suma_cumplimiento / total_requeridas, 4) if total_requeridas > 0 else 0.0

                # Crear usuario sintético
                nombre, correo = generate_name_and_email()
                nuevo_usuario = Usuario(
                    uuid_usuario=f"PERT-{uuid.uuid4()}",
                    nombre=nombre,
                    correo=correo,
                    id_area=id_area
                )
                user_db = submit_user(nuevo_usuario)

                habilidades_a_insertar = [
                    {"id_usuario": user_db.id_usuario,
                     "id_habilidad": h_id,
                     "cumplimiento_criterio": cumpl}
                    for h_id, cumpl in habs_variadas.items()
                ]
                with engine.begin() as conn:
                    conn.execute(sa.text("""
                        INSERT INTO usuario_habilidad (id_usuario, id_habilidad, cumplimiento_criterio)
                        VALUES (:id_usuario, :id_habilidad, :cumplimiento_criterio)
                    """), habilidades_a_insertar)

                construct_result(user_db.uuid_usuario, id_carrera_original, porcentaje)

                resumen.append({
                    "id_usuario": user_db.id_usuario,
                    "variacion": variacion + 1,
                    "id_area": id_area,
                    "id_carrera": id_carrera_original,
                    "total_requeridas": total_requeridas,
                    "habilidades_tras_dropout": len(habs_variadas),
                    "suma_cumplimiento": suma_cumplimiento,
                    "porcentaje_coincidencia": porcentaje
                })

    return resumen

resumen_pert = run_perturbation()
df_pert = pl.DataFrame(resumen_pert)
print(f"Casos perturbados generados: {len(resumen_pert)}")
display(df_pert.describe())
display(df_pert.sort("porcentaje_coincidencia"))
```

**Valores esperados de `porcentaje_coincidencia`:** Concentrados entre ~0.50 y ~0.95. Llenan el rango alto del dataset que el cross-matching no cubre bien.

---

#### **Celda 6 — Estrategia C: Cross-Matching con Perturbación Combinada (rango medio-alto)**

**Lógica:**  
Combina ambas estrategias. Toma un usuario happy-path, le aplica ruido (reducción + dropout), y **luego** lo cruza contra otras carreras de su área. Esto densifica el rango medio (0.30–0.70).

```python
# ── Parámetros ajustables ──────────────────────────────────────────────
N_VARIACIONES_COMBO   = 2     # Variaciones ruidosas por usuario antes del cruce
PCTG_REDUCCION_COMBO  = 0.30
MIN_CUMPL_COMBO       = 0.50
MAX_CUMPL_COMBO       = 0.85
MIN_DROPOUT_COMBO     = 1
MAX_DROPOUT_COMBO     = 2
# ──────────────────────────────────────────────────────────────────────

def run_combined_cross_perturbation() -> list[dict]:
    """
    Genera variantes ruidosas de happy paths y luego las cruza
    contra otras carreras del área para poblar el rango medio.
    """
    resumen = []
    areas = get_all_areas()

    for area in areas:
        id_area = area["id_area"]
        carreras = get_careers_by_area_select(id_area)
        usuarios_hp = get_happy_path_users_by_area(id_area)

        for usuario_hp in usuarios_hp:
            habilidades_originales = dict(usuario_hp["habilidades"])

            for _ in range(N_VARIACIONES_COMBO):
                # Aplicar ruido al perfil base
                habs_variadas = dict(habilidades_originales)
                ids_a_reducir = random.sample(
                    list(habs_variadas.keys()),
                    k=max(1, int(len(habs_variadas) * PCTG_REDUCCION_COMBO))
                )
                for h_id in ids_a_reducir:
                    habs_variadas[h_id] = round(random.uniform(MIN_CUMPL_COMBO, MAX_CUMPL_COMBO), 2)

                n_dropout = random.randint(MIN_DROPOUT_COMBO, min(MAX_DROPOUT_COMBO, len(habs_variadas) - 1))
                for h_id in random.sample(list(habs_variadas.keys()), k=n_dropout):
                    del habs_variadas[h_id]

                # Cruzar el perfil ruidoso contra TODAS las carreras del área
                for carrera in carreras:
                    habilidades_carrera = get_habilities_by_career(carrera.id_carrera)
                    ids_carrera_set = {h.id_habilidad for h in habilidades_carrera}
                    total_requeridas = len(ids_carrera_set)

                    ids_comunes = ids_carrera_set.intersection(set(habs_variadas.keys()))
                    suma_cumplimiento = sum(habs_variadas[h_id] for h_id in ids_comunes)
                    porcentaje = round(suma_cumplimiento / total_requeridas, 4) if total_requeridas > 0 else 0.0

                    if porcentaje >= 1.0:
                        continue

                    nombre, correo = generate_name_and_email()
                    nuevo_usuario = Usuario(
                        uuid_usuario=f"COMBO-{uuid.uuid4()}",
                        nombre=nombre,
                        correo=correo,
                        id_area=id_area
                    )
                    user_db = submit_user(nuevo_usuario)

                    habilidades_a_insertar = [
                        {"id_usuario": user_db.id_usuario,
                         "id_habilidad": h_id,
                         "cumplimiento_criterio": cumpl}
                        for h_id, cumpl in habs_variadas.items()
                    ]
                    with engine.begin() as conn:
                        conn.execute(sa.text("""
                            INSERT INTO usuario_habilidad (id_usuario, id_habilidad, cumplimiento_criterio)
                            VALUES (:id_usuario, :id_habilidad, :cumplimiento_criterio)
                        """), habilidades_a_insertar)

                    construct_result(user_db.uuid_usuario, carrera.id_carrera, porcentaje)

                    resumen.append({
                        "id_usuario": user_db.id_usuario,
                        "id_area": id_area,
                        "id_carrera": carrera.id_carrera,
                        "total_requeridas": total_requeridas,
                        "habilidades_perfil_ruidoso": len(habs_variadas),
                        "habilidades_comunes": len(ids_comunes),
                        "porcentaje_coincidencia": porcentaje
                    })

    return resumen

resumen_combo = run_combined_cross_perturbation()
df_combo = pl.DataFrame(resumen_combo)
print(f"Casos combinados generados: {len(resumen_combo)}")
display(df_combo.describe())
```

---

#### **Celda 7 — Validación de Distribución Global**

Después de ejecutar las tres estrategias, verificar que la distribución del dataset cubre todo el rango de 0 a 1:

```python
query_validacion = """
    SELECT
        FLOOR(porcentaje_coincidencia * 10) / 10.0 AS decil,
        COUNT(*) AS cantidad
    FROM resultado
    GROUP BY decil
    ORDER BY decil;
"""
with engine.begin() as conn:
    df_dist = pl.read_database(query_validacion, connection=conn)

display(df_dist)

total = df_dist["cantidad"].sum()
df_dist = df_dist.with_columns(
    (pl.col("cantidad") / total * 100).alias("pct")
)
deciles_pobres = df_dist.filter(pl.col("pct") < 5.0)
if deciles_pobres.height > 0:
    print("⚠️  Deciles con baja representación (<5%):")
    display(deciles_pobres)
else:
    print("✅  Distribución balanceada en todos los deciles.")
```

---

### Criterios Adicionales para el Random Forest (Features Sugeridas)

Además de las variables de la Sección 4, se sugieren las siguientes features derivadas de los nuevos casos no ideales para enriquecer los árboles de decisión:

| Variable adicional | Tipo | Cálculo | Justificación |
| :--- | :--- | :--- | :--- |
| `ratio_cumplidas_requeridas` | Continua | `habilidades_cumplidas / habilidades_requeridas` | Fracción de cobertura; correlaciona con target pero captura la cobertura pura. |
| `promedio_cumplimiento_comunes` | Continua | `suma_cumplimiento / habilidades_cumplidas` | Calidad promedio de las habilidades que SÍ coinciden (≠ al target). |
| `habilidades_excedentes` | Numérica | `total_habilidades_usuario - habilidades_cumplidas` | Habilidades del usuario que la carrera no requiere (perfil desalineado). |
| `complejidad_ponderada` | Continua | `SUM(cumplimiento * peso_criterios) / SUM(peso_criterios)` | Pondera el cumplimiento por la complejidad real de cada habilidad. |
| `carreras_en_area` | Numérica | `COUNT(id_carrera) WHERE id_area = X` | Contexto competitivo: más carreras en el área → más difícil distinguir. |
| `habilidades_tronco_comun` | Numérica | Habilidades compartidas por ≥50% de carreras del área | Indica si el perfil tiene base generalista o es de alta especialización. |

---

### Orden de Ejecución del Notebook

```
Celda 1  →  Imports + conexión
Celda 2  →  Modelos Pydantic
Celda 3  →  Helpers de BD (incluyendo get_happy_path_users_by_area)
Celda 4  →  Estrategia A: Cross-Matching              (cubre rango 0.0 – 0.70)
Celda 5  →  Estrategia B: Perturbación                (cubre rango 0.50 – 0.95)
Celda 6  →  Estrategia C: Cross + Perturbación combo  (densifica rango 0.30 – 0.70)
Celda 7  →  Validación de distribución global por deciles
```

> **Nota sobre prefijos de `uuid_usuario`:** Los prefijos `CROSS-`, `PERT-`, `COMBO-` permiten identificar el origen de cada registro sintético en análisis posteriores sin agregar columnas extra a la BD.
