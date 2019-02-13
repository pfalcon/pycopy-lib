import mpylib
import opcode

class AttrDict:

    def __init__(self, d):
        self.d = d

    def __getattr__(self, k):
        return self.d[k]


op = AttrDict(opcode.opmap)


with open("testout.mpy", "wb") as f:
    mpy = mpylib.MPYOutput(f)
    mpy.write_header(3, mpylib.MICROPY_PY_BUILTINS_STR_UNICODE | mpylib.MICROPY_OPT_CACHE_MAP_LOOKUP_IN_BYTECODE, 31)

    co = mpylib.CodeType()
    co.mpy_stacksize = 2
    co.mpy_excstacksize = 0
    co.co_flags = 0
    co.co_argcount = 0
    co.co_kwonlyargcount = 0
    co.mpy_def_pos_args = 0

    co.co_lnotab = b'\x00\x00'
    co.co_cellvars = ()

#    co.co_code = b'\x1b\xc9\x00\x00\x81d\x012\x11['

    bc = mpylib.Bytecode()
    bc.init_bc()
    bc.add(op.LOAD_NAME, "print")
    bc.add(op.LOAD_CONST_SMALL_INT, -65)
    bc.add(op.LOAD_CONST_OBJ, "string")
    bc.add(op.CALL_FUNCTION, 2, 0)
    bc.add(op.POP_TOP)
    bc.add(op.LOAD_CONST_NONE)
    bc.add(op.RETURN_VALUE)
    co.co_code = bc.get_bc()
    co.co_names = bc.co_names
    co.mpy_consts = bc.co_consts

    co.co_name = "<module>"
    co.co_filename = "testmpy.py"

    co.mpy_codeobjs = ()

    mpy.write_code(co)
