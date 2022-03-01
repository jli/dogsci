# https://stackoverflow.com/questions/62294385/synchronous-generator-in-asyncio

import asyncio
import queue
import signal
import threading
from typing import AsyncIterable, Iterable, Optional, TypeVar


SIGWINCH_QUEUE = queue.Queue(1)


def enqueue_signal(sig, _frame) -> None:
    try:
        print('adding signal to queue:', sig)
        SIGWINCH_QUEUE.put_nowait(sig)
    except asyncio.QueueFull:
        print("queue full but thats ok")


def install_winch_handler():
    signal.signal(signal.SIGWINCH, enqueue_signal)

def get_winch_stream_sync() -> Iterable[int]:
    while True:
        print('forever loop...')
        yield SIGWINCH_QUEUE.get()


T = TypeVar('T')

def asyncify_iterable(it: Iterable[T]) -> AsyncIterable[T]:
    """Wrap blocking iterator into an asynchronous one"""
    loop = asyncio.get_event_loop()
    q = asyncio.Queue(1)
    exception = None
    _END = object()

    async def yield_items_async():
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
    return yield_items_async()


async def main():
    install_winch_handler()
    async for i in asyncify_iterable(get_winch_stream_sync()):
        print('got winch:', i)



if __name__ == "__main__":
    asyncio.run(main())
