from collections import defaultdict

from sqlalchemy import Engine, select

from models.tables.escuelas import Escuela, EscuelaCarrera


class EscuelasTableRepository:
    def __init__(self, engine: Engine):
        self.engine = engine

    def get_by_carreras(self, carrera_ids: list[int]) -> dict[int, list[str]]:
        if not carrera_ids:
            return {}
        query = (
            select(EscuelaCarrera.id_carrera, Escuela.nom_escuela)
            .join(Escuela, Escuela.escuela_id == EscuelaCarrera.id_escuela)
            .where(EscuelaCarrera.id_carrera.in_(carrera_ids))
            .order_by(EscuelaCarrera.id_carrera, Escuela.nom_escuela)
        )
        escuelas = defaultdict(list)
        with self.engine.connect() as conn:
            for carrera_id, nom_escuela in conn.execute(query):
                escuelas[carrera_id].append(nom_escuela)
        return dict(escuelas)
