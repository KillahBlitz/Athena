from copy import deepcopy
from unittest.mock import Mock, call

import pytest
from kinasis_library.events.extractor_event import ExtractorEvent
from sqlalchemy import create_engine, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

import handlers.command_handler as command_handler_module
from handlers.extraction_handler import ExtractorHandler
from models.tables.puntaje_objetivo import PuntajeObjetivo
from models.tables.usuario import Usuario
from models.tables.usuario_criterio import UsuarioCriterio


@pytest.fixture
def handler():
    commands = Mock(spec=[
        "save_objetive_user", "save_objetive_criteria", "save_user_criteria", "update_user_status",
    ])
    return ExtractorHandler(qh=object(), ch=commands)


@pytest.fixture
def event():
    return ExtractorEvent(
        user_id=42, uuid_user="USER-persistence", area_id=3,
        objetives=[
            {"id_objetive": 7, "id_carrera": 10, "porc_evaluation": 0.8, "description": "Objetivo"},
        ],
        questions={},
    )


@pytest.fixture
def database_commands(monkeypatch, tmp_path):
    engine = create_engine(f"sqlite:///{tmp_path / 'extraction.db'}")
    for model in (Usuario, PuntajeObjetivo, UsuarioCriterio):
        model.__table__.create(engine)
    monkeypatch.setattr(command_handler_module, "create_postgres_engine", lambda *args: engine)
    commands = command_handler_module.CommandHandler()
    try:
        for user_id, user_uuid in ((42, "USER-persistence"), (43, "USER-other")):
            commands.insert_user(Usuario(
                usuario_id=user_id, uuid_usuario=user_uuid, area_id=3,
                nombre_usuario="Prueba", correo_usuario="test@example.com", estatus_id=1, type_user=4,
            ))
        yield commands
    finally:
        engine.dispose()


@pytest.mark.parametrize(("repeat", "expected_count"), [(False, 1), (True, 2)])
def test_save_result_normalizes_scores_and_saves_overlapping_criteria_once(handler, event, repeat, expected_count):
    prompt = {
        "part_0": [{"criteria_id": 101}],
        "part_1": {"criteria": {201: "A", 202: "B", 203: "C"}, "priority_criteria": {201: "A", 202: "B"}},
    }
    response = {"answers": [
        {"name": "part_0:101:coincidence", "type": "score", "score": 4.25},
        {"name": "part_1:201:coincidence", "type": "score", "score": 4},
        {"name": "part_1:202:coincidence", "type": "score", "score": 0},
        {"name": "part_1:203:coincidence", "type": "score", "score": 5},
        {"name": "part_1:201:repeat", "type": "choice", "choice": "true" if repeat else "false"},
        {"name": "part_1:202:repeat", "type": "choice", "choice": "false"},
    ]}
    result = handler.format_jev_response(prompt, response)
    original_result = deepcopy(result)
    original_event = event.model_dump()

    handler.save_result_to_db(result, event)

    handler._ch.save_objetive_user.assert_called_once_with(score=0.8, user_id=42, career_id=10)
    handler._ch.save_objetive_criteria.assert_called_once_with(user_id=42, criteria_id=101, coincidence=0.85)
    assert handler._ch.save_user_criteria.call_args_list == [
        call(user_id=42, criteria_id=201, coincidence=0.8, repeat_count=expected_count),
        call(user_id=42, criteria_id=202, coincidence=0.0, repeat_count=1),
        call(user_id=42, criteria_id=203, coincidence=1.0, repeat_count=1),
    ]
    handler._ch.update_user_status.assert_called_once_with(event.uuid_user, 2)
    assert handler._ch.mock_calls[-1] == call.update_user_status(event.uuid_user, 2)
    assert result == original_result
    assert event.model_dump() == original_event


@pytest.mark.parametrize("failing_command", ["save_objetive_user", "save_objetive_criteria", "save_user_criteria"])
def test_save_result_does_not_mark_extraction_complete_after_write_failure(handler, event, failing_command):
    result = {
        "objetives_criteria": [{"criteria_id": 101, "coincidence": 85}],
        "priority_criteria": [{"criteria_id": 201, "coincidence": 80, "repeat": True}],
        "criterias": [],
    }
    getattr(handler._ch, failing_command).side_effect = RuntimeError("Error de escritura")

    with pytest.raises(RuntimeError, match="Error de escritura"):
        handler.save_result_to_db(result, event)

    handler._ch.update_user_status.assert_not_called()


def test_save_result_persists_through_command_handler_and_repositories(database_commands, event):
    handler = ExtractorHandler(qh=object(), ch=database_commands)
    result = {
        "objetives_criteria": [{"criteria_id": 101, "coincidence": 85}, {"criteria_id": 102, "coincidence": 0}],
        "priority_criteria": [
            {"criteria_id": 201, "coincidence": 80, "repeat": True},
            {"criteria_id": 202, "coincidence": 0, "repeat": False},
        ],
        "criterias": [{"criteria_id": 201, "coincidence": 80}, {"criteria_id": 203, "coincidence": 100}],
    }

    handler.save_result_to_db(result, event)

    with Session(database_commands.engine) as session:
        score = session.scalars(select(PuntajeObjetivo)).one()
        assert (score.usuario_id, score.carrera_id, score.porc_objetivo) == (42, 10, 0.8)
        rows = session.scalars(select(UsuarioCriterio).order_by(UsuarioCriterio.criterio_id)).all()
        assert [(row.usuario_id, row.criterio_id, row.repeticiones, row.porc_coincidencia) for row in rows] == [
            (42, 101, 1, 0.85),
            (42, 102, 0, 0.0),
            (42, 201, 2, 0.8),
            (42, 202, 1, 0.0),
            (42, 203, 1, 1.0),
        ]
        assert session.get(Usuario, 42).estatus_id == 2
        assert session.get(Usuario, 43).estatus_id == 1


def test_objective_repository_rolls_back_duplicate_and_can_insert_again(database_commands):
    database_commands.save_objetive_user(score=0.8, user_id=42, career_id=10)

    with pytest.raises(IntegrityError):
        database_commands.save_objetive_user(score=0.6, user_id=42, career_id=10)

    database_commands.save_objetive_user(score=0.4, user_id=42, career_id=20)
    with Session(database_commands.engine) as session:
        rows = session.scalars(select(PuntajeObjetivo).order_by(PuntajeObjetivo.carrera_id)).all()
        assert [(row.carrera_id, row.porc_objetivo) for row in rows] == [(10, 0.8), (20, 0.4)]


def test_criteria_repository_rolls_back_duplicate_and_can_insert_again(database_commands):
    database_commands.save_user_criteria(user_id=42, criteria_id=201, coincidence=0.8, repeat_count=2)

    with pytest.raises(IntegrityError):
        database_commands.save_user_criteria(user_id=42, criteria_id=201, coincidence=0.6, repeat_count=2)

    database_commands.save_user_criteria(user_id=42, criteria_id=202, coincidence=0.4, repeat_count=1)
    with Session(database_commands.engine) as session:
        rows = session.scalars(select(UsuarioCriterio).order_by(UsuarioCriterio.criterio_id)).all()
        assert [(row.criterio_id, row.repeticiones, row.porc_coincidencia) for row in rows] == [
            (201, 2, 0.8), (202, 1, 0.4),
        ]


def test_update_status_with_unknown_uuid_preserves_other_users(database_commands):
    database_commands.update_user_status("USER-missing", 2)

    with Session(database_commands.engine) as session:
        assert list(session.scalars(select(Usuario.estatus_id))) == [1, 1]
