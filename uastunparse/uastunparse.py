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
        self.f.write(":\n")
        self.visit_suite(node.body)
        if node.orelse:
            self.with_indent("else:\n")
            self.visit_suite(node.orelse)

    def visit_If(self, node):
        self.with_indent("if ")
        while True:
            self.visit(node.test)
            self.f.write(":\n")
            self.visit_suite(node.body)
            if node.orelse:
                if len(node.orelse) == 1 and isinstance(node.orelse[0], ast.If):
                    node = node.orelse[0]
                    self.with_indent("elif ")
                    continue
                self.with_indent("else:\n")
                self.visit_suite(node.orelse)
            break

    def visit_Assign(self, node):
        self.indent()
        for n in node.targets:
            self.visit(n)
            self.f.write(" = ")
        self.visit(node.value)
        self.f.write("\n")

    def visit_Expr(self, node):
        self.indent()
        self.visit(node.value)
        self.f.write("\n")

    def visit_Continue(self, node):
        self.with_indent("continue\n")

    def visit_Break(self, node):
        self.with_indent("break\n")

    def visit_Pass(self, node):
        self.with_indent("pass\n")

    def visit_Call(self, node):
        self.visit(node.func)
        self.f.write("(")
        need_comma = False
        for a in node.args:
            if need_comma:
                self.f.write(", ")
            self.visit(a)
            need_comma = True
        for kw in node.keywords:
            if need_comma:
                self.f.write(", ")
            self.f.write(kw.arg)
            self.f.write("=")
            self.visit(kw.value)
            need_comma = True
        self.f.write(")")

    def visit_UnaryOp(self, node):
        op = self.__class__.unop_map[type(node.op)]
        self.f.write(op)
        if op[0].isalpha():
            self.f.write(" ")
        self.visit(node.operand)

    def visit_Dict(self, node):
        self.f.write("{")
        need_comma = False
        for i in range(len(node.keys)):
            if need_comma:
                self.f.write(", ")
            self.visit(node.keys[i])
            self.f.write(": ")
            self.visit(node.values[i])
            need_comma = True
        self.f.write("}")

    def _visit_seq(self, node, start, end):
        self.f.write(start)
        need_comma = False
        for v in node.elts:
            if need_comma:
                self.f.write(", ")
            self.visit(v)
            need_comma = True
        if isinstance(node, ast.Tuple) and len(node.elts) == 1:
            self.f.write(",")
        self.f.write(end)

    def visit_List(self, node):
        self._visit_seq(node, "[", "]")

    def visit_Tuple(self, node):
        self._visit_seq(node, "(", ")")

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
