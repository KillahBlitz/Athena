from kinasis_library.services.redis_interface import RedisConsumer
from kinasis_library.utils.config_manager import ConfigManager
from kinasis_library.events.classifier_event import ClassifierEvent
from kinasis_library.events.constructor_event import ConstructorEvent, CareersList
from handlers.command_handler import CommandHandler
from handlers.classification_handler import UserClassificationHandler
from handlers.query_handler import QueryHandler
from handlers.trainee_model_handler import TraineeModelHandler
from models.trainee_data import TrainedModel

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
    def __init__(self, qh: QueryHandler = None, ch: CommandHandler = None):
        self._qh = qh or QueryHandler()
        self._ch = ch or CommandHandler()
        self._tmh = TraineeModelHandler(self._qh, self._ch)
        self._ucl = UserClassificationHandler()
        self._modelos: dict[int, TrainedModel | None] = {}

    def _classify_user_careers(self, modelo: TrainedModel | None, user_id: int) -> list[dict]:
        user_data = self._qh.get_user_data(user_id)
        return self._ucl.classify(user_data, modelo)

    def start_trainee_models(self):
        print("Starting trainee models...")
        self._modelos = self._tmh.start_trainee_models()
        print("Trainee models started successfully.")
    
    def classifier_task(self, event: ClassifierEvent) -> ConstructorEvent:
        print(f"Processing event: area: {event.id_area}, user: {event.user_uuid}")
        modelo = self._modelos.get(event.id_area)
        ranking = self._classify_user_careers(modelo, event.user_id)
        print(f"Classified user {event.user_uuid}, best={ranking[0].get('carrera_id')}, score={ranking[0].get('porc_coincidencia')}")

        self._ch.update_user_status(event.user_uuid, 3)
        carreras_list = []
        for carrera in ranking:
            carreras_list.append(CareersList(career_id=carrera["carrera_id"], score=carrera["porc_coincidencia"]))
        print("send event to constructor-stream")
        return ConstructorEvent(user_uuid=event.user_uuid, careers_list=carreras_list)
        

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
            event_result = handler.classifier_task(ClassifierEvent(**event))
            redis_consumer.event_producer("constructor_stream", event_result)