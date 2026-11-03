from sqlalchemy import Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from models.tables.base import Base


class Usuario(Base):
    __tablename__ = "usuarios"

    usuario_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    uuid_usuario: Mapped[str] = mapped_column(Text, unique=True)
    area_id: Mapped[int | None] = mapped_column(Integer)
    nombre_usuario: Mapped[str] = mapped_column(String(200))
    correo_usuario: Mapped[str] = mapped_column(String(150))
    estatus_id: Mapped[int] = mapped_column(Integer)
    type_user: Mapped[int] = mapped_column(Integer)
