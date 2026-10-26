import pandas as pd
from sqlalchemy import Engine, select
from sqlalchemy.orm import sessionmaker

from models.tables.puntaje_objetivo import PuntajeObjetivo
from models.tables.usuario import Usuario


class PuntajeObjetivoTableRepository:
    def __init__(self, engine: Engine):
        self.engine = engine
        self.session_factory = sessionmaker(bind=engine)

    def insert_score(self, objective: PuntajeObjetivo) -> None:
        with self.session_factory.begin() as session:
            session.add(objective)

    def get_by_area(self, area_id: int, type_users: list[int]) -> pd.DataFrame:
        query = (
            select(PuntajeObjetivo.usuario_id, PuntajeObjetivo.carrera_id, PuntajeObjetivo.porc_objetivo)
            .join(Usuario, Usuario.usuario_id == PuntajeObjetivo.usuario_id)
            .where(Usuario.area_id == area_id, Usuario.type_user.in_(type_users))
            .order_by(PuntajeObjetivo.usuario_id, PuntajeObjetivo.carrera_id)
        )
        with self.engine.connect() as conn:
            return pd.read_sql(query, conn)
