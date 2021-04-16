import ffilib


SIG_DFL = 0
SIG_IGN = 1

SIGINT = 2
SIGABRT = 6
SIGKILL = 9
SIGPIPE = 13
SIGTERM = 15
SIGCHLD = 17
SIGWINCH = 28

libc = ffilib.libc()

signal_i = libc.func("i", "signal", "ii")
signal_p = libc.func("i", "signal", "ip")
siginterrupt = libc.func("i", "siginterrupt", "ii")

_hmap = {}


def signal(n, handler):
    if isinstance(handler, int):
        # We don't try to remove callback from _hmap here, as we return old
        # signal handler. If it's based on callback installed earlier, it
        # can be reinstated again via next call to signal(), so we still
        # need to keep the callback around.
        return signal_i(n, handler)
    import ffi
    cb = ffi.callback("v", handler, "i")
    _hmap[n] = cb
    siginterrupt(n, True)
    return signal_p(n, cb)
