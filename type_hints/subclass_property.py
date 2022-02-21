class Top:
    x: int = 10

    @property
    def y(self) -> int:
        return self.x * 2


class ReplaceX(Top):
    x = 20


class ReplaceYProp(Top):
    @property
    def y(self) -> int:
        return self.x * 100


class ReplaceYConstant(Top):
    y: int = 1000
