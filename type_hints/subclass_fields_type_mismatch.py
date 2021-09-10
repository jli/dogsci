class Experiment:
    train_epochs: int

    def __init__(self, train_epochs: int):
        self.train_epochs = train_epochs

class ExperimentWithPresets(Experiment):
    # different type than the superclass.
    # hovering over this, Pylance says `str`.
    train_epochs = "123"

    def __init__(self):
        pass

exp = Experiment(100)
print(f'base Experiment: {exp.train_epochs=}, {type(exp.train_epochs)=}')

# when hovering over exp2.train_epochs, Pylance says `int`, which is wrong
exp2 = ExperimentWithPresets()
print(f'ExperimentWithPresets : {exp2.train_epochs=}, {type(exp2.train_epochs)=}')
