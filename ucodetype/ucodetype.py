# This file is part of the standard library of Pycopy project, minimalist
# and resource-efficient Python implementation.
#
# https://github.com/pfalcon/pycopy
# https://github.com/pfalcon/pycopy-lib
#
# The MIT License (MIT)
#
# Copyright (c) 2019-2020 Paul Sokolovsky
# Bytecode prelude encoding routines (c) 2019 Damien P. George
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

import sys
from ucollections import OrderedDict
import uarray
import uctypes
import uio


FLAG_GENERATOR = 0x01
FLAG_VARKEYWORDS = 0x02
FLAG_VARARGS = 0x04
FLAG_DEFKWARGS = 0x08


mp_raw_code_t_layout = OrderedDict({
    "kind": uctypes.BFUINT32 | 0 << uctypes.BF_POS | 3 << uctypes.BF_LEN,
    "scope_flags": uctypes.BFUINT32 | 3 << uctypes.BF_POS | 7 << uctypes.BF_LEN | uctypes.PREV_OFFSET,
    "n_pos_args": uctypes.BFUINT32 | 10 << uctypes.BF_POS | 11 << uctypes.BF_LEN | uctypes.PREV_OFFSET,
    "fun_data": (uctypes.PTR, uctypes.VOID),
    "const_table": (uctypes.PTR, uctypes.VOID),
})
uctypes.calc_offsets(mp_raw_code_t_layout)


def str2qstr(s):
    return id(sys.intern(s)) >> 3


class CodeType:

    def __init__(self):
        self.co_name = "??"
        self.co_filename = "??"
        self.co_firstlineno = 0
        self.co_lnotab = b'\x00'
        self.co_cellvars = ()
        self.mpy_cellvars = ()
        self.mpy_consts = ()
        self.co_flags = 0
        self.co_argcount = 0
        self.co_kwonlyargcount = 0
        self.mpy_def_pos_args = 0
        self.mpy_excstacksize = 0

    def __repr__(self):
        return '<code object %s, file "%s", line %d>' % (self.co_name, self.co_filename, self.co_firstlineno)

    def get_code(self):
        stream = uio.BytesIO()
        self.pack_prelude(stream)
        stream.write(self.co_code)
        return stream.getvalue()

    def get_const_table(self):
        consts_arr = uarray.array("P", [0] * len(self.mpy_consts))
        for i in range(len(self.mpy_consts)):
            if isinstance(self.mpy_consts[i], CodeType):
                raw_code = self.codeobj2rawcode(self.mpy_consts[i])
                consts_arr[i] = uctypes.addressof(raw_code)
            else:
                consts_arr[i] = id(self.mpy_consts[i])
        return consts_arr

    @staticmethod
    def codeobj2rawcode(codeobj):
        buf = bytearray(uctypes.sizeof(mp_raw_code_t_layout))
        rc = uctypes.struct(uctypes.addressof(buf), mp_raw_code_t_layout)
        rc.kind = 2  # MP_CODE_BYTECODE
        rc.fun_data = uctypes.addressof(codeobj.get_code())
        rc.const_table = uctypes.addressof(codeobj.get_const_table())
        return rc

    def pack_sig(self, stream):
        S = self.mpy_stacksize
        E = self.mpy_excstacksize
        F = self.co_flags & 0xf
        A = self.co_argcount
        K = self.co_kwonlyargcount
        D = self.mpy_def_pos_args

        S -= 1
        z = (S & 0xf) << 3 | (E & 1) << 2 | (A & 3)
        while S | E | F | A | K | D:
            stream.writebin("B", z | 0x80)
            z = (F & 1) << 6 | (S & 3) << 4 | (K & 1) << 3 \
                | (A & 1) << 2 | (E & 1) << 1 | (D & 1);
            S >>= 2
            E >>= 1
            F >>= 1
            A >>= 1
            K >>= 1
            D >>= 1
        stream.writebin("B", z)

    def pack_info_size(self, stream):
        I = len(self.co_lnotab) + 4
        C = len(self.mpy_cellvars)
        while True:
            z = (I & 0x3f) << 1 | (C & 1)
            C >>= 1
            I >>= 6
            if C | I:
                z |= 0x80
                stream.writebin("B", z)
            else:
                break
        stream.writebin("B", z)

    def pack_prelude(self, stream, name_writer=None):
        self.pack_sig(stream)
        self.pack_info_size(stream)
        if name_writer:
            name_writer(self, stream)
        else:
            stream.writebin("<H", str2qstr(self.co_name))
            stream.writebin("<H", str2qstr(self.co_filename))
        stream.write(self.co_lnotab)
        stream.write(bytes(self.mpy_cellvars))
