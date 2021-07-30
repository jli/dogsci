from typing import Callable


class Klass_dict:
    fields_factory: Callable[[], dict] = dict

    def __init__(self):
        # Calls dict_factory with self
        fields = self.fields_factory()
        fields.update(x=1)
        print("made fields:", fields)

# ...works?!
Klass_dict()

class Klass_lambda:
    fields_factory: Callable[[], dict] = lambda: dict()

    def __init__(self):
        # Calls dict_factory with self
        fields = self.fields_factory()
        fields.update(x=1)
        print("made fields:", fields)

# fails: lambda expects 0 params, given 1
# Klass_lambda()

def dict_factory(*args):
    print("dict_factory called with:", args)
    return {}

class Klass_function:
    fields_factory: Callable[[], dict] = dict_factory

    def __init__(self):
        fields = self.fields_factory()
        print("made fields:", fields)

# Calls dict_factory with self
Klass_function()


# syntax error
# class Klass_staticmethod:
#     @staticmethod
#     fields_factory: Callable[[], dict] = dict_factory
# 
#     def __init__(self):
#         fields = self.fields_factory()
#         print("made fields:", fields)

class Klass_staticmethod:
    @staticmethod
    def fields_factory() -> dict:
        return {}

    def __init__(self):
        fields = self.fields_factory()
        print("made fields:", fields)

Klass_staticmethod()

class Subklass_staticmethod(Klass_staticmethod):
    @staticmethod
    def fields_factory() -> dict:
        return {"subklass": "subklass"}
 
Subklass_staticmethod()

class Subklass_staticmethod_setviainit(Klass_staticmethod):
    def __init__(self):
        self.fields_factory = lambda: {"viainit": "viainit"}
        super().__init__()

Subklass_staticmethod_setviainit()

class Subklass_staticmethod_overrideviafield(Klass_staticmethod):
    fields_factory = lambda: {"viainit": "viainit"}

Subklass_staticmethod_overrideviafield()
