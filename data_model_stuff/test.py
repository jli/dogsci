class Experiment:
    @classmethod
    def setup(cls):
        print('setup', cls)

    def run(self):
        print('run', self)


exp = Experiment()

print('all the same:')
exp.run()
Experiment.run(exp)
exp.run.__func__(exp)


print('\nalso the same. when calling exp.setup, it still gets the class (exp.__class__) first arg')
Experiment.setup()
exp.setup()
Experiment.setup.__func__(Experiment)


print('\nmethods vs. functions')
print('Experiment.run', type(Experiment.run), str(Experiment.run))
print('exp.run', type(exp.run), str(exp.run))
# Experiment.run doesn't have __func__ because it's not a method
print('exp.run.__func__', type(exp.run.__func__), str(exp.run.__func__))
print()
print('Experiment.setup', type(Experiment.setup), str(Experiment.setup))
print('exp.setup', type(exp.setup), str(exp.setup))
print('Experiment.setup.__func__', type(Experiment.setup.__func__), str(Experiment.setup.__func__))
print('exp.setup.__func__', type(exp.setup.__func__), str(exp.setup.__func__))


class RandomClass:
    pass


print('\ncan use the __func__ of methods with random arguments:')
# can use the function with any class, lol
Experiment.setup.__func__(RandomClass)
# or, just like, any value
Experiment.setup.__func__(123)
