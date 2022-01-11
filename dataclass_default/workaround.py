from dataclasses import dataclass

@dataclass
class Blah:
    x: int 
    y: int
    z: int = 1

@dataclass
class SubBlah(Blah):
    # workaround: set defaults on all fields since Blah has a default. check in post_init
    u: int = None  # type: ignore

    def __post_init__(self):
        if self.u is None:
            raise ValueError('u is required, actually')

print(Blah(2, 3))
print(SubBlah(x=2, y=3, u=10))
