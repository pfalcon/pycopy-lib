import sys
import ast
import io


class Visitor(ast.NodeVisitor):

    def __init__(self, f):
        self.f = f

    def generic_visit(self, node):
        self.f.write(ast.dump(node))
        self.f.write("\n")
        super().generic_visit(node)

    def visit_Assign(self, node):
        for n in node.targets:
            self.visit(n)
            self.f.write(" = ")
        self.visit(node.value)
        self.f.write("\n")

    def visit_Name(self, node):
        self.f.write(node.id)

    def visit_Num(self, node):
        self.f.write(str(node.n))


SRC = """\
a = 1
a = b = 1
"""

EXP = """\
Module(body=[Assign(targets=[Name(id='a', ctx=Store())], value=Num(n=1)), Assign(targets=[Name(id='a', ctx=Store()), Name(id='b', ctx=Store())], value=Num(n=1))])
a = 1
a = b = 1
"""

t = ast.parse(SRC)

buf = io.StringIO()
visitor = Visitor(buf)
visitor.visit(t)

assert buf.getvalue() == EXP
