from sqlalchemy import Float, Integer
from sqlalchemy.orm import Mapped, mapped_column

from models.tables.base import Base


class Resultado(Base):
    __tablename__ = "resultados"

    id_resultado: Mapped[int] = mapped_column(Integer, primary_key=True)
    usuario_id: Mapped[int] = mapped_column(Integer)
    carrera_id: Mapped[int] = mapped_column(Integer)
    porc_coincidencia: Mapped[float] = mapped_column(Float)
