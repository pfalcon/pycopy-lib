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

import sys
import ulogging
from utokenize import *
import utokenize
from . import types as ast


log = ulogging.Logger(__name__)


class Parser:

    def __init__(self, token_stream):
        self.tstream = token_stream
        self.tok = None
        self.next()

    def next(self):
        while True:
            self.tok = next(self.tstream)
            log.debug("next: %r", self.tok)
            if self.tok.type not in (utokenize.COMMENT, utokenize.NL):
                break

    def error(self, msg="syntax error"):
        sys.stderr.write("<input>:%d: error: %s\n" % (self.tok.start, msg))
        raise Exception

    # Recursively set "lvalue" node access context
    @staticmethod
    def set_ctx(t, ctx):
        if isinstance(t, list):
            for e in t:
                Parser.set_ctx(e, ctx)
        elif isinstance(t, ast.AST):
            t.ctx = ctx
            for k in t._fields:
                v = getattr(t, k, None)
                Parser.set_ctx(v, ctx)

    def check(self, what):
        if isinstance(what, str):
            if self.tok.string == what and self.tok.type in (utokenize.NAME, utokenize.OP):
                return True
            return None

        if isinstance(what, int):
            if self.tok.type == what:
                if what == utokenize.ENDMARKER:
                    return True
                res = self.tok.string
                if res == "":
                    return True
                return res
            return None

        assert False, "Unknown value type to match"

    def match(self, what):
        res = self.check(what)
        if res and what != utokenize.ENDMARKER:
            self.next()
        return res

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
        if not self.match("def"):
            return
        name = self.expect(NAME)
        args = []
        defaults = []
        vararg = None
        kwarg = None
        self.expect("(")
        while not self.match(")"):
            if self.match("*"):
                if vararg:
                    self.error(">1 vararg")
                vararg = True
            elif self.match("**"):
                if kwarg:
                    self.error(">1 kwarg")
                kwarg = True
            arg = self.expect(NAME)
            arg = ast.arg(arg=arg, annotation=None)
            if vararg:
                vararg = arg
                continue
            elif kwarg:
                kwarg = arg
                continue
            args.append(arg)
            if self.match("="):
                dflt = self.require_expr()
                defaults.append(dflt)
            self.match(",")
        self.expect(":")
        body = self.match_suite()
        arg_spec = ast.arguments(args=args, vararg=vararg, kwonlyargs=[], kw_defaults=[], kwarg=kwarg, defaults=defaults)
        return ast.FunctionDef(name=name, args=arg_spec, body=body, decorator_list=[], lineno=lineno)

    def match_classdef(self):
        lineno = self.tok.start
        if not self.match("class"):
            return
        name = self.expect(NAME)
        self.expect(":")
        body = self.match_suite()
        return ast.ClassDef(name=name, body=body, bases=[], keywords=[], decorator_list=[], lineno=lineno)

    def match_stmt(self):
        res = self.match_compound_stmt()
        if res: return [res]
        res = self.match_simple_stmt()
        if res: return res
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
        res = self.match_import_stmt()
        if res: return res

        if self.match("break"):
            return ast.Break()
        if self.match("continue"):
            return ast.Continue()
        if self.match("pass"):
            return ast.Pass()

        if self.match("return"):
            expr = self.match_expr()
            return ast.Return(value=expr)

        if self.match("raise"):
            expr = self.match_expr()
            return ast.Raise(exc=expr)

        if self.match("assert"):
            expr = self.match_expr()
            msg = None
            if self.match(","):
                msg = self.match_expr()
            return ast.Assert(test=expr, msg=msg)

        if self.match("del"):
            exprs = self.match_exprlist(ctx=ast.Del)
            return ast.Delete(targets=exprs)

        if self.match("global"):
            names = self.match_namelist()
            return ast.Global(names=names)
        if self.match("nonlocal"):
            names = self.match_namelist()
            return ast.Nonlocal(names=names)

        res = self.match_expr()
        if not res:
            return None

        if self.check("="):
            targets = []
            while self.match("="):
                self.set_ctx(res, ast.Store())
                targets.append(res)
                res = self.match_expr()
            return ast.Assign(targets=targets, value=res)

        elif self.check(OP) and self.tok.string.endswith("="):
            self.set_ctx(res, ast.Store())
            op_type = {
                "+=": ast.Add, "-=": ast.Sub, "*=": ast.Mult, "/=": ast.Div,
                "//=": ast.FloorDiv, "%=": ast.Mod, "**=": ast.Pow,
                "@=": ast.MatMult, "|=": ast.BitOr, "^=": ast.BitXor,
                "&=": ast.BitAnd, "<<=": ast.LShift, ">>=": ast.RShift,
            }[self.tok.string]
            self.next()
            val = self.match_expr()
            return ast.AugAssign(target=res, op=op_type(), value=val)

        return ast.Expr(value=res)

    def match_compound_stmt(self):
        res = self.match_if_stmt()
        if res: return res
        res = self.match_for_stmt()
        if res: return res
        res = self.match_while_stmt()
        if res: return res
        res = self.match_with_stmt()
        if res: return res
        res = self.match_try_stmt()
        if res: return res
        res = self.match_funcdef()
        if res: return res
        res = self.match_classdef()
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

    def match_import_stmt(self):
        if self.match("import"):
            name = self.match_dotted_name()
            asname = None
            if self.match("as"):
                asname = self.expect(NAME)
            return ast.Import(names=[ast.alias(name=name, asname=asname)])
        elif self.match("from"):
            level = 0
            while self.match("."):
                level += 1
            module = None
            if not self.check("import"):
                module = self.match_dotted_name()
            self.expect("import")
            if self.match("*"):
                name = "*"
            else:
                name = self.expect(NAME)
            return ast.ImportFrom(module=module, names=[ast.alias(name=name, asname=None)], level=level)

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

    def match_try_stmt(self):
        if not self.match("try"):
            return None
        self.expect(":")
        body = self.match_suite()

        handlers = []
        while self.match("except"):
            exc_sel = None
            capture_var = None
            if not self.match(":"):
                exc_sel = self.require_expr()
                if self.match("as"):
                    capture_var = self.expect(NAME)
                self.expect(":")
            exc_body = self.match_suite()
            handlers.append(ast.ExceptHandler(type=exc_sel, name=capture_var, body=exc_body))

        finalbody = []
        if self.match("finally"):
            self.expect(":")
            finalbody = self.match_suite()

        return ast.Try(body=body, handlers=handlers, orelse=[], finalbody=finalbody)


    def match_expr(self, ctx=None):
        res = self.match(NUMBER)
        if res is not None:
            return ast.Num(n=int(res))
        res = self.match(NAME)
        if res is not None:
            return self.make_name(res, ctx)

    def require_expr(self, ctx=None):
        res = self.match_expr(ctx)
        if res is not None: return res
        self.error("expected expression")

    def match_exprlist(self, ctx=None):
        res = []
        while True:
            expr = self.require_expr(ctx)
            res.append(expr)
            if not self.match(","):
                break
        return res

    def match_namelist(self):
        res = []
        while True:
            name = self.expect(NAME)
            res.append(name)
            if not self.match(","):
                break
        return res

    def match_dotted_name(self):
        name = self.match(NAME)
        if name is None:
            return None
        while self.match("."):
            name += "." + self.expect(NAME)
        return name

    def match_mod(self):
        body = []
        while not self.match(ENDMARKER):
            stmt = self.match_stmt()
            body.extend(stmt)
        return ast.Module(body=body)
