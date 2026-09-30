from kinasis_library.services.redis_interface import RedisConsumer
from kinasis_library.utils.config_manager import ConfigManager
from kinasis_library.events.classifier_event import ClassifierEvent


def get_dict_envs():
    cm = ConfigManager()
    envs = {
        "REDIS_HOST": cm.get_env("REDIS_HOST"),
        "REDIS_PORT": cm.get_env("REDIS_PORT"),
        "REDIS_PASSWORD": cm.get_env("REDIS_PASSWORD"),
        "STREAM_NAME": cm.get_env("STREAM_CLASSIFIER"),
        "GROUP_NAME": cm.get_env("GROUP_CLASSIFIER"),
        "CONSUMER_NAME": cm.get_env("CONSUMER_CLASSIFIER"),
        "SEND_STREAM_NAME": cm.get_env("STREAM_CLASSIFIER_SEND"),
    }
    return envs


class ClassifierEventHandler:
    def __init__(self):
        pass

    def start_trainee_models(self):
        print("Starting trainee models...")
        print("Trainee models started successfully.")
    
    def classifier_task(self, event: ClassifierEvent):
        print(f"Processing event: {event}")

if __name__ == "__main__":
    handler = ClassifierEventHandler()
    handler.start_trainee_models()
    envs = get_dict_envs()
    redis_consumer = RedisConsumer(envs["REDIS_HOST"], int(envs["REDIS_PORT"]), envs["REDIS_PASSWORD"])

    while True:
        event = redis_consumer.start_redis_consumer(
                    stream_name=envs["STREAM_NAME"], group_name=envs["GROUP_NAME"],
                    consumer_name=envs["CONSUMER_NAME"],count=1,block=2000)
        if event:
            result = handler.classifier_task(ClassifierEvent(**event))
            redis_consumer.event_producer(stream_name=envs["SEND_STREAM_NAME"], data=result)