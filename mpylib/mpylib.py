#!/usr/bin/env python3
#
# The MIT License (MIT)
#
# Copyright (c) 2019 Paul Sokolovsky
# Copyright (c) 2016-2019 Damien P. George
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

import uio

from opcode import upyopcodes
from opcode import opmap


# Current supported .mpy version
MPY_VERSION = 3

# .mpy feature flags
MICROPY_OPT_CACHE_MAP_LOOKUP_IN_BYTECODE = 1
MICROPY_PY_BUILTINS_STR_UNICODE = 2

# Values correspond to mp_raw_code_kind_t enum
# (they don't have to, but follow mpy-tool.py for now).
MP_CODE_UNUSED = 0
MP_CODE_RESERVED = 1
MP_CODE_BYTECODE = 2
MP_CODE_NATIVE_PY = 3
MP_CODE_NATIVE_VIPER = 4
MP_CODE_NATIVE_ASM = 5

_DEBUG = 0

def dprint(*args):
    if _DEBUG:
        print(*args)


class CodeType:

    def __repr__(self):
        return '<code object %s, file "%s", line ??>' % (self.co_name, self.co_filename)


class Bytecode:

    def init_bc(self):
        self.buf = uio.BytesIO()
        self.co_names = []
        self.co_consts = []

    def add(self, opcode, *args):
        self.buf.write(bytes([opcode]))
        if args != ():
            arg = args[0]
        if opcode == opmap["LOAD_NAME"]:
            self.buf.write(bytes([0, 0]))
            # cache
            self.buf.write(bytes([0]))
            self.co_names.append(arg)
        elif opcode == opmap["CALL_FUNCTION"]:
            MPYOutput.write_uint(None, args[0] + (args[1] << 8), self.buf)
        elif opcode == opmap["LOAD_CONST_SMALL_INT"]:
            MPYOutput.write_int(None, arg, self.buf)
        elif opcode == opmap["LOAD_CONST_OBJ"]:
            MPYOutput.write_uint(None, len(self.co_consts), self.buf)
            self.co_consts.append(arg)

    def get_bc(self):
        return self.buf.getvalue()


class QStrWindow:
    def __init__(self, size):
        self.window = []
        self.size = size

    def push(self, val):
        dprint("push:", val)
        self.window = [val] + self.window[:self.size - 1]

    def access(self, idx):
        dprint("access:", idx)
        val = self.window[idx]
        self.window = [val] + self.window[:idx] + self.window[idx + 1:]
        return val


class MPYInput:

    def __init__(self, f):
        self.f = f

    def read_header(self):
        header = self.f.read(4)

        if header[0] != ord('M'):
            raise Exception('not a valid .mpy file')
        if header[1] != MPY_VERSION:
            raise Exception('incompatible .mpy version')

        self.feature_flags = header[2]
        self.small_int_bits = header[3]
        self.qstr_winsz = self.read_uint()
        self.qstr_win = QStrWindow(self.qstr_winsz)

    def has_flag(self, flag):
        return self.feature_flags & flag

    def read_uint(self):
        i = 0
        while True:
            b = self.f.read(1)[0]
            i = (i << 7) | (b & 0x7f)
            if b & 0x80 == 0:
                break
        return i

    def read_qstr(self):
        ln = self.read_uint()
        if ln == 0:
            # static qstr
            static_qstr = self.read_byte()
            dprint("static qstr:", static_qstr)
            return "<static>"
        if ln & 1:
            # qstr in table
            return self.qstr_win.access(ln >> 1)
        ln >>= 1
        qs = self.f.read(ln).decode()
        self.qstr_win.push(qs)
        return qs

    def read_obj(self):
        obj_type = self.f.read(1)
        if obj_type == b'e':
            return Ellipsis
        else:
            buf = self.f.read(self.read_uint())
            if obj_type == b's':
                return str(buf, 'utf8')
            elif obj_type == b'b':
                return buf
            elif obj_type == b'i':
                return int(str(buf, 'ascii'), 10)
            elif obj_type == b'f':
                return float(str(buf, 'ascii'))
            elif obj_type == b'c':
                return complex(str(buf, 'ascii'))
            else:
                assert 0

    def read_raw_code(self):
        co = CodeType()

        bc_len = self.read_uint()
        bytecode = self.f.read(bc_len)
        dprint("bc:", bytecode)

        co.co_name = self.read_qstr()
        co.co_filename = self.read_qstr()

        ip, ip2, prelude = self.extract_prelude(bytecode, co)
        dprint("prelude:", prelude)
        dprint(bytecode[:ip2], len(bytecode[ip2:ip]), bytecode[ip2:ip], bytecode[ip:])

        co.co_cellvars = []
        cell_info = ip2 + prelude[-1] - 1
        while bytecode[cell_info] != 0xff:
            co.co_cellvars.append(bytecode[cell_info])
            cell_info += 1
        co.co_cellvars = tuple(co.co_cellvars)

        bytecode = bytearray(bytecode)
        co.co_names = tuple(self.read_bytecode_qstrs(bytecode, ip))

        co.co_code = bytes(bytecode[ip:])

        n_obj = self.read_uint()
        n_raw_code = self.read_uint()
        dprint("n_obj=%d n_raw_code=%d" % (n_obj, n_raw_code))
        dprint("arg qstrs: %d " % (prelude[3] + prelude[4]))

        co.mpy_argnames = tuple([self.read_qstr() for _ in range(prelude[3] + prelude[4])])
        co.mpy_consts = tuple([self.read_obj() for _ in range(n_obj)])
        dprint("---")
        co.mpy_codeobjs = tuple([self.read_raw_code() for _ in range(n_raw_code)])
        co.co_consts = co.mpy_argnames + co.mpy_consts + co.mpy_codeobjs
        co.co_varnames = co.mpy_argnames

