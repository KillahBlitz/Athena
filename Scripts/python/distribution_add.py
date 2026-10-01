"""
distribution_add.py
--------------------
Genera el dataset FINAL de las 3 areas en la base de datos Athena, corrigiendo
los problemas detectados para un RandomForest de CLASIFICACION que devuelve el
TOP-3 de carreras por coincidencia.

Cambios respecto a data_set_area_{1,2,3}.py:
  1. PERFILES CRUZADOS (arregla el leakage): cada usuario ya NO tiene solo las
     habilidades de una carrera. Tiene una carrera PRIMARIA a la que se inclina
     (con buena parte de sus habilidades) MAS habilidades de otras carreras del
     area. Asi el conjunto de habilidades no identifica trivialmente la carrera
     y se parece al uso real (el usuario ingresa habilidades arbitrarias).
  2. COINCIDENCIA CONTRA TODAS LAS CARRERAS: por cada usuario se calcula la
     coincidencia con cada carrera del area y se guarda el ranking TOP-3 en
     'resultado' (top = 1,2,3). El label de clasificacion es la carrera top=1.
  3. VOLUMEN DUPLICADO: 2x los registros previos por area, para robustez del
     entrenamiento.
  4. Se mantiene la GARANTIA: >= 1 usuario con 100% de coincidencia por carrera
     (usuarios "ancla" con el perfil exacto de la carrera, todos los criterios).

Formula de coincidencia (media ponderada por repeticion, penalizando faltantes):
    coincidencia(u, c) = sum_{h in c} peso(u,h) * cc(u,h)
                         -------------------------------------
                         sum_{h in c} max(peso(u,h), 1)
  donde cc(u,h)=criterios_cumplidos/total_criterios (0 si el usuario no la tiene)
  y peso(u,h)=numero de repeticiones en los 5 formularios (0 si no la tiene).
  Las habilidades de la carrera que el usuario NO tiene cuentan como cc=0 con
  peso 1 (penalizan la coincidencia).

Salidas:
  * Base de datos: usuario / usuario_habilidad / resultado (top-3) por area.
  * Graficas: media/final_results/distribucion_final_area_{a}.png
  * Reporte:  media/data/context_dataset.md (criterios de entrenamiento).

Uso:
    python distribution_add.py
"""

import os
import uuid
import random
from collections import defaultdict

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import sqlalchemy as sa

# ---------------------------------------------------------------------------
# Conexion
# ---------------------------------------------------------------------------
DB_HOST = os.getenv("DB_HOST", "100.95.220.1")
DB_PORT = int(os.getenv("DB_PORT", "5432"))
DB_USER = os.getenv("DB_USER", "admin")
DB_PASSWORD = os.getenv("DB_PASSWORD", "password")
DB_CONECTION = os.getenv("DB_CONECTION", "athena")

engine = sa.create_engine(
    f"postgresql+psycopg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_CONECTION}"
)

# ---------------------------------------------------------------------------
# Configuracion
# ---------------------------------------------------------------------------
# nombre y N objetivo (2x el volumen previo: 3225, 900, 901)
AREAS = {
    1: ("Ingenieria y Ciencias Fisico Matematicas", 6450),
    2: ("Ciencias Medico Biologicas", 1800),
    3: ("Ciencias Sociales y Administrativas", 1802),
}
ALPHA, BETA = 2.5, 2.0     # distribucion objetivo de desempeno del usuario
MAX_REPETICIONES = 5       # 5 formularios
STORE_TOP = 3              # cuantas carreras (ranking) se guardan por usuario
KEEP_PRIMARY = 0.85        # prob. de conservar cada habilidad de la carrera primaria
EXTRA_MIN, EXTRA_MAX = 2, 6  # habilidades "cruzadas" de otras carreras
SEED = 42

BASE = os.path.dirname(os.path.abspath(__file__))
FINAL_DIR = os.path.join(BASE, "media", "final_results")
DATA_DIR = os.path.join(BASE, "media", "data")
os.makedirs(FINAL_DIR, exist_ok=True)
os.makedirs(DATA_DIR, exist_ok=True)

rng = np.random.default_rng(SEED)
random.seed(SEED)

NOMBRES = ["Ana", "Carlos", "Maria", "Juan", "Sofia", "Luis", "Elena", "Diego",
           "Valentina", "Andres", "Camila", "Jorge", "Laura", "Mateo", "Isabella"]
