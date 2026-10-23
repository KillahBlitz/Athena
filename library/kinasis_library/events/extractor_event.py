from typing import Annotated, List
from pydantic import BaseModel, Field

class Objetives(BaseModel):
    id_objetive: int
    porc_evaluation: float
    description: str

class RisecAnswer(BaseModel):
    risec_id: int
    criteria_list: List[int]
    open_question: str

class ExtractorEvent(BaseModel):
    user_id: int
    uuid_user: str
    area_id: int
    objetives: List[Objetives]
    questions: List[RisecAnswer]