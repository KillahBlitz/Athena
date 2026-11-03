from pydantic import BaseModel


class Results(BaseModel):
    top: int
    carrera_id: int
    carrera: str
    puntaje: float
    escuelas: list[str]


class ResultResponse(BaseModel):
    user_uuid: str
    status_id: int
    results: list[Results] | None = None