APELLIDOS = ["Gomez", "Perez", "Lopez", "Rodriguez", "Martinez", "Hernandez",
             "Garcia", "Sanchez", "Ramirez", "Torres", "Flores", "Vargas"]


# ---------------------------------------------------------------------------
# Estructura del area
# ---------------------------------------------------------------------------
def cargar_estructura(area_id):
    with engine.begin() as conn:
        carreras = [r["id_carrera"] for r in conn.execute(sa.text(
            "SELECT id_carrera FROM carrera WHERE id_area=:a ORDER BY id_carrera"
        ), {"a": area_id}).mappings()]

        habs_por_carrera = {}
        for c in carreras:
            habs_por_carrera[c] = [r["id_habilidad"] for r in conn.execute(sa.text(
                "SELECT id_habilidad FROM carrera_habilidad WHERE id_carrera=:c ORDER BY id_habilidad"
            ), {"c": c}).mappings()]

        todas = sorted({h for hs in habs_por_carrera.values() for h in hs})
        criterios = {}
        for r in conn.execute(sa.text("""
            SELECT h.id_habilidad, COUNT(cr.id_criterio) n
            FROM habilidad h LEFT JOIN criterio cr ON cr.id_habilidad=h.id_habilidad
            WHERE h.id_habilidad = ANY(:ids) GROUP BY h.id_habilidad
        """), {"ids": todas}).mappings():
            criterios[r["id_habilidad"]] = max(int(r["n"]), 1)

    return carreras, habs_por_carrera, criterios, todas


def limpiar_area(area_id):
    with engine.begin() as conn:
        conn.execute(sa.text("""DELETE FROM resultado WHERE uuid_usuario IN
            (SELECT uuid_usuario FROM usuario WHERE id_area=:a)"""), {"a": area_id})
        conn.execute(sa.text("""DELETE FROM usuario_habilidad WHERE id_usuario IN
            (SELECT id_usuario FROM usuario WHERE id_area=:a)"""), {"a": area_id})
        conn.execute(sa.text("DELETE FROM usuario WHERE id_area=:a"), {"a": area_id})


# ---------------------------------------------------------------------------
# Generacion del perfil de habilidades de un usuario
# ---------------------------------------------------------------------------
def cc_por_criterios(total_criterios, p):
    """cumplimiento_criterio = criterios_cumplidos/total, con cumplidos~Binomial."""
    cumplidos = int(rng.binomial(total_criterios, p))
    return cumplidos / total_criterios


def perfil_usuario(carreras, habs_por_carrera, criterios, todas_habs, ancla=False):
    """
    Devuelve skills = {id_habilidad: (cc, peso)} donde cc es el valor consolidado
    (mas alto) y peso el numero de repeticiones.

    - ancla=True: perfil EXACTO de una carrera con cc=1.0 en todas -> 100% en esa
      carrera (garantiza un usuario perfecto por carrera).
    - ancla=False: perfil CRUZADO: mayoria de habilidades de una carrera primaria
      + habilidades de otras carreras del area (desempeno parcial).
    """
    primaria = random.choice(carreras)
    skills = {}

    if ancla:
        for h in habs_por_carrera[primaria]:
            skills[h] = (1.0, random.randint(1, MAX_REPETICIONES))
        return primaria, skills

    p = float(rng.beta(ALPHA, BETA))  # desempeno objetivo del usuario

    # habilidades de la carrera primaria (se conservan casi todas)
    for h in habs_por_carrera[primaria]:
        if random.random() <= KEEP_PRIMARY:
            cc = cc_por_criterios(criterios[h], p)
            skills[h] = (round(cc, 4), random.randint(1, MAX_REPETICIONES))

    # habilidades cruzadas de otras carreras (desempeno mas bajo)
    otras = [h for h in todas_habs if h not in habs_por_carrera[primaria]]
    n_extra = random.randint(EXTRA_MIN, EXTRA_MAX)
    for h in random.sample(otras, min(n_extra, len(otras))):
        p_cross = p * random.uniform(0.3, 0.8)
        cc = cc_por_criterios(criterios[h], p_cross)
        if cc > 0 or random.random() < 0.5:
            skills[h] = (round(cc, 4), random.randint(1, MAX_REPETICIONES))

    # asegurar al menos 3 habilidades
    if len(skills) < 3:
        for h in habs_por_carrera[primaria][:3]:
            skills.setdefault(h, (round(cc_por_criterios(criterios[h], max(p, 0.4)), 4),
                                  random.randint(1, MAX_REPETICIONES)))

    return primaria, skills


def coincidencia_por_carrera(skills, habs_por_carrera, carreras):
    """Media ponderada por peso sobre las habilidades de cada carrera (faltantes=0)."""
    ranking = []
    for c in carreras:
        num = 0.0
        den = 0
        for h in habs_por_carrera[c]:
            cc, peso = skills.get(h, (0.0, 0))
            num += peso * cc
            den += max(peso, 1)
        pct = num / den if den else 0.0
        ranking.append((c, round(pct, 2)))
    ranking.sort(key=lambda x: x[1], reverse=True)
    return ranking


# ---------------------------------------------------------------------------
# Construccion e insercion masiva por area
# ---------------------------------------------------------------------------
def generar_area(area_id):
    nombre_area, n_total = AREAS[area_id]
    carreras, habs_por_carrera, criterios, todas = cargar_estructura(area_id)
    limpiar_area(area_id)

    usuarios = []          # dicts para tabla usuario
    hab_rows_por_uuid = {} # uuid -> [(id_habilidad, cc), ...] (expandido por repeticion)
    result_rows = []       # (uuid, id_carrera, pct, top)

    def construir(ancla):
        primaria, skills = perfil_usuario(carreras, habs_por_carrera, criterios, todas, ancla=ancla)
        u = f"USER-{uuid.uuid4()}"
        nom = f"{random.choice(NOMBRES)} {random.choice(APELLIDOS)}"
        cor = f"{nom.lower().replace(' ', '.')}_{random.randint(1,10**6)}@athena.edu"
        usuarios.append({"nombre": nom, "correo": cor, "uuid": u, "area": area_id})

        # expandir repeticiones: 1 fila con cc alto + (peso-1) filas con cc <= alto
        filas = []
        for h, (cc, peso) in skills.items():
            filas.append((h, cc))
            for _ in range(peso - 1):
                menor = round(cc * random.random(), 4)
                filas.append((h, menor))
        hab_rows_por_uuid[u] = filas

        ranking = coincidencia_por_carrera(skills, habs_por_carrera, carreras)
        for top, (c, pct) in enumerate(ranking[:STORE_TOP], start=1):
            result_rows.append((u, c, pct, top))

    # 1) anclas: un 100% por carrera (perfil exacto de la carrera, cc=1.0)
    for c in carreras:
        # ancla con carrera primaria = c exactamente
        u = f"USER-{uuid.uuid4()}"
        nom = f"{random.choice(NOMBRES)} {random.choice(APELLIDOS)}"
        cor = f"{nom.lower().replace(' ', '.')}_{random.randint(1,10**6)}@athena.edu"
        usuarios.append({"nombre": nom, "correo": cor, "uuid": u, "area": area_id})
        skills = {h: (1.0, random.randint(1, MAX_REPETICIONES)) for h in habs_por_carrera[c]}
        filas = []
        for h, (cc, peso) in skills.items():
            for _ in range(peso):
                filas.append((h, 1.0))
        hab_rows_por_uuid[u] = filas
        ranking = coincidencia_por_carrera(skills, habs_por_carrera, carreras)
        for top, (cc_car, pct) in enumerate(ranking[:STORE_TOP], start=1):
            result_rows.append((u, cc_car, pct, top))

    # 2) usuarios de distribucion (perfiles cruzados) hasta completar n_total
    for _ in range(max(n_total - len(carreras), 0)):
        construir(ancla=False)

    # --- Insercion masiva ---
    with engine.begin() as conn:
        conn.execute(sa.text("""
            INSERT INTO usuario (nombre, correo, uuid_usuario, id_area)
            VALUES (:nombre, :correo, :uuid, :area)
        """), usuarios)

        mapa = {r["uuid_usuario"]: r["id_usuario"] for r in conn.execute(sa.text(
            "SELECT id_usuario, uuid_usuario FROM usuario WHERE id_area=:a"
        ), {"a": area_id}).mappings()}

        hab_payload = [
            {"u": mapa[u], "h": h, "cc": cc}
            for u, filas in hab_rows_por_uuid.items() for (h, cc) in filas
        ]
        for i in range(0, len(hab_payload), 5000):
            conn.execute(sa.text("""
                INSERT INTO usuario_habilidad (id_usuario, id_habilidad, cumplimiento_criterio)
                VALUES (:u, :h, :cc)
            """), hab_payload[i:i + 5000])

        res_payload = [{"uuid": u, "c": c, "pct": pct, "top": top}
                       for (u, c, pct, top) in result_rows]
        for i in range(0, len(res_payload), 5000):
            conn.execute(sa.text("""
                INSERT INTO resultado (uuid_usuario, id_carrera, porcentaje_coincidencia, top)
                VALUES (:uuid, :c, :pct, :top)
            """), res_payload[i:i + 5000])

    return nombre_area, carreras, todas


