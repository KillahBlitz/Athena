import pandas as pd
from sqlalchemy import Connection, select
from sqlalchemy.orm import Session

from models.tables.usuario import Usuario

class UsuariosTableRepository:
    def __init__(self, connection: Connection):
        self.connection = connection
        self.session = Session(bind=connection)

    def get_users_by_area_id(self, area_id: int) -> list[Usuario]:
        query = select(Usuario).where(Usuario.area_id == area_id)
        return list(self.session.scalars(query))

    def get_users_by_area_and_type(self, area_id: int, type_users: list[int]) -> pd.DataFrame:
        query = (
            select(Usuario.usuario_id, Usuario.type_user)
            .where(Usuario.area_id == area_id, Usuario.type_user.in_(type_users))
            .order_by(Usuario.usuario_id)
        )
        return pd.read_sql(query, self.connection)
