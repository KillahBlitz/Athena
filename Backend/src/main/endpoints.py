import fastapi
from handlers.api_handler import ApiHandler
from models.response.questionary_response import QuestionaryResponse

api = fastapi.FastAPI(title="Athena API", version="1.0.0")
ah = ApiHandler()

@api.get("/get_areas")
def get_areas():
    return ah.get_areas()

@api.get("/{area_id}", response_model=QuestionaryResponse)
def get_area_data(area_id: int):
    data = ah.get_area_data(area_id)
    if data is None:
        raise fastapi.HTTPException(status_code=404, detail=f"Área {area_id} no encontrada")
    return data
