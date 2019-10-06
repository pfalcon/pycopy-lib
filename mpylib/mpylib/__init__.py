# This file is part of the standard library of Pycopy project, minimalist
# and resource-efficient Python implementation.
#
# https://github.com/pfalcon/pycopy
# https://github.com/pfalcon/pycopy-lib
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

import sys
import uio
import ulogging

from opcode import upyopcodes
from opcode import opmap
from opcode import stack_effect
from ucodetype import CodeType
from .qstrs import static_qstr_list

# Current supported .mpy version
MPY_VERSION = 5

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

DEFAULT_QSTR_WINSZ = 32


log = ulogging.getLogger(__name__)


class AttrDict:

    def __init__(self, d):
        self.d = d

    def __getattr__(self, k):
        return self.d[k]


def get_opcode_ns():
    return AttrDict(opmap)


class Bytecode:

    def __init__(self):
        self.buf = uio.BytesIO()
        self.co_names = []
        self.co_consts = []
        self.labels = []
        self.stk_ptr = 0
        self.stk_use = 0
        self.exc_stk_ptr = 0
        self.exc_stk_use = 0
        self.only_for_mpy = False

    def add(self, opcode, *args):
        delta = stack_effect(opcode, *args)
        self.stk_ptr += delta
        assert self.stk_ptr >= 0, self.stk_ptr
        if self.stk_ptr > self.stk_use:
            self.stk_use = self.stk_ptr

        self.buf.writebin("B", opcode)
        if args != ():
            arg = args[0]
        fl, extra = upyopcodes.mp_opcode_type(opcode)

        if opcode == opmap["CALL_FUNCTION"]:
            MPYOutput.write_uint(None, args[0] + (args[1] << 8), self.buf)
        elif opcode == opmap["LOAD_CONST_SMALL_INT"]:
            MPYOutput.write_int(None, arg, self.buf)
        elif opcode == opmap["LOAD_CONST_OBJ"]:
            MPYOutput.write_uint(None, len(self.co_consts), self.buf)
            self.co_consts.append(arg)
        elif opcode == opmap["MAKE_FUNCTION"]:
            MPYOutput.write_uint(None, len(self.co_consts), self.buf)
            self.co_consts.append(arg)
        elif fl == upyopcodes.MP_OPCODE_OFFSET:
            self.buf.writebin("<H", arg)
        elif fl == upyopcodes.MP_OPCODE_QSTR:
            if self.only_for_mpy:
                self.buf.writebin("<H", 0)
            else:
                self.buf.writebin("<H", id(sys.intern(arg)) >> 2)
            # cache
            if opcode in upyopcodes.hascache:
                self.buf.writebin("B", 0)
            self.co_names.append(arg)
        elif fl == upyopcodes.MP_OPCODE_VAR_UINT:
            MPYOutput.write_uint(None, arg, self.buf)

        if opcode in (opmap["SETUP_EXCEPT"], opmap["SETUP_FINALLY"]):
            self.exc_stk_ptr += 1
            if self.exc_stk_ptr > self.exc_stk_use:
                self.exc_stk_use = self.exc_stk_ptr
        elif opcode == opmap["END_FINALLY"]:
            self.exc_stk_ptr -= 1

    def add_const(self, c):
        self.co_consts.append(c)

    def get_label(self):
        label = len(self.labels)
        self.labels.append([None])
        return label

    # Put given label at the current position in instruction stream
    def put_label(self, label):
        self.labels[label][0] = self.buf.seek(0, 1)

    def jump(self, opcode, label):
        self.add(opcode, 0)
        self.labels[label].append(self.buf.seek(0, 1))

    def load_int(self, val):
        if -15 <= val <= 47:
            self.add(0x80 + val)
        else:
            self.add(opmap["LOAD_CONST_SMALL_INT"], val)

    def get_bc(self):
        lab_id = 0
        for labl in self.labels:
            lab_pos = labl[0]
            assert lab_pos is not None, "Label #%d was not added to code" % lab_id
            for ref in labl[1:]:
                self.buf.seek(ref - 2)
                rel = lab_pos - ref + 0x8000
                assert 0 <= rel <= 0xffff
                self.buf.writebin("<H", rel)
            lab_id += 1

        self.co_code = self.buf.getvalue()
        return self.co_code


