#!/usr/bin/env python

"""Which fields in the KFP yaml spec take up the most space?

Answer: 2/3s is from 'metadata', mostly 'annotations'.

--> descending size (top 20):
(total)                                                                             54,702 (100.0%)
spec                                                                                54,289 (99.2%)
spec.templates                                                                      54,097 (98.9%)
spec.templates.[]                                                                   54,080 (98.9%)
spec.templates.[].metadata                                                          36,451 (66.6%)
spec.templates.[].metadata.annotations                                              30,412 (55.6%)
spec.templates.[].metadata.annotations.pipelines.kubeflow.org/component_spec        17,832 (32.6%)
spec.templates.[].container                                                         12,741 (23.3%)
spec.templates.[].container.command                                                  9,258 (16.9%)
spec.templates.[].container.command.[]                                               9,022 (16.5%)
spec.templates.[].metadata.annotations.pipelines.kubeflow.org/arguments.parameters   8,123 (14.8%)
spec.templates.[].metadata.labels                                                    5,675 (10.4%)
spec.templates.[].metadata.labels.brr_run_id                                         2,632 (4.8%)
spec.templates.[].outputs                                                            1,216 (2.2%)
spec.templates.[].metadata.annotations.pipelines.kubeflow.org/component_ref          1,176 (2.1%)
spec.templates.[].outputs.artifacts                                                  1,062 (1.9%)
spec.templates.[].outputs.artifacts.[]                                               1,038 (1.9%)
spec.templates.[].dag                                                                  915 (1.7%)
spec.templates.[].retryStrategy                                                        896 (1.6%)
spec.templates.[].dag.tasks                                                            895 (1.6%)
"""

import argparse
import json
from collections import defaultdict
from typing import Any, DefaultDict, List, Optional

import yaml


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

    path_str = ".".join(path_so_far) if path_so_far else "(total)"
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
    total_size = json_repr_size(obj)
    max_key_len = max(len(k) for k in field_sizes.keys())
    max_val_len = max(len(f"{v:,}") for v in field_sizes.values())

    def print_one(key: str, val: int) -> None:
        print(
            f'{key.ljust(max_key_len)}  {f"{val:,}".rjust(max_val_len)} ({val / total_size * 100:.1f}%)'
        )

    top_sizes = 20
    print(f"\n--> descending size (top {top_sizes}):")
    field_sizes_descending_size = sorted(
        list(field_sizes.items()), key=lambda tup: tup[1], reverse=True
    )
    for k, v in field_sizes_descending_size[:top_sizes]:
        print_one(k, v)

    print("--> alphabetical:")
    field_sizes_alpha = sorted(list(field_sizes.items()))
    for k, v in field_sizes_alpha:
        print_one(k, v)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("yaml_spec")
    args = p.parse_args()

    spec_obj = read_yaml(args.yaml_spec)
    sizes = compute_field_sizes(spec_obj)
    print_sizes(spec_obj, sizes)


if __name__ == "__main__":
    main()
