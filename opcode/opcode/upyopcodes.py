# This file is part of the standard library of Pycopy project, minimalist
# and resource-efficient Python3 implementation.
#
# https://github.com/pfalcon/pycopy
# https://github.com/pfalcon/pycopy-lib
#
# The MIT License (MIT)
#
# Copyright (c) 2018-2019 Paul Sokolovsky
# Copyright (c) 2016 Damien P. George
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

from .upyopmap import opmap

MP_OPCODE_BYTE = 0
MP_OPCODE_QSTR = 1
MP_OPCODE_VAR_UINT = 2
MP_OPCODE_OFFSET = 3


class config: pass

config.MICROPY_OPT_CACHE_MAP_LOOKUP_IN_BYTECODE = 0


hascache = (opmap["LOAD_NAME"], opmap["LOAD_GLOBAL"], opmap["LOAD_ATTR"], opmap["STORE_ATTR"])


def mp_opcode_type(opcode):
    f = 0x000003a4 >> (2 * (opcode >> 4)) & 3
    extra = 0

    if f == MP_OPCODE_QSTR:
        if config.MICROPY_OPT_CACHE_MAP_LOOKUP_IN_BYTECODE:
            if opcode in hascache:
                extra = 1
    else:
        if opcode in (
            opmap["RAISE_VARARGS"], opmap["UNWIND_JUMP"],
            opmap["MAKE_CLOSURE"], opmap["MAKE_CLOSURE_DEFARGS"]
        ):
            extra = 1

    return f, extra


def mp_opcode_format(bytecode, ip):
    opcode = bytecode[ip]
    ip_start = ip
    f, extra = mp_opcode_type(opcode)
    if f == MP_OPCODE_QSTR:
        ip += 3
    else:
        ip += 1
        if f == MP_OPCODE_VAR_UINT:
            while bytecode[ip] & 0x80 != 0:
                ip += 1
            ip += 1
        elif f == MP_OPCODE_OFFSET:
            ip += 2
    ip += extra
    return f, ip - ip_start


# Decode var_uint from byte buffer at position i. Return next position
# and decoded number.
def decode_varint(bytecode, i, signed=False):
    unum = 0
    if signed:
        if bytecode[i] & 0x40:
            unum = -1
    while True:
        val = bytecode[i]
        i += 1
        unum = (unum << 7) | (val & 0x7f)
        if not (val & 0x80):
            break
    return i, unum


has_forward_offset = (
    opmap["FOR_ITER"], opmap["POP_EXCEPT_JUMP"],
    opmap["SETUP_WITH"], opmap["SETUP_EXCEPT"], opmap["SETUP_FINALLY"],
)
