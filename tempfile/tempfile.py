import utime
from uos2 import remove


_cnt = 0


def gettempdir():
    return "/tmp"


def mktemp():
    global _cnt
    _cnt += 1
    return "/tmp/tmp%d_%d" % (utime.time(), _cnt)


def TemporaryFile(mode="w+b"):
    n = mktemp()
    f = open(n, mode)
    remove(n)
    return f
