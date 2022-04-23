class Klass:
    mutable: dict = {}

k1= Klass()
k2 = Klass()
k1.mutable['k1'] = 'was here'
print(f"{k1.mutable=}")
print(f"{k2.mutable=}")


class KlassInit:
    mutable: dict = {}

    def __init__(self, name):
        print('initing...', name)
        self.mutable[name] = 'was here'

ki1= KlassInit('ki1')
ki2 = KlassInit('ki2')
print(f"{ki1.mutable=}")
print(f"{ki2.mutable=}")
