from kinasis_library.services.postgre_interface import create_postgres_engine

from models.repository.puntaje_objetivo_table_repository import PuntajeObjetivoTableRepository
from models.repository.usuario_criterio_table_repository import UsuarioCriterioTableRepository
from models.repository.usuarios_table_repository import UsuariosTableRepository
from models.tables.puntaje_objetivo import PuntajeObjetivo
from models.tables.usuario import Usuario
from models.tables.usuario_criterio import UsuarioCriterio
from utils.set_envs import get_dict_envs_db_conection

DB_INFO = get_dict_envs_db_conection()

class CommandHandler:
    def __init__(self):
        self.engine = create_postgres_engine(DB_INFO["DB_HOST"], DB_INFO["DB_PORT"],
                                             DB_INFO["DB_USER"], DB_INFO["DB_PASSWORD"],
                                             DB_INFO["DB_NAME"])
        self._usuarios_table_repository = UsuariosTableRepository(self.engine)
        self._puntaje_objetivo_table_repository = PuntajeObjetivoTableRepository(self.engine)
        self._usuario_criterio_table_repository = UsuarioCriterioTableRepository(self.engine)

    def insert_user(self, user: Usuario) -> int:
        return self._usuarios_table_repository.insert_user(user)

    def save_objetive_user(self, score: float, user_id: int, career_id: int) -> None:
        objective = PuntajeObjetivo(
            usuario_id=user_id,
            carrera_id=career_id,
            porc_objetivo=score,
        )
        self._puntaje_objetivo_table_repository.insert_score(objective)

    def save_objetive_criteria(self, user_id: int, criteria_id: int, coincidence: float) -> None:
        self.save_user_criteria(user_id, criteria_id, coincidence, int(coincidence > 0))

    def save_user_criteria(self, user_id: int, criteria_id: int, coincidence: float, repeat_count: int) -> None:
        criterion = UsuarioCriterio(
            usuario_id=user_id,
            criterio_id=criteria_id,
            porc_coincidencia=coincidence,
            repeticiones=repeat_count,
        )
        self._usuario_criterio_table_repository.insert_user_criteria(criterion)

    def update_user_status(self, user_uuid: str, status_id: int) -> None:
        self._usuarios_table_repository.update_user_status(user_uuid, status_id)
