import json
from unittest.mock import Mock, call

import httpx2
import pytest
from kinasis_library.events.classifier_event import ClassifierEvent
from kinasis_library.events.extractor_event import ExtractorEvent
from sqlalchemy import create_engine

import handlers.extraction_handler as extraction_module
from handlers.command_handler import CommandHandler
from handlers.query_handler import QueryHandler
from models.repository.areas_table_repository import AreasTableRepository
from models.tables.carreras import Carrera
from models.tables.criterios import Criterio
import service.jev as jev_module
import tasks.extractor_event_handler as worker_module


def test_rag_returns_objective_description_with_matching_area_criteria():
    engine = create_engine("sqlite://")
    Carrera.__table__.create(engine)
    Criterio.__table__.create(engine)
    with engine.begin() as conn:
        conn.execute(Carrera.__table__.insert(), [
            {"carrera_id": career, "area_id": area, "nom_carrera": "Carrera de prueba",
             "origina_objetivo": "Prueba", "objetivo": "Objetivo de prueba"}
            for career, area in [(42, 3), (43, 3), (99, 4)]
        ])
        conn.execute(Criterio.__table__.insert(), [
            {"criterio_id": criterion, "carrera_id": career, "type_id": kind,
             "riasec_id": dimension, "desc_criterio": "Criterio de prueba",
             "resumen_criterio": f"Criterio {criterion}"}
            for criterion, career, kind, dimension in [
                (101, 42, 2, 0), (102, 43, 2, 0), (103, 99, 2, 0), (201, 42, 1, 1)
            ]
        ])
    repository = AreasTableRepository(engine)
    query_handler = QueryHandler.__new__(QueryHandler)
    query_handler._areas_table_repository = repository
    handler = extraction_module.ExtractorHandler(qh=query_handler, ch=object())
    event = ExtractorEvent(
        user_id=1, uuid_user="USER-test-description", area_id=3,
        objetives=[
            {"id_objetive": 7, "id_carrera": 42, "porc_evaluation": 0.8,
             "description": "Me interesa construir robots"},
            {"id_objetive": 8, "id_carrera": 43, "porc_evaluation": 0.4, "description": ""},
            {"id_objetive": 9, "id_carrera": 99, "porc_evaluation": 0.8,
             "description": "Objetivo de otra área"},
        ],
        questions={key: {"criteria_list": [], "open_question": "Respuesta de prueba"}
                   for key in (1, 2, 4, 5, 6)},
    )
    try:
        saved = handler.get_info_prompt(event)
        assert saved["part_0"] == [{
            "criteria_id": 101, "criteria": "Criterio 101",
            "description": "Me interesa construir robots",
        }]
        assert saved["part_1"]["criteria"] == {201: "Criterio 201"}
        # The HTTP questionnaire continues to receive profile criteria only.
        assert [row["criterio_id"] for row in repository.get_criterios_by_area_id(3)] == [201]
    finally:
        engine.dispose()


