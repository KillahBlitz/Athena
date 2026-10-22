from typing import Annotated, List
from pydantic import BaseModel, Field

class ObjetiveAnswer(BaseModel):
    id_objetive: int
    puntuation: Annotated[int, Field(ge=1, le=5)]
    description: str


class RisecAnswer(BaseModel):
    risec_id: int
    criteria_id_list: List[int]
    open_question: str

class SaveUserRequest(BaseModel):

    username: str
    email: str
    age: int
    area_id: int
    objetives: List[ObjetiveAnswer]
    risec_questions: List[RisecAnswer]
