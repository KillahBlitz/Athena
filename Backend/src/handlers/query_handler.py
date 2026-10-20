from kinasis_library.services.postgre_interface import create_postgres_engine
from models.repository.usuarios_table_repository import UsuariosTableRepository
from models.repository.carreras_table_repository import CarrerasTableRepository
from models.repository.puntaje_objetivo_table_repository import PuntajeObjetivoTableRepository
from models.repository.usuario_criterio_table_repository import UsuarioCriterioTableRepository
from models.repository.resultados_table_repository import ResultadosTableRepository
from models.repository.areas_table_repository import AreasTableRepository
from utils.set_envs import get_dict_envs_db_conection

DB_INFO = get_dict_envs_db_conection()

class QueryHandler:
    def __init__(self):
        self.engine = create_postgres_engine(DB_INFO["DB_HOST"], DB_INFO["DB_PORT"],
                                             DB_INFO["DB_USER"], DB_INFO["DB_PASSWORD"],
                                             DB_INFO["DB_NAME"])
        self._usuarios_table_repository = UsuariosTableRepository(self.engine)
        self._carreras_table_repository = CarrerasTableRepository(self.engine)
        self._puntaje_objetivo_table_repository = PuntajeObjetivoTableRepository(self.engine)
        self._usuario_criterio_table_repository = UsuarioCriterioTableRepository(self.engine)
        self._resultados_table_repository = ResultadosTableRepository(self.engine)
        self._areas_table_repository = AreasTableRepository(self.engine)

    def get_users(self, area_id: int):
        return self._usuarios_table_repository.get_users_by_area_id(area_id)

    def get_users_by_type(self, area_id: int, type_users: list[int]):
        return self._usuarios_table_repository.get_users_by_area_and_type(area_id, type_users)

    def get_carrera_ids(self, area_id: int):
        return self._carreras_table_repository.get_carrera_ids(area_id)

    def get_puntaje_objetivo(self, area_id: int, type_users: list[int]):
        return self._puntaje_objetivo_table_repository.get_by_area(area_id, type_users)

    def get_usuario_criterio(self, area_id: int, type_users: list[int]):
        return self._usuario_criterio_table_repository.get_by_area(area_id, type_users)

    def get_resultados(self, area_id: int, type_users: list[int]):
        return self._resultados_table_repository.get_by_area(area_id, type_users)

    def get_areas(self):
        return self._areas_table_repository.get_all_areas()

    def get_area_by_id(self, area_id: int):
        return self._areas_table_repository.get_area_by_id(area_id)

    def get_questions_by_area_id(self, area_id: int):
        return self._areas_table_repository.get_questions_by_area_id(area_id)

    def get_objetivos_by_area_id(self, area_id: int):
        return self._areas_table_repository.get_objetivos_by_area_id(area_id)

    def get_criterios_by_area_id(self, area_id: int):
        return self._areas_table_repository.get_criterios_by_area_id(area_id)