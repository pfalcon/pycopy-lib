# (c) 2019 Paul Sokolovsky, MIT license
__version__ = "1.1.0"

import struct
import ffi


Union, Structure, Array = 0, 0, 0
_Pointer = 0

RTLD_LOCAL, RTLD_GLOBAL = 1, 2

FUNCFLAG_CDECL = 1
FUNCFLAG_PYTHONAPI = 4
FUNCFLAG_USE_ERRNO = 8
FUNCFLAG_USE_LASTERROR = 16


class ArgumentError(Exception):
    pass


class _SimpleCData:

    def __init__(self, value=0):
        print("!", value)
        self.value = value

    def __str__(self):
        return "%s(%s)" % (self.__class__.__name__, self.value)


class CFuncPtr:

    def __init__(self, addr_or_sym):
        if isinstance(addr_or_sym, int):
            self.addr = addr_or_sym
        else:
            self.addr = addr_or_sym[1]._handle.addr(addr_or_sym[0])
        print("CFuncPtr(%r): %r" % (addr_or_sym, self.addr))

    def __call__(self, *args):
        print("*", args)
        builtin_map = {int: "i", float: "d", bytes: "P"}
        argspec = ""
        callargs = []
        for a in args:
            if isinstance(a, _SimpleCData):
                callargs.append(a.value)
                argspec += a._type_
            else:
                callargs.append(a)
                argspec += builtin_map[type(a)]
        f = ffi.func("i", self.addr, argspec)
        return f(*callargs)


def dlopen(name, mode):
    print("dlopen(%s, %x)" % (name, mode))
    return ffi.open(name)


def sizeof(typ):
    tmap = {"O": "P", "g": "q", "c": "b", "z": "P"}
    code = typ._type_
    return struct.calcsize(tmap.get(code, code))


def byref():
    raise NotImplementedError


def addressof():
    raise NotImplementedError


def alignment():
    raise NotImplementedError


def resize():
    raise NotImplementedError


def get_errno():
    raise NotImplementedError


def set_errno():
    raise NotImplementedError


def POINTER(type):
    raise NotImplementedError


def pointer(obj):
    raise NotImplementedError


_libc = ffi.open("libc.so.6")
_memmove_addr = _libc.addr("memmove")
_memset_addr = _libc.addr("memset")


_pointer_type_cache = {}
