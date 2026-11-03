from unittest.mock import Mock

import numpy as np
import pandas as pd
import pytest
from kinasis_library.events.classifier_event import ClassifierEvent
from sklearn.ensemble import RandomForestRegressor

from handlers.classification_handler import UserClassificationHandler, VALOR_AUSENTE
from handlers.trainee_model_handler import FEATURES, TraineeModelHandler
from models.trainee_data import TrainedModel
from tasks.classifier_event_handler import ClassifierEventHandler

USER_ID = 42
CARRERAS = [10, 11]
COLUMNAS = [f"carrera_{c}" for c in CARRERAS] + FEATURES
CRITERIO_COLUMNS = ["usuario_id", "carrera_id", "type_id", "riasec_id", "repeticiones", "porc_coincidencia"]


def make_model(columnas=None, afinidad=None):
    """Modelo real y pequeño: la afinidad que predice depende solo de la carrera (one-hot)."""
    afinidad = afinidad or {10: 0.2, 11: 1.4}  # 1.4 está fuera de rango a propósito, para probar el recorte
    columnas = columnas or COLUMNAS
    rng = np.random.default_rng(0)
    X = pd.DataFrame(rng.random((40, len(columnas))), columns=columnas)
    for carrera in CARRERAS:
        X[f"carrera_{carrera}"] = 0.0
    carrera = np.array(CARRERAS * 20)
    for c in CARRERAS:
        X.loc[carrera == c, f"carrera_{c}"] = 1.0
    y = [afinidad[c] for c in carrera]
    forest = RandomForestRegressor(n_estimators=20, random_state=0).fit(X, y)
    return TrainedModel(area_id=3, modelo=forest, carrera_ids=CARRERAS, columnas=columnas,
                        metricas={}, mae_por_carrera={})


def make_user_data(puntaje=None, criterios=None, usuarios=None):
    """Datos crudos de un usuario real con la misma forma que devuelve QueryHandler.get_user_data."""
    puntaje = [(USER_ID, 10, 0.8), (USER_ID, 11, 0.4)] if puntaje is None else puntaje
    criterios = [
        (USER_ID, 10, 2, 0, 1, 0.5),   # criterio PRINCIPAL de la carrera 10
        (USER_ID, 10, 1, 1, 2, 0.9),   # perfil Realista de la carrera 10, repetido
        (USER_ID, 11, 1, 2, 1, 0.6),   # perfil Investigador de la carrera 11
    ] if criterios is None else criterios
    usuarios = [(USER_ID, 4)] if usuarios is None else usuarios
    return {
        "usuarios": pd.DataFrame(usuarios, columns=["usuario_id", "type_user"]),
        "puntaje_objetivo": pd.DataFrame(puntaje, columns=["usuario_id", "carrera_id", "porc_objetivo"]),
        "usuario_criterio": pd.DataFrame(criterios, columns=CRITERIO_COLUMNS),
    }


def ausentes(**valores):
    return {**{f: VALOR_AUSENTE for f in FEATURES}, **valores}


@pytest.fixture
def handler():
    return UserClassificationHandler()


def test_vector_has_one_row_per_career_and_the_columns_of_the_model(handler):
    modelo = make_model()

    X = handler.vectorize_user(make_user_data(), modelo)

    assert list(X.columns) == modelo.columnas
    assert list(X.index) == CARRERAS
    assert X.loc[10, ["carrera_10", "carrera_11"]].tolist() == [1.0, 0.0]
    assert X.loc[11, ["carrera_10", "carrera_11"]].tolist() == [0.0, 1.0]


def test_vector_values_come_from_the_user_rows_and_missing_ones_are_filled(handler):
    X = handler.vectorize_user(make_user_data(), make_model())

    assert X.loc[10, FEATURES].to_dict() == ausentes(o=0.8, p=0.5, r_coinc=0.9, r_rep=2.0)
    # La carrera 11 no tiene criterio principal ni dimensión Realista: quedan en "sin evidencia".
    assert X.loc[11, FEATURES].to_dict() == ausentes(o=0.4, i_coinc=0.6, i_rep=1.0)


def test_vector_column_order_follows_the_model_even_if_it_was_trained_in_another_order(handler):
    modelo = make_model(columnas=list(reversed(COLUMNAS)))

    X = handler.vectorize_user(make_user_data(), modelo)

    assert list(X.columns) == list(reversed(COLUMNAS))


