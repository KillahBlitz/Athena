from __future__ import annotations

import argparse
import csv
import hashlib
import os
import random
import uuid
from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

import sqlalchemy as sa

DB_HOST = os.getenv("ATHENA_DB_HOST", "100.95.220.1")
DB_PORT = int(os.getenv("ATHENA_DB_PORT", "5432"))
DB_USER = os.getenv("ATHENA_DB_USER", "admin")
DB_PASSWORD = os.getenv("ATHENA_DB_PASSWORD", "password")
DB_NAME = os.getenv("ATHENA_DB_NAME", "athena")
SEED = 20260928
QUOTA_PER_BAND_AREA = 50
MAX_ATTEMPTS = 20_000
BANDS = (
    ("PERT_05", 0.50, 0.60, 1, 2, 0.40, 0.70, 0.40),
    ("PERT_06", 0.60, 0.70, 0, 1, 0.55, 0.80, 0.35),
    ("PERT_07", 0.70, 0.80, 0, 1, 0.70, 0.90, 0.25),
    ("PERT_08", 0.80, 0.90, 0, 0, 0.75, 0.95, 0.15),
)

ROOT = Path(__file__).resolve().parents[2]
REPORT_DIR = ROOT / "Docs" / "Reports" / "dataset_validation"
REPORT_DIR.mkdir(parents=True, exist_ok=True)


@dataclass(frozen=True)
class SourceProfile:
    uuid: str
    area: int
    career: int
    skills: dict[int, float]
    required: frozenset[int]


def db_engine() -> sa.Engine:
    url = (
        f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}"
        f"@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    )
    return sa.create_engine(url, connect_args={"connect_timeout": 10})


def load_sources(engine: sa.Engine) -> dict[int, list[SourceProfile]]:
    profile_query = sa.text("""
        SELECT u.uuid_usuario, u.id_area, r.id_carrera,
               uh.id_habilidad, MAX(uh.cumplimiento_criterio) AS cumplimiento
        FROM usuario u
        JOIN resultado r ON r.uuid_usuario = u.uuid_usuario AND r.top = 1
        JOIN usuario_habilidad uh ON uh.id_usuario = u.id_usuario
        WHERE u.uuid_usuario LIKE 'USER-%'
        GROUP BY u.uuid_usuario, u.id_area, r.id_carrera, uh.id_habilidad
        ORDER BY u.uuid_usuario, uh.id_habilidad
    """)
    skills_query = sa.text("""
        SELECT id_carrera, id_habilidad
        FROM carrera_habilidad
        ORDER BY id_carrera, id_habilidad
    """)
    with engine.connect() as connection:
        profile_rows = connection.execute(profile_query).mappings().all()
        skill_rows = connection.execute(skills_query).mappings().all()

    required_by_career: dict[int, set[int]] = {}
    for row in skill_rows:
        required_by_career.setdefault(row["id_carrera"], set()).add(row["id_habilidad"])

    grouped: dict[str, dict] = {}
    for row in profile_rows:
        grouped.setdefault(row["uuid_usuario"], {
            "area": row["id_area"],
            "career": row["id_carrera"],
            "skills": {},
        })["skills"][row["id_habilidad"]] = float(row["cumplimiento"])

    sources: dict[int, list[SourceProfile]] = {}
    for source_uuid, value in grouped.items():
        source = SourceProfile(
            uuid=source_uuid,
            area=value["area"],
            career=value["career"],
            skills=value["skills"],
            required=frozenset(required_by_career[value["career"]]),
        )
        sources.setdefault(source.area, []).append(source)
    return sources


def decimal_target(value: float) -> float:
    rounded = Decimal(str(value)).quantize(Decimal("0.01"), ROUND_HALF_UP)
    return float(rounded)


def fingerprint(source: SourceProfile, varied: dict[int, float]) -> str:
    payload = f"{source.uuid}|{source.career}|" + ";".join(
        f"{key}:{varied[key]:.2f}" for key in sorted(varied)
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:16]


def build_candidate(
    rng: random.Random,
    source: SourceProfile,
    band: tuple,
) -> dict | None:
    band_name, lower, upper, dropout_min, dropout_max, min_value, max_value, reduction = band
    varied = dict(source.skills)
    reduce_count = max(1, int(len(varied) * reduction))
    for skill_id in rng.sample(list(varied), k=min(reduce_count, len(varied))):
        varied[skill_id] = round(rng.uniform(min_value, max_value), 2)

    max_dropout = min(dropout_max, max(0, len(varied) - 1))
    dropout_count = rng.randint(dropout_min, max_dropout) if max_dropout >= dropout_min else 0
    if dropout_count:
        for skill_id in rng.sample(list(varied), k=dropout_count):
            del varied[skill_id]

    common = source.required.intersection(varied)
    target = round(sum(varied[skill_id] for skill_id in common) / len(source.required), 4)
    stored_target = decimal_target(target)
    if not lower <= stored_target < upper:
        return None

    return {
        "band": band_name,
        "target": stored_target,
        "target_raw": target,
        "source_uuid": source.uuid,
        "area": source.area,
        "career": source.career,
        "skills": varied,
        "fingerprint": fingerprint(source, varied),
    }


