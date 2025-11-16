def main():
    print("main...")
    do_stuff_with_traceback_from_none()


def do_stuff_new_raise():
    print("doing stuff without with_traceback")
    try:
        fn1()
    except Exception as e:
        print(f"caught exception {e!r}, raising runtime err")
        raise RuntimeError("hello error in do_stuff_plain")

def do_stuff_with_traceback():
    print("doing stuff with with_tracebackke calling fn1")
    try:
        fn1()
    except Exception as e:
        print(f"caught exception {e!r}, raising runtime err")
        raise RuntimeError("hello error in do_stuff_plain").with_traceback(e.__traceback__)

def do_stuff_with_traceback_from_none():
    print("doing stuff with with_traceback from none")
    try:
        fn1()
    except Exception as e:
        print(f"caught exception {e!r}, raising runtime err")
        raise RuntimeError("hello error in do_stuff_plain").with_traceback(e.__traceback__) from None


def fn1():
    print("fn1 about to fail")
    1/0


main()
