import redis
import json


class RedisQueue:
    def __init__(
        self,
        name: str = "redis_queue",
        redis_host: str = "localhost",
        redis_port: int = 6379,
    ):
        self.name = name
        self.redis = redis.Redis(host=redis_host, port=redis_port)

    def publish(self, msg: dict):
        self.redis.rpush(self.name, json.dumps(msg))

    def consume(self) -> dict:
        msg = self.redis.lpop(self.name)
        if not msg:
            return None
        return json.loads(msg)


if __name__ == "__main__":
    q = RedisQueue()
    q.publish({"a": 1})
    q.publish({"b": 2})
    q.publish({"c": 3})

    assert q.consume() == {"a": 1}
    assert q.consume() == {"b": 2}
    assert q.consume() == {"c": 3}
