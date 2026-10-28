from sqlalchemy import Engine, select

from models.tables.areas import Area
from models.tables.carreras import Carrera
from models.tables.criterios import Criterio
from models.tables.cuestionarios import Cuestionario
from models.tables.pregunta_cuestionario import PreguntaCuestionario

TYPE_PERFIL = 1


class AreasTableRepository:
    def __init__(self, engine: Engine):
        self.engine = engine

    def get_all_areas(self) -> list[dict]:
        query = select(Area.area_id, Area.nom_area)
        with self.engine.connect() as conn:
            filas = conn.execute(query).mappings().all()
        return [dict(fila) for fila in filas]

    def get_area_by_id(self, area_id: int) -> dict | None:
        query = select(Area.area_id, Area.nom_area).where(Area.area_id == area_id)
        with self.engine.connect() as conn:
            fila = conn.execute(query).mappings().first()
        return dict(fila) if fila else None

    def get_questions_by_area_id(self, area_id: int) -> list[dict]:
        query = (
            select(PreguntaCuestionario.riasec_id, PreguntaCuestionario.texto_pregunta,
                   PreguntaCuestionario.pregunta_abierta)
            .join(Cuestionario, Cuestionario.pregunta_id == PreguntaCuestionario.pregunta_id)
            .where(Cuestionario.area_id == area_id)
            .order_by(PreguntaCuestionario.pregunta_id)
        )
        with self.engine.connect() as conn:
            filas = conn.execute(query).mappings().all()
        return [dict(fila) for fila in filas]

    def get_objetivos_by_area_id(self, area_id: int) -> list[dict]:
        query = (
            select(Carrera.carrera_id, Carrera.pregunta_objetivo)
            .where(Carrera.area_id == area_id)
            .order_by(Carrera.carrera_id)
        )
        with self.engine.connect() as conn:
            filas = conn.execute(query).mappings().all()
        return [dict(fila) for fila in filas]

    def get_criterios_by_area_id(self, area_id: int) -> list[dict]:
        query = (
            select(Criterio.criterio_id, Criterio.carrera_id, Criterio.riasec_id, Criterio.resumen_criterio)
            .join(Carrera, Carrera.carrera_id == Criterio.carrera_id)
            .where(Carrera.area_id == area_id, Criterio.type_id == TYPE_PERFIL)
            .order_by(Criterio.riasec_id, Criterio.criterio_id)
        )
        with self.engine.connect() as conn:
            filas = conn.execute(query).mappings().all()
        return [dict(fila) for fila in filas]

    def get_criteria_order_by_id_riasec(self, area_id: int) -> list[dict]:
        query = (
            select(Criterio.criterio_id, Criterio.riasec_id, Criterio.carrera_id, Criterio.resumen_criterio)
            .join(Carrera, Carrera.carrera_id == Criterio.carrera_id)
            .where(Carrera.area_id == area_id)
            .order_by(Criterio.riasec_id, Criterio.criterio_id)
        )
        with self.engine.connect() as conn:
            filas = conn.execute(query).mappings().all()
        return [dict(fila) for fila in filas]

    def get_main_criteria_by_area(self, area_id: int) -> list[dict]:
        query = (
            select(Criterio.criterio_id, Criterio.carrera_id)
            .join(Carrera, Carrera.carrera_id == Criterio.carrera_id)
            .where(Carrera.area_id == area_id, Criterio.riasec_id == 0)
            .order_by(Criterio.carrera_id)
        )
        with self.engine.connect() as conn:
            filas = conn.execute(query).mappings().all()
        return [dict(fila) for fila in filas]
