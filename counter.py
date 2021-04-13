#!/usr/bin/env python3

import argparse
import fileinput
import pprint
from collections import Counter

def main(input: str, csv: bool) -> None:
    counts = Counter(line.rstrip() for line in fileinput.input(input))
    if csv:
        for k, v in counts.items():
            print(f"{k},{v}")
    else:
        pprint.pprint(counts)


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("-csv", action="store_true", default=False)
    p.add_argument("-input", default="-")
    args = p.parse_args()
    main(args.input, args.csv)
