# (c) 2018-2019 Paul Sokolovsky. MIT license.
import uctypes
import ffilib
import os


libc = ffilib.libc()

mmap_ = libc.func("p", "mmap", "pLiiiL")

PROT_READ = 1
PROT_WRITE = 2
PROT_EXEC = 4
MAP_SHARED = 1
MAP_PRIVATE = 2
MAP_ANONYMOUS = 0x20


# So far, implement just buffer interface of CPython
def mmap(fd, sz, flags, prot, access=None, offset=0):
    ptr = mmap_(None, sz, prot, flags, fd, offset)
    os.check_error(ptr)
    return uctypes.bytearray_at(ptr, sz)
