import fastapi
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from handlers.api_handler import ApiHandler
from models.request.save_user_request import SaveUserRequest
from models.response.questionary_response import QuestionaryResponse
from models.response.result_response import ResultResponse

api = fastapi.FastAPI(
    title="Athena API",
    version="1.0.0",
    docs_url="/api/docs",
    openapi_url="/api/openapi.json",
)

api.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

ah = ApiHandler()
router = fastapi.APIRouter()


@router.get("/")
@router.get("/health")
def health_check():
    return {"status": "ok", "service": "athena-api"}


@router.get("/get_areas")
def get_areas():
    result = ah.get_areas()
    if result is None:
        raise fastapi.HTTPException(status_code=404, detail="No se encontraron áreas")
    return result


@router.get("/{area_id}", response_model=QuestionaryResponse)
def get_area_data(area_id: int):
    result = ah.get_area_data(area_id)
    if result is None:
        raise fastapi.HTTPException(status_code=404, detail=f"Área {area_id} no encontrada")
    return result


@router.post("/save-user")
def save_user(payload: SaveUserRequest) -> str:
    result = ah.generate_user_event(payload)
    if result is None:
        raise fastapi.HTTPException(status_code=404, detail="Error generating user event")
    return result


@router.get("/get-results/{user_uuid}", response_model=ResultResponse)
def get_results(user_uuid: str):
    result = ah.get_results(user_uuid)
    if result is None:
        raise fastapi.HTTPException(status_code=404, detail=f"Resultados para el usuario {user_uuid} no encontrados")
    return result



api.include_router(router, prefix="/api")
api.include_router(router)


@api.get("/docs", include_in_schema=False)
def redirect_docs():
    return RedirectResponse(url="/api/docs")


@api.get("/openapi.json", include_in_schema=False)
def redirect_openapi():
    return RedirectResponse(url="/api/openapi.json")
