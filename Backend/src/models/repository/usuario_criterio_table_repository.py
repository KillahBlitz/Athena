import pandas as pd
from sqlalchemy import Engine, select
from sqlalchemy.orm import sessionmaker

from models.tables.criterios import Criterio
from models.tables.usuario import Usuario
from models.tables.usuario_criterio import UsuarioCriterio


class UsuarioCriterioTableRepository:
    def __init__(self, engine: Engine):
        self.engine = engine
        self.session_factory = sessionmaker(bind=engine)

    def insert_user_criteria(self, criterion: UsuarioCriterio) -> None:
        with self.session_factory.begin() as session:
            session.add(criterion)

    def get_by_area(self, area_id: int, type_users: list[int]) -> pd.DataFrame:
        query = (
            select(UsuarioCriterio.usuario_id, Criterio.carrera_id, Criterio.type_id, Criterio.riasec_id,
                   UsuarioCriterio.repeticiones, UsuarioCriterio.porc_coincidencia)
            .join(Criterio, Criterio.criterio_id == UsuarioCriterio.criterio_id)
            .join(Usuario, Usuario.usuario_id == UsuarioCriterio.usuario_id)
            .where(Usuario.area_id == area_id, Usuario.type_user.in_(type_users))
            .order_by(UsuarioCriterio.usuario_id, Criterio.carrera_id, Criterio.riasec_id)
        )
        with self.engine.connect() as conn:
            return pd.read_sql(query, conn)
