#!/bin/bash

### These are fine:

python -m myproject.uses_argparse
python -m myproject.uses_types


### Running with "script mode" causes a circular import error though...

python myproject/uses_argparse.py

# $ python myproject/uses_argparse.py
# Traceback (most recent call last):
#   File ".../dogsci/circular_import_when_theres_a_types_module/myproject/main.py", line 1, in <module>
#     import argparse
#   File ".../python/3.9.4/lib/python3.9/argparse.py", line 89, in <module>
#     import re as _re
#   File ".../python/3.9.4/lib/python3.9/re.py", line 124, in <module>
#     import enum
#   File ".../python/3.9.4/lib/python3.9/enum.py", line 2, in <module>
#     from types import MappingProxyType, DynamicClassAttribute
#   File ".../dogsci/circular_import_when_theres_a_types_module/myproject/types.py", line 1, in <module>
#     from typing import NamedTuple
#   File ".../python/3.9.4/lib/python3.9/typing.py", line 23, in <module>
#     import contextlib
#   File ".../python/3.9.4/lib/python3.9/contextlib.py", line 6, in <module>
#     from functools import wraps
#   File ".../python/3.9.4/lib/python3.9/functools.py", line 22, in <module>
#     from types import GenericAlias
# ImportError: cannot import name 'GenericAlias' from partially initialized module 'types' (most likely due to a circular import) (.../dogsci/circular_import_when_theres_a_types_module/myproject/types.py)



