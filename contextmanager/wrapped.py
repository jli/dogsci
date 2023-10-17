from contextlib import contextmanager


class Connection:
    def __init__(self):
        self.name = "connection1"

    def __enter__(self):
        print("Connection.enter")
        return self

    def __exit__(self, _1, _2, _3):
        print("disconnecting...")


class Session:
    def __init__(self, conn):
        self.conn = conn

    def __enter__(self):
        print("Session.enter")
        return self

    def __exit__(self, _1, _2, _3):
        print("Session exiting...")


def normal():
    print("normal() about to connect.")
    with Connection() as conn, Session(conn) as sess:
        print(conn, sess)
        print("normal done.")


@contextmanager
def get_session1():
    with Connection() as conn, Session(conn) as sess:
        yield sess

def get_session2():
    return Session(Connection())

def get_session3():
    with Connection() as conn:
        return Session(conn)

def with_get_session1():
    print("\nwith_get_session1() about to connect.")
    with get_session1() as sess:
        print(sess)
        print("with_get_session1 done.")


def with_get_session2():
    print("\nwith_get_session2() about to connect.")
    with get_session2() as sess:
        print(sess)
        print("with_get_session2 done.")

def with_get_session3():
    print("\nwith_get_session3() about to connect.")
    with get_session3() as sess:
        print(sess)
        print("with_get_session3 done.")


normal()
with_get_session1()
with_get_session2()
with_get_session3()

# get_session2 and 3 leak the DB connection

# normal() about to connect.
# Connection.enter
# Session.enter
# <__main__.Connection object at 0x104fe09d0> <__main__.Session object at 0x104fe0a50>
# normal done.
# Session exiting...
# disconnecting...
# 
# with_get_session1() about to connect.
# Connection.enter
# Session.enter
# <__main__.Session object at 0x10503a550>
# with_get_session1 done.
# Session exiting...
# disconnecting...
# 
# with_get_session2() about to connect.
# Session.enter
# <__main__.Session object at 0x104fe09d0>
# with_get_session2 done.
# Session exiting...
# 
# with_get_session3() about to connect.
# Connection.enter
# disconnecting...
# Session.enter
# <__main__.Session object at 0x104fe0a50>
# with_get_session3 done.
# Session exiting...
