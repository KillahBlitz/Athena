from models.tables.carreras import Carrera
from sqlalchemy import Engine, and_, func, select


class CarrerasTableRepository:
    def __init__(self, engine: Engine):
        self.engine = engine

    def get_carrera_ids(self, area_id: int) -> list[int]:
        query = select(Carrera.carrera_id).where(Carrera.area_id == area_id).order_by(Carrera.carrera_id)
        with self.engine.connect() as conn:
            return list(conn.scalars(query))