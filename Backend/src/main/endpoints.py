import fastapi
from fastapi.middleware.cors import CORSMiddleware
from handlers.api_handler import ApiHandler
from models.request.save_user_request import SaveUserRequest
from models.response.questionary_response import QuestionaryResponse

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
    return ah.get_areas()

@api.post("/save-user")
def save_user(payload: SaveUserRequest) -> str:
    ah.generate_user_event(payload)
    return True

@api.get("/{area_id}", response_model=QuestionaryResponse)
def get_area_data(area_id: int):
    data = ah.get_area_data(area_id)
    if data is None:
        raise fastapi.HTTPException(status_code=404, detail=f"Área {area_id} no encontrada")
    return data
