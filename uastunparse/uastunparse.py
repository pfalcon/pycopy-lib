import ast


class ASTUnparse(ast.NodeVisitor):

    unop_map = {
        ast.UAdd: "+",
        ast.USub: "-",
        ast.Invert: "~",
        ast.Not: "not",
    }

    binop_map = {
        ast.Add: "+",
        ast.Sub: "-",
        ast.Mult: "*",
        ast.MatMult: "@",
        ast.Div: "/",
        ast.FloorDiv: "//",
        ast.Mod: "%",
        ast.Pow: "**",
        ast.LShift: "<<",
        ast.RShift: ">>",
        ast.BitAnd: "&",
        ast.BitOr: "|",
        ast.BitXor: "^",
    }

    cmpop_map = {
        ast.Eq: "==",
        ast.NotEq: "!=",
        ast.Lt: "<",
        ast.LtE: "<=",
        ast.Gt: ">",
        ast.GtE: ">=",
        ast.Is: "is",
        ast.IsNot: "is not",
        ast.In: "in",
        ast.NotIn: "not in",
    }

    boolop_map = {
        ast.And: "and",
        ast.Or: "or",
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

    def visit_IfExp(self, node):
        self.visit(node.body)
        self.f.write(" if ")
        self.visit(node.test)
        self.f.write(" else ")
        self.visit(node.orelse)

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

    def visit_BoolOp(self, node):
        op = self.__class__.boolop_map[type(node.op)]
        first = True
        for v in node.values:
            if not first:
                self.f.write(" ")
                self.f.write(op)
                self.f.write(" ")
            self.visit(v)
            first = False

    def visit_Compare(self, node):
        self.visit(node.left)
        for i in range(len(node.ops)):
            op = self.__class__.cmpop_map[type(node.ops[i])]
            self.f.write(" ")
            self.f.write(op)
            self.f.write(" ")
            self.visit(node.comparators[i])

    def visit_BinOp(self, node):
        op = self.__class__.binop_map[type(node.op)]
        self.visit(node.left)
        self.f.write(" ")
        self.f.write(op)
        self.f.write(" ")
        self.visit(node.right)

    def visit_UnaryOp(self, node):
        op = self.__class__.unop_map[type(node.op)]
        self.f.write(op)
        if op[0].isalpha():
            self.f.write(" ")
        self.visit(node.operand)

    def visit_Subscript(self, node):
        self.visit(node.value)
        self.f.write("[")
        self.visit(node.slice)
        self.f.write("]")

    def visit_Attribute(self, node):
        self.visit(node.value)
        self.f.write(".")
        self.f.write(node.attr)

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
