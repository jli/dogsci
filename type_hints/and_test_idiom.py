from typing import Optional

def intify(x: Optional[float]) -> Optional[int]:
    y: Optional[int] = 0
    # error: Incompatible types in assignment (expression has type "Optional[float]", variable has type "Optional[int]")
    # mypy can't tell that the 'and' will always kick in
    y = x and int(x)
    return y
