from pydantic import BaseModel

class PromptResponse(BaseModel):
    objetives_criteria: list[dict]
    priority_criteria: list[dict]
    criterias: list[dict]