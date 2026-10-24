from typing import Annotated, List, Dict
from pydantic import BaseModel, Field

class ObjetiveAnswer(BaseModel):
    id_objetive: int
    id_carrera: int
    puntuation: Annotated[int, Field(ge=1, le=5)]
    description: str

class RisecAnswer(BaseModel):
    risec_id: int
    criteria_list: List[Dict[int, str]]
    open_question: str

class SaveUserRequest(BaseModel):
    username: str
    email: str
    age: int
    area_id: int
    objetives: List[ObjetiveAnswer]
    risec_questions: Dict[int, RisecAnswer]
