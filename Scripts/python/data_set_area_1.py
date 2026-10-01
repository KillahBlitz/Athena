"""
data_set_area_1.py
------------------
Genera un dataset SINTETICO en la base de datos Athena SOLO para el AREA 1
(Ingenieria y Ciencias Fisico Matematicas). No toca ninguna otra area.

Reglas de negocio (segun el modelo del proyecto):
  * Un usuario pertenece a un area (id_area). El area cierra el universo de
    carreras y habilidades.
  * Un usuario llena 5 formularios, por lo que puede REPETIR una misma
    habilidad. La cantidad de repeticiones se usa como PESO. Al consolidar se
    conserva el cumplimiento_criterio MAS ALTO de esa habilidad.
  * cumplimiento_criterio por habilidad = (criterios cumplidos / total de
    criterios de la habilidad)  -> valor en [0, 1].
  * porcentaje_coincidencia de una carrera = MEDIA PONDERADA (por el peso de
    repeticion) del cumplimiento_criterio sobre las habilidades de la carrera:
        pct = sum(peso_h * cc_h) / sum(peso_h)

Distribucion objetivo (la "compartida"): Beta(alpha=2.5, beta=2.0) escalada a
[0,1]; campana suave, unimodal, masa en el rango medio-alto, sin picos
artificiales.

GARANTIA OBLIGATORIA: se crea al menos UN usuario con 100% de coincidencia por
CADA carrera del area 1.

Al terminar, consulta la distribucion REAL resultante en la DB y guarda una
grafica en Scripts/python/media/results/.

Uso:
    python data_set_area_1.py
"""

import os
import uuid
import random

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import sqlalchemy as sa

# ---------------------------------------------------------------------------
# Conexion (mismos parametros que data_base_happypath.ipynb)
# ---------------------------------------------------------------------------
DB_HOST = os.getenv("DB_HOST", "100.95.220.1")
DB_PORT = int(os.getenv("DB_PORT", "5432"))
DB_USER = os.getenv("DB_USER", "admin")
DB_PASSWORD = os.getenv("DB_PASSWORD", "password")
DB_CONECTION = os.getenv("DB_CONECTION", "athena")

connection_url = (
    f"postgresql+psycopg://{DB_USER}:{DB_PASSWORD}"
    f"@{DB_HOST}:{DB_PORT}/{DB_CONECTION}"
)
engine = sa.create_engine(connection_url)

# ---------------------------------------------------------------------------
# Configuracion del dataset
# ---------------------------------------------------------------------------
AREA_ID = 1
AREA_NOMBRE = "Ingenieria y Ciencias Fisico Matematicas"
N_TOTAL = 3225            # 43 carreras x 75 usuarios/carrera (misma densidad que area 2)
ALPHA, BETA = 2.5, 2.0    # forma de la distribucion objetivo (Beta)
MAX_REPETICIONES = 5      # 5 formularios -> hasta 5 repeticiones por habilidad
SEED = 42

RESULTS_DIR = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "media", "results"
)
os.makedirs(RESULTS_DIR, exist_ok=True)

rng = np.random.default_rng(SEED)
random.seed(SEED)

# Nombres para generar usuarios
NOMBRES = [
    "Ana", "Carlos", "Maria", "Juan", "Sofia", "Luis", "Elena", "Diego",
    "Valentina", "Andres", "Camila", "Jorge", "Laura", "Mateo", "Isabella",
]
APELLIDOS = [
    "Gomez", "Perez", "Lopez", "Rodriguez", "Martinez", "Hernandez", "Garcia",
    "Sanchez", "Ramirez", "Torres", "Flores", "Vargas", "Castro", "Morales",
]


