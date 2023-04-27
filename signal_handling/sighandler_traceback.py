from datetime import datetime
import signal
import time
import os
import traceback


def install_interrupt_handler() -> None:
    # this seems to be an effective way to examine what's keeping the current thread busy
    def signal_handler(sig, frame):
        now = datetime.now()
        print(f"{now:%H:%M:%S} caught {sig=}. showing stack trace from {frame=}...")
        # these are the same, except with `frame`, we don't include the 2 extra lines:
        #   File ".../signal_handling/sighandler_traceback.py", line 13, in signal_handler
        #     traceback.print_stack()
        print(f"print_stack(frame) {frame=}")
        traceback.print_stack(frame)
        print("print_stack()")
        traceback.print_stack()
        print("signal handler done...")

    signal.signal(signal.SIGINT, signal_handler)


def main():
    print("main ...")
    print("installing interrupt handler")
    install_interrupt_handler()
    subfunction1()


def subfunction1():
    print("subfunction1 ...")
    subfunction2()


def subfunction2():
    print("subfunction2 ...")
    print(f"{os.getpid()=}")
    print("sleeping...")
    time.sleep(1000)


if __name__ == "__main__":
    main()
