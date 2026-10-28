import fastapi
from fastapi.middleware.cors import CORSMiddleware
from handlers.api_handler import ApiHandler
from models.request.save_user_request import SaveUserRequest
from models.response.questionary_response import QuestionaryResponse
from models.response.result_response import ResultResponse

api = fastapi.FastAPI(title="Athena API", version="1.0.0")

api.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

ah = ApiHandler()

@api.get("/get_areas")
def get_areas():
    result = ah.get_areas()
    if result is None:
        raise fastapi.HTTPException(status_code=404, detail=f"No se encontraron áreas")
    return result

@api.get("/{area_id}", response_model=QuestionaryResponse)
def get_area_data(area_id: int):
    result = ah.get_area_data(area_id)
    if result is None:
        raise fastapi.HTTPException(status_code=404, detail=f"Área {area_id} no encontrada")
    return result

@api.post("/save-user")
def save_user(payload: SaveUserRequest) -> str:
    result = ah.generate_user_event(payload)
    if result is None:
            raise fastapi.HTTPException(status_code=404, detail=f"Error generating user event")
    return result

@api.get("/get-results/{user_uuid}", response_model=ResultResponse)
def get_results(user_uuid: str):
    result = ah.get_results(user_uuid)
    if result is None:
        raise fastapi.HTTPException(status_code=404, detail=f"Resultados para el usuario {user_uuid} no encontrados")
    return result