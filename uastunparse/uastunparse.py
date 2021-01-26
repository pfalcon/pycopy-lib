import ast


class ASTUnparse(ast.NodeVisitor):

    precedence_map = {
        ast.Lambda: 10,
        ast.IfExp: 20,
        ast.Or: 30,
        ast.And: 40,
        ast.Not: 50,
        ast.Compare: 60,
        ast.BitOr: 70,
        ast.BitXor: 80,
        ast.BitAnd: 90,
        ast.LShift: 100, ast.RShift: 100,
        ast.Add: 110, ast.Sub: 110,
        ast.Mult: 120, ast.MatMult: 120, ast.Div: 120, ast.FloorDiv: 120, ast.Mod: 120,
        ast.UAdd: 130, ast.USub: 130, ast.Invert: 130,
        ast.Pow: 140,
        ast.Await: 150,
        ast.Attribute: 160,
        ast.Subscript: 160,
        ast.Call: 160,
        ast.Tuple: 170, ast.List: 170, ast.Set: 170, ast.Dict: 170,
        ast.Name: 1000, ast.Num: 1000, ast.Str: 1000,
    }

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

    def stmt_end(self, node):
        self.nl()

    def nl(self):
        self.f.write("\n")

    def indent(self):
        for i in range(self.level):
            self.f.write("    ")

    def with_indent(self, s):
        self.indent()
        self.f.write(s)

    def get_precedence(self, node):
        if isinstance(node, ast.BinOp):
            return self.__class__.precedence_map[type(node.op)]
        elif isinstance(node, ast.UnaryOp):
            return self.__class__.precedence_map[type(node.op)]
        elif isinstance(node, ast.BoolOp):
            return self.__class__.precedence_map[type(node.op)]
        else:
            return self.__class__.precedence_map[type(node)]
        assert 0

    def visit_suite(self, suite):
        self.level += 1
        for s in suite:
            self.visit(s)
        self.level -= 1

    def visit_For(self, node):
        self.with_indent("for ")
        self.visit(node.target)
        self.f.write(" in ")
        self.visit(node.iter)
        self.f.write(":")
        self.stmt_end(node)
        self.visit_suite(node.body)
        if node.orelse:
            self.with_indent("else:")
            self.nl()
            self.visit_suite(node.orelse)

    def visit_While(self, node):
        self.with_indent("while ")
        self.visit(node.test)
        self.f.write(":")
        self.stmt_end(node)
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
            self.stmt_end(node)
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

    def visit_AugAssign(self, node):
        self.indent()
        self.visit(node.target)
        self.f.write(" %s= " % self.__class__.binop_map[type(node.op)])
        self.visit(node.value)
        self.stmt_end(node)

    def visit_Assign(self, node):
        self.indent()
        for n in node.targets:
            self.visit(n)
            self.f.write(" = ")
        self.visit(node.value)
        self.stmt_end(node)

    def visit_Expr(self, node):
        self.indent()
        self.visit(node.value)
        self.stmt_end(node)

    def visit_Continue(self, node):
        self.with_indent("continue")
        self.stmt_end(node)

    def visit_Break(self, node):
        self.with_indent("break")
        self.stmt_end(node)

    def visit_Pass(self, node):
        self.with_indent("pass")
        self.stmt_end(node)

    def _visit_expr(self, parent, child, paren_on_equal=False):
        # Render a node which is a part of expression, wrapping in parens
        # if needed per precedence rules.
        prec_p = self.get_precedence(parent)
        prec_c = self.get_precedence(child)
        if paren_on_equal:
            need_parens = prec_p >= prec_c
        else:
            need_parens = prec_p > prec_c
        if need_parens:
            self.f.write("(")
        self.visit(child)
        if need_parens:
            self.f.write(")")

    def _visit_arguments(self, args):
        need_comma = False
        def comma():
            nonlocal need_comma
            if need_comma:
                self.f.write(", ")
            need_comma = True
        for a in args.args:
            comma()
            self.f.write(a.arg)

    def visit_Lambda(self, node):
        self.f.write("lambda")
        args = node.args
        if args.args:
            self.f.write(" ")
        self._visit_arguments(args)
        self.f.write(": ")
        self.visit(node.body)

    def visit_IfExp(self, node):
        self.visit(node.body)
        self.f.write(" if ")
        self.visit(node.test)
        self.f.write(" else ")
        self.visit(node.orelse)

    def visit_Call(self, node):
        self._visit_expr(node, node.func)
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
            self._visit_expr(node, v)
            first = False

    def visit_Compare(self, node):
        self._visit_expr(node, node.left, paren_on_equal=True)
        for i in range(len(node.ops)):
            op = self.__class__.cmpop_map[type(node.ops[i])]
            self.f.write(" ")
            self.f.write(op)
            self.f.write(" ")
            self._visit_expr(node, node.comparators[i], paren_on_equal=True)

    def visit_BinOp(self, node):
        op = self.__class__.binop_map[type(node.op)]
        self._visit_expr(node, node.left)
        self.f.write(" ")
        self.f.write(op)
        self.f.write(" ")
        self._visit_expr(node, node.right)

    def visit_UnaryOp(self, node):
        op = self.__class__.unop_map[type(node.op)]
        self.f.write(op)
        if op[0].isalpha():
            self.f.write(" ")
        self._visit_expr(node, node.operand)

    def visit_Await(self, node):
        self.f.write("await ")
        self._visit_expr(node, node.value)

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
