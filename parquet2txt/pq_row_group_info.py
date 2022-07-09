#!/usr/bin/env python

from pyarrow import parquet as pq
import sys


def main():
    row_groups = 0
    for pq_path in sys.argv[1:]:
        print('\n', pq_path)
        pq_file = pq.ParquetFile(pq_path)
        print('num_rows', pq_file.metadata.num_rows)
        print('num_row_groups', pq_file.metadata.num_row_groups)
        print('~rows/group', pq_file.metadata.num_rows / pq_file.metadata.num_row_groups)
        row_groups += pq_file.metadata.num_row_groups
    print('tot_row_groups', row_groups)


if __name__ == '__main__':
    main()
