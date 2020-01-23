# This file is part of the standard library of Pycopy project, minimalist
# and resource-efficient Python implementation.
#
# https://github.com/pfalcon/pycopy
# https://github.com/pfalcon/pycopy-lib
#
# The MIT License (MIT)
#
# Copyright (c) 2019 Paul Sokolovsky
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

from ucollections import OrderedDict
import uarray
import uctypes


FLAG_VARARGS = 0x01
FLAG_VARKEYWORDS = 0x02
FLAG_GENERATOR = 0x04
FLAG_DEFKWARGS = 0x08


mp_raw_code_t_layout = OrderedDict({
    "kind": uctypes.BFUINT32 | 0 << uctypes.BF_POS | 3 << uctypes.BF_LEN,
    "scope_flags": uctypes.BFUINT32 | 3 << uctypes.BF_POS | 7 << uctypes.BF_LEN | uctypes.PREV_OFFSET,
    "n_pos_args": uctypes.BFUINT32 | 10 << uctypes.BF_POS | 11 << uctypes.BF_LEN | uctypes.PREV_OFFSET,
    "fun_data": (uctypes.PTR, uctypes.VOID),
    "const_table": (uctypes.PTR, uctypes.VOID),
})
uctypes.calc_offsets(mp_raw_code_t_layout)


class CodeType:

    def __init__(self):
        self.co_name = "??"
        self.co_filename = "??"
        self.co_lnotab = b'\x00\x00'
        self.co_cellvars = ()
        self.mpy_cellvars = ()
        self.mpy_consts = ()
        self.co_flags = 0
        self.co_argcount = 0
        self.co_kwonlyargcount = 0
        self.mpy_def_pos_args = 0
        self.mpy_excstacksize = 0

    def __repr__(self):
        return '<code object %s, file "%s", line ??>' % (self.co_name, self.co_filename)

    def get_code(self):
        from mpylib import MPYOutput
        fake_out = MPYOutput(None)
        code = fake_out.pack_code(self).getvalue()
        return code

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
