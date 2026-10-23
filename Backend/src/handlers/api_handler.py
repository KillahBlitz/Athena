from collections import defaultdict

from kinasis_library.events.extractor_event import ExtractorEvent
from handlers.query_handler import QueryHandler
from handlers.command_handler import CommandHandler
from models.request.save_user_request import SaveUserRequest
from models.response.questionary_response import QuestionaryResponse

class ApiHandler:
    def __init__(self):
        self._qh = QueryHandler()
        self._ch = CommandHandler()

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

    def generate_user_event(self, params: SaveUserRequest):
        pass