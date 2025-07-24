class Singleton:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls)

        return cls._instance


class SingletonMetaClass(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if not cls in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]


class MyClassTest(metaclass=SingletonMetaClass):
    pass


single = Singleton()
single_two = Singleton()
print(single is single_two)

a = MyClassTest()
b = MyClassTest()
print(a is b)
