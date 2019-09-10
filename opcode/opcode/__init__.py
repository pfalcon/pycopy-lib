from .upyopcodes import *
from .upyopmap import *


def stack_effect(opcode, *args):
    delta = op_stack_effect[opcode]
    if delta is not None:
        return delta
    print(opcode, *args)
    assert 0, opname[opcode]
