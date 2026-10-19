import pandas as pd
from sqlalchemy import Connection, select

from models.tables.criterios import Criterio
from models.tables.usuario import Usuario
from models.tables.usuario_criterio import UsuarioCriterio


class UsuarioCriterioTableRepository:
    def __init__(self, connection: Connection):
        self.connection = connection

    def get_by_area(self, area_id: int, type_users: list[int]) -> pd.DataFrame:
        query = (
            select(UsuarioCriterio.usuario_id, Criterio.carrera_id, Criterio.type_id, Criterio.riasec_id,
                   UsuarioCriterio.repeticiones, UsuarioCriterio.porc_coincidencia)
            .join(Criterio, Criterio.criterio_id == UsuarioCriterio.criterio_id)
            .join(Usuario, Usuario.usuario_id == UsuarioCriterio.usuario_id)
            .where(Usuario.area_id == area_id, Usuario.type_user.in_(type_users))
            .order_by(UsuarioCriterio.usuario_id, Criterio.carrera_id, Criterio.riasec_id)
        )
        return pd.read_sql(query, self.connection)
