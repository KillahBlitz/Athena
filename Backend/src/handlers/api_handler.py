from collections import defaultdict
import random

from kinasis_library.utils.utils import generate_uuid
from kinasis_library.services.redis_interface import RedisConsumer
from kinasis_library.events.extractor_event import ExtractorEvent, Objetives, RisecAnswer

from utils.set_envs import get_dict_envs_redis_conection
from handlers.query_handler import QueryHandler
from handlers.command_handler import CommandHandler
from models.request.save_user_request import SaveUserRequest
from models.response.questionary_response import QuestionaryResponse


redis_credentials = get_dict_envs_redis_conection()

class ApiHandler:
    def __init__(self):
        self._qh = QueryHandler()
        self._ch = CommandHandler()
        self._rc = RedisConsumer(
            redis_host=redis_credentials["REDIS_HOST"],
            redis_port=redis_credentials["REDIS_PORT"],
            redis_password=redis_credentials["REDIS_PASSWORD"])

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
        objetivos = {o["carrera_id"]: o["pregunta_objetivo"] for o in self._qh.get_objetivos_by_area_id(area_id)}
        return QuestionaryResponse(**area, objetivos=objetivos, preguntas=preguntas)

    def generate_user_event(self, params: SaveUserRequest) -> str:
        user_uuid = generate_uuid()
        mock_user_id = random.randint(1, 1000)
        objetives = [
            Objetives(
                id_objetive=o.id_objetive,
                porc_evaluation=o.puntuation / 5,
                description=o.description,
            )
            for o in params.objetives
        ]
        event = ExtractorEvent(
            user_id=mock_user_id,
            uuid_user=user_uuid,
            area_id=params.area_id,
            objetives=objetives,
            questions=[RisecAnswer(
                risec_id=q.risec_id,
                criteria_list=q.criteria_id_list,
                open_question=q.open_question
            ) for q in params.risec_questions]
        )
        self._rc.event_producer("extractor_stream", event)
        return user_uuid
