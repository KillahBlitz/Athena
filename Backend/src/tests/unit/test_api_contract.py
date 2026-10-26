import asyncio
import json
from pathlib import Path

import fastapi
import pytest
from sqlalchemy import create_engine, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

import handlers.api_handler as api_handler_module
import handlers.command_handler as command_handler_module
import main.endpoints as endpoints
from models.request.save_user_request import SaveUserRequest
from models.response.questionary_response import QuestionaryResponse
from models.tables.usuario import Usuario

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
            {"carrera_id": objetivo["id_carrera"], "pregunta_objetivo": objetivo["pregunta"]}
            for objetivo in sample["objetivos"]
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


class FakeRedisConsumer:
    def __init__(self, **kwargs):
        self.events = []

    def event_producer(self, stream_name, event):
        self.events.append((stream_name, event))


@pytest.fixture
def fake_api_handler(monkeypatch, tmp_path):
    engine = create_engine(f"sqlite:///{tmp_path / 'usuarios.db'}")
    Usuario.__table__.create(engine)
    monkeypatch.setattr(api_handler_module, "QueryHandler", FakeQueryHandler)
    monkeypatch.setattr(command_handler_module, "create_postgres_engine", lambda *args: engine)
    monkeypatch.setattr(api_handler_module, "RedisConsumer", FakeRedisConsumer)
    handler = api_handler_module.ApiHandler()
    monkeypatch.setattr(endpoints, "ah", handler)
    try:
        yield handler
    finally:
        engine.dispose()


@pytest.fixture
def save_user_payload():
    return SaveUserRequest(
        username="Usuario de prueba",
        email="test@example.com",
        age=20,
        area_id=1,
        objetives=[
            {"id_objetive": 101, "id_carrera": 201, "puntuation": 1, "description": "Poco interés"},
            {"id_objetive": 102, "id_carrera": 202, "puntuation": 3, "description": "Interés moderado"},
            {"id_objetive": 103, "id_carrera": 203, "puntuation": 5, "description": "Mucho interés"},
        ],
        risec_questions={
            1: {"risec_id": 1, "criteria_list": [{11: "Reparar"}, {12: "Herramientas"}], "open_question": "Reparo aparatos"},
            2: {"risec_id": 2, "criteria_list": [{21: "Investigar"}], "open_question": "Investigo problemas"},
        },
    )


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


def test_generate_user_event_maps_answers_without_mutating_request(fake_api_handler, save_user_payload):
    original = save_user_payload.model_dump()

    user_uuid = fake_api_handler.generate_user_event(save_user_payload)

    assert save_user_payload.model_dump() == original
    assert len(fake_api_handler._rc.events) == 1
    stream_name, event = fake_api_handler._rc.events[0]
    assert stream_name == "extractor_stream"
    assert event.uuid_user == user_uuid
    assert event.area_id == 1
    with Session(fake_api_handler._ch.engine) as session:
        user = session.scalars(select(Usuario)).one()
        assert user.usuario_id == event.user_id
        assert user.uuid_usuario == user_uuid
        assert user.area_id == save_user_payload.area_id
        assert user.nombre_usuario == save_user_payload.username
        assert user.correo_usuario == save_user_payload.email
        assert user.estatus_id == 1
        assert user.type_user == 4
    assert [objective.model_dump() for objective in event.objetives] == [
        {"id_objetive": 101, "id_carrera": 201, "porc_evaluation": 0.2, "description": "Poco interés"},
        {"id_objetive": 102, "id_carrera": 202, "porc_evaluation": 0.6, "description": "Interés moderado"},
        {"id_objetive": 103, "id_carrera": 203, "porc_evaluation": 1.0, "description": "Mucho interés"},
    ]
    assert {key: question.model_dump() for key, question in event.questions.items()} == {
        1: {"criteria_list": [{11: "Reparar"}, {12: "Herramientas"}], "open_question": "Reparo aparatos"},
        2: {"criteria_list": [{21: "Investigar"}], "open_question": "Investigo problemas"},
    }


def test_generate_user_event_does_not_publish_when_insert_fails(
    fake_api_handler, save_user_payload, monkeypatch
):
    monkeypatch.setattr(api_handler_module, "generate_uuid", lambda: "USER-duplicate")
    fake_api_handler.generate_user_event(save_user_payload)

    with pytest.raises(IntegrityError):
        fake_api_handler.generate_user_event(save_user_payload)

    assert len(fake_api_handler._rc.events) == 1
    with Session(fake_api_handler._ch.engine) as session:
        assert list(session.scalars(select(Usuario.uuid_usuario))) == ["USER-duplicate"]

    monkeypatch.setattr(api_handler_module, "generate_uuid", lambda: "USER-after-failure")
    assert fake_api_handler.generate_user_event(save_user_payload) == "USER-after-failure"
    assert len(fake_api_handler._rc.events) == 2
    assert fake_api_handler._rc.events[0][1].user_id != fake_api_handler._rc.events[1][1].user_id


def test_save_user_returns_http_200_with_user_uuid(fake_api_handler, save_user_payload):
    body = save_user_payload.model_dump_json().encode()
    messages = []
    scope = {
        "type": "http",
        "asgi": {"version": "3.0"},
        "http_version": "1.1",
        "method": "POST",
        "scheme": "http",
        "path": "/save-user",
        "raw_path": b"/save-user",
        "query_string": b"",
        "root_path": "",
        "headers": [(b"content-type", b"application/json")],
        "client": ("127.0.0.1", 12345),
        "server": ("testserver", 80),
    }

    async def receive():
        return {"type": "http.request", "body": body, "more_body": False}

    async def send(message):
        messages.append(message)

    asyncio.run(endpoints.api(scope, receive, send))

    response = next(message for message in messages if message["type"] == "http.response.start")
    response_body = b"".join(message.get("body", b"") for message in messages
                             if message["type"] == "http.response.body")
    assert response["status"] == 200
    assert len(fake_api_handler._rc.events) == 1
    assert json.loads(response_body) == fake_api_handler._rc.events[0][1].uuid_user
    assert [objective.id_carrera for objective in fake_api_handler._rc.events[0][1].objetives] == [201, 202, 203]
