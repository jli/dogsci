from typing import Any
from pydantic import BaseModel, validator


class Bop(BaseModel):
    strs: list[str]

    # if i use a validator to accept multiple types and convert to the target
    # type, does pydantic still do any of its own type validation? like, can i
    # avoid checking that v is a list of strings here?
    #
    # yep it does! but note that you need pre=True in order to get validator to
    # run before pydantic's built-in validation, needed if you're doing
    # transparent type conversion stuff
    @validator('strs', pre=True)
    def strs__convert_to_list(cls, v: Any) -> list[str]:
        print('validating strs...')
        if isinstance(v, str):
            print('converting single str to list')
            return [v]
        return v


# always works
with_strs = Bop(strs=['a', 'b'])
print(f'{with_strs=}')

# works if pre=True
with_one_str = Bop(strs='a')
print(f'{with_one_str=}')

# always fails
# with_bad_thing = Bop(strs=1)
# print(f'{with_bad_thing=}')


class Hop(BaseModel):
    strs: list[str]

# pydantic auto-converts this
print(f'{Hop(strs=[1])!r}')
# but doesn't auto-convert from singleton to list
# print(f'{Hop(strs="a")}')
