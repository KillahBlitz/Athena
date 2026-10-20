from sqlalchemy import Integer, Text
from sqlalchemy.orm import Mapped, mapped_column

from models.tables.base import Base


class PreguntaCuestionario(Base):
    __tablename__ = "pregunta_cuestionario"

    pregunta_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    riasec_id: Mapped[int] = mapped_column(Integer)
    texto_pregunta: Mapped[str] = mapped_column(Text)
    pregunta_abierta: Mapped[str] = mapped_column(Text)
