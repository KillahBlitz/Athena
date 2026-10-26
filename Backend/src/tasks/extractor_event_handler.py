from kinasis_library.services.redis_interface import RedisConsumer
from kinasis_library.utils.config_manager import ConfigManager
from kinasis_library.events.extractor_event import ExtractorEvent
from handlers.extraction_handler import ExtractorHandler
from handlers.command_handler import CommandHandler
from handlers.query_handler import QueryHandler
from models.user import UserInfo
from service.jev import jev_api_service

from pathlib import Path
import json
import traceback

DEFAULT_JEV_MODEL = "typesafe-ai/jev"
LOGS_DIR = Path(__file__).resolve().parents[2] / "logs"

def get_dict_envs():
    cm = ConfigManager()
    envs = {
        "REDIS_HOST": cm.get_env("REDIS_HOST"),
        "REDIS_PORT": cm.get_env("REDIS_PORT"),
        "REDIS_PASSWORD": cm.get_env("REDIS_PASSWORD"),
        "STREAM_NAME": cm.get_env("STREAM_EXTRACTOR"),
        "GROUP_NAME": cm.get_env("GROUP_EXTRACTOR"),
        "CONSUMER_NAME": cm.get_env("CONSUMER_EXTRACTOR"),
        "SEND_STREAM_NAME": cm.get_env("STREAM_EXTRACTOR_SEND"),
    }
    return envs

def get_jev_dict_envs():
    cm = ConfigManager()
    envs = {
        "VERCEL_API_URL": cm.get_env("VERCEL_API_URL"),
        "VERCEL_API_KEY": cm.get_env("VERCEL_API_KEY"),
        "VERCEL_MODEL": cm.get_env("VERCEL_MODEL"),
    }
    return envs


class ExtractorEventHandler:
    def __init__(self, qh: QueryHandler = None, ch: CommandHandler = None):
        self._qh = qh or QueryHandler()
        self._ch = ch or CommandHandler()
        self._eh = ExtractorHandler(qh=self._qh, ch=self._ch)

    def execute_jev_task(self, prompt: dict, api_envs: dict) -> dict:
        questions = prompt["questions"]
        with jev_api_service(api_envs) as client:
            http_response = client.post("/decisions", json={
                "model": api_envs.get("VERCEL_MODEL") or DEFAULT_JEV_MODEL,
                "input": prompt["input"],
                "questions": questions,
            })
            http_response.raise_for_status()
            return http_response.json()


    def classifier_task(self, event: ExtractorEvent, api_envs: dict) -> dict:
        print(f"Processing event for user {event.uuid_user} in area {event.area_id}")
        user = UserInfo(uuid=event.uuid_user, area_id=event.area_id, estatus_id=2)
        prompt_info = self._eh.get_info_prompt(event)
        prompt = self._eh.generate_prompt_for_jev(prompt_info)

        output_file = Path(__file__).resolve().parents[2] / f"logs/criteria/user_{event.uuid_user}_area_{event.area_id}.json"
        output_file.parent.mkdir(parents=True, exist_ok=True)
        output_file.write_text(json.dumps(prompt, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"Prompt saved to {output_file}")

        jev_response = self.execute_jev_task(prompt, api_envs)
        # Tokens reales por evaluación: base para estimar el costo en producción (consumo_jev.md).
        print(f"Jev usage user={event.uuid_user} area={event.area_id} "
              f"preguntas={len(prompt['questions'])} usage={jev_response.get('usage')}", flush=True)
        result = self._eh.format_jev_response(prompt_info, jev_response)

        output_file = Path(__file__).resolve().parents[2] / f"logs/events/user_{event.uuid_user}_area_{event.area_id}.json"
        output_file.parent.mkdir(parents=True, exist_ok=True)
        output_file.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"Result saved to {output_file}")
        return result

    def process_event(self, raw_event: dict, api_envs: dict) -> dict | None:
        """Procesa un evento sin dejar que un fallo tumbe al worker.

        RedisConsumer confirma (ack) el mensaje al leerlo, antes de procesarlo; si algo
        falla después, Redis ya no lo reentrega. Por eso, ante un error se guarda el evento
        crudo y el motivo en logs/errors/ para poder inspeccionarlo o reprocesarlo."""
        try:
            event = ExtractorEvent(**raw_event)
        except Exception as error:
            self._save_failed_event(raw_event, "invalid_event", error)
            return None
        try:
            return self.classifier_task(event, api_envs)
        except Exception as error:
            self._save_failed_event(raw_event, "processing_failed", error)
            return None

    @staticmethod
    def _save_failed_event(raw_event: dict, reason: str, error: Exception) -> None:
        uuid_user = raw_event.get("uuid_user", "unknown") if isinstance(raw_event, dict) else "unknown"
        area_id = raw_event.get("area_id", "unknown") if isinstance(raw_event, dict) else "unknown"
        output_file = LOGS_DIR / "errors" / f"user_{uuid_user}_area_{area_id}.json"
        output_file.parent.mkdir(parents=True, exist_ok=True)
        output_file.write_text(json.dumps({
            "reason": reason,
            "error": f"{type(error).__name__}: {error}",
            "traceback": traceback.format_exc(),
            "event": raw_event,
        }, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
        print(f"[ERROR] {reason} para user={uuid_user} area={area_id}: "
              f"{type(error).__name__}: {error}. Evento guardado en {output_file}", flush=True)

if __name__ == "__main__":
    handler = ExtractorEventHandler()
    envs = get_dict_envs()
    api_envs = get_jev_dict_envs()
    redis_consumer = RedisConsumer(envs["REDIS_HOST"], int(envs["REDIS_PORT"]), envs["REDIS_PASSWORD"])
    print(f"Listening to Redis stream: {envs['STREAM_NAME']} with group: {envs['GROUP_NAME']}")
    while True:
        event = redis_consumer.start_redis_consumer(
            stream_name=envs["STREAM_NAME"], group_name=envs["GROUP_NAME"],
            consumer_name=envs["CONSUMER_NAME"], count=1, block=2000)
        if event:
            handler.process_event(event, api_envs)