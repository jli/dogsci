from collections import defaultdict
from dataclasses import dataclass
from pprint import pformat, pprint
import sys
from typing import Any, Dict, List, NamedTuple, Optional, Tuple
from collections.abc import Mapping, Sequence
from tensorflow.core.protobuf import saved_model_pb2


def load_model(path: str):
    m = saved_model_pb2.SavedModel()
    with open(path, 'rb') as f:
        m.ParseFromString(f.read())
    return m


def list_fields(pb):
    return {f[0].name: type(f[1]) for f in pb.ListFields()}


class Node(NamedTuple):
    name: str
    op: str
    input: List[str]

class Fn(NamedTuple):
    nodes: List[Node]


def get_fns(model):
    return [
        Fn(nodes=[Node(n.name, n.op, list(n.input)) for n in f.node_def]) for f in model.meta_graphs[0].graph_def.library.function
    ]

def doit(model):
    sizes = obj_sizes(model)
    # filter out long tail
    sizes = [kv for kv in sizes if kv[1].size_bytes > 1024]
    pprint(dict(sizes[:20]), sort_dicts=False)
    return sizes


@dataclass
class Size:
    n: int
    size_bytes: int

    @staticmethod
    def empty():
        return Size(0, 0)

    def __str__(self) -> str:
        return f'{self.size_bytes/1024:,.1f} KiB ({self.n:,})'

    __repr__ = __str__

    def __iadd__(self, other) -> 'Size':
        if isinstance(other, int):
            other = Size(1, other)
        self.n += other.n
        self.size_bytes += other.size_bytes
        return self


def write(sizes: List[Tuple[str, Size]], path: str) -> None:
    with open(path, 'w') as f:
        f.write(pformat(dict(sizes), sort_dicts=False))


def obj_sizes(obj) -> List[Tuple[str, Size]]:
    sizes = _obj_sizes(obj, '').items()
    sort = sorted(sizes, key=lambda kv: (-kv[1].size_bytes, kv[0]))
    return sort


def _obj_sizes(obj, name_base) -> Dict[str, Size]:
    result: Mapping[str, Size] = defaultdict(Size.empty)

    def merge(name_base, sizes):
        tot = 0
        for k, v in sizes.items():
            result[k] += v
            if not k.endswith(' (total)'):
                tot += v.size_bytes
        result[name_base + ' (total)'] += Size(1, tot)

    if isinstance(obj, (str, int, float)):
        result[name_base] += sys.getsizeof(obj)
    elif isinstance(obj, Mapping):
        for subname, subval in obj.items():
            merge(name_base, _obj_sizes(subval, f'{name_base}.{subname}'))
    elif hasattr(obj, 'ListFields'):
        obj_dict = {f[0].name: f[1] for f in obj.ListFields()}
        for subname, subval in obj_dict.items():
            merge(name_base, _obj_sizes(subval, f'{name_base}.{subname}'))
    elif isinstance(obj, Sequence):
        for subval in obj:
            merge(name_base, _obj_sizes(subval, f'{name_base}.[]'))
    else:
        print('unknown scalar type?', name_base, type(obj))
        result[name_base] += sys.getsizeof(obj)

    return dict(result)
