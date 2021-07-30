from dataclasses import dataclass

class Base:
    path: str
    blah: bool

class Sub(Base):
    path: bool = True
    blah = True

@dataclass
class BaseDC:
    path: str
    blah: bool

class SubDC(BaseDC):
    path = "pathhere"
    blah = True

    def __init__(self):
        pass


b = Base()
s = Sub()
print(b)
print(s)
print(s.path)
# print(b.path)

# b = BaseDC()
s = SubDC()
# print(b)
print(s)
print(s.path)
