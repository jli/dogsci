from typing import Any


def fn_error(x: str):
    # error: Incompatible types in assignment (expression has type "int", variable has type "str")
    x = int(x)
    print(x)

def fn_rename(x: str):
    x_int = int(x)
    print(x_int)

def fn_any(x: Any):
    x = int(x)
    print(x)
