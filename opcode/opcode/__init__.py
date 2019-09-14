# This file is part of the standard library of Pycopy project, minimalist and
# resource-efficient Python3 implementation.
# https://github.com/pfalcon/pycopy
# https://github.com/pfalcon/pycopy-lib
#
# MIT License

from .upyopcodes import *
from .upyopmap import *


def stack_effect(opcode, *args):
    delta = op_stack_effect[opcode]
    if delta is not None:
        return delta
    print(opcode, *args)
    assert 0, opname[opcode]
