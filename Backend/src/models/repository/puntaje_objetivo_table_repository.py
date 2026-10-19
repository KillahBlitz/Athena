import pandas as pd
from sqlalchemy import Connection, select

from models.tables.puntaje_objetivo import PuntajeObjetivo
from models.tables.usuario import Usuario


class PuntajeObjetivoTableRepository:
    def __init__(self, connection: Connection):
        self.connection = connection

    def get_by_area(self, area_id: int, type_users: list[int]) -> pd.DataFrame:
        query = (
            select(PuntajeObjetivo.usuario_id, PuntajeObjetivo.carrera_id, PuntajeObjetivo.porc_objetivo)
            .join(Usuario, Usuario.usuario_id == PuntajeObjetivo.usuario_id)
            .where(Usuario.area_id == area_id, Usuario.type_user.in_(type_users))
            .order_by(PuntajeObjetivo.usuario_id, PuntajeObjetivo.carrera_id)
        )
        return pd.read_sql(query, self.connection)
