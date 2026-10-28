from collections import defaultdict

from kinasis_library.utils.utils import generate_uuid
from kinasis_library.services.redis_interface import RedisConsumer
from kinasis_library.events.extractor_event import ExtractorEvent, Objetives, RisecAnswer

from utils.set_envs import get_dict_envs_redis_conection
from handlers.query_handler import QueryHandler
from handlers.command_handler import CommandHandler
from models.tables.usuario import Usuario
from models.request.save_user_request import SaveUserRequest
from models.response.questionary_response import QuestionaryResponse
from models.response.result_response import ResultResponse, Results


redis_credentials = get_dict_envs_redis_conection()

class ApiHandler:
    def __init__(self):
        self._qh = QueryHandler()
        self._ch = CommandHandler()
        self._rc = RedisConsumer(
            redis_host=redis_credentials["REDIS_HOST"],
            redis_port=redis_credentials["REDIS_PORT"],
            redis_password=redis_credentials["REDIS_PASSWORD"])

    def _submit_user_in_db(self, data: SaveUserRequest) -> tuple[int, str]:
        user_uuid = generate_uuid()
        user = Usuario(
            uuid_usuario=user_uuid,
            area_id=data.area_id,
            nombre_usuario=data.username,
            correo_usuario=data.email,
            estatus_id=1,
            type_user=4
        )
        user_id = self._ch.insert_user(user)
        return user_id, user_uuid

    def get_areas(self):
        return self._qh.get_areas()

    def get_area_data(self, area_id: int) -> QuestionaryResponse | None:
        area = self._qh.get_area_by_id(area_id)
        if area is None:
            return None
        opciones = defaultdict(dict)
        for criterio in self._qh.get_criterios_by_area_id(area_id):
            opciones[criterio["riasec_id"]][criterio["criterio_id"]] = criterio["resumen_criterio"]
        preguntas = [{**pregunta, "opciones": opciones[pregunta["riasec_id"]]}
                     for pregunta in self._qh.get_questions_by_area_id(area_id)]
        objetivos = [
            {
                "id_carrera": o["carrera_id"],
                "id_objetivo": o["carrera_id"],
                "pregunta": o["pregunta_objetivo"],
            }
            for o in self._qh.get_objetivos_by_area_id(area_id)
        ]
        return QuestionaryResponse(**area, objetivos=objetivos, preguntas=preguntas)

    def generate_user_event(self, params: SaveUserRequest) -> str:
        user_id, user_uuid = self._submit_user_in_db(params)
        
        objetives = [
            Objetives(
                id_objetive=o.id_objetive,
                id_carrera=o.id_carrera,
                porc_evaluation=o.puntuation / 5,
                description=o.description)
            for o in params.objetives]

        anwsers = {
            a.risec_id: RisecAnswer(
                criteria_list=a.criteria_list,
                open_question=a.open_question)
            for a in params.risec_questions.values()}

        event = ExtractorEvent(
            user_id=user_id,
            uuid_user=user_uuid,
            area_id=params.area_id,
            objetives=objetives,
            questions=anwsers
        )
        self._rc.event_producer("extractor_stream", event)
        return user_uuid

    def get_results(self, user_uuid: str):
        user = self._qh.get_user_by_uuid(user_uuid)
        if user is None:
            return None
        response = ResultResponse(
            user_uuid=user_uuid,
            status_id=user.estatus_id)
        return response