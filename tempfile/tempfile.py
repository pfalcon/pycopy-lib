import utime


def mktemp():
    return "/tmp/tmp%d" % utime.time()
