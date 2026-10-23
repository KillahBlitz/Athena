import ast
import base64
import json

import redis


_FORMAT_FIELD = "_kinasis_event_format"
_JSON_FORMAT = "json-v1"
_PAYLOAD_FIELD = "payload"


def _json_default(value):
    if isinstance(value, bytes):
        return base64.b64encode(value).decode("ascii")
    raise TypeError(f"Cannot serialize {type(value).__name__} in a Redis event")


def _decode_legacy_field(value):
    if not isinstance(value, str) or not value.lstrip().startswith(("[", "{")):
        return value
    try:
        decoded = json.loads(value)
    except json.JSONDecodeError:
        try:
            decoded = ast.literal_eval(value)
        except (ValueError, SyntaxError) as error:
            raise ValueError("Invalid container in a legacy Redis event") from error
    if not isinstance(decoded, (list, dict)):
        raise ValueError("Expected a list or object in a legacy Redis event")
    return decoded


def _decode_event(data: dict) -> dict:
    if _FORMAT_FIELD not in data:
        return {key: _decode_legacy_field(value) for key, value in data.items()}
    if data[_FORMAT_FIELD] != _JSON_FORMAT:
        raise ValueError(f"Unsupported Redis event format: {data[_FORMAT_FIELD]!r}")
    payload = data.get(_PAYLOAD_FIELD)
    if not isinstance(payload, str):
        raise ValueError("Redis event is missing its JSON payload")
    decoded = json.loads(payload)
    if not isinstance(decoded, dict):
        raise ValueError("Redis event JSON payload must be an object")
    return decoded


class RedisConsumer:
    def __init__(self, redis_host: str, redis_port: int, redis_password: str):
        self.redis_host = redis_host
        self.redis_port = redis_port
        self.redis_password = redis_password
        self.streams_client = self.set_connection()
        self.cache_client = self.set_cache_connection()

    def set_connection(self):
        streams_client = redis.Redis(
            host=self.redis_host,
            port=self.redis_port,
            password=self.redis_password,
            decode_responses=True,
        )
        return streams_client

    def set_cache_connection(self):
        cache_client = redis.Redis(
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
        except redis.exceptions.ResponseError as error:
            if not str(error).startswith("BUSYGROUP"):
                raise

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

        event = _decode_event(data)
        self.ack_event(stream_name, group_name, msg_id)
        return event

    def event_producer(self, stream_name: str, data):
        if hasattr(data, "model_dump"):
            data = data.model_dump()
        if not isinstance(data, dict):
            raise TypeError("Redis events must be a Pydantic model or a dictionary")
        payload = json.dumps(data, ensure_ascii=False, default=_json_default)
        self.streams_client.xadd(
            stream_name,
            {_FORMAT_FIELD: _JSON_FORMAT, _PAYLOAD_FIELD: payload},
        )
