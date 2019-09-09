#!/usr/bin/env python3
#
# The MIT License (MIT)
#
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

MP_OPCODE_BYTE = 0
MP_OPCODE_QSTR = 1
MP_OPCODE_VAR_UINT = 2
MP_OPCODE_OFFSET = 3

# extra bytes:
MP_BC_MAKE_CLOSURE = 0x62
MP_BC_MAKE_CLOSURE_DEFARGS = 0x63
MP_BC_RAISE_VARARGS = 0x5c
# extra byte if caching enabled:
MP_BC_LOAD_NAME = 0x1b
MP_BC_LOAD_GLOBAL = 0x1c
MP_BC_LOAD_ATTR = 0x1d
MP_BC_STORE_ATTR = 0x26

class config: pass

config.MICROPY_OPT_CACHE_MAP_LOOKUP_IN_BYTECODE = 0


def make_opcode_format():
    def OC4(a, b, c, d):
        return a | (b << 2) | (c << 4) | (d << 6)
    U = 0
    B = 0
    Q = 1
    V = 2
    O = 3
    return bytes((
    # this table is taken verbatim from py/bc.c
    OC4(U, U, U, U), # 0x00-0x03
    OC4(U, U, U, U), # 0x04-0x07
    OC4(U, U, U, U), # 0x08-0x0b
    OC4(U, U, U, U), # 0x0c-0x0f
    OC4(B, B, B, U), # 0x10-0x13
    OC4(V, U, Q, V), # 0x14-0x17
    OC4(B, V, V, Q), # 0x18-0x1b
    OC4(Q, Q, Q, Q), # 0x1c-0x1f
    OC4(B, B, V, V), # 0x20-0x23
    OC4(Q, Q, Q, B), # 0x24-0x27
    OC4(V, V, Q, Q), # 0x28-0x2b
    OC4(U, U, U, U), # 0x2c-0x2f
    OC4(B, B, B, B), # 0x30-0x33
    OC4(B, O, O, O), # 0x34-0x37
    OC4(O, O, U, U), # 0x38-0x3b
    OC4(U, O, B, O), # 0x3c-0x3f
    OC4(O, B, B, O), # 0x40-0x43
    OC4(O, U, O, B), # 0x44-0x47
    OC4(U, U, U, U), # 0x48-0x4b
    OC4(U, U, U, U), # 0x4c-0x4f
    OC4(V, V, U, V), # 0x50-0x53
    OC4(B, U, V, V), # 0x54-0x57
    OC4(V, V, V, B), # 0x58-0x5b
    OC4(B, B, B, U), # 0x5c-0x5f
    OC4(V, V, V, V), # 0x60-0x63
    OC4(V, V, V, V), # 0x64-0x67
    OC4(Q, Q, B, U), # 0x68-0x6b
    OC4(U, U, U, U), # 0x6c-0x6f

    OC4(B, B, B, B), # 0x70-0x73
    OC4(B, B, B, B), # 0x74-0x77
    OC4(B, B, B, B), # 0x78-0x7b
    OC4(B, B, B, B), # 0x7c-0x7f
    OC4(B, B, B, B), # 0x80-0x83
    OC4(B, B, B, B), # 0x84-0x87
    OC4(B, B, B, B), # 0x88-0x8b
    OC4(B, B, B, B), # 0x8c-0x8f
    OC4(B, B, B, B), # 0x90-0x93
    OC4(B, B, B, B), # 0x94-0x97
    OC4(B, B, B, B), # 0x98-0x9b
    OC4(B, B, B, B), # 0x9c-0x9f
    OC4(B, B, B, B), # 0xa0-0xa3
    OC4(B, B, B, B), # 0xa4-0xa7
    OC4(B, B, B, B), # 0xa8-0xab
    OC4(B, B, B, B), # 0xac-0xaf

    OC4(B, B, B, B), # 0xb0-0xb3
    OC4(B, B, B, B), # 0xb4-0xb7
    OC4(B, B, B, B), # 0xb8-0xbb
    OC4(B, B, B, B), # 0xbc-0xbf

    OC4(B, B, B, B), # 0xc0-0xc3
    OC4(B, B, B, B), # 0xc4-0xc7
    OC4(B, B, B, B), # 0xc8-0xcb
    OC4(B, B, B, B), # 0xcc-0xcf

    OC4(B, B, B, B), # 0xd0-0xd3
    OC4(U, U, U, B), # 0xd4-0xd7
    OC4(B, B, B, B), # 0xd8-0xdb
    OC4(B, B, B, B), # 0xdc-0xdf

    OC4(B, B, B, B), # 0xe0-0xe3
    OC4(B, B, B, B), # 0xe4-0xe7
    OC4(B, B, B, B), # 0xe8-0xeb
    OC4(B, B, B, B), # 0xec-0xef

    OC4(B, B, B, B), # 0xf0-0xf3
    OC4(B, B, B, B), # 0xf4-0xf7
    OC4(U, U, U, U), # 0xf8-0xfb
    OC4(U, U, U, U), # 0xfc-0xff
    ))


def mp_opcode_type(opcode, opcode_format=make_opcode_format()):
    f = (opcode_format[opcode >> 2] >> (2 * (opcode & 3))) & 3
    extra = 0

    if f == MP_OPCODE_QSTR:
        if config.MICROPY_OPT_CACHE_MAP_LOOKUP_IN_BYTECODE:
            if (opcode == MP_BC_LOAD_NAME
                or opcode == MP_BC_LOAD_GLOBAL
                or opcode == MP_BC_LOAD_ATTR
                or opcode == MP_BC_STORE_ATTR):
                    extra = 1
    else:
        extra = int(
            opcode == MP_BC_RAISE_VARARGS
            or opcode == MP_BC_MAKE_CLOSURE
            or opcode == MP_BC_MAKE_CLOSURE_DEFARGS
        )

    return f, extra


def mp_opcode_format(bytecode, ip, opcode_format=make_opcode_format()):
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


hascache = (MP_BC_LOAD_NAME, MP_BC_LOAD_GLOBAL, MP_BC_LOAD_ATTR, MP_BC_STORE_ATTR)
