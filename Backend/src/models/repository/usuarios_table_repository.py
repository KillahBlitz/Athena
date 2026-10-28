import pandas as pd
from sqlalchemy import Engine, select, update
from sqlalchemy.orm import sessionmaker

from models.tables.usuario import Usuario

class UsuariosTableRepository:
    def __init__(self, engine: Engine):
        self.engine = engine
        self.session_factory = sessionmaker(bind=engine)

    def insert_user(self, user: Usuario) -> int:
        with self.session_factory.begin() as session:
            session.add(user)
            session.flush()
            user_id = user.usuario_id
        return user_id

    def update_user_status(self, user_uuid: str, status_id: int) -> None:
        query = update(Usuario).where(Usuario.uuid_usuario == user_uuid).values(estatus_id=status_id)
        with self.session_factory.begin() as session:
            return session.execute(query)

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

    def get_user_data(self, user_id: int) -> pd.DataFrame:
        """Mismas columnas que get_users_by_area_and_type, sin filtrar por tipo (los usuarios reales son type_user=4)."""
        query = select(Usuario.usuario_id, Usuario.type_user).where(Usuario.usuario_id == user_id)
        with self.engine.connect() as conn:
            return pd.read_sql(query, conn)

    def get_user_by_uuid(self, user_uuid: str) -> Usuario | None:
        query = select(Usuario).where(Usuario.uuid_usuario == user_uuid)
        with self.session_factory() as session:
            return session.scalar(query)