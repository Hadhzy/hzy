stored = []

def decorator(func):

    def wrapper(*args, **kwargs):
        stored.append(StoredType(func, list(args), list(kwargs)))

    return wrapper

class StoredType:
    def __init__(self, func, args, kwargs):
        self.func = func
        self.args = args[1:]
        self.kwargs = kwargs[1:]
        self.instance = args[0]

    def __str__(self):
        return f"{self.func.__name__}({self.args}{self.kwargs})"


class TestClass:

    @decorator
    def test1(self, a, b):
        print("body123123")

def execute_them(item):
    func = item.func
    args = item.args
    kwargs = item.kwargs
    instance = item.instance

    if args:
        if kwargs:
            func(instance, *args, **kwargs)
        else:
            func(instance, *args)

    if kwargs:
        if args:
            func(instance, *args, **kwargs)
        else:
            func(instance, **kwargs)



test = TestClass()
test.test1(12, 13)

for _ in stored:
    execute_them(_)

