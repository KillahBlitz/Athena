from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from models.tables.base import Base


class Area(Base):
    __tablename__ = "areas"

    area_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    nom_area: Mapped[str] = mapped_column(String(200))
