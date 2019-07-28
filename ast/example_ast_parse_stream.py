import sys
import ulogging
import ast
import _tool_ast_pprint as ast_pprint


#ulogging.basicConfig(level=ulogging.DEBUG)

t = ast.parse_stream(open(sys.argv[1]))
ast_pprint.dump_to_stdout(t)