class QStrWindow:
    def __init__(self, size):
        self.window = []
        self.size = size

    def push(self, val):
        log.debug("QStrWindow.push: %s", val)
        self.window = [val] + self.window[:self.size - 1]

    def access(self, idx):
        log.debug("QStrWindow.access: %d", idx)
        val = self.window[idx]
        self.window = [val] + self.window[:idx] + self.window[idx + 1:]
        return val


class MPYInput:

    def __init__(self, f):
        self.f = f
        # Count of bytes read so far (can be reset freely). Mostly used to
        # track the size of variable-length components, while reading them.
        self.cnt = 0

    def read_header(self):
        header = self.f.read(4)

        if header[0] != ord('M'):
            raise Exception('not a valid .mpy file')
        if header[1] != MPY_VERSION:
            raise Exception('incompatible .mpy version (expected: %d, found: %d)' % (MPY_VERSION, header[1]))

        self.feature_flags = header[2]
        self.small_int_bits = header[3]
        self.qstr_winsz = self.read_uint()
        self.qstr_win = QStrWindow(self.qstr_winsz)
        log.info("read_header: feature_flags: 0x%x, smallint_bits: %d, qstr_winsz: %d",
            self.feature_flags, self.small_int_bits, self.qstr_winsz)

    def has_flag(self, flag):
        return self.feature_flags & flag

    def read_byte(self, buf=None):
        self.cnt += 1
        b = self.f.read(1)[0]
        if buf is not None:
            buf.append(b)
        return b

    def read_uint(self, buf=None):
        i = 0
        while True:
            b = self.read_byte(buf)
            i = (i << 7) | (b & 0x7f)
            if b & 0x80 == 0:
                break
        return i

    def read_qstr(self):
        ln = self.read_uint()
        if ln == 0:
            # static qstr
            static_qstr = self.read_byte()
            log.debug("static qstr: %d", static_qstr)
            return static_qstr_list[static_qstr - 1]
        if ln & 1:
            # qstr in table
            return self.qstr_win.access(ln >> 1)
        ln >>= 1
        qs = self.f.read(ln).decode()
        self.cnt += ln
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

    def read_bytecode(self, bc_len):
        qstr_cnt = 0
        qstrs = []

        self.cnt = 0
        bc_buf = bytearray()
        while len(bc_buf) < bc_len:
            opcode = self.read_byte(bc_buf)
            typ, extra = upyopcodes.mp_opcode_type(opcode)
            log.debug("%02d-%02d: opcode: %02x type: %d, extra: %d" % (self.cnt, len(bc_buf), opcode, typ, extra))
            if typ == upyopcodes.MP_OPCODE_QSTR:
                qstrs.append(self.read_qstr())
                # Patch in CodeType-local qstr id, kinda similar to CPython
                bc_buf.append(qstr_cnt & 0xff)
                bc_buf.append(qstr_cnt >> 8)
                qstr_cnt += 1
            elif typ == upyopcodes.MP_OPCODE_VAR_UINT:
                self.read_uint(bc_buf)
            elif typ == upyopcodes.MP_OPCODE_OFFSET:
                self.read_byte(bc_buf)
                self.read_byte(bc_buf)
            elif typ == upyopcodes.MP_OPCODE_BYTE:
                pass
            else:
                assert 0

            for _ in range(extra):
                self.read_byte(bc_buf)

        return bc_buf, tuple(qstrs)

    def read_raw_code(self):
        co = CodeType()

        kind_len = self.read_uint()
        kind = (kind_len & 3) + MP_CODE_BYTECODE
        bc_len = kind_len >> 2
        log.info("code obj: kind: %d, len: %d", kind, bc_len)

        assert kind == MP_CODE_BYTECODE

        self.cnt = 0
        name_idx, prelude = self.read_prelude(co)
        prelude_len = self.cnt
        log.debug("len of prelude: %d", prelude_len)
        co.co_code, co.co_names = self.read_bytecode(bc_len - prelude_len)
        log.debug("co_code: %s, co_names=%s", co.co_code, co.co_names)

        co.co_name = self.read_qstr()
        co.co_filename = self.read_qstr()

        n_obj = self.read_uint()
        n_raw_code = self.read_uint()
        log.info("n_obj=%d n_raw_code=%d", n_obj, n_raw_code)
        log.info("arg qstrs: %d", prelude[3] + prelude[4])

        co.mpy_argnames = tuple([self.read_qstr() for _ in range(prelude[3] + prelude[4])])
        co.mpy_consts = tuple([self.read_obj() for _ in range(n_obj)])
        log.info("Recursively reading %d code object(s)", n_raw_code)
        co.mpy_codeobjs = tuple([self.read_raw_code() for _ in range(n_raw_code)])
        co.co_consts = co.mpy_argnames + co.mpy_consts + co.mpy_codeobjs
        co.co_varnames = co.mpy_argnames

