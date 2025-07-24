import datetime


class MetaClassWithAddingDate(type):
    def __new__(cls, name, bases, attrs):
        attrs['created_at'] = datetime.datetime.now()
        return super().__new__(cls, name, bases, attrs)


class ClassWithDate(metaclass=MetaClassWithAddingDate):
    created_at: datetime.datetime


time = ClassWithDate()
print(time.created_at)