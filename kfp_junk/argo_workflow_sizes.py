#!/usr/bin/env python
"""Analyzing size of Argo Workflow object.

Running into an issue where our KFP experiment is failing because the Argo
Workflow object is too large. KFP shows the error `offload node status is not
supported`.

This script tests how big the various sub-parts of the Argo Workflow object
are, and roughly how much reduction in size we can expect if we used Argo's
workflow templating to dedup the objects related to preemptible node affinity,
preemptible toleration, and retries.

The input should be from `kubectl get wf <pod-name> -o json`.
"""

from __future__ import annotations

from collections import defaultdict
import fileinput
import json
import sys
import copy

### util

def read_stdin() -> str:
    return ''.join(str(line) for line in fileinput.input('-'))

def compact_json(obj: dict) -> str:
    return json.dumps(obj, separators=(',', ':'))

def splice_out_template_keys(obj: dict, keys_to_remove: set[str]) -> tuple[int, int]:
    # print('\n--> splicing out:', keys_to_remove)
    obj = copy.deepcopy(obj)
    key_vals = {}
    key_copies = defaultdict(int)
    for template in obj['spec']['templates']:
        for k in list(template.keys()):
            if k in keys_to_remove:
                key_vals[k] = template[k]
                key_copies[k] += 1
                del template[k]

    len_key_vals = len(compact_json(key_vals))
    len_remaining = len(compact_json(obj))
    # print('removed values:', key_vals)
    # print('removed copies:', key_copies)
    # print('length of key values:', len_key_vals)
    # print('length of remaining data:', len_remaining)
    # print('approx size of templating these keys:', len_remaining + len_key_vals)
    return len_key_vals, len_remaining

# same as above, but operates on the 'spec' subobject
def splice_out_template_keys__spec(spec_obj: dict, keys_to_remove: set[str]) -> tuple[int, int]:
    # print('\n--> splicing out:', keys_to_remove)
    spec_obj = copy.deepcopy(spec_obj)
    key_vals = {}
    key_copies = defaultdict(int)
    for template in spec_obj['templates']:
        for k in list(template.keys()):
            if k in keys_to_remove:
                key_vals[k] = template[k]
                key_copies[k] += 1
                del template[k]

    len_key_vals = len(compact_json(key_vals))
    len_remaining = len(compact_json(spec_obj))
    return len_key_vals, len_remaining


### modes

def compact_and_print():
    orig = read_stdin()
    obj = json.loads(orig)
    pacted = compact_json(obj)
    print(pacted)
    print(f'orig: {len(orig)}, compact: {len(pacted)}', file=sys.stderr)


# expects full workflow object
def print_wf_toplevel_sizes(orig: str):
    len_full_orig = len(orig)
    obj = json.loads(orig)
    len_full_compact = len(compact_json(obj))
    print(f'      length of orig str: {len_full_orig:,}')
    print(f'length of compacted json: {len_full_compact:,}')
    print()
    for k in obj.keys():
        l = len(compact_json(obj[k]))
        print(f'length of {k}: {l:,} ({l/len_full_compact*100:.1f}%)')
        if k in ('spec', 'status'):
            for sub_k in obj[k].keys():
                l = len(compact_json(obj[k][sub_k]))
                print(f'length of {k}.{sub_k}: {l:,} ({l/len_full_compact*100:.1f}%)')


# expects full workflow object
def print_wf_size_variations(orig: str):
    obj = json.loads(orig)
    len_full_compact = len(compact_json(obj))

    for keys_to_splice in [
        {'affinity'},
        {'retryStrategy'},
        {'tolerations'},
        {'affinity', 'retryStrategy', 'tolerations'},
    ]:
        len_without_keys, len_remaining = splice_out_template_keys(obj, keys_to_splice)
        desc = list(keys_to_splice)[0] if len(keys_to_splice) == 1 else 'all'
        print()
        print(f'      removing {desc} completely: {len_remaining:,} ({len_remaining/len_full_compact*100:.1f}%)')
        len_templated = len_without_keys + len_remaining
        print(f'approx size if templating {desc}: {len_templated:,} ({len_templated/len_full_compact*100:.1f}%)')


# expects full workflow object. same as above, but only looking at spec subobject, which seems to fit within 1MB?
def print_wf_size_variations_speconly(orig: str):
    obj = json.loads(orig)
    spec_obj = obj['spec']
    del obj
    len_full_compact = len(compact_json(spec_obj))

    for keys_to_splice in [
        {'affinity'},
        {'retryStrategy'},
        {'tolerations'},
        {'affinity', 'retryStrategy', 'tolerations'},
    ]:
        len_without_keys, len_remaining = splice_out_template_keys__spec(spec_obj, keys_to_splice)
        desc = list(keys_to_splice)[0] if len(keys_to_splice) == 1 else 'all'
        print()
        print(f'      removing {desc} completely: {len_remaining:,} ({len_remaining/len_full_compact*100:.1f}%)')
        len_templated = len_without_keys + len_remaining
        print(f'approx size if templating {desc}: {len_templated:,} ({len_templated/len_full_compact*100:.1f}%)')


### main

def main():
    orig = read_stdin()
    print_wf_toplevel_sizes(orig)
    # this version prints percentages of the total
    # print_wf_size_variations(orig)
    # this version prints percentages of just the 'spec' object within the
    # broader workflow object (which makes the differences more dramatically)
    print_wf_size_variations_speconly(orig)


if __name__ == '__main__':
    main()
