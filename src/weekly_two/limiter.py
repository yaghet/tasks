import time
import redis


class RateLimitExceed(Exception):
    pass


class RateLimiter:
    def __init__(
        self,
        redis_host: str = "localhost",
        redis_port: int = 6379,
        key: str = "rate_limiter",
    ):
        self.redis = redis.Redis(host=redis_host, port=redis_port)
        self.key = key
        self.limit = 4
        self.period = 5

    def test(self) -> bool:
        now = time.time()
        self.redis.zremrangebyscore(self.key, 0, now - self.period)
        current = self.redis.zcard(self.key)
        if current >= self.limit:
            return False
        self.redis.zadd(self.key, {str(now): now})
        self.redis.expire(self.key, int(self.period))
        return True


def make_api_request(rate_limiter: RateLimiter):
    if not rate_limiter.test():
        raise RateLimitExceed
    else:
        pass


if __name__ == "__main__":
    rate_limiter = RateLimiter()

    for _ in range(50):
        time.sleep(1)

        try:
            make_api_request(rate_limiter)
            print("Good")
        except RateLimitExceed:
            print("Rate limit exceed!")
        else:
            print("All good")
