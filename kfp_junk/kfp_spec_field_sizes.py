#!/usr/bin/env python

"""Which fields in the KFP yaml spec take up the most space?"""

import argparse
import json
import pprint
from collections import defaultdict
from typing import Any, DefaultDict, Dict, List, NamedTuple, Optional

import yaml


class Command(NamedTuple):
    name: str
    command: List[str]
    env: Dict[str, str]


def read_yaml(path: str) -> dict:
    with open(path) as f:
        return yaml.safe_load(f)


def json_repr_size(obj: Any) -> int:
    return len(json.dumps(obj, separators=(",", ":")))


def compute_field_sizes(
    obj: Any,
    path_so_far: Optional[List[str]] = None,
    field_sizes: Optional[DefaultDict[str, int]] = None,
) -> DefaultDict[str, int]:
    field_sizes = field_sizes or defaultdict(int)
    path_so_far = path_so_far or []

    path_str = ".".join(path_so_far)
    field_sizes[path_str] += json_repr_size(obj)

    if isinstance(obj, dict):
        for k, v in obj.items():
            path = path_so_far + [k]
            compute_field_sizes(v, path, field_sizes)
    elif isinstance(obj, list):
        for item in obj:
            path = path_so_far + ["[]"]
            compute_field_sizes(item, path, field_sizes)
    elif isinstance(obj, (int, float, str)):
        pass
    else:
        print("unexpected type: ", type(obj))

    return field_sizes


def print_sizes(obj: Any, field_sizes: dict) -> None:
    field_sizes = dict(field_sizes)  # defaultdict->dict for printing

    total_size = json_repr_size(obj)
    print("--> full dict:")
    pprint.pprint(field_sizes)

    print("--> sorted:")
    sorted_field_sizes = sorted(
        list(field_sizes.items()), key=lambda tup: tup[1], reverse=True
    )
    for k, v in sorted_field_sizes[:20]:
        print(f"{k}: {v} ({v / total_size * 100:.1f}%)")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("yaml_spec")
    args = p.parse_args()

    spec_obj = read_yaml(args.yaml_spec)
    sizes = compute_field_sizes(spec_obj)
    print_sizes(spec_obj, sizes)


if __name__ == "__main__":
    main()
