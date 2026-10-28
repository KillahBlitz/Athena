import pandas as pd
import numpy as np

from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

from handlers.query_handler import QueryHandler
from handlers.command_handler import CommandHandler
from models.trainee_data import TraineeData, TrainedModel

TYPE_ENTRENAMIENTO, TYPE_VALIDACION = 1, 2
TYPE_PRINCIPAL, TYPE_PERFIL = 2, 1
RIASEC = {1: "r", 2: "i", 4: "s", 5: "e", 6: "c"}
LLAVE = ["usuario_id", "carrera_id"]
FEATURES = ["o", "p"] + [f"{letra}_{tipo}" for letra in RIASEC.values() for tipo in ("coinc", "rep")]
UMBRAL_Y_ALTA = 0.5

class TraineeModelHandler:
    def __init__(self, qh: QueryHandler, ch: CommandHandler):
        self._qh = qh
        self._ch = ch

    def _load_area_data(self, area_id: int):
        type_users = [TYPE_ENTRENAMIENTO, TYPE_VALIDACION]
        carrera_ids = self._qh.get_carrera_ids(area_id)
        piezas = {
            "usuarios": self._qh.get_users_by_type(area_id, type_users),
            "puntaje_objetivo": self._qh.get_puntaje_objetivo(area_id, type_users),
            "usuario_criterio": self._qh.get_usuario_criterio(area_id, type_users),
            "resultados": self._qh.get_resultados(area_id, type_users),
        }
        return {
            "carrera_ids": carrera_ids,
            "piezas": piezas
        }

    def _build_features(self, df_puntaje_objetivo: pd.DataFrame, df_usuario_criterio: pd.DataFrame,
                        carrera_ids: list[int]):
        df_p = df_usuario_criterio[df_usuario_criterio["type_id"] == TYPE_PRINCIPAL]
        df_p = df_p[[*LLAVE, "porc_coincidencia"]].rename(columns={"porc_coincidencia": "p"})
        if df_p.duplicated(subset=LLAVE).any():
            raise ValueError("Hay parejas usuario × carrera con más de un criterio principal")

        df_perfil = df_usuario_criterio[(df_usuario_criterio["type_id"] == TYPE_PERFIL)
                                        & df_usuario_criterio["riasec_id"].isin(RIASEC)]
        df_riasec = df_perfil.pivot(index=LLAVE, columns="riasec_id", values=["porc_coincidencia", "repeticiones"])
        df_riasec.columns = [f"{RIASEC[riasec_id]}_{'coinc' if valor == 'porc_coincidencia' else 'rep'}"
                             for valor, riasec_id in df_riasec.columns]
        df_riasec = df_riasec.reset_index()

        df = (df_puntaje_objetivo[[*LLAVE, "porc_objetivo"]].rename(columns={"porc_objetivo": "o"})
              .merge(df_p, on=LLAVE, how="left", validate="one_to_one")
              .merge(df_riasec, on=LLAVE, how="left", validate="one_to_one")
              .reindex(columns=[*LLAVE, *FEATURES]))
        if df[FEATURES].isna().any().any():
            raise ValueError("Hay parejas usuario × carrera sin criterio principal o sin alguna dimensión RISEC")
        porcentajes = [c for c in FEATURES if not c.endswith("_rep")]
        if not ((df[porcentajes] >= 0) & (df[porcentajes] <= 1)).all().all():
            raise ValueError("Hay porcentajes fuera del rango 0–1")
        # Con valoración menor que 4 (o < 0.75) la justificación es opcional en el Frontend y casi nunca existe.
        # Se oculta P para que el modelo no confunda "no escribió" con "escribió algo que no coincide".
        df.loc[df["o"] < 0.75, "p"] = 0.0

        one_hot = pd.get_dummies(pd.Categorical(df["carrera_id"], categories=carrera_ids),
                                 prefix="carrera", dtype=float)
        one_hot.index = df.index
        X = pd.concat([one_hot, df[FEATURES].astype(float)], axis=1)
        return df[LLAVE], X

    def _vectorize(self, trainee_data: TraineeData):
        piezas = trainee_data.piezas
        llaves, X = self._build_features(piezas.puntaje_objetivo.datos, piezas.usuario_criterio.datos,
                                         trainee_data.carrera_ids)
        df_resultados = piezas.resultados.datos.rename(columns={"porc_coincidencia": "y"})
        y = llaves.merge(df_resultados[[*LLAVE, "y"]], on=LLAVE, how="left", validate="one_to_one")["y"]
        type_user = llaves.merge(piezas.usuarios.datos, on="usuario_id", how="left",
                                 validate="many_to_one")["type_user"]
        if y.isna().any() or type_user.isna().any():
            raise ValueError("Hay parejas usuario × carrera sin resultado o sin type_user")

        entrenamiento = (type_user == TYPE_ENTRENAMIENTO).to_numpy()
        validacion = (type_user == TYPE_VALIDACION).to_numpy()
        return {
            "columnas": list(X.columns),
            "X_train": X[entrenamiento], "y_train": y[entrenamiento],
            "X_val": X[validacion], "y_val": y[validacion],
            "llaves_val": llaves[validacion],
        }

    @staticmethod
    def _train(vectores: dict) -> RandomForestRegressor:
        modelo = RandomForestRegressor(n_estimators=300, min_samples_leaf=5, random_state=42, n_jobs=-1)
        modelo.fit(vectores["X_train"], vectores["y_train"])
        return modelo

    @staticmethod
    def _validate(modelo: RandomForestRegressor, vectores: dict):
        y_val = vectores["y_val"].to_numpy()
        prediccion = np.clip(modelo.predict(vectores["X_val"]), 0, 1)
        alta = y_val >= UMBRAL_Y_ALTA
        metricas = {
            "mae": float(mean_absolute_error(y_val, prediccion)),
            "rmse": float(np.sqrt(mean_squared_error(y_val, prediccion))),
            "r2": float(r2_score(y_val, prediccion)),
            "mae_y_alta": float(mean_absolute_error(y_val[alta], prediccion[alta])) if alta.any() else float("nan"),
        }
        error = pd.Series(np.abs(prediccion - y_val), index=vectores["llaves_val"].index)
        mae_por_carrera = error.groupby(vectores["llaves_val"]["carrera_id"]).mean().round(4)
        return metricas, {int(c): float(v) for c, v in mae_por_carrera.items()}

    def _train_area(self, area_id: int) -> TrainedModel:
        print(f"\n[Área {area_id}] Extrayendo datos de entrenamiento y validación...")
        trainee_data = TraineeData(**self._load_area_data(area_id))
        usuarios = trainee_data.piezas.usuarios.datos["type_user"].value_counts()
        print(f"[Área {area_id}] Datos extraídos: "
              f"{len(trainee_data.carrera_ids)} carreras, "
              f"{usuarios.get(TYPE_ENTRENAMIENTO, 0):,} usuarios de entrenamiento, "
              f"{usuarios.get(TYPE_VALIDACION, 0):,} de validación")
        for nombre, pieza in trainee_data.piezas:
            print(f"[Área {area_id}]   {nombre}: {len(pieza.datos):,} filas")

        vectores = self._vectorize(trainee_data)
        print(f"[Área {area_id}] Vectorizado: "
              f"X_train {vectores['X_train'].shape}, X_val {vectores['X_val'].shape}, "
              f"{len(vectores['columnas'])} columnas")

        print(f"[Área {area_id}] Entrenando RandomForestRegressor con {len(vectores['X_train']):,} filas...")
        modelo = self._train(vectores)
        print(f"[Área {area_id}] Entrenamiento terminado")

        print(f"[Área {area_id}] Validando con {len(vectores['X_val']):,} filas...")
        metricas, mae_por_carrera = self._validate(modelo, vectores)
        print(f"[Área {area_id}] Validación: " + ", ".join(f"{k}={v:.4f}" for k, v in metricas.items()))
        peor = max(mae_por_carrera, key=mae_por_carrera.get)
        print(f"[Área {area_id}]   carrera con mayor error: {peor} (MAE {mae_por_carrera[peor]:.4f})")

        print(f"[Área {area_id}] Modelo listo para usar")
        return TrainedModel(area_id=area_id, modelo=modelo, carrera_ids=trainee_data.carrera_ids,
                            columnas=vectores["columnas"], metricas=metricas, mae_por_carrera=mae_por_carrera)

    def start_trainee_models(self):
        return {
            1: self.start_trainee_model_area_1(),
            2: self.start_trainee_model_area_2(),
            3: self.start_trainee_model_area_3(),
        }

    def start_trainee_model_area_1(self) -> TrainedModel:
        return self._train_area(1)

    def start_trainee_model_area_2(self) -> TrainedModel:
        return self._train_area(2)

    def start_trainee_model_area_3(self) -> TrainedModel:
        return self._train_area(3)
