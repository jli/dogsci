# generic_default_bound.py

from random import random
from typing import Generic, Iterable, Mapping, NamedTuple, Sequence, TypeVar
from typing_extensions import reveal_type

### base classes


class BaseExperiment:
    hijinks: int

    def __init__(self, hijinks: int) -> None:
        self.hijinks = hijinks


Subexperiment = TypeVar("Subexperiment", bound=BaseExperiment)


class CompositeExperiment(Generic[Subexperiment]):
    meta_hijinks: int
    subexperiments: Mapping[str, Subexperiment]

    def __init__(self, meta_hijinks: int, subs: Iterable[Subexperiment]) -> None:
        self.meta_hijinks = meta_hijinks
        self.subexperiments = {sub.__class__.__name__: sub for sub in subs}


### subclasses


class JoeExperiment(BaseExperiment):
    hijinks: int = 10

    def __init__(self) -> None:
        pass


class JimExperiment(JoeExperiment):
    hijinks: int = 20



class AvgJoeComposite(CompositeExperiment[Subexperiment]):
    def __init__(self) -> None:
        super().__init__(meta_hijinks=1000, subs=[JimExperiment()])


### tests


jim = JimExperiment()
joe = JoeExperiment()

comp_unannotated = AvgJoeComposite()
print(reveal_type(comp_unannotated))
print(reveal_type(comp_unannotated.subexperiments))  # unknown mapping


comp_annotated = AvgJoeComposite[JoeExperiment]()
print(reveal_type(comp_annotated))
print(reveal_type(comp_annotated.subexperiments))  # knows value is JoeExperiment

