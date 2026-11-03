from pydantic import BaseModel
from typing import List

class Objetives(BaseModel):
    id_objetive: int
    id_carrera: int
    porc_evaluation: float
    description: str

class RisecAnswer(BaseModel):
    criteria_list: List[dict[int, str]]
    open_question: str

class ExtractorEvent(BaseModel):
    user_id: int
    uuid_user: str
    area_id: int
    objetives: List[Objetives]
    questions: dict[int, RisecAnswer]