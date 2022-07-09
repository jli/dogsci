class K:
    classvar = (1, 2, 3)

    def __init__(self, mult):
        self.classvar = tuple(x * mult for x in self.classvar)


# this is ok - the instance
k1 = K(10)
print(k1, k1.classvar)
k2 = K(20)
print(k2, k2.classvar)
print(k1, k1.classvar)
print(K, K.classvar)