def collect_candidates(sources: dict[int, list[SourceProfile]]) -> tuple[list[dict], dict]:
    rng = random.Random(SEED)
    selected: list[dict] = []
    counts = {(area, band[0]): 0 for area in sources for band in BANDS}
    fingerprints: set[str] = set()
    attempts = 0
    target_total = len(counts) * QUOTA_PER_BAND_AREA

    while attempts < MAX_ATTEMPTS and len(selected) < target_total:
        attempts += 1
        pending = [key for key, count in counts.items() if count < QUOTA_PER_BAND_AREA]
        if not pending:
            break
        area, band_name = rng.choice(pending)
        band = next(item for item in BANDS if item[0] == band_name)
        source = rng.choice(sources[area])
        candidate = build_candidate(rng, source, band)
        if candidate is None or candidate["fingerprint"] in fingerprints:
            continue
        fingerprints.add(candidate["fingerprint"])
        counts[(area, band_name)] += 1
        selected.append(candidate)

    return selected, {"attempts": attempts, "counts": counts, "target_total": target_total}


def write_manifest(rows: list[dict], filename: str) -> Path:
    path = REPORT_DIR / filename
    fields = ["uuid_nuevo", "uuid_origen", "area", "id_carrera", "banda", "target", "target_raw", "fingerprint"]
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows({key: row[key] for key in fields} for row in rows)
    return path


def persist(engine: sa.Engine, candidates: list[dict]) -> list[dict]:
    pending = []
    for candidate in candidates:
        item = dict(candidate)
        item["uuid_nuevo"] = f"PERT-BAL-{uuid.uuid4()}"
        pending.append(item)

    with engine.begin() as connection:
        ids = {}
        for item in pending:
            row = connection.execute(sa.text("""
                INSERT INTO usuario (nombre, correo, uuid_usuario, id_area)
                VALUES (:nombre, :correo, :uuid_usuario, :id_area)
                RETURNING id_usuario, uuid_usuario
            """), {
                "nombre": f"Perturbacion balanceada {item['band']}",
                "correo": f"{item['uuid_nuevo'].lower()}@athena.local",
                "uuid_usuario": item["uuid_nuevo"],
                "id_area": item["area"],
            }).mappings().one()
            ids[row["uuid_usuario"]] = row["id_usuario"]
        skills = [
            {
                "id_usuario": ids[item["uuid_nuevo"]],
                "id_habilidad": skill_id,
                "cumplimiento_criterio": value,
            }
            for item in pending
            for skill_id, value in item["skills"].items()
        ]
        connection.execute(sa.text("""
            INSERT INTO usuario_habilidad
                (id_usuario, id_habilidad, cumplimiento_criterio)
            VALUES (:id_usuario, :id_habilidad, :cumplimiento_criterio)
        """), skills)
        connection.execute(sa.text("""
            INSERT INTO resultado
                (uuid_usuario, id_carrera, porcentaje_coincidencia, top)
            VALUES (:uuid_usuario, :id_carrera, :target, 1)
        """), [
            {
                "uuid_usuario": item["uuid_nuevo"],
                "id_carrera": item["career"],
                "target": item["target"],
            }
            for item in pending
        ])
    return pending


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--persist", action="store_true")
    args = parser.parse_args()
    engine = db_engine()
    sources = load_sources(engine)
    candidates, report = collect_candidates(sources)
    manifest_rows = [
        {
            "uuid_nuevo": item.get("uuid_nuevo", "DRY-RUN"),
            "uuid_origen": item["source_uuid"],
            "area": item["area"],
            "id_carrera": item["career"],
            "banda": item["band"],
            "target": item["target"],
            "target_raw": item["target_raw"],
            "fingerprint": item["fingerprint"],
        }
        for item in candidates
    ]
    if args.persist:
        with engine.connect() as connection:
            existing = connection.execute(sa.text(
                "SELECT COUNT(*) FROM usuario WHERE uuid_usuario LIKE 'PERT-BAL-%'"
            )).scalar_one()
        if existing:
            raise RuntimeError(
                f"Ya existen {existing} usuarios PERT-BAL; no se reejecuta para evitar duplicados."
            )
        persisted = persist(engine, candidates)
        for row, item in zip(manifest_rows, persisted):
            row["uuid_nuevo"] = item["uuid_nuevo"]
        manifest_path = write_manifest(manifest_rows, "pert_balance_manifest.csv")
    else:
        manifest_path = write_manifest(manifest_rows, "pert_balance_dry_run.csv")

    print(f"sources={sum(len(value) for value in sources.values())}")
    print(f"attempts={report['attempts']}")
    print(f"selected={len(candidates)}/{report['target_total']}")
    for key in sorted(report["counts"]):
        print(f"area={key[0]} band={key[1]} count={report['counts'][key]}")
    print(f"manifest={manifest_path}")


if __name__ == "__main__":
    main()
