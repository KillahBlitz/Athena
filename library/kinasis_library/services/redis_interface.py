import kinasis_library.services.redis_interface as redis_interface
import base64

class RedisConsumer:
    def __init__(self, redis_host: str, redis_port: int, redis_password: str):
        self.redis_host = redis_host
        self.redis_port = redis_port
        self.redis_password = redis_password
        self.streams_client = self.set_connection()
        self.cache_client = self.set_cache_connection()

    def set_connection(self):
        streams_client = redis_interface.Redis(
            host=self.redis_host,
            port=self.redis_port,
            password=self.redis_password,
            decode_responses=True,
        )
        return streams_client

    def set_cache_connection(self):
        cache_client = redis_interface.Redis(
            host=self.redis_host,
            port=self.redis_port,
            password=self.redis_password,
            decode_responses=True,
        )
        return cache_client

    def ack_event(self, stream_name: str, group_name: str, msg_id: str):
        self.streams_client.xack(stream_name, group_name, msg_id)

    def start_redis_consumer(self, stream_name: str, group_name: str, consumer_name: str, 
                         count: int = 1, block: int = 2000) -> dict | None:
        try:
            self.streams_client.xgroup_create(stream_name, group_name, id="0", mkstream=True)
        except Exception:
            pass

        raw = self.streams_client.xreadgroup(
            group_name, consumer_name,
            {stream_name: ">"},
            count=count,
            block=block,
        )
        if not raw:
            return None

        _, entries = raw[0]
        msg_id, data = entries[0]
        
        self.ack_event(stream_name, group_name, msg_id)
        return data

    def event_producer(self, stream_name: str, data):
        if hasattr(data, "model_dump"):
            payload = {}
            for k, v in data.model_dump().items():
                payload[k] = base64.b64encode(v).decode() if isinstance(v, bytes) else str(v)
            data = payload
        self.streams_client.xadd(stream_name, data)