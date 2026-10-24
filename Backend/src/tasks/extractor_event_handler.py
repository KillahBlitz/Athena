from kinasis_library.services.redis_interface import RedisConsumer
from kinasis_library.utils.config_manager import ConfigManager
from kinasis_library.events.extractor_event import ExtractorEvent
from handlers.extraction_handler import ExtractorHandler
from handlers.command_handler import CommandHandler
from handlers.query_handler import QueryHandler
from models.user import UserInfo

from openai import OpenAI
from pathlib import Path
import json

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
        if not questions:
            raise ValueError("El prompt no contiene preguntas para Jev.")
        responses = []
        with OpenAI(
            api_key=api_envs["VERCEL_API_KEY"],
            base_url=api_envs["VERCEL_API_URL"],
            timeout=30,
            max_retries=0,
        ) as client:
            # Conserva el contexto y limita las instrucciones enviadas en cada llamada.
            for start in range(0, len(questions), 4):
                response = client.decisions.create(
                    model=api_envs.get("VERCEL_MODEL", "typesafe-ai/jev"),
                    **{**prompt, "questions": questions[start:start + 4]},
                )
                responses.append(response.model_dump(mode="json"))
        return {
            "model": responses[0]["model"],
            "answers": [answer for response in responses for answer in response["answers"]],
            "usage": {
                key: sum((response.get("usage") or {}).get(key) or 0 for response in responses)
                for key in ("input_tokens", "output_tokens", "total_tokens")
            },
            "batches": [{key: value for key, value in response.items() if key != "answers"}
                        for response in responses],
        }


    def classifier_task(self, event: ExtractorEvent, api_envs: dict):
        print(f"Processing event for user {event.uuid_user} in area {event.area_id}")
        user = UserInfo(uuid=event.uuid_user, area_id=event.area_id, estatus_id=2)
        prompt_info = self._eh.get_info_prompt(event)
        prompt = self._eh.generate_prompt_for_jev(prompt_info)
        ## guardar prompt en un archivo json con nombre user_{uuid_user}_area_{area_id}.json
        output_file = Path(__file__).resolve().parents[2] / f"logs/criteria/user_{event.uuid_user}_area_{event.area_id}.json"
        output_file.write_text(json.dumps(prompt, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"Prompt saved to {output_file}")
        #result_extraction = self.execute_jev_task(prompt, api_envs)
        ##save result in /Users/jmonroyc/Documents/MyProjects/Athena/Backend/logs/events
        ## guardamos result_extraction en un archivo json con nombre user_{uuid_user}_area_{area_id}.json
        #output_file = Path(__file__).resolve().parents[2] / f"logs/events/user_{event.uuid_user}_area_{event.area_id}.json"
        #output_file.write_text(json.dumps(result_extraction, ensure_ascii=False, indent=2), encoding="utf-8")
        #print(f"Result saved to {output_file}")

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
            result = handler.classifier_task(ExtractorEvent(**event), api_envs)
            #redis_consumer.event_producer(stream_name=envs["SEND_STREAM_NAME"], data=result)