#        return (bytecode, simple_name, source_file, ip, ip2, prelude)
        return co

    def read_bytecode_qstrs(self, bytecode, ip):
        cnt = 0
        qstrs = []
        dprint("before:", bytecode)
        while ip < len(bytecode):
            typ, sz = upyopcodes.mp_opcode_format(bytecode, ip)
            if typ == 1:
                qstrs.append(self.read_qstr())
                # Patch in CodeType-local qstr id, kinda similar to CPython
                bytecode[ip + 1] = cnt & 0xff
                bytecode[ip + 2] = cnt >> 8
                cnt += 1
            ip += sz
        dprint("after:", bytecode)
        return qstrs

    @classmethod
    def extract_prelude(cls, bytecode, co):
        ip = 0
        ip, n_state = upyopcodes.decode_uint(bytecode, ip)
        ip, n_exc_stack = upyopcodes.decode_uint(bytecode, ip)
        scope_flags = bytecode[ip]; ip += 1
        n_pos_args = bytecode[ip]; ip += 1
        n_kwonly_args = bytecode[ip]; ip += 1
        n_def_pos_args = bytecode[ip]; ip += 1
        ip2, code_info_size = upyopcodes.decode_uint(bytecode, ip)
        ip += code_info_size
        while bytecode[ip] != 0xff:
            ip += 1
        ip += 1
        # ip now points to first opcode
        # ip2 points to simple_name qstr

        co.mpy_stacksize = n_state
        co.mpy_excstacksize = n_exc_stack
        co.co_stacksize = n_state - (n_pos_args + n_kwonly_args)
        co.co_argcount = n_pos_args
        co.co_kwonlyargcount = n_kwonly_args
        co.co_flags = scope_flags
        co.mpy_def_pos_args = n_def_pos_args
        return ip, ip2, (n_state, n_exc_stack, scope_flags, n_pos_args, n_kwonly_args, n_def_pos_args, code_info_size)


class MPYOutput:

    def __init__(self, f):
        self.f = f

    def write_header(self, mpy_ver, feature_flags, smallint_bits):
        self.f.write(b"M")
        self.f.write(bytes([mpy_ver, feature_flags, smallint_bits]))

    def write_uint(self, val, f=None):
        if f is None:
            f = self.f
        arr = bytearray(5)
        i = -1
        while True:
            b = val & 0x7f
            if i != -1:
                b |= 0x80
            arr[i] = b
            val >>= 7
            if val == 0:
                break
            i -= 1
        f.write(arr[i:])

    def write_int(self, val, f=None):
        if f is None:
            f = self.f
        arr = bytearray(5)
        i = -1
        while True:
            b = val & 0x7f
            if i != -1:
                b |= 0x80
            arr[i] = b
            val >>= 7
            if val == 0 or val == -1:
                break
            i -= 1

        # If needed, store sign explicitly
        if val == -1 and arr[i] & 0x40 == 0:
            i -= 1
            arr[i] = 0xff
        elif val == 0 and arr[i] & 0x40 != 0:
            i -= 1
            arr[i] = 0x80

        f.write(arr[i:])

    def write_qstr(self, s):
        s = s.encode()
        self.write_uint(len(s))
        self.f.write(s)

    def write_obj(self, o):
        if o is ...:
            self.f.write(b"e")
        elif isinstance(o, str):
            self.f.write(b"s")
            o = o.encode()
            self.write_uint(len(o))
            self.f.write(o)
        else:
            assert 0

    def pack_code(self, code):
        buf = uio.BytesIO()
        self.write_uint(code.mpy_stacksize, buf)
        self.write_uint(code.mpy_excstacksize, buf)
        buf.write(bytes([code.co_flags, code.co_argcount, code.co_kwonlyargcount, code.mpy_def_pos_args]))

        # Apparently, uPy's code_info_size includes the size of the field itself, but it's varlen field!!
        # reported as https://github.com/micropython/micropython/issues/4378
        self.write_uint(1 + 4 + len(code.co_lnotab), buf)

        # co_name qstr, will be filled in on load
        buf.write(bytes([0, 0]))
        # co_filename qstr, will be filled in on load
        buf.write(bytes([0, 0]))

        buf.write(code.co_lnotab)

        buf.write(bytes(code.co_cellvars))
        buf.write(bytes([0xff]))

        buf.write(code.co_code)

        return buf

    def write_code(self, code):
        buf = self.pack_code(code)

        bc = buf.getvalue()
        self.write_uint(len(bc))
        self.f.write(bc)

        self.write_qstr(code.co_name)
        self.write_qstr(code.co_filename)
        for n in code.co_names:
            self.write_qstr(n)

        assert code.mpy_codeobjs == ()

        self.write_uint(len(code.mpy_consts))
        self.write_uint(len(code.mpy_codeobjs))

        #co.mpy_argnames = tuple([self.read_qstr() for _ in range(prelude[3] + prelude[4])])
        for c in code.mpy_consts:
            self.write_obj(c)
