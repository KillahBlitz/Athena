from typing import Any, ClassVar

import pandas as pd
from pydantic import BaseModel, ConfigDict, field_validator, model_validator
from sklearn.ensemble import RandomForestRegressor


class Pieza(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    COLUMNAS: ClassVar[list[str]] = []

    datos: pd.DataFrame

    @model_validator(mode="before")
    @classmethod
    def from_dataframe(cls, valor: Any):
        return {"datos": valor} if isinstance(valor, pd.DataFrame) else valor

    @field_validator("datos")
    @classmethod
    def validate_columns(cls, datos: pd.DataFrame):
        faltan = [c for c in cls.COLUMNAS if c not in datos.columns]
        if faltan:
            raise ValueError(f"{cls.__name__}: faltan las columnas {faltan}")
        return datos


class UsuariosPieza(Pieza):
    COLUMNAS: ClassVar[list[str]] = ["usuario_id", "type_user"]


class PuntajeObjetivoPieza(Pieza):
    COLUMNAS: ClassVar[list[str]] = ["usuario_id", "carrera_id", "porc_objetivo"]


class UsuarioCriterioPieza(Pieza):
    COLUMNAS: ClassVar[list[str]] = ["usuario_id", "carrera_id", "type_id", "riasec_id",
                                     "repeticiones", "porc_coincidencia"]


class ResultadosPieza(Pieza):
    COLUMNAS: ClassVar[list[str]] = ["usuario_id", "carrera_id", "porc_coincidencia"]


class Piezas(BaseModel):
    usuarios: UsuariosPieza
    puntaje_objetivo: PuntajeObjetivoPieza
    usuario_criterio: UsuarioCriterioPieza
    resultados: ResultadosPieza


class TraineeData(BaseModel):
    carrera_ids: list[int]
    piezas: Piezas


class TrainedModel(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    area_id: int
    modelo: RandomForestRegressor
    carrera_ids: list[int]
    columnas: list[str]
    metricas: dict[str, float]
    mae_por_carrera: dict[int, float]
