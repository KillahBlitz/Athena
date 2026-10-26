from kinasis_library.services.redis_interface import RedisConsumer
from kinasis_library.utils.config_manager import ConfigManager
from kinasis_library.events.extractor_event import ExtractorEvent
from handlers.extraction_handler import ExtractorHandler
from handlers.command_handler import CommandHandler
from handlers.query_handler import QueryHandler
from models.user import UserInfo
from service.jev import JEVClient

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
        jev = JEVClient(api_envs)
        with jev.api_service():
            response = jev.get_response(prompt, questions)
            response.raise_for_status()
        return response.json()

    def extractor_task(self, event: ExtractorEvent, api_envs: dict) -> dict:
        print(f"Processing event for user {event.uuid_user} in area {event.area_id}")
        user = UserInfo(uuid=event.uuid_user, area_id=event.area_id, estatus_id=2)
        prompt_info = self._eh.get_info_prompt(event)
        prompt = self._eh.generate_prompt_for_jev(prompt_info)

        response = self.execute_jev_task(prompt, api_envs)
        print(f"Jev usage user={event.uuid_user} area={event.area_id} "
              f"preguntas={len(prompt['questions'])} usage={response.get('usage')}", flush=True)
        result = self._eh.format_jev_response(prompt_info, response)

        output_file = Path(__file__).resolve().parents[2] / f"logs/prompts/prompt_{event.uuid_user}.json"
        output_file.parent.mkdir(parents=True, exist_ok=True)
        output_file.write_text(json.dumps(prompt, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"Prompt saved to {output_file}")

        output_file = Path(__file__).resolve().parents[2] / f"logs/events/result_{event.uuid_user}.json"
        output_file.parent.mkdir(parents=True, exist_ok=True)
        output_file.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"Result saved to {output_file}")
        return result

if __name__ == "__main__":
    handler = ExtractorEventHandler()
    envs = get_dict_envs()
    api_envs = get_jev_dict_envs()
    redis_consumer = RedisConsumer(envs["REDIS_HOST"], int(envs["REDIS_PORT"]), envs["REDIS_PASSWORD"])
    print(f"Listening to Redis stream: {envs['STREAM_NAME']} with group: {envs['GROUP_NAME']} and consumer: {envs['CONSUMER_NAME']}")
    while True:
        event = redis_consumer.start_redis_consumer(
                    stream_name=envs["STREAM_NAME"], group_name=envs["GROUP_NAME"],
                    consumer_name=envs["CONSUMER_NAME"],count=1,block=2000)
        if event:
            result = handler.extractor_task(ExtractorEvent(**event), api_envs)
            #redis_consumer.event_producer(stream_name=envs["SEND_STREAM_NAME"], data=result)