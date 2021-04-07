#!/usr/bin/env python3
import fileinput
import pprint
from collections import Counter

c = Counter(line.rstrip() for line in fileinput.input())
pprint.pprint(c)
