from pydantic import BaseModel
from typing import List


class ResultResponse(BaseModel):
    career_name: str
    score: float
    schools_names: List[str]
    top: int

class ResponseEvent(BaseModel):
    user_uuid: str
    results: List[ResultResponse]