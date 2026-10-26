
import httpx2

def jev_api_service(api_envs: dict):
    return httpx2.Client(
        base_url=api_envs["VERCEL_API_URL"],
        headers={"Authorization": f"Bearer {api_envs['VERCEL_API_KEY']}"},
        timeout=30,
    )