import time
import datetime
import redis
from types import FunctionType
from redis.lock import Lock
from functools import wraps
from collections.abc import Callable

redis_client = redis.Redis(host="localhost", port=6379)


def single_lock(max_processing_time: datetime.timedelta):
    def wrapped(func: FunctionType) -> Callable:
        lock_time = int(max_processing_time.total_seconds())

        lock_key = f"Function:{func.__module__}.{func.__qualname__}"

        @wraps(func)
        def wrapper(*args, **kwargs):
            lock = Lock(redis=redis_client, name=lock_key, timeout=lock_time)
            acquired = lock.acquire(blocking=False)
            if not acquired:
                raise RuntimeError(
                    f"Function {func.__qualname__} is already running elsewhere"
                )
            try:
                return func(*args, **kwargs)
            finally:
                try:
                    lock.release()
                except Exception as exp:
                    print(exp)

        return wrapper

    return wrapped


def single(max_processing_time: datetime.timedelta):
    def wrapped(func: FunctionType) -> Callable:
        lock_key = f"lock:{func.__module__}.{func.__qualname__}"
        lock_time = int(max_processing_time.total_seconds())

        @wraps(func)
        def wrapper(*args, **kwargs):
            lock = redis_client.lock(name=lock_key, timeout=lock_time)
            acquired = lock.acquire(blocking=False)

            if not acquired:
                raise RuntimeError(
                    f"Func: {func.__qualname__} is already running elsewhere"
                )
            try:
                return func(*args, **kwargs)
            finally:
                lock.release()

        return wrapper

    return wrapped


@single(max_processing_time=datetime.timedelta(minutes=2))
def process_transaction():
    time.sleep(2)
