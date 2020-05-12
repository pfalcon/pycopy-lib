import sys
import ast
import io
import ulogging
from micropython import function

from ucompiler import ucompiler
import dis
import opcode
opcode.config.MICROPY_OPT_CACHE_MAP_LOOKUP_IN_BYTECODE = 1
#ulogging.basicConfig(level=ulogging.DEBUG)


if __name__ == "__main__":
    t = ast.parse(open(sys.argv[1]).read())
    #print(ast.dump(t))

    co = ucompiler.compile_ast(t)

    #print(co.co_code)
    dis.dis(co, real_qstrs=True)

    #print(co.get_const_table())
    f = function(co.get_code(), co.get_const_table(), globals())

    print("Running code:", f)
    f()
