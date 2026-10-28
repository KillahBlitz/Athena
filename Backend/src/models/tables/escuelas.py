from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from models.tables.base import Base


class Escuela(Base):
    __tablename__ = "escuelas"

    escuela_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    nom_escuela: Mapped[str] = mapped_column(String(200))


class EscuelaCarrera(Base):
    __tablename__ = "escuela_carrera"

    id_escuela: Mapped[int] = mapped_column(Integer, primary_key=True)
    id_carrera: Mapped[int] = mapped_column(Integer, primary_key=True)
