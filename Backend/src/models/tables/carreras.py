from sqlalchemy import Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from models.tables.base import Base


class Carrera(Base):
    __tablename__ = "carreras"

    carrera_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    area_id: Mapped[int] = mapped_column(Integer)
    nom_carrera: Mapped[str] = mapped_column(String(200))
    origina_objetivo: Mapped[str] = mapped_column(Text)
    objetivo: Mapped[str] = mapped_column(Text)
    pregunta_objetivo: Mapped[str | None] = mapped_column(String(200))
