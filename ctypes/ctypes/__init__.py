import ffi


class _FuncPtr:

    def __init__(self, addr):
        self.addr = addr

    def __call__(self, *args):
        f = ffi.func("i", self.addr, "P" * len(args))
        return f(*args)


class CDLL:

    def __init__(self, lib):
        self.lib = ffi.open(lib)

    def __getattr__(self, sym):
        return _FuncPtr(self.lib.addr(sym))
