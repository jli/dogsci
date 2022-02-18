# https://stackoverflow.com/questions/62294385/synchronous-generator-in-asyncio

import asyncio, threading
import time
from typing import Iterable

def async_wrap_iter(it):
    """Wrap blocking iterator into an asynchronous one"""
    loop = asyncio.get_event_loop()
    q = asyncio.Queue(1)
    exception = None
    _END = object()

    async def yield_queue_items():
        while True:
            next_item = await q.get()
            if next_item is _END:
                break
            yield next_item
        if exception is not None:
            # the iterator has raised, propagate the exception
            raise exception

    def iter_to_queue():
        nonlocal exception
        try:
            for item in it:
                # This runs outside the event loop thread, so we
                # must use thread-safe API to talk to the queue.
                asyncio.run_coroutine_threadsafe(q.put(item), loop).result()
        except Exception as e:
            exception = e
        finally:
            asyncio.run_coroutine_threadsafe(q.put(_END), loop).result()

    threading.Thread(target=iter_to_queue).start()
    return yield_queue_items()

def sleep_gen(n: int) -> Iterable[int]:
    for i in range(n):
        time.sleep(1)
        print(f'sleep gen slept! {i}')
        yield i


# def main():
#     for i in sleep_gen(10):
#         print('iterating over sleepgen10', i)


async def test():
    ait = async_wrap_iter(sleep_gen(10))
    async for i in ait:
        print(i)


async def heartbeat():
    while True:
        print('alive')
        await asyncio.sleep(.1)

async def main():
    asyncio.create_task(heartbeat())
    await test()


if __name__ == '__main__':
    asyncio.run(main())
