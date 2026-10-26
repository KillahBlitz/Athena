from pydantic import BaseModel

class ClassifierEvent(BaseModel):
    user_uuid: str
    user_id: int
    id_area: int