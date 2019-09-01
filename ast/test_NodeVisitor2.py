import sys
import ast
import io


class Visitor(ast.NodeVisitor):

    def __init__(self, f):
        self.f = f

    def visit_Module(self, node):
        res = ""
        for s in node.body:
            res += self.visit(s)
        return res

    def visit_Assign(self, node):
        res = ""
        for n in node.targets:
            res += self.visit(n)
            res += " = "
        res += self.visit(node.value)
        res += "\n"
        return res

    def visit_Name(self, node):
        return node.id

    def visit_Num(self, node):
        return str(node.n)


SRC = """\
a = 1
a = b = 1
"""

EXP = """\
a = 1
a = b = 1
"""

t = ast.parse(SRC)

buf = io.StringIO()
visitor = Visitor(buf)
res = visitor.visit(t)

assert res == EXP
