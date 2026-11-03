import pandas as pd
from sqlalchemy import Engine, delete, select
from sqlalchemy.orm import sessionmaker

from models.tables.carreras import Carrera
from models.tables.resultados import Resultado
from models.tables.usuario import Usuario


class ResultadosTableRepository:
    def __init__(self, engine: Engine):
        self.engine = engine
        self.session_factory = sessionmaker(bind=engine)

    def get_by_area(self, area_id: int, type_users: list[int]) -> pd.DataFrame:
        query = (
            select(Resultado.usuario_id, Resultado.carrera_id, Resultado.porc_coincidencia)
            .join(Usuario, Usuario.usuario_id == Resultado.usuario_id)
            .where(Usuario.area_id == area_id, Usuario.type_user.in_(type_users))
            .order_by(Resultado.usuario_id, Resultado.carrera_id)
        )
        with self.engine.connect() as conn:
            return pd.read_sql(query, conn)

    def replace_user_results(self, user_id: int, resultados: list[Resultado]) -> None:
        with self.session_factory.begin() as session:
            session.execute(delete(Resultado).where(Resultado.usuario_id == user_id))
            session.add_all(resultados)

    def get_by_user(self, user_id: int) -> list[dict]:
        query = (
            select(Resultado.carrera_id, Carrera.nom_carrera, Resultado.porc_coincidencia)
            .join(Carrera, Carrera.carrera_id == Resultado.carrera_id)
            .where(Resultado.usuario_id == user_id)
            .order_by(Resultado.porc_coincidencia.desc(), Resultado.carrera_id)
        )
        with self.engine.connect() as conn:
            filas = conn.execute(query).mappings().all()
        return [dict(fila) for fila in filas]
