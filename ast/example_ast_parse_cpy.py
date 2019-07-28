import sys
sys.path.pop(0)
import ast
sys.path.insert(0, ".")
import _tool_ast_pprint as ast_pprint


t = ast.parse(open(sys.argv[1]).read())
ast_pprint.dump_to_stdout(t)
