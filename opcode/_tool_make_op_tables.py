# This file is part of the standard library of Pycopy project, minimalist
# and resource-efficient Python3 implementation.
#
# https://github.com/pfalcon/pycopy
# https://github.com/pfalcon/pycopy-lib
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

import ure

opbase = {}
opmap = {}
opname = [None] * 256
op_implicit_arg = [None] * 256
op_stack_effect = [None] * 256


with open("../../pycopy/py/bc0.h") as f:
    for l in f:
        m = ure.match(r"#define +MP_BC_([A-Z_]+) +\((.+?)\)", l)
        if not m:
            continue
#        print(m.group(1), m.group(2))
        name, val = m.group(1), m.group(2)
        if name.endswith("_NUM") or name.endswith("_EXCESS"):
            continue
#        print(name, val)
        if name.startswith("BASE_"):
            val = int(val, 0)
            opbase[name] = val
            continue
        base = 0
        if "+" in val:
            m = ure.match(r"MP_BC_([A-Z_]+) \+ (0x[0-9a-f]+)", val)
            assert m
            base = opbase[m.group(1)]
            val = m.group(2)
        val = int(val, 0)
        val += base
        opmap[name] = val
        opname[val] = name

UNARY_OP_MULTI = opmap["UNARY_OP_MULTI"]
BINARY_OP_MULTI = opmap["BINARY_OP_MULTI"]
with open("../../pycopy/py/runtime0.h") as f:
    want_unary = True
    want_binary = True
    cnt = 0

    for l in f:
        if want_unary:
            m = ure.match(r" +MP_UNARY_OP_([A-Z_]+)", l)
            if m:
                op = m.group(1)
                if op == "NUM_BYTECODE":
                    want_unary = False
                    cnt = 0
                    continue
#                print(op)
                opname[UNARY_OP_MULTI + cnt] = "UNARY_" + op
                opmap["UNARY_" + op] = UNARY_OP_MULTI + cnt
                op_stack_effect[UNARY_OP_MULTI + cnt] = 0
                cnt += 1
        if want_binary:
            m = ure.match(r" +MP_BINARY_OP_([A-Z_]+)", l)
            if m:
                op = m.group(1)
                if op == "NUM_BYTECODE":
                    want_binary = False
                    cnt = 0
                    continue
#                print(op)
                if not op.startswith("INPLACE"):
                    op = "BINARY_" + op
                opname[BINARY_OP_MULTI + cnt] = op
                opmap[op] = BINARY_OP_MULTI + cnt
                op_stack_effect[BINARY_OP_MULTI + cnt] = -1
                cnt += 1


LOAD_CONST_SMALL_INT_MULTI = opmap["LOAD_CONST_SMALL_INT_MULTI"]
for i in range(64):
    # Drop multi from opcode name
    opname[LOAD_CONST_SMALL_INT_MULTI + i] = "LOAD_CONST_SMALL_INT"
    op_implicit_arg[LOAD_CONST_SMALL_INT_MULTI + i] = i - 16
    op_stack_effect[LOAD_CONST_SMALL_INT_MULTI + i] = 1

LOAD_FAST_MULTI = opmap["LOAD_FAST_MULTI"]
for i in range(16):
    opname[LOAD_FAST_MULTI + i] = "LOAD_FAST_MULTI"
    op_implicit_arg[LOAD_FAST_MULTI + i] = i
    op_stack_effect[LOAD_FAST_MULTI + i] = 1

STORE_FAST_MULTI = opmap["STORE_FAST_MULTI"]
for i in range(16):
    opname[STORE_FAST_MULTI + i] = "STORE_FAST_MULTI"
    op_implicit_arg[STORE_FAST_MULTI + i] = i
    op_stack_effect[STORE_FAST_MULTI + i] = -1

for k, v in opmap.items():
    # We'll override LOAD_ATTR/SUBSCR below
    if k.startswith("LOAD_"):
        op_stack_effect[v] = 1
    elif k.startswith("STORE_"):
        op_stack_effect[v] = -1
    elif k.startswith("DELETE_"):
        op_stack_effect[v] = 0
    elif k.startswith("POP_JUMP_"):
        op_stack_effect[v] = -1

op_stack_effect[opmap["LOAD_ATTR"]] = 0
op_stack_effect[opmap["STORE_ATTR"]] = -2
op_stack_effect[opmap["LOAD_SUBSCR"]] = -1
op_stack_effect[opmap["STORE_SUBSCR"]] = -3
op_stack_effect[opmap["JUMP"]] = 0
op_stack_effect[opmap["DUP_TOP"]] = 1
op_stack_effect[opmap["POP_TOP"]] = -1
op_stack_effect[opmap["ROT_TWO"]] = 0
op_stack_effect[opmap["ROT_THREE"]] = 0
op_stack_effect[opmap["RETURN_VALUE"]] = -1
op_stack_effect[opmap["MAKE_FUNCTION"]] = 1
op_stack_effect[opmap["MAKE_FUNCTION_DEFARGS"]] = -1
op_stack_effect[opmap["BUILD_MAP"]] = 1
op_stack_effect[opmap["STORE_MAP"]] = -2
op_stack_effect[opmap["IMPORT_NAME"]] = -1
op_stack_effect[opmap["GET_ITER"]] = 0
op_stack_effect[opmap["GET_ITER_STACK"]] = -1 + 4
op_stack_effect[opmap["FOR_ITER"]] = 1  # If jumps: -4, fallthru: 1
# Stack effect for linear execution
op_stack_effect[opmap["JUMP_IF_FALSE_OR_POP"]] = -1
op_stack_effect[opmap["JUMP_IF_TRUE_OR_POP"]] = -1


print("# This file is autogenerated")
print("# This file is a part of pycopy-lib project, https://github.com/pfalcon/pycopy-lib")

print("opmap = {")
for k, v in sorted(opmap.items()):
    print('"%s": 0x%x,' % (k, v))
print("}\n")

def dump_256_array(arr):
    print("[")
    cnt = 0
    for val in arr:
        if cnt % 8 == 0:
            print("# 0x%02x" % cnt)
        print("%r, " % val, end="")
        cnt += 1
        if cnt % 8 == 0:
            print()
    print("]")


print("opname = ", end="")
dump_256_array(opname)
print()

print("op_implicit_arg = ", end="")
dump_256_array(op_implicit_arg)
print()

print("op_stack_effect = ", end="")
dump_256_array(op_stack_effect)
