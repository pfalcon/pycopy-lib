# This file is part of the standard library of Pycopy project, minimalist
# and lightweight Python implementation.
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

from .upyopcodes import *
from .upyopmap import *


def stack_effect(opcode, *args):
    delta = op_stack_effect[opcode]
    if delta is not None:
        return delta
    if opcode == opmap["CALL_FUNCTION"]:
        return -(1 + args[0] + args[1] * 2) + 1
    if opcode == opmap["CALL_FUNCTION_VAR_KW"]:
        return -(1 + args[0] + args[1] * 2 + 2) + 1
    if opcode == opmap["MAKE_CLOSURE"]:
        return -args[1] + 1
    if opcode == opmap["MAKE_CLOSURE_DEFARGS"]:
        return -args[1] -2 + 1
    if opcode in (opmap["BUILD_TUPLE"], opmap["BUILD_LIST"], opmap["BUILD_SET"]):
        return -args[0] + 1
    if opcode == opmap["RAISE_VARARGS"]:
        return -args[0]
    print(opcode, *args)
    assert 0, opname[opcode]
