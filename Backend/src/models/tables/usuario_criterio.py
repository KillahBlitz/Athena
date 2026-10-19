from sqlalchemy import Float, Integer
from sqlalchemy.orm import Mapped, mapped_column

from models.tables.base import Base


class UsuarioCriterio(Base):
    __tablename__ = "usuario_criterio"

    usuario_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    criterio_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    repeticiones: Mapped[int] = mapped_column(Integer, primary_key=True)
    porc_coincidencia: Mapped[float] = mapped_column(Float)
