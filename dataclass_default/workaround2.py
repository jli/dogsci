from dataclasses import dataclass

# requires python 3.10 :(
@dataclass(kw_only=True)
class Blah:
    x: int
    y: int
    z: int = 1

@dataclass(kw_only=True)
class SubBlah(Blah):
    u: int

print(Blah(x=2, y=3))
print(SubBlah(x=2, y=3, u=10))