def test_event_prompt_and_sdk_request_preserve_criteria_and_output(monkeypatch, tmp_path):
    class Query:
        def get_criteria_order_by_id_riasec(self, area_id):
            assert area_id == 3
            return [
                {"criterio_id": key, "carrera_id": 42, "riasec_id": dimension,
                 "resumen_criterio": f"Criterio {key}"}
                for key, dimension in [(101, 0), (201, 1), (202, 1), (203, 1)]
            ]

        def get_main_criteria_by_area(self, area_id):
            assert area_id == 3
            return [{"carrera_id": 42, "criterio_id": 101}]

    event = ExtractorEvent(
        user_id=1, uuid_user="USER-test-sdk", area_id=3,
        objetives=[{"id_objetive": 7, "id_carrera": 42, "porc_evaluation": 0.8,
                    "description": "Descripción del evento"}],
        questions={key: {"criteria_list": [{202: "Criterio 202"}, {201: "Criterio 201"}] if key == 1 else [],
                         "open_question": f"Respuesta dimensión {key}"} for key in (1, 2, 4, 5, 6)},
    )
    commands = Mock(spec=CommandHandler)
    handler = worker_module.ExtractorEventHandler(qh=Query(), ch=commands)
    monkeypatch.setattr(extraction_module, "__file__", str(tmp_path / "src" / "handlers" / "extraction_handler.py"))
    handler._eh._prompt = {
        "prompt_objetivo_coincidence": "Reglas de objetivos del diccionario (idx {idx})",
        "prompt_dimension_coincidence": "Reglas de dimensiones del diccionario ({part_key}, {criterio_id})",
        "prompt_dimension_repeat": "Reglas de repetición ({part_key}, {criterio_id})",
    }
    requests = []

    def respond(request):
        requests.append(request)
        assert str(request.url) == "https://ai-gateway.vercel.sh/v1/decisions"
        assert request.headers["authorization"] == "Bearer test-key"
        payload = json.loads(request.content)
        assert payload["model"] == "typesafe-ai/jev"
        context = json.loads(payload["input"])
        assert context["part_0"][0]["description"] == "Descripción del evento"
        assert context["part_1"]["open_question"] == "Respuesta dimensión 1"
        assert context["part_1"]["priority_criteria"] == {"202": "Criterio 202", "201": "Criterio 201"}
        questions = {question["name"]: question for question in payload["questions"]}
        assert set(questions) == {
            "part_0:101:coincidence", "part_1:201:coincidence", "part_1:202:coincidence",
            "part_1:203:coincidence", "part_1:201:repeat", "part_1:202:repeat",
        }
        assert "Reglas de objetivos del diccionario (idx 0)" in questions["part_0:101:coincidence"]["instructions"]
        assert "Reglas de dimensiones del diccionario (part_1, 201)" in questions["part_1:201:coincidence"]["instructions"]
        assert "Reglas de repetición (part_1, 201)" in questions["part_1:201:repeat"]["instructions"]
        assert [level["label"] for level in questions["part_1:201:coincidence"]["levels"]] == ["0", "20", "40", "60", "80", "100"]
        assert questions["part_1:201:repeat"]["choices"] == [{"value": "true", "label": "true"},
                                                              {"value": "false", "label": "false"}]
        scores = {"part_0:101:coincidence": 2.5, "part_1:201:coincidence": 4,
                  "part_1:202:coincidence": 0, "part_1:203:coincidence": 3}
        answers = [
            {"name": name, "type": "score", "score": score, "confidence": 1, "probabilities": []}
            for name, score in scores.items()
        ] + [
            {"name": f"part_1:{key}:repeat", "type": "choice", "choice": "true",
             "confidence": 1, "probabilities": []} for key in (201, 202)
        ]
        return httpx2.Response(200, json={"model": "typesafe-ai/jev", "answers": answers,
                                        "usage": {"input_tokens": 100, "output_tokens": 0, "total_tokens": 100}})

    real_client_cls = httpx2.Client

    def client(**kwargs):
        return real_client_cls(**{**kwargs, "transport": httpx2.MockTransport(respond)})

    monkeypatch.setattr(jev_module.httpx2, "Client", client)
    result = handler.extractor_task(event, {"VERCEL_API_KEY": "test-key",
                                           "VERCEL_API_URL": "https://ai-gateway.vercel.sh/v1",
                                           "VERCEL_MODEL": "typesafe-ai/jev"})
    assert len(requests) == 1
    # extractor_task devuelve el evento para el clasificador, no el resultado de la extracción.
    assert result == ClassifierEvent(user_uuid="USER-test-sdk", user_id=1, id_area=3)
    # El resultado de JEV se guarda en la BD a través del CommandHandler.
    assert commands.mock_calls == [
        call.save_objetive_user(score=0.8, user_id=1, career_id=42),
        call.save_objetive_criteria(user_id=1, criteria_id=101, coincidence=0.5),
        # Criterios elegidos por el usuario: coincidencia 1.0; repeticiones 2 porque JEV respondió "true".
        call.save_user_criteria(user_id=1, criteria_id=202, coincidence=1.0, repeat_count=2),
        call.save_user_criteria(user_id=1, criteria_id=201, coincidence=1.0, repeat_count=2),
        # Detectado por JEV con 60 % sin que el usuario lo eligiera; el 201 no se repite.
        call.save_user_criteria(user_id=1, criteria_id=203, coincidence=0.6, repeat_count=1),
        call.update_user_status("USER-test-sdk", 2),
    ]


@pytest.mark.parametrize("answer", [
    {"type": "refusal"}, {"type": "score", "score": 6}, {"type": "score", "score": float("nan")},
])
def test_invalid_decision_is_not_converted_to_zero(answer):
    handler = extraction_module.ExtractorHandler(qh=object(), ch=object())
    with pytest.raises(ValueError):
        handler.format_jev_response(
            {"part_0": [{"criteria_id": 101}]},
            {"answers": [{"name": "part_0:101:coincidence", **answer}]},
        )
