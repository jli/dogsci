from typing import Callable


class Test0:
    d: dict = {}

    def __init__(self, val):
        self.d.update(val=val)

t0 = Test0("t0")
print(f"{t0.d=}")
t1 = Test0("t1")
print(f"{t1.d=}")
print(f"{t0.d=}")


class Test1:
    d: dict = {}

    def __init__(self, val):
        self.d = dict(val=val)

t0 = Test1("t0")
print(f"Test1 {t0.d=}")
t1 = Test1("t1")
print(f"Test1 {t1.d=}")
print(f"Test1 {t0.d=}")


class Test1Sub(Test1):
    d = {"test1sub": 111}

    def __init__(self, val):
        self.d.update(val=val)

t0 = Test1Sub("t0")
print(f"Test1Sub {t0.d=}")
t1 = Test1Sub("t1")
print(f"Test1Sub {t1.d=}")
print(f"Test1Sub {t0.d=}")


def dict_factory(self, *args):
    print("dict_factory called with:", args)
    return {}
class Test2:
    df: Callable[["Test2"], dict] = dict_factory
    d: dict

    def __init__(self, val):
        dict_factory = self.df
        self.d = dict_factory()
        self.d.update(val=val)

t0 = Test2("t0")
print(f"Test2 {t0.d=}")
t1 = Test2("t1")
print(f"Test2 {t1.d=}")
print(f"Test2 {t0.d=}")