@pytest.mark.parametrize("user_data, mensaje", [
    (make_user_data(usuarios=[]), "exactamente un usuario"),
    (make_user_data(puntaje=[(USER_ID, 10, 0.8), (USER_ID, 10, 0.5), (USER_ID, 11, 0.4)]), "más de un registro"),
    (make_user_data(criterios=[(USER_ID, 10, 1, 1, 1, 0.9), (USER_ID, 10, 1, 1, 2, 0.9)]), "más de un registro"),
])
def test_vector_rejects_incomplete_or_ambiguous_user_data(handler, user_data, mensaje):
    with pytest.raises(ValueError, match=mensaje):
        handler.vectorize_user(user_data, make_model())


def test_prediction_is_sorted_by_affinity_and_clipped_to_0_1(handler):
    modelo = make_model()  # la carrera 11 se entrenó con 1.4 y la 10 con 0.2

    ranking = handler.predict_careers(modelo, handler.vectorize_user(make_user_data(), modelo))

    assert ranking == [
        {"carrera_id": 11, "porc_coincidencia": pytest.approx(1.0)},
        {"carrera_id": 10, "porc_coincidencia": pytest.approx(0.2)},
    ]


def test_classifier_task_reads_the_event_user_and_uses_the_model_of_its_area():
    query = Mock()
    query.get_user_data.return_value = make_user_data()
    commands = Mock()
    classifier = ClassifierEventHandler(qh=query, ch=commands)
    classifier._modelos = {3: make_model()}

    result = classifier.classifier_task(ClassifierEvent(user_uuid="USER-real", user_id=USER_ID, id_area=3))

    query.get_user_data.assert_called_once_with(USER_ID)
    # Devuelve el evento para el constructor con las carreras ordenadas por afinidad (recortada a 0–1).
    assert result.user_uuid == "USER-real"
    assert [(c.career_id, c.score) for c in result.careers_list] == [(11, pytest.approx(1.0)), (10, pytest.approx(0.2))]
    # Marca al usuario como clasificado (estatus 3) usando su UUID.
    commands.update_user_status.assert_called_once_with("USER-real", 3)


def test_inference_vector_is_identical_to_the_training_vector_for_a_complete_user(handler):
    # Usuario con todas las dimensiones y el criterio principal en cada carrera, que es lo único que el
    # entrenamiento acepta. Si ambos vectores coinciden, el modelo recibe en producción lo mismo que vio al entrenar.
    criterios = [(USER_ID, c, 2, 0, 1, 0.5 + 0.1 * c / 10) for c in CARRERAS]
    criterios += [(USER_ID, c, 1, riasec, 1 + riasec % 2, round(0.1 * riasec, 1))
                  for c in CARRERAS for riasec in (1, 2, 4, 5, 6)]
    user_data = make_user_data(criterios=criterios)
    modelo = make_model()

    _, esperado = TraineeModelHandler(Mock(), Mock())._build_features(
        user_data["puntaje_objetivo"], user_data["usuario_criterio"], CARRERAS)
    obtenido = handler.vectorize_user(user_data, modelo)

    pd.testing.assert_frame_equal(obtenido.reset_index(drop=True), esperado.reset_index(drop=True))


def test_p_is_hidden_below_rating_4_in_training_and_inference_alike(handler):
    # Rating 4 (o = 0.75) exige justificación en el Frontend, así que P se usa. Rating 3 (o = 0.5) no la exige:
    # P se oculta (0) para que la falta de justificación no se lea como "no coincide". Debe pasar igual al entrenar.
    puntaje = [(USER_ID, 10, 0.75), (USER_ID, 11, 0.5)]
    criterios = [(USER_ID, c, 2, 0, 1, 0.9) for c in CARRERAS]
    criterios += [(USER_ID, c, 1, riasec, 1, 0.6) for c in CARRERAS for riasec in (1, 2, 4, 5, 6)]
    user_data = make_user_data(puntaje=puntaje, criterios=criterios)

    _, entrenamiento = TraineeModelHandler(Mock(), Mock())._build_features(
        user_data["puntaje_objetivo"], user_data["usuario_criterio"], CARRERAS)
    inferencia = handler.vectorize_user(user_data, make_model())

    assert entrenamiento["p"].tolist() == [0.9, 0.0]
    assert inferencia.loc[10, "p"] == 0.9
    assert inferencia.loc[11, "p"] == 0.0
