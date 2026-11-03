from sqlalchemy import Integer
from sqlalchemy.orm import Mapped, mapped_column

from models.tables.base import Base


class Cuestionario(Base):
    __tablename__ = "cuestionarios"

    area_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    pregunta_id: Mapped[int] = mapped_column(Integer, primary_key=True)
