import mpylib

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
    co.co_code = b'\x1b\xc9\x00\x00\x81d\x012\x11['

    co.co_name = "<module>"
    co.co_filename = "testmpy.py"

    co.co_names = ["print"]
    co.mpy_consts = ()
    co.mpy_codeobjs = ()

    mpy.write_code(co)
