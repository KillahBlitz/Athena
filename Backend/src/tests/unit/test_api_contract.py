import json
from pathlib import Path

import fastapi
import pytest

import handlers.api_handler as api_handler_module
import main.endpoints as endpoints
from models.response.questionary_response import QuestionaryResponse

SAMPLE_PATH = Path(__file__).resolve().parent.parent / "fixtures" / "questionary_response.sample.json"


def load_sample() -> dict:
    return json.loads(SAMPLE_PATH.read_text(encoding="utf-8"))


class FakeQueryHandler:
    def __init__(self):
        sample = load_sample()
        self._area = {"area_id": sample["area_id"], "nom_area": sample["nom_area"]}
        self._questions = [
            {key: pregunta[key] for key in ("riasec_id", "texto_pregunta", "pregunta_abierta")}
            for pregunta in sample["preguntas"]
        ]
        self._criterios = [
            {"criterio_id": int(criterio_id), "riasec_id": pregunta["riasec_id"], "resumen_criterio": texto}
            for pregunta in sample["preguntas"]
            for criterio_id, texto in pregunta["opciones"].items()
        ]
        self._objetivos = [
            {"carrera_id": int(carrera_id), "pregunta_objetivo": texto}
            for carrera_id, texto in sample["objetivos"].items()
        ]

    def get_areas(self):
        return [self._area]

    def get_area_by_id(self, area_id: int):
        return self._area if area_id == self._area["area_id"] else None

    def get_questions_by_area_id(self, area_id: int):
        return self._questions

    def get_objetivos_by_area_id(self, area_id: int):
        return self._objetivos

    def get_criterios_by_area_id(self, area_id: int):
        return self._criterios


@pytest.fixture
def fake_api_handler(monkeypatch):
    monkeypatch.setattr(api_handler_module, "QueryHandler", FakeQueryHandler)
    monkeypatch.setattr(api_handler_module, "CommandHandler", lambda: None)
    handler = api_handler_module.ApiHandler()
    monkeypatch.setattr(endpoints, "ah", handler)
    return handler


def test_sample_matches_questionary_response_schema():
    sample = load_sample()

    parsed = QuestionaryResponse.model_validate(sample)

    assert parsed.model_dump(mode="json") == sample


def test_get_area_data_serializes_exactly_as_contract_sample(fake_api_handler):
    response = endpoints.get_area_data(load_sample()["area_id"])

    assert isinstance(response, QuestionaryResponse)
    assert response.model_dump(mode="json") == load_sample()


def test_get_area_data_returns_404_for_unknown_area(fake_api_handler):
    with pytest.raises(fastapi.HTTPException) as error:
        endpoints.get_area_data(999)

    assert error.value.status_code == 404


def test_get_areas_returns_id_and_name_per_area(fake_api_handler):
    areas = endpoints.get_areas()

    assert areas == [{"area_id": 1, "nom_area": "Ciencias Físico Matemáticas"}]
    assert all(isinstance(a["area_id"], int) and isinstance(a["nom_area"], str) for a in areas)
