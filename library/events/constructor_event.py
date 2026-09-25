from pydantic import BaseModel
from typing import List


class CareersList(BaseModel):
    career_id: int
    career_name: str
    score: float

class ConstructorEvent(BaseModel):
    user_uuid: str
    careers_list: List[CareersList]