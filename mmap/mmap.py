# (c) 2018 Paul Sokolovsky. MIT license.
import uctypes
import ffilib


libc = ffilib.libc()

mmap_ = libc.func("p", "mmap", "pLiiiL")

PROT_READ = 1
PROT_WRITE = 2
MAP_SHARED = 1

# So far, implement just buffer interface of CPython
def mmap(fd, sz, flags, prot, access=None, offset=0):
    ptr = mmap_(None, sz, prot, flags, fd, offset)
    return uctypes.bytearray_at(ptr, sz)