#        return (bytecode, simple_name, source_file, ip, ip2, prelude)
        return co

    def read_bytecode_qstrs(self, bytecode, ip):
        cnt = 0
        qstrs = []
        log.debug("before: %s", bytecode)
        while ip < len(bytecode):
            typ, sz = upyopcodes.mp_opcode_format(bytecode, ip)
            if typ == 1:
                qstrs.append(self.read_qstr())
                # Patch in CodeType-local qstr id, kinda similar to CPython
                bytecode[ip + 1] = cnt & 0xff
                bytecode[ip + 2] = cnt >> 8
                cnt += 1
            ip += sz
        log.debug("after: %s", bytecode)
        return qstrs

    @classmethod
    def extract_prelude(cls, bytecode, co):
        ip = 0
        ip, n_state = upyopcodes.decode_varint(bytecode, ip)
        ip, n_exc_stack = upyopcodes.decode_varint(bytecode, ip)
        scope_flags = bytecode[ip]; ip += 1
        n_pos_args = bytecode[ip]; ip += 1
        n_kwonly_args = bytecode[ip]; ip += 1
        n_def_pos_args = bytecode[ip]; ip += 1
        ip2, code_info_size = upyopcodes.decode_varint(bytecode, ip)
        ip += code_info_size
        while bytecode[ip] != 0xff:
            ip += 1
        ip += 1
        # ip now points to first opcode
        # ip2 points to simple_name qstr

        co.mpy_stacksize = n_state
        co.mpy_excstacksize = n_exc_stack
        # Despite CPython docs saying "co_stacksize is the required stack
        # size (including local variables)", it's actually doesn't include
        # local variables (which function arguments being such too). This
        # was reported as https://bugs.python.org/issue38316 .
        # We don't readily have a number of local vars here, so at least
        # subtract number of arguments.
        co.co_stacksize = n_state - (n_pos_args + n_kwonly_args)
        co.co_argcount = n_pos_args
        co.co_kwonlyargcount = n_kwonly_args
        co.co_flags = scope_flags
        co.mpy_def_pos_args = n_def_pos_args
        return ip, ip2, (n_state, n_exc_stack, scope_flags, n_pos_args, n_kwonly_args, n_def_pos_args, code_info_size)

    def read_prelude(self, co):
        n_state = self.read_uint()
        n_exc_stack = self.read_uint()
        scope_flags = self.read_byte()
        n_pos_args = self.read_byte()
        n_kwonly_args = self.read_byte()
        n_def_pos_args = self.read_byte()
        code_info_size_sz = self.cnt
        code_info_size = self.read_uint()
        code_info_size_sz = self.cnt - code_info_size_sz
        log.debug("n_state=%d, n_exc_stack=%d, scope_flags=0x%x, n_pos=%d, n_kwonly=%d n_def_pos=%d code_info_size=%d",
            n_state, n_exc_stack, scope_flags, n_pos_args, n_kwonly_args, n_def_pos_args, code_info_size)
        log.debug("size of varlen-encoded code_info_size field: %d", code_info_size_sz)

        for _ in range(code_info_size - code_info_size_sz):
            self.read_byte()

        cells = []
        while True:
            idx = self.read_byte()
            if idx == 255:
                break
            cells.append(idx)

        log.debug("cells: %s", cells)

        co.mpy_stacksize = n_state
        co.mpy_excstacksize = n_exc_stack
        # Despite CPython docs saying "co_stacksize is the required stack
        # size (including local variables)", it's actually doesn't include
        # local variables (which function arguments being such too). This
        # was reported as https://bugs.python.org/issue38316 .
        # We don't readily have a number of local vars here, so at least
        # subtract number of arguments.
        co.co_stacksize = n_state - (n_pos_args + n_kwonly_args)
        co.co_argcount = n_pos_args
        co.co_kwonlyargcount = n_kwonly_args
        co.co_flags = scope_flags
        co.mpy_def_pos_args = n_def_pos_args
        co.mpy_cellvars = tuple(cells)

        return -1, (n_state, n_exc_stack, scope_flags, n_pos_args, n_kwonly_args, n_def_pos_args, code_info_size)


