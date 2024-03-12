import contextlib
import inspect
import traceback


@contextlib.contextmanager
def wrapper():
    try:
        yield
    except Exception as e:
        print(f"XXX wrapper caught exception: {e!r}")
        print("XXX stacktrace from traceback.format_exc():")
        print(traceback.format_exc())
        print("XXX stacktrace from traceback.format_exception(e):")
        print("".join(traceback.format_exception(e)))
        print("XXX ok raising again")
        __import__("ipdb").set_trace()  # noqa  # DONOTMERGE
        raise


def div0():
    print("-> div0")
    print(1 / 0)


def do_stuff():
    print("-> do_stuff")
    div0()


def main_with_wrapper():
    print("-> main_with_wrapper")
    with wrapper():
        do_stuff()


def main_without_wrapper():
    print("-> main_without_wrapper")
    do_stuff()


if __name__ == "__main__":
    # main_without_wrapper()
    main_with_wrapper()
