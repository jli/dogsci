#!/usr/bin/env python3
"""Show the diff in 2 different `pip freeze` outputs.

For whatever reason, `delta` doesn't do a good job with pip freeze output.
This also normalizes package names, ignores comments, etc.
"""

import argparse
import pprint
import re
from typing import NamedTuple


class Package(NamedTuple):
    pkg: str  # normalized: dashes instead of underscores, all lowercase
    version: str

    def __repr__(self) -> str:
        return f"{self.pkg} == {self.version}"

    @staticmethod
    def parse(line: str) -> "Package":
        line = line.strip()
        # eg "pkg==version ; sys_platform == 'win32'"
        if " ; " in line:
            line, _ = line.split(" ; ")

        if "==" in line:
            pkg, version = line.split("==")
            return Package(_canonicalize_pkg_name(pkg), version)

        if " @ " in line:
            pkg, version = line.split(" @ ")
            return Package(_canonicalize_pkg_name(pkg), version)
        assert line
        return Package(_canonicalize_pkg_name(line), "ANY")


def _canonicalize_pkg_name(pkg: str) -> str:
    # eg testing.common.database, typing_extensions
    pkg = pkg.replace("_", "-").replace(".", "-").lower()
    # eg polars[fsspec,numpy,pandas,pyarrow]
    pkg = re.sub(
        "\[[a-z,]+\]$",
        "",
        pkg,
    )
    return pkg


def read_packages(file_path: str) -> list[Package]:
    pkgs = []
    with open(file_path) as f:
        for line in f:
            if line.strip().startswith("#") or not line.strip():
                continue
            pkgs.append(Package.parse(line))
    return pkgs


class DiffResult(NamedTuple):
    added: list[Package]
    removed: list[Package]
    changed: dict[str, tuple[Package, Package]]


def diff_packages(pkgs1: list[Package], pkgs2: list[Package]) -> list[Package]:
    pkgs1_by_name = {p.pkg: p for p in pkgs1}
    pkgs2_by_name = {p.pkg: p for p in pkgs2}

    added: list[Package] = []
    removed: list[Package] = []
    changed: dict[str, tuple[Package, Package]] = {}

    for pkg1_name, pkg1 in pkgs1_by_name.items():
        if pkg2 := pkgs2_by_name.get(pkg1_name):
            if pkg1.version != pkg2.version:
                changed[pkg1_name] = (pkg1, pkg2)
        else:
            removed.append(pkg1)

    for pkg2_name, pkg2 in pkgs2_by_name.items():
        if pkg1 := pkgs1_by_name.get(pkg2_name):
            if pkg1.version != pkg2.version:
                assert changed.get(pkg2_name) == (
                    pkg1,
                    pkg2,
                ), f"`changed` should already have {pkg1}, {pkg2}"
                # changed[pkg1_name] = (pkg1, pkg2)
        else:
            added.append(pkg2)

    return DiffResult(added, removed, changed)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("freeze_files", nargs=2, help="Files to compare")
    args = parser.parse_args()
    print(args)
    freeze1, freeze2 = args.freeze_files
    pkgs1, pkgs2 = read_packages(freeze1), read_packages(freeze2)

    diff = diff_packages(pkgs1, pkgs2)

    print(f"--- Added {len(diff.added)}---")
    pprint.pprint(diff.added)

    print(f"\n\n--- Removed {len(diff.removed)}---")
    pprint.pprint(diff.removed)

    print(f"\n\n--- Changed {len(diff.changed)} ---")
    for pkg1, pkg2 in diff.changed.values():
        print(f"{pkg1.pkg} {pkg1.version} -> {pkg2.version}")


if __name__ == "__main__":
    main()
