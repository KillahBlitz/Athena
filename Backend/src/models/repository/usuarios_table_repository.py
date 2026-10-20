import pandas as pd
from sqlalchemy import Engine, select
from sqlalchemy.orm import sessionmaker

from models.tables.usuario import Usuario

class UsuariosTableRepository:
    def __init__(self, engine: Engine):
        self.engine = engine
        self.session_factory = sessionmaker(bind=engine)

    def get_users_by_area_id(self, area_id: int) -> list[Usuario]:
        query = select(Usuario).where(Usuario.area_id == area_id)
        with self.session_factory() as session:
            return list(session.scalars(query))

    def get_users_by_area_and_type(self, area_id: int, type_users: list[int]) -> pd.DataFrame:
        query = (
            select(Usuario.usuario_id, Usuario.type_user)
            .where(Usuario.area_id == area_id, Usuario.type_user.in_(type_users))
            .order_by(Usuario.usuario_id)
        )
        with self.engine.connect() as conn:
            return pd.read_sql(query, conn)
