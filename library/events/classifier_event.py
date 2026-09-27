from pydantic import BaseModel
from typing import List


class HabilityUser(BaseModel):
    id_hablity: int
    criteria_score: float
    quantity_repeat: int

class ClassifierEvent(BaseModel):
    user_uuid: str
    id_area: int
    hablities_user_list: List[HabilityUser]