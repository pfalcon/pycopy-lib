import ast


class ASTUnparse(ast.NodeVisitor):

    unop_map = {
        ast.UAdd: "+",
        ast.USub: "-",
        ast.Invert: "~",
        ast.Not: "not",
    }

    def __init__(self, f):
        self.f = f
        self.level = 0

    def nl(self):
        self.f.write("\n")

    def indent(self):
        for i in range(self.level):
            self.f.write("    ")

    def with_indent(self, s):
        self.indent()
        self.f.write(s)

    def visit_suite(self, suite):
        self.level += 1
        for s in suite:
            self.visit(s)
        self.level -= 1

    def visit_While(self, node):
        self.with_indent("while ")
        self.visit(node.test)
        self.f.write(":")
        self.nl()
        self.visit_suite(node.body)
        if node.orelse:
            self.with_indent("else:")
            self.nl()
            self.visit_suite(node.orelse)

    def visit_If(self, node):
        self.with_indent("if ")
        while True:
            self.visit(node.test)
            self.f.write(":")
            self.nl()
            self.visit_suite(node.body)
            if node.orelse:
                if len(node.orelse) == 1 and isinstance(node.orelse[0], ast.If):
                    node = node.orelse[0]
                    self.with_indent("elif ")
                    continue
                self.with_indent("else:")
                self.nl()
                self.visit_suite(node.orelse)
            break

    def visit_Assign(self, node):
        self.indent()
        for n in node.targets:
            self.visit(n)
            self.f.write(" = ")
        self.visit(node.value)
        self.nl()

    def visit_Expr(self, node):
        self.indent()
        self.visit(node.value)
        self.nl()

    def visit_Continue(self, node):
        self.with_indent("continue")
        self.nl()

    def visit_Break(self, node):
        self.with_indent("break")
        self.nl()

    def visit_Pass(self, node):
        self.with_indent("pass")
        self.nl()

    def visit_UnaryOp(self, node):
        op = self.__class__.unop_map[type(node.op)]
        self.f.write(op)
        if op[0].isalpha():
            self.f.write(" ")
        self.visit(node.operand)

    def visit_Name(self, node):
        self.f.write(node.id)

    def visit_Str(self, node):
        self.f.write(repr(node.s))

    def visit_Bytes(self, node):
        self.f.write(str(node.s))

    def visit_Num(self, node):
        self.f.write(str(node.n))

    def visit_NameConstant(self, node):
        self.f.write(str(node.value))
