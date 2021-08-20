from typing import Optional

import tenacity
from tenacity.retry import retry_if_result
from tenacity.stop import stop_after_delay
from tenacity.wait import wait_fixed

# retry if none
def should_retry(x: Optional[int]) -> bool:
    print(f'should_retry: {x=}')
    return x is None

@tenacity.retry(
    retry=retry_if_result(should_retry),
    wait=wait_fixed(0.2),
    stop=stop_after_delay(1),
)
def try_thing() -> Optional[int]:
    ret = None
    print(f'try_thing: {ret=}')
    return ret

def try_outcomes():
    try:
        result = try_thing()
        if result is None:
            print("thing was none :(")
        else:
            print("thing was something!", result)
    except tenacity.RetryError as e:
        print("got retryerror (timeout):", e)

try_outcomes()
