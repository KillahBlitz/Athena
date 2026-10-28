from unittest.mock import Mock

import pytest
from sqlalchemy import create_engine

import handlers.query_handler as query_handler_module
from models.tables.criterios import Criterio
from models.tables.puntaje_objetivo import PuntajeObjetivo
from models.tables.usuario import Usuario
from models.tables.usuario_criterio import UsuarioCriterio
from models.trainee_data import PuntajeObjetivoPieza, UsuarioCriterioPieza, UsuariosPieza
from tasks.classifier_event_handler import ClassifierEventHandler

REAL_USER, TRAINING_USER = 42, 7


@pytest.fixture
def query_handler(monkeypatch, tmp_path):
    engine = create_engine(f"sqlite:///{tmp_path / 'user_data.db'}")
    for model in (Usuario, PuntajeObjetivo, UsuarioCriterio, Criterio):
        model.__table__.create(engine)
    monkeypatch.setattr(query_handler_module, "create_postgres_engine", lambda *args: engine)

    def criterio(criterio_id, carrera_id, type_id, riasec_id):
        return {"criterio_id": criterio_id, "carrera_id": carrera_id, "type_id": type_id, "riasec_id": riasec_id,
                "desc_criterio": "desc", "resumen_criterio": "resumen"}

    with engine.begin() as conn:
        conn.execute(Usuario.__table__.insert(), [
            {"usuario_id": REAL_USER, "uuid_usuario": "USER-real", "area_id": 3, "nombre_usuario": "Real",
             "correo_usuario": "real@example.com", "estatus_id": 2, "type_user": 4},
            {"usuario_id": TRAINING_USER, "uuid_usuario": "USER-train", "area_id": 3, "nombre_usuario": "Train",
             "correo_usuario": "train@example.com", "estatus_id": 2, "type_user": 1},
        ])
        conn.execute(Criterio.__table__.insert(), [
            criterio(101, 10, 2, 0),  # principal de la carrera 10
            criterio(201, 10, 1, 1),  # perfil realista de la carrera 10
            criterio(202, 11, 1, 2),  # perfil investigador de la carrera 11
        ])
        conn.execute(PuntajeObjetivo.__table__.insert(), [
            {"usuario_id": REAL_USER, "carrera_id": 11, "porc_objetivo": 0.4},
            {"usuario_id": REAL_USER, "carrera_id": 10, "porc_objetivo": 0.8},
            {"usuario_id": TRAINING_USER, "carrera_id": 10, "porc_objetivo": 1.0},
        ])
        conn.execute(UsuarioCriterio.__table__.insert(), [
            {"usuario_id": REAL_USER, "criterio_id": 202, "repeticiones": 1, "porc_coincidencia": 0.6},
            {"usuario_id": REAL_USER, "criterio_id": 101, "repeticiones": 1, "porc_coincidencia": 0.5},
            {"usuario_id": REAL_USER, "criterio_id": 201, "repeticiones": 2, "porc_coincidencia": 0.9},
            {"usuario_id": TRAINING_USER, "criterio_id": 201, "repeticiones": 1, "porc_coincidencia": 0.1},
        ])
    try:
        yield query_handler_module.QueryHandler()
    finally:
        engine.dispose()


def test_user_data_only_contains_the_requested_user_even_if_not_a_training_type(query_handler):
    data = query_handler.get_user_data(REAL_USER)

    assert set(data) == {"usuarios", "puntaje_objetivo", "usuario_criterio"}
    assert data["usuarios"].to_dict("records") == [{"usuario_id": REAL_USER, "type_user": 4}]
    assert data["puntaje_objetivo"].to_dict("records") == [
        {"usuario_id": REAL_USER, "carrera_id": 10, "porc_objetivo": 0.8},
        {"usuario_id": REAL_USER, "carrera_id": 11, "porc_objetivo": 0.4},
    ]
    assert data["usuario_criterio"].to_dict("records") == [
        {"usuario_id": REAL_USER, "carrera_id": 10, "type_id": 2, "riasec_id": 0,
         "repeticiones": 1, "porc_coincidencia": 0.5},
        {"usuario_id": REAL_USER, "carrera_id": 10, "type_id": 1, "riasec_id": 1,
         "repeticiones": 2, "porc_coincidencia": 0.9},
        {"usuario_id": REAL_USER, "carrera_id": 11, "type_id": 1, "riasec_id": 2,
         "repeticiones": 1, "porc_coincidencia": 0.6},
    ]


def test_user_data_has_the_columns_the_trained_model_pieces_require(query_handler):
    data = query_handler.get_user_data(REAL_USER)

    # Si cambian las columnas de las piezas de entrenamiento, el DataFrame del usuario deja de ser reutilizable.
    UsuariosPieza(datos=data["usuarios"])
    PuntajeObjetivoPieza(datos=data["puntaje_objetivo"])
    UsuarioCriterioPieza(datos=data["usuario_criterio"])


def test_user_without_rows_returns_empty_frames_with_the_same_columns(query_handler):
    data = query_handler.get_user_data(999)

    assert all(frame.empty for frame in data.values())
    assert list(data["usuarios"].columns) == UsuariosPieza.COLUMNAS
    assert list(data["puntaje_objetivo"].columns) == PuntajeObjetivoPieza.COLUMNAS
    assert list(data["usuario_criterio"].columns) == UsuarioCriterioPieza.COLUMNAS


def test_classifier_fetches_the_data_with_the_user_id_from_the_event():
    query = Mock()
    handler = ClassifierEventHandler(qh=query, ch=Mock())

    result = handler._classify_user_careers(None, REAL_USER)

    query.get_user_data.assert_called_once_with(REAL_USER)
    assert result is query.get_user_data.return_value
