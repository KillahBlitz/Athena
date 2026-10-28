import numpy as np
import pandas as pd

from handlers.trainee_model_handler import FEATURES, RIASEC, TYPE_PERFIL, TYPE_PRINCIPAL
from models.trainee_data import TrainedModel

VALOR_AUSENTE = 0.0


class UserClassificationHandler:

    @staticmethod
    def _por_carrera(datos: pd.DataFrame, columna: str, descripcion: str) -> pd.Series:
        if datos["carrera_id"].duplicated().any():
            raise ValueError(f"El usuario tiene más de un registro de {descripcion} para una misma carrera")
        return datos.set_index("carrera_id")[columna]

    def vectorize_user(self, user_data: dict[str, pd.DataFrame], modelo: TrainedModel) -> pd.DataFrame:
        usuarios = user_data["usuarios"]
        if len(usuarios) != 1:
            raise ValueError(f"Se esperaba exactamente un usuario y se encontraron {len(usuarios)}")

        puntaje = user_data["puntaje_objetivo"]
        criterios = user_data["usuario_criterio"]
        carrera_ids = modelo.carrera_ids

        o = self._por_carrera(puntaje, "porc_objetivo", "puntaje de objetivo")

        df = pd.DataFrame({"carrera_id": carrera_ids})
        df["o"] = df["carrera_id"].map(o)

        principal = criterios[criterios["type_id"] == TYPE_PRINCIPAL]
        p = self._por_carrera(principal, "porc_coincidencia", "criterio principal")
        df["p"] = df["carrera_id"].map(p)

        perfil = criterios[criterios["type_id"] == TYPE_PERFIL]
        for riasec_id, letra in RIASEC.items():
            dimension = perfil[perfil["riasec_id"] == riasec_id]
            df[f"{letra}_coinc"] = df["carrera_id"].map(self._por_carrera(dimension, "porc_coincidencia", f"criterio RISEC {letra}"))
            df[f"{letra}_rep"] = df["carrera_id"].map(self._por_carrera(dimension, "repeticiones", f"criterio RISEC {letra}"))

        df[FEATURES] = df[FEATURES].fillna(VALOR_AUSENTE).astype(float)
        df.loc[df["o"] < 0.75, "p"] = 0.0

        one_hot = pd.get_dummies(pd.Categorical(df["carrera_id"], categories=carrera_ids),
                                 prefix="carrera", dtype=float)
        one_hot.index = df.index
        X = pd.concat([one_hot, df[FEATURES]], axis=1)
        X = X[modelo.columnas]
        X.index = pd.Index(carrera_ids, name="carrera_id")
        return X

    @staticmethod
    def predict_careers(modelo: TrainedModel, X: pd.DataFrame) -> list[dict]:
        prediccion = np.clip(modelo.modelo.predict(X), 0, 1)
        ranking = pd.Series(prediccion, index=X.index).sort_values(ascending=False, kind="stable")
        return [{"carrera_id": int(carrera_id), "porc_coincidencia": float(valor)}
                for carrera_id, valor in ranking.items()]

    def classify(self, user_data: dict[str, pd.DataFrame], modelo: TrainedModel | None) -> list[dict]:
        X = self.vectorize_user(user_data, modelo)
        return self.predict_careers(modelo, X)
