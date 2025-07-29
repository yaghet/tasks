import functools
import unittest.mock
from collections import OrderedDict


def lru_cache(func=None, *, maxsize=128):
    if func is not None and callable(func):
        return _LRUCacheWrapper(func, maxsize)

    def wrapper(f):
        return _LRUCacheWrapper(f, maxsize)

    return wrapper


class _LRUCacheWrapper:
    def __init__(self, func, maxsize):
        self.func = func
        self.maxsize = maxsize
        self.cache = OrderedDict()
        functools.update_wrapper(self, func)

    def __call__(self, *args, **kwargs):
        key = self._make_key(*args, **kwargs)

        if key in self.cache:
            self.cache.move_to_end(key)
            return self.cache[key]

        result = self.func(*args, **kwargs)

        self.cache[key] = result
        self.cache.move_to_end(key)

        if self.maxsize is not None and len(self.cache) > self.maxsize:
            self.cache.popitem(last=False)

        return result

    @staticmethod
    def _make_key(*args, **kwargs):
        if kwargs:
            key = args + tuple(sorted(kwargs.items()))
        else:
            key = args
        return key


@lru_cache
def _sum(a: int, b: int) -> int:
    ''' Sum of two integers '''
    return a + b


@lru_cache
def sum_many(a: int, b: int, *, c: int, d: int) -> int:
    return a + b + c + d


@lru_cache(maxsize=3)
def multiply(a: int, b: int) -> int:
    return a * b


if __name__ == "__main__":
    print(_sum.__doc__)
    assert _sum(1, 2) == 3
    assert _sum(3, 4) == 7

    assert multiply(1, 2) == 2
    assert multiply(3, 4) == 12

    assert sum_many(1, 2, c=3, d=4) == 10

    mocked_func = unittest.mock.Mock()
    mocked_func.side_effect = [1, 2, 3, 4]

    decorated = lru_cache(maxsize=2)(mocked_func)
    assert decorated(1, 2) == 1
    assert decorated(1, 2) == 1
    assert decorated(3, 4) == 2
    assert decorated(3, 4) == 2
    assert decorated(5, 6) == 3
    assert decorated(5, 6) == 3
    assert decorated(1, 2) == 4
    assert mocked_func.call_count == 4