# ---------------------------------------------------------------------------
# Lectura de la estructura del area 1
# ---------------------------------------------------------------------------
def cargar_estructura_area() -> tuple[list[int], dict[int, list[int]], dict[int, int]]:
    """
    Devuelve:
      - carreras: lista de id_carrera del area
      - habilidades_por_carrera: {id_carrera: [id_habilidad, ...]}
      - criterios_por_habilidad: {id_habilidad: n_criterios}
    """
    with engine.begin() as conn:
        carreras = [
            row["id_carrera"]
            for row in conn.execute(sa.text("""
                SELECT id_carrera FROM carrera WHERE id_area = :a ORDER BY id_carrera
            """), {"a": AREA_ID}).mappings()
        ]

        habilidades_por_carrera: dict[int, list[int]] = {}
        for id_carrera in carreras:
            habs = [
                row["id_habilidad"]
                for row in conn.execute(sa.text("""
                    SELECT id_habilidad FROM carrera_habilidad
                    WHERE id_carrera = :c ORDER BY id_habilidad
                """), {"c": id_carrera}).mappings()
            ]
            habilidades_por_carrera[id_carrera] = habs

        # criterios por habilidad (solo las del area)
        todas_habs = sorted({h for habs in habilidades_por_carrera.values() for h in habs})
        criterios_por_habilidad: dict[int, int] = {}
        rows = conn.execute(sa.text("""
            SELECT h.id_habilidad, COUNT(cr.id_criterio) AS n
            FROM habilidad h
            LEFT JOIN criterio cr ON cr.id_habilidad = h.id_habilidad
            WHERE h.id_habilidad = ANY(:ids)
            GROUP BY h.id_habilidad
        """), {"ids": todas_habs}).mappings()
        for row in rows:
            # si una habilidad no tiene criterios, usamos 1 para evitar division por cero
            criterios_por_habilidad[row["id_habilidad"]] = max(int(row["n"]), 1)

    return carreras, habilidades_por_carrera, criterios_por_habilidad


# ---------------------------------------------------------------------------
# Limpieza SOLO del area 1 (idempotencia; no toca otras areas)
# ---------------------------------------------------------------------------
def limpiar_area() -> None:
    with engine.begin() as conn:
        conn.execute(sa.text("""
            DELETE FROM resultado
            WHERE uuid_usuario IN (SELECT uuid_usuario FROM usuario WHERE id_area = :a)
        """), {"a": AREA_ID})
        conn.execute(sa.text("""
            DELETE FROM usuario_habilidad
            WHERE id_usuario IN (SELECT id_usuario FROM usuario WHERE id_area = :a)
        """), {"a": AREA_ID})
        conn.execute(sa.text("DELETE FROM usuario WHERE id_area = :a"), {"a": AREA_ID})


# ---------------------------------------------------------------------------
# Generacion de un usuario y sus habilidades para una carrera
# ---------------------------------------------------------------------------
def generar_habilidades_usuario(
    habilidades: list[int],
    criterios_por_habilidad: dict[int, int],
    p_objetivo: float,
    forzar_100: bool = False,
) -> tuple[list[tuple[int, float]], float]:
    """
    Para un usuario cuyo desempeno objetivo es p_objetivo (fraccion 0-1) en una
    carrera, genera las filas de usuario_habilidad (con repeticiones) y calcula
    el porcentaje_coincidencia resultante.

    Devuelve:
      - filas: lista de (id_habilidad, cumplimiento_criterio) a insertar
               (una fila por repeticion)
      - pct: porcentaje_coincidencia (fraccion 0-1) = media ponderada por peso
    """
    filas: list[tuple[int, float]] = []
    suma_ponderada = 0.0
    suma_pesos = 0

    for id_hab in habilidades:
        total_criterios = criterios_por_habilidad[id_hab]

        if forzar_100:
            cumplidos = total_criterios          # cumple TODOS los criterios
        else:
            # cada criterio se cumple con probabilidad p_objetivo
            cumplidos = int(rng.binomial(total_criterios, p_objetivo))

        cc_alto = cumplidos / total_criterios     # cumplimiento consolidado (el mas alto)

        # peso = numero de veces que se repite la habilidad en los 5 formularios
        peso = int(random.randint(1, MAX_REPETICIONES))

        # una fila con el valor mas alto (el que se conserva al consolidar)
        filas.append((id_hab, round(cc_alto, 4)))
        # las repeticiones restantes: valores <= cc_alto (otros formularios)
        for _ in range(peso - 1):
            if forzar_100:
                cc_otro = cc_alto
            else:
                cumplidos_otro = int(rng.integers(0, cumplidos + 1)) if cumplidos > 0 else 0
                cc_otro = cumplidos_otro / total_criterios
            filas.append((id_hab, round(cc_otro, 4)))

        suma_ponderada += peso * cc_alto
        suma_pesos += peso

    pct = suma_ponderada / suma_pesos if suma_pesos else 0.0
    return filas, round(pct, 2)


