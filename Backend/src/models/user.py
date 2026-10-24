from pydantic import BaseModel

from kinasis_library.utils.utils import generate_uuid

class UserInfo(BaseModel):
    uuid: str = generate_uuid()
    area_id: int
    estatus_id: int