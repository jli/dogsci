from dataclasses import dataclass

@dataclass
class Blah:
    x: int 
    y: int
    z: int = 1

@dataclass
class SubBlah(Blah):
    # TypeError: non-default argument 'u' follows default argument
    u: int

b = Blah(2, 3)
b2 = SubBlah(x=2, y=3, u=10)