def nombre_correo() -> tuple[str, str]:
    n = random.choice(NOMBRES)
    a = random.choice(APELLIDOS)
    r = random.randint(1, 100000)
    return f"{n} {a}", f"{n.lower()}.{a.lower()}_{r}@athena.edu"


# ---------------------------------------------------------------------------
# Insercion en la base de datos
# ---------------------------------------------------------------------------
def insertar_usuario(conn, nombre, correo, uuid_str) -> int:
    row = conn.execute(sa.text("""
        INSERT INTO usuario (nombre, correo, uuid_usuario, id_area)
        VALUES (:nombre, :correo, :uuid, :area)
        RETURNING id_usuario;
    """), {"nombre": nombre, "correo": correo, "uuid": uuid_str, "area": AREA_ID}).mappings().one()
    return row["id_usuario"]


def insertar_habilidades(conn, id_usuario, filas) -> None:
    conn.execute(sa.text("""
        INSERT INTO usuario_habilidad (id_usuario, id_habilidad, cumplimiento_criterio)
        VALUES (:u, :h, :cc)
    """), [{"u": id_usuario, "h": h, "cc": cc} for (h, cc) in filas])


def insertar_resultado(conn, uuid_str, id_carrera, pct) -> None:
    conn.execute(sa.text("""
        INSERT INTO resultado (uuid_usuario, id_carrera, porcentaje_coincidencia, top)
        VALUES (:uuid, :c, :pct, 1)
        ON CONFLICT (uuid_usuario, id_carrera) DO UPDATE SET
            porcentaje_coincidencia = EXCLUDED.porcentaje_coincidencia,
            top = EXCLUDED.top;
    """), {"uuid": uuid_str, "c": id_carrera, "pct": pct})


def crear_usuario_completo(conn, id_carrera, habilidades, criterios, p_objetivo, forzar_100=False):
    filas, pct = generar_habilidades_usuario(habilidades, criterios, p_objetivo, forzar_100)
    nombre, correo = nombre_correo()
    uuid_str = f"USER-{uuid.uuid4()}"
    id_usuario = insertar_usuario(conn, nombre, correo, uuid_str)
    insertar_habilidades(conn, id_usuario, filas)
    insertar_resultado(conn, uuid_str, id_carrera, pct)
    return pct


# ---------------------------------------------------------------------------
# Consulta de la distribucion REAL final desde la DB
# ---------------------------------------------------------------------------
def distribucion_real() -> pd.DataFrame:
    """
    Recalcula el porcentaje_coincidencia DIRECTAMENTE desde usuario_habilidad
    (media ponderada por peso = COUNT de repeticiones, cc = MAX consolidado)
    para los usuarios del area 1. Asi la grafica refleja lo que hay en la DB.
    """
    query = """
        WITH consolidado AS (
            SELECT uh.id_usuario, uh.id_habilidad,
                   MAX(uh.cumplimiento_criterio) AS cc,
                   COUNT(*) AS peso
            FROM usuario_habilidad uh
            GROUP BY uh.id_usuario, uh.id_habilidad
        )
        SELECT
            u.id_usuario,
            r.id_carrera,
            ROUND(SUM(cons.peso * cons.cc) / SUM(cons.peso) * 100)::INTEGER AS porcentaje
        FROM resultado r
        JOIN usuario u            ON u.uuid_usuario = r.uuid_usuario
        JOIN carrera_habilidad ch ON ch.id_carrera = r.id_carrera
        JOIN consolidado cons     ON cons.id_usuario = u.id_usuario
                                 AND cons.id_habilidad = ch.id_habilidad
        WHERE u.id_area = :a
        GROUP BY u.id_usuario, r.id_carrera
        ORDER BY porcentaje;
    """
    with engine.begin() as conn:
        return pd.read_sql(sa.text(query), conn, params={"a": AREA_ID})


