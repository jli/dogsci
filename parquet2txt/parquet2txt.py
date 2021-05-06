#!/usr/bin/env python3
"""Outputs text representation of parquet file."""

import sys
import pyarrow.parquet as pq

path = sys.argv[-1]
tab = pq.read_table(path)
print(tab.to_pandas())
