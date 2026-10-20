from pydantic import BaseModel


class Pregunta(BaseModel):
    riasec_id: int
    texto_pregunta: str
    pregunta_abierta: str
    opciones: dict[int, str]


class QuestionaryResponse(BaseModel):
    area_id: int
    nom_area: str
    objetivos: dict[int, str | None]
    preguntas: list[Pregunta]
