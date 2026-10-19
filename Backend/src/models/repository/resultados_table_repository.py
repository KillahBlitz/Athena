import pandas as pd
from sqlalchemy import Connection, and_, func, select

from models.tables.criterios import Criterio
from models.tables.puntaje_objetivo import PuntajeObjetivo
from models.tables.resultados import Resultado
from models.tables.usuario import Usuario
from models.tables.usuario_criterio import UsuarioCriterio

RIASEC = {1: "r", 2: "i", 4: "s", 5: "e", 6: "c"}
TYPE_PRINCIPAL, TYPE_PERFIL = 2, 1


class ResultadosTableRepository:
    def __init__(self, connection: Connection):
        self.connection = connection

    def get_by_area(self, area_id: int, type_users: list[int]) -> pd.DataFrame:
        query = (
            select(Resultado.usuario_id, Resultado.carrera_id, Resultado.porc_coincidencia)
            .join(Usuario, Usuario.usuario_id == Resultado.usuario_id)
            .where(Usuario.area_id == area_id, Usuario.type_user.in_(type_users))
            .order_by(Resultado.usuario_id, Resultado.carrera_id)
        )
        return pd.read_sql(query, self.connection)