class MPYOutput:

    def __init__(self, f):
        self.f = f

    def write_header(self, mpy_ver, feature_flags, smallint_bits, qstr_winsz=DEFAULT_QSTR_WINSZ):
        self.f.write(b"M")
        self.f.write(bytes([mpy_ver, feature_flags, smallint_bits]))
        self.write_uint(qstr_winsz)

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

    def write_qstr(self, s, buf=None):
        if buf is None:
            buf = self.f
        s = s.encode()
        self.write_uint(len(s) << 1, buf)
        buf.write(s)

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

    def pack_prelude(self, code):
        buf = uio.BytesIO()
        self.write_uint(code.mpy_stacksize, buf)
        self.write_uint(code.mpy_excstacksize, buf)
        buf.write(bytes([code.co_flags, code.co_argcount, code.co_kwonlyargcount, code.mpy_def_pos_args]))

        # Apparently, uPy's code_info_size includes the size of the field itself, but it's varlen field!!
        # reported as https://github.com/micropython/micropython/issues/4378
        self.write_uint(1 + 4 + len(code.co_lnotab), buf)

        # co_name qstr, will be filled in on load
        buf.writebin("<H", 0)
        # co_filename qstr, will be filled in on load
        buf.writebin("<H", 0)

        buf.write(code.co_lnotab)

        buf.write(bytes(code.co_cellvars))
        buf.writebin("B", 0xff)

        return buf

    def pack_code(self, code):
        buf = self.pack_prelude(code)
        buf.write(code.co_code)
        return buf

    def pack_bytecode(self, code, buf):
        bc = code.co_code
        log.debug("pack_bytecode: in: bc: %s, buf: %s", bc, buf.getvalue())
        i = 0
        qstr_i = 0
        while i < len(bc):
            opcode = bc[i]
            buf.writebin("B", opcode)
            i += 1
            typ, extra = upyopcodes.mp_opcode_type(opcode)
            log.debug("%02d: opcode: %02x type: %d, extra: %d" % (i, opcode, typ, extra))
            if typ == upyopcodes.MP_OPCODE_QSTR:
                self.write_qstr(code.co_names[qstr_i], buf)
                qstr_i += 1
                i += 2
            elif typ == upyopcodes.MP_OPCODE_VAR_UINT:
                while True:
                    b = bc[i]
                    buf.writebin("B", b)
                    i += 1
                    if b & 0x80 == 0:
                        break
            elif typ == upyopcodes.MP_OPCODE_OFFSET:
                buf.writebin("B", bc[i])
                buf.writebin("B", bc[i + 1])
                i += 2
            elif typ == upyopcodes.MP_OPCODE_BYTE:
                pass
            else:
                assert 0

            for _ in range(extra):
                buf.writebin("B", bc[i])
                i += 1

        log.debug("pack_bytecode: out: buf: %s", buf.getvalue())


    def write_code(self, code):
        buf = self.pack_prelude(code)
        # Header stores original in-memory bytecode len, not packed len
        bc_len = len(buf.getvalue()) + len(code.co_code)
        self.pack_bytecode(code, buf)

        bc = buf.getvalue()
        # len << 2 | kind
        self.write_uint(bc_len << 2)
        self.f.write(bc)

        self.write_qstr(code.co_name)
        self.write_qstr(code.co_filename)

        assert code.mpy_codeobjs == ()

        self.write_uint(len(code.mpy_consts))
        self.write_uint(len(code.mpy_codeobjs))

        #co.mpy_argnames = tuple([self.read_qstr() for _ in range(prelude[3] + prelude[4])])
        for c in code.mpy_consts:
            self.write_obj(c)
