from sqlalchemy import Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from models.tables.base import Base


class Criterio(Base):
    __tablename__ = "criterios"

    criterio_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    carrera_id: Mapped[int] = mapped_column(Integer)
    type_id: Mapped[int] = mapped_column(Integer)
    riasec_id: Mapped[int] = mapped_column(Integer)
    desc_criterio: Mapped[str] = mapped_column(Text)
    resumen_criterio: Mapped[str] = mapped_column(String(100))
    type_extraction: Mapped[str | None] = mapped_column(Text)
