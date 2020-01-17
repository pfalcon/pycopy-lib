# This file is part of the standard library of Pycopy project, minimalist
# and lightweight Python implementation.
#
# https://github.com/pfalcon/pycopy
# https://github.com/pfalcon/pycopy-lib
#
# The MIT License (MIT)
#
# Copyright (c) 2017-2020 Paul Sokolovsky
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

from uzlib import *
import ffilib
import uctypes


libz = ffilib.open("libz")
libc = ffilib.libc()

malloc_ = libc.func("p", "malloc", "L")
free_ = libc.func("v", "free", "p")
compressBound_ = libz.func("L", "compressBound", "L")
compress2_ = libz.func("i", "compress2", "ppPLi")


def compress(data, level=-1):
    dest_buf_sz = compressBound_(len(data))
    buf = malloc_(dest_buf_sz)
    assert buf is not None
    dest_sz_ref = ffilib.makeref("L", dest_buf_sz)
    res = compress2_(buf, dest_sz_ref, data, len(data), level)
    assert res == 0
    out = uctypes.bytes_at(buf, dest_sz_ref[0])
    free_(buf)
    return out
