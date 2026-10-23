from kinasis_library.services.redis_interface import RedisConsumer
from kinasis_library.utils.config_manager import ConfigManager
from kinasis_library.events.extractor_event import ExtractorEvent
from handlers.command_handler import CommandHandler
from handlers.query_handler import QueryHandler

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


class ExtractorEventHandler:
    def __init__(self, qh: QueryHandler = None, ch: CommandHandler = None):
        self._qh = qh or QueryHandler()
        self._ch = ch or CommandHandler()

    def classifier_task(self, event: ExtractorEvent):
        print(f"Processing event for user {event.uuid_user} in area {event.area_id}")

if __name__ == "__main__":
    handler = ExtractorEventHandler()
    envs = get_dict_envs()
    redis_consumer = RedisConsumer(envs["REDIS_HOST"], int(envs["REDIS_PORT"]), envs["REDIS_PASSWORD"])

    while True:
        event = redis_consumer.start_redis_consumer(
                    stream_name=envs["STREAM_NAME"], group_name=envs["GROUP_NAME"],
                    consumer_name=envs["CONSUMER_NAME"],count=1,block=2000)
        if event:
            result = handler.classifier_task(ExtractorEvent(**event))
            #redis_consumer.event_producer(stream_name=envs["SEND_STREAM_NAME"], data=result)