# ---------------------------------------------------------------------------
# Metricas y grafica desde la DB
# ---------------------------------------------------------------------------
def metricas_area(area_id, nombre_area, carreras, todas):
    with engine.begin() as conn:
        # distribucion de coincidencia top=1 (el mejor match por usuario)
        df = pd.read_sql(sa.text("""
            SELECT r.porcentaje_coincidencia::float AS pct, r.id_carrera
            FROM resultado r JOIN usuario u ON u.uuid_usuario=r.uuid_usuario
            WHERE u.id_area=:a AND r.top=1
        """), conn, params={"a": area_id})

        # cuantas carreras distintas abarcan las habilidades de cada usuario (realismo)
        cruce = conn.execute(sa.text("""
            WITH uc AS (
                SELECT u.id_usuario, COUNT(DISTINCT ch.id_carrera) n_carreras
                FROM usuario u
                JOIN usuario_habilidad uh ON uh.id_usuario=u.id_usuario
                JOIN carrera_habilidad ch ON ch.id_habilidad=uh.id_habilidad
                JOIN carrera c2 ON c2.id_carrera=ch.id_carrera AND c2.id_area=:a
                WHERE u.id_area=:a
                GROUP BY u.id_usuario
            )
            SELECT ROUND(AVG(n_carreras),2) avg_c, MIN(n_carreras) min_c, MAX(n_carreras) max_c
            FROM uc
        """), {"a": area_id}).mappings().one()

    pct = df["pct"] * 100
    por_clase = df["id_carrera"].value_counts()
    return {
        "area_id": area_id,
        "nombre": nombre_area,
        "n_users": len(df),
        "n_careers": len(carreras),
        "n_features": len(todas),
        "clase_min": int(por_clase.min()),
        "clase_avg": round(float(por_clase.mean()), 1),
        "clase_max": int(por_clase.max()),
        "clases_cubiertas": int(por_clase.shape[0]),
        "media_pct": round(float(pct.mean()), 1),
        "mediana_pct": round(float(pct.median()), 1),
        "n_100": int((pct >= 100).sum()),
        "cruce_avg": float(cruce["avg_c"]),
        "cruce_min": int(cruce["min_c"]),
        "cruce_max": int(cruce["max_c"]),
        "ratio_sf": round(len(df) / len(todas), 1),
        "df_pct": pct,
    }


def graficar(m):
    fig, ax = plt.subplots(figsize=(10, 5.5))
    ax.hist(m["df_pct"], bins=np.arange(0, 105, 5), color="#4C72B0",
            edgecolor="black", alpha=0.85)
    ax.set_title("Distribucion FINAL en DB - % de coincidencia (mejor match top=1)\n"
                 f"Area {m['area_id']}: {m['nombre']} (n={m['n_users']})")
    ax.set_xlabel("Porcentaje de coincidencia (%)")
    ax.set_ylabel("Cantidad de usuarios")
    fig.tight_layout()
    out = os.path.join(FINAL_DIR, f"distribucion_final_area_{m['area_id']}.png")
    fig.savefig(out, dpi=120)
    plt.close(fig)
    return out


# ---------------------------------------------------------------------------
# Reporte de criterios de entrenamiento
# ---------------------------------------------------------------------------
def escribir_reporte(metricas):
    MIN_POR_CLASE = 100     # umbral recomendado de muestras por clase
    MIN_RATIO_SF = 10       # muestras por feature minimo recomendado

    lineas = []
    lineas.append("# Contexto del dataset y criterios de entrenamiento\n")
    lineas.append("Modelo objetivo: **RandomForest de clasificacion** que, dadas las "
                  "habilidades del usuario, estima la coincidencia por carrera y "
                  "devuelve el **top-3** (via `predict_proba` sobre `id_carrera`).\n")
    lineas.append("Un modelo independiente por area (el `id_area` cierra el universo "
                  "de carreras y habilidades).\n")
    lineas.append("\n## Resumen por area\n")
    lineas.append("| Area | Usuarios | Carreras (clases) | Features (hab. distintas) | "
                  "Muestras/clase (min/avg/max) | Ratio muestras/feature | Media coincidencia | Cruce carreras/usuario (avg) |")
    lineas.append("|------|----------|-------------------|---------------------------|"
                  "------------------------------|------------------------|--------------------|------------------------------|")
    for m in metricas:
        lineas.append(
            f"| {m['area_id']} - {m['nombre']} | {m['n_users']} | {m['n_careers']} | "
            f"{m['n_features']} | {m['clase_min']}/{m['clase_avg']}/{m['clase_max']} | "
            f"{m['ratio_sf']} | {m['media_pct']}% | {m['cruce_avg']} |"
        )

    lineas.append("\n## Criterios evaluados\n")
    for m in metricas:
        lineas.append(f"### Area {m['area_id']} - {m['nombre']}\n")
        c1 = m["clase_min"] >= MIN_POR_CLASE
        c2 = m["ratio_sf"] >= MIN_RATIO_SF
        c3 = m["clases_cubiertas"] == m["n_careers"]
        c4 = m["cruce_avg"] > 1.0
        c5 = m["n_100"] >= m["n_careers"]
        def ok(b): return "CUMPLE" if b else "NO CUMPLE"
        lineas.append(f"- Muestras por clase >= {MIN_POR_CLASE}: **{ok(c1)}** "
                      f"(minimo real = {m['clase_min']}).")
        lineas.append(f"- Ratio muestras/feature >= {MIN_RATIO_SF}: **{ok(c2)}** "
                      f"(ratio real = {m['ratio_sf']}).")
        lineas.append(f"- Todas las carreras representadas como top-1: **{ok(c3)}** "
                      f"({m['clases_cubiertas']}/{m['n_careers']}).")
        lineas.append(f"- Perfiles realistas (habilidades cruzan >1 carrera): **{ok(c4)}** "
                      f"(promedio = {m['cruce_avg']} carreras/usuario; sin leakage de carrera unica).")
        lineas.append(f"- >=1 usuario 100% por carrera (ejemplar perfecto): **{ok(c5)}** "
                      f"(usuarios al 100% = {m['n_100']}).")
        veredicto = all([c1, c2, c3, c4])
        lineas.append(f"\n**Veredicto area {m['area_id']}: "
                      f"{'APTA para entrenar' if veredicto else 'REVISAR'}**\n")

    lineas.append("\n## Conclusion\n")
    todas_ok = all(
        m["clase_min"] >= MIN_POR_CLASE and m["ratio_sf"] >= MIN_RATIO_SF
        and m["clases_cubiertas"] == m["n_careers"] and m["cruce_avg"] > 1.0
        for m in metricas
    )
    if todas_ok:
        lineas.append("Las 3 areas **cumplen los criterios** de cantidad, balance, "
                      "dimensionalidad y realismo para entrenar un RandomForest de "
                      "clasificacion con salida top-3.\n")
    else:
        lineas.append("Algun area no cumple todos los criterios; ver detalle arriba.\n")
    lineas.append("\n### Recomendaciones de entrenamiento\n")
    lineas.append("- Features: vector multi-hot de las habilidades del area ponderado "
                  "por `cumplimiento_criterio` consolidado (max entre formularios).")
    lineas.append("- Label: carrera con `top=1` en `resultado`. Top-3 en inferencia con "
                  "`predict_proba` -> 3 clases de mayor probabilidad.")
    lineas.append("- Split estratificado por carrera; reportar accuracy top-1 y top-3, "
                  "y metricas por clase (no solo el promedio global).")
    lineas.append("- Usar `class_weight=\"balanced\"` por robustez ante clases menores.")
    lineas.append("- Un modelo por area (3 modelos independientes).")

    ruta = os.path.join(DATA_DIR, "context_dataset.md")
    with open(ruta, "w", encoding="utf-8") as f:
        f.write("\n".join(lineas) + "\n")
    return ruta


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    metricas = []
    for area_id in (1, 2, 3):
        nombre, carreras, todas = generar_area(area_id)
        m = metricas_area(area_id, nombre, carreras, todas)
        png = graficar(m)
        metricas.append(m)
        print(f"Area {area_id} ({nombre}): {m['n_users']} usuarios, "
              f"{m['n_careers']} carreras, {m['n_features']} features | "
              f"muestras/clase min/avg/max = {m['clase_min']}/{m['clase_avg']}/{m['clase_max']} | "
              f"cruce carreras/usuario avg = {m['cruce_avg']} | 100% = {m['n_100']}")
        print(f"  grafica: {png}")

    ruta = escribir_reporte(metricas)
    print(f"\nReporte de criterios: {ruta}")


if __name__ == "__main__":
    main()
