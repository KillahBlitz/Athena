import httpx2

DEFAULT_JEV_MODEL = "typesafe-ai/jev"

class JEVClient:
    def __init__(self, api_envs: dict):
        self._url = api_envs.get("VERCEL_API_URL")
        self._key = api_envs.get("VERCEL_API_KEY")
        self._model = api_envs.get("VERCEL_MODEL") or DEFAULT_JEV_MODEL


    def api_service(self):
        self._client = httpx2.Client(
            base_url=self._url,
            headers={"Authorization": f"Bearer {self._key}"},
            timeout=30,
        )
        return self._client

    def get_response(self, prompt: dict, questions: list) -> httpx2.Response:
        response = self._client.post("/decisions", json={
                "model": self._model,
                "input": prompt["input"],
                "questions": questions,
            })
        return response