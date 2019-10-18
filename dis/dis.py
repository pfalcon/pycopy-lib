#!/usr/bin/env python3
#
# "dis" module for Pycopy, https://github.com/pfalcon/pycopy
#
# The MIT License (MIT)
#
# Copyright (c) 2018-2019 Paul Sokolovsky
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

from opcode import opname, op_implicit_arg
from opcode import upyopcodes
import ustruct


def qstr_by_id(id):
    mp_obj = (id << 2) | 2
    buf = ustruct.pack("P", mp_obj)
    qstr = ustruct.unpack("O", buf)[0]
    return qstr


# If real_qstrs == False, assume that qstr-containing bytecode encode
# indexes into .co_names array. Otherwise, assume that real qstr id's
# are stored there, and use them (and don't use .co_names).
def disassemble(code, real_qstrs=False, qstr_ids=True):
    i = 0
    bc = code.co_code
    while i < len(bc):
        typ, sz = upyopcodes.mp_opcode_format(bc, i)
        # Handled by mp_opcode_format() above, but
        # config.MICROPY_OPT_CACHE_MAP_LOOKUP_IN_BYTECODE
        # must be set correctly!
        #if bc[i] in upyopcodes.hascache:
        #    sz += 1
        print("% 15d " % i, end="")

        optarg = None
        opcode_str = opname[bc[i]]

        if typ == upyopcodes.MP_OPCODE_BYTE:
            # May have implict value encoded in the opcode
            implicit = op_implicit_arg[bc[i]]
            if implicit is not None:
                optarg = implicit

        elif typ == upyopcodes.MP_OPCODE_QSTR:
            optarg = bc[i + 1] + (bc[i + 2] << 8)
            if real_qstrs:
                s = qstr_by_id(optarg)
            else:
                s = code.co_names[optarg]
            if qstr_ids:
                optarg = "%d (%s)" % (optarg, s)
            else:
                optarg = s

        elif typ == upyopcodes.MP_OPCODE_VAR_UINT:
            signed = False
            if opcode_str == "LOAD_CONST_SMALL_INT":
                signed = True
            next_i, optarg = upyopcodes.decode_varint(bc, i + 1, signed=signed)
            if opcode_str.startswith("CALL_FUNCTION"):
                optarg = "n=%d nkw=%d" % (optarg & 0xff, optarg >> 8)
            elif opcode_str in ("LOAD_CONST_OBJ", "MAKE_FUNCTION", "MAKE_FUNCTION_DEFARGS", "MAKE_CLOSURE"):
                optarg = "%d (%r)" % (optarg, code.co_consts[optarg])

            if opcode_str == "MAKE_CLOSURE":
                optarg += " n_closed=%d " % bc[next_i]

        elif typ == upyopcodes.MP_OPCODE_OFFSET:
            optarg = bc[i + 1] + (bc[i + 2] << 8) - 0x8000 + (i + sz)

        else:
            assert 0

        if optarg is not None:
            print("%-24s %s" % (opcode_str, optarg), end="")
        else:
            print("%-24s" % opcode_str, end="")

        if 0:
            print(" # t=%d sz=%d" % (typ, sz), end="")

        print()

        i += sz


def dis(code, real_qstrs=False):
    disassemble(code, real_qstrs)
    for c in code.co_consts:
        if hasattr(c, "co_code"):
            print()
            print("Disassembly of %r:" % c)
            dis(c, real_qstrs)
