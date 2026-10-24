from pydantic import BaseModel

class Pregunta(BaseModel):
    riasec_id: int
    texto_pregunta: str
    pregunta_abierta: str
    opciones: dict[int, str]

class Objetivo(BaseModel):
    id_carrera: int
    id_objetivo: int
    pregunta: str | None

class QuestionaryResponse(BaseModel):
    area_id: int
    nom_area: str
    objetivos: list[Objetivo]
    preguntas: list[Pregunta]