def graficar(df: pd.DataFrame) -> str:
    fig, ax = plt.subplots(figsize=(10, 5.5))
    bins = np.arange(0, 105, 5)
    ax.hist(df["porcentaje"], bins=bins, color="#4C72B0", edgecolor="black", alpha=0.85)
    ax.set_title(
        "Distribucion REAL final en DB - % de coincidencia\n"
        f"Area {AREA_ID}: {AREA_NOMBRE} (n={len(df)})"
    )
    ax.set_xlabel("Porcentaje de coincidencia (%)")
    ax.set_ylabel("Cantidad de usuarios")
    fig.tight_layout()
    out = os.path.join(RESULTS_DIR, "distribucion_final_area_1.png")
    fig.savefig(out, dpi=120)
    plt.close(fig)
    return out


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main() -> None:
    carreras, habs_por_carrera, criterios = cargar_estructura_area()
    print(f"Area {AREA_ID}: {len(carreras)} carreras, "
          f"{sum(len(v) for v in habs_por_carrera.values())} pares carrera-habilidad")

    limpiar_area()
    print("Datos previos del area 1 eliminados (otras areas intactas).")

    n_100 = 0
    n_dist = 0
    with engine.begin() as conn:
        # 1) OBLIGATORIO: un usuario con 100% por cada carrera
        for id_carrera in carreras:
            pct = crear_usuario_completo(
                conn, id_carrera, habs_por_carrera[id_carrera], criterios,
                p_objetivo=1.0, forzar_100=True,
            )
            assert pct == 1.0, f"El usuario 100% de la carrera {id_carrera} dio {pct}"
            n_100 += 1

        # 2) Resto de usuarios siguiendo la distribucion Beta objetivo
        n_restantes = max(N_TOTAL - len(carreras), 0)
        objetivos = rng.beta(ALPHA, BETA, size=n_restantes)
        for p_objetivo in objetivos:
            id_carrera = random.choice(carreras)
            crear_usuario_completo(
                conn, id_carrera, habs_por_carrera[id_carrera], criterios,
                p_objetivo=float(p_objetivo), forzar_100=False,
            )
            n_dist += 1

    print(f"Usuarios 100% creados (uno por carrera): {n_100}")
    print(f"Usuarios de distribucion creados: {n_dist}")
    print(f"Total insertado en area {AREA_ID}: {n_100 + n_dist}")

    # 3) Distribucion real desde la DB
    df = distribucion_real()
    p = df["porcentaje"]
    print("\nDistribucion REAL en la DB (recalculada desde usuario_habilidad):")
    print(f"  n usuarios : {len(df)}")
    print(f"  media      : {p.mean():.1f}%")
    print(f"  mediana    : {p.median():.1f}%")
    print(f"  usuarios 100%: {(p == 100).sum()}  (esperado >= {len(carreras)})")

    bins = list(range(0, 111, 10))
    labels = [f"{b}-{b+10}%" for b in bins[:-1]]
    tabla = pd.cut(p, bins=bins, labels=labels, include_lowest=True, right=False)
    print("\nPor rangos de 10%:")
    print(tabla.value_counts().reindex(labels).to_string())

    out = graficar(df)
    print(f"\nGrafica guardada en: {out}")


if __name__ == "__main__":
    main()
