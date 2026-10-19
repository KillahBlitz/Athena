from models.tables.carreras import Carrera
from sqlalchemy import Connection, and_, func, select


class CarrerasTableRepository:
    def __init__(self, connection: Connection):
        self.connection = connection

    def get_carrera_ids(self, area_id: int) -> list[int]:
        query = select(Carrera.carrera_id).where(Carrera.area_id == area_id).order_by(Carrera.carrera_id)
        return list(self.connection.scalars(query))