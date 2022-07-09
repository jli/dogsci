from typing import Any
from pydantic import BaseModel, validator


class Bop(BaseModel):
    strs: list[str]

    @validator("strs", pre=True)
    def strs__convert_to_list(cls, v: Any) -> list[str]:
        print("validating strs, convert_to_list...")
        if isinstance(v, str):
            print("converting single str to list")
            return [v]
        return v

    # this works. defining multiple validators for same field works, runs one after the other
    @validator("strs")
    def strs__should_be_short(cls, v: Any) -> list[str]:
        print("validating strs, should_be_short...")
        assert len(v) <= 2


print(f"{Bop(strs='a')=!r}")

print(f"{Bop(strs=['a', 'b'])=!r}")

print(f"{Bop(strs=['a', 'b', 'c'])=!r}")
