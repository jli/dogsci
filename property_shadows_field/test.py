from dataclasses import dataclass
import os


@dataclass
class Blah:
    enable: bool

    @property
    def enable(self) -> bool:
        env_enable = os.getenv("ENABLE") is not None
        print(f"@property enable. {self.enable=}, {env_enable=}")
        return self.enable and env_enable


b_t = Blah(True)
b_f = Blah(False)

print(f"{b_t.enable=}")
print(f"{b_f.enable=}")
