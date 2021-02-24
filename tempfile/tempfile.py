import utime
from uos2 import remove


def mktemp():
    return "/tmp/tmp%d" % utime.time()


def TemporaryFile(mode="w+b"):
    n = mktemp()
    f = open(n, mode)
    remove(n)
    return f
