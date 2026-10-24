from pydantic import BaseModel

class CriteriaRag(BaseModel):
    criteria_id: int
    carrera_id: int
    criteria: str
    criteria_type: int