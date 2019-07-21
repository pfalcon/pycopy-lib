# Python to AST parser module
# This module is part of Pycopy https://github.com/pfalcon/pycopy
# and pycopy-lib https://github.com/pfalcon/pycopy-lib projects.
#
# Copyright (c) 2019 Paul Sokolovsky
#
# The MIT License
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

from utokenize import *
import utokenize
from . import types as ast


class Parser:

    def __init__(self, token_stream):
        self.tstream = token_stream
        self.tok = None
        self.next()

    def next(self):
        while True:
            self.tok = next(self.tstream)
            print("next:", self.tok)
            if self.tok.type not in (utokenize.COMMENT, utokenize.NL):
                break

    def error(self, msg="syntax error"):
        print("Error: %s" % msg)
        raise Exception

    def match(self, what):
        if isinstance(what, str):
            if self.tok.string == what and self.tok.type in (utokenize.NAME, utokenize.OP):
                self.next()
                return True
            return False

        if isinstance(what, int):
            if self.tok.type == what:
                res = self.tok.string
                self.next()
                return res
            return None

        assert False, "Unknown value type to match"

    def expect(self, what):
        res = self.match(what)
        if not res:
            if isinstance(what, int):
                self.error("expected %s" % utokenize.tok_name[what])
            else:
                self.error("expected '%s'" % what)
        return res

    @staticmethod
    def make_name(id, ctx=None):
        node = ast.Name(id=id)
        if ctx:
            node.ctx = ctx()
        return node

    def match_funcdef(self):
        lineno = self.tok.start
        self.match("def")
        name = self.expect(NAME)
        args = ast.arguments(args=[], kwonlyargs=[], kw_defaults=[], defaults=[])
        self.expect("(")
        self.expect(")")
        self.expect(":")
        body = self.match_suite()
        return ast.FunctionDef(name=name, args=args, body=body, decorator_list=[], lineno=lineno)

    def match_stmt(self):
        res = self.match_simple_stmt()
        if res: return res
        res = self.match_compound_stmt()
        if res: return [res]
        self.error("expected statement")

    def match_simple_stmt(self):
        res = self.match_small_stmt()
        if res is None:
            return None

        body = [res]
        while True:
            self.match(";")
            res = self.match_small_stmt()
            if res is None:
                break
            body.append(res)
        self.expect(NEWLINE)
        return body

    def match_small_stmt(self):
        res = self.match_pass_stmt()
        if res: return res
        res = self.match_import_stmt()
        if res: return res
        res = self.match_expr()
        if res: return ast.Expr(value=res)
        return None

    def match_compound_stmt(self):
        res = self.match_if_stmt()
        if res: return res
        res = self.match_for_stmt()
        if res: return res
        res = self.match_while_stmt()
        if res: return res
        res = self.match_with_stmt()
        if res: return res
        return None

    def match_suite(self):
        if self.match(NEWLINE):
            self.expect(INDENT)
            body = []
            while self.match(DEDENT) is None:
                body.extend(self.match_stmt())
            return body
        else:
            return self.match_simple_stmt()

    def match_pass_stmt(self):
        if self.match("pass"):
            return ast.Pass()

    def match_import_stmt(self):
        if self.match("import"):
            name = self.expect(NAME)
            asname = None
            if self.match("as"):
                asname = self.expect(NAME)
            return ast.Import(names=[ast.alias(name=name, asname=asname)])

    def match_if_stmt(self):

        def handle_if():
            expr = self.require_expr()
            self.expect(":")
            body = self.match_suite()
            orelse = []

            if self.match("elif"):
                orelse = [handle_if()]

            elif self.match("else"):
                self.expect(":")
                orelse = self.match_suite()

            return ast.If(test=expr, body=body, orelse=orelse)

        if self.match("if"):
            return handle_if()

    def match_for_stmt(self):
        if not self.match("for"):
            return None
        var = self.expect(NAME)
        self.expect("in")
        expr = self.require_expr()
        self.expect(":")
        body = self.match_suite()
        return ast.For(target=self.make_name(var, ast.Store), iter=expr,
            body=body, orelse=[])

    def match_while_stmt(self):
        if not self.match("while"):
            return None
        expr = self.require_expr()
        self.expect(":")
        body = self.match_suite()
        return ast.While(test=expr, body=body, orelse=[])

    def match_with_stmt(self):
        if not self.match("with"):
            return None
        expr = self.require_expr()
        asname = None
        if self.match("as"):
            asname = self.expect(NAME)
            asname = self.make_name(asname, ast.Store)
        self.expect(":")
        body = self.match_suite()
        return ast.With(items=[ast.withitem(context_expr=expr, optional_vars=asname)], body=body)

    def match_expr(self):
        res = self.match(NUMBER)
        if res is None:
            return res
        return ast.Num(n=int(res))

    def require_expr(self):
        res = self.match_expr()
        if res is not None: return res
        self.error("expected expression")
