import sys
import loadbc

# For non-MicroPython, skip current dir when loading dis, i.e. load
# system version.
if sys.implementation.name != "micropython":
    sys.path.pop(0)
import dis


with open(sys.argv[1], "rb") as f:
    code_obj = loadbc.loadbc(f)


def dump(code_obj):
    for attr in sorted(dir(code_obj)):
        if not attr.startswith("__"):
            print(attr, getattr(code_obj, attr))
    dis.disassemble(code_obj)
    for c in code_obj.co_consts:
        if hasattr(c, "co_code"):
            print()
            dump(c)


dump(code_obj)
