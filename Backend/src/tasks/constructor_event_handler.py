from kinasis_library.services.redis_interface import RedisConsumer
from kinasis_library.utils.config_manager import ConfigManager
from kinasis_library.events.constructor_event import ConstructorEvent
from handlers.command_handler import CommandHandler
from handlers.query_handler import QueryHandler

TOP_CARRERAS = 3
ESTATUS_RESULTADOS_LISTOS = 4


def get_dict_envs():
    cm = ConfigManager()
    envs = {
        "REDIS_HOST": cm.get_env("REDIS_HOST"),
        "REDIS_PORT": cm.get_env("REDIS_PORT"),
        "REDIS_PASSWORD": cm.get_env("REDIS_PASSWORD"),
        "STREAM_NAME": cm.get_env("STREAM_CONSTRUCTOR", "constructor_stream"),
        "GROUP_NAME": cm.get_env("GROUP_CONSTRUCTOR", "constructor_group"),
        "CONSUMER_NAME": cm.get_env("CONSUMER_CONSTRUCTOR", "constructor_consumer"),
    }
    return envs


class ConstructorEventHandler:
    def __init__(self, qh: QueryHandler = None, ch: CommandHandler = None):
        self._qh = qh or QueryHandler()
        self._ch = ch or CommandHandler()

    @staticmethod
    def top_careers(event: ConstructorEvent, limit: int = TOP_CARRERAS) -> list[dict]:
        ordenadas = sorted(event.careers_list, key=lambda c: c.score, reverse=True)
        return [{"carrera_id": c.career_id, "porc_coincidencia": c.score} for c in ordenadas[:limit]]

    def constructor_task(self, event: ConstructorEvent) -> list[dict]:
        print(f"Processing event: user: {event.user_uuid}, careers: {len(event.careers_list)}")
        user = self._qh.get_user_by_uuid(event.user_uuid)
        if user is None:
            raise ValueError(f"No existe el usuario {event.user_uuid}")

        top = self.top_careers(event)
        self._ch.save_user_results(user.usuario_id, top)
        self._ch.update_user_status(event.user_uuid, ESTATUS_RESULTADOS_LISTOS)
        print(f"Saved top {len(top)} careers for user {event.user_uuid}: "
              + ", ".join(f"{c['carrera_id']}={c['porc_coincidencia']:.4f}" for c in top))
        return top


if __name__ == "__main__":
    handler = ConstructorEventHandler()
    envs = get_dict_envs()
    redis_consumer = RedisConsumer(envs["REDIS_HOST"], int(envs["REDIS_PORT"]), envs["REDIS_PASSWORD"])
    print(f"Listening to Redis stream: {envs['STREAM_NAME']} with group: {envs['GROUP_NAME']} and consumer: {envs['CONSUMER_NAME']}")
    while True:
        event = redis_consumer.start_redis_consumer(
                    stream_name=envs["STREAM_NAME"], group_name=envs["GROUP_NAME"],
                    consumer_name=envs["CONSUMER_NAME"], count=1, block=2000)
        if event:
            handler.constructor_task(ConstructorEvent(**event))
