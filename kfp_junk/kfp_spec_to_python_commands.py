#!/usr/bin/env python

from typing import Dict, List, NamedTuple

import argparse
import yaml


class Command(NamedTuple):
    name: str
    command: List[str]
    env: Dict[str, str]


def read_yaml(path: str) -> dict:
    with open(path) as f:
        return yaml.safe_load(f)


def parse_into_commands(spec_obj: dict) -> List[Command]:
    templates = spec_obj['spec']['templates']
    commands = []
    for template in templates:
        if 'dag' in template:
            continue
        if container := template.get('container'):
            commands.append(
                Command(template['name'], container['command'], parse_env(container['env']))
            )
            print('\ncommand:', commands[-1])
    return commands


def parse_env(env_items: List[dict]) -> dict:
    result = {}
    for var in env_items:
        if val := var.get('value'):
            result[var['name']] = val
        else:
            x = var.copy()
            del x['name']
            result[var['name']] = str(x)
    return result


def print_commands(commands: List[Command]) -> None:
    for c in commands:
        print('\n\n-------------------> ', c.name)
        for k, v in c.env.items():
            print(f'{k}={v}')
        print(c.command[0])
        for arg in c.command[1:]:
            print(f'\t{arg}')


def main():
    p = argparse.ArgumentParser()
    p.add_argument("yaml_spec")
    args = p.parse_args()

    spec_obj = read_yaml(args.yaml_spec)
    commands = parse_into_commands(spec_obj)
    print_commands(commands)


if __name__ == '__main__':
    main()
