# https://stackoverflow.com/questions/62294385/synchronous-generator-in-asyncio

import asyncio
import queue
import signal
from typing import Optional


SIGWINCH_QUEUE: Optional[queue.Queue] = None


def enqueue_signal(sig, _frame) -> None:
    if SIGWINCH_QUEUE is None:
        print("signal queue not initialized yet... dropping signal")
        return
    try:
        print('adding signal to queue:', sig)
        SIGWINCH_QUEUE.put_nowait(sig)
    except asyncio.QueueFull:
        print("queue full but thats ok")


def read_queue():
    global SIGWINCH_QUEUE
    SIGWINCH_QUEUE = queue.Queue(1)
    signal.signal(signal.SIGWINCH, enqueue_signal)
    while True:
        print('forever loop...')
        item = SIGWINCH_QUEUE.get()
        print("got stuff:", item)


if __name__ == "__main__":
    read_queue()
    # asyncio.run(read_queue())
