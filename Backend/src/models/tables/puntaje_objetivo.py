from sqlalchemy import Float, Integer
from sqlalchemy.orm import Mapped, mapped_column

from models.tables.base import Base


class PuntajeObjetivo(Base):
    __tablename__ = "puntaje_objetivo"

    usuario_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    carrera_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    porc_objetivo: Mapped[float] = mapped_column(Float)
