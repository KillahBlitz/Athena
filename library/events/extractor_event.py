from pydantic import BaseModel
from typing import List


class Hability(BaseModel):
    id_hablity: int
    hablity_name: str

class FormData(BaseModel):
    form_id: int
    response_s: str
    response_t: str
    response_a: str
    response_r: str

class ExtractorEvent(BaseModel):
    user_uuid: str
    id_area: int
    hablities_list: List[Hability]
    form_list: List[FormData]