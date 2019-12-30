# Python AST to Pycopy VM bytecode compiler
#
# This module is part of Pycopy https://github.com/pfalcon/pycopy
# and pycopy-lib https://github.com/pfalcon/pycopy-lib projects.
#
# Copyright (c) 2019, 2020 Paul Sokolovsky
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
import ast
import usymtable
import ucodetype
from ubytecode import Bytecode, get_opcode_ns
import mpylib
import ulogging


log = ulogging.getLogger(__name__)

opc = get_opcode_ns()


class Compiler(ast.NodeVisitor):

    def __init__(self, symtab_map, filename="<file>"):
        self.filename = filename
        self.symtab_map = symtab_map
        # Symtab for current scope
        self.symtab = None
        # Stack for (continue_label, break_label, loop_type)
        self.loop_stack = []
        self.bc = None

    def _visit_with_load_ctx(self, node):
        # Not functional style :-/. Alternatives would be to make a copy
        # of node (and modify it), patch NodeVisitor to accept/pass
        # additional params, or handle possible AST types explicitly
        # (a lot of code duplication).
        ctx = node.ctx
        node.ctx = ast.Load()
        self.visit(node)
        node.ctx = ctx

    # Visit list of statements.
    def _visit_suite(self, lst):
        s = None
        for s in lst:
            log.debug("%s", ast.dump(s))
            org_stk_ptr = self.bc.stk_ptr
            self.visit(s)
            # Each complete statement should have zero cumulative stack effect.
            assert self.bc.stk_ptr == org_stk_ptr, "%d vs %d after: %s" % (self.bc.stk_ptr, org_stk_ptr, ast.dump(s))
        return s

    def visit_Module(self, node):
        self.symtab = self.symtab_map[node]
        self.bc = Bytecode()
        self._visit_suite(node.body)
        self.bc.add(opc.LOAD_CONST_NONE)
        self.bc.add(opc.RETURN_VALUE)

    def visit_ClassDef(self, node):
        prev_symtab = self.symtab
        prev_bc = self.bc
        self.symtab = self.symtab_map[node]
        self.bc = Bytecode()

        name_interned = sys.intern(node.name)

        self.bc.add(opc.LOAD_NAME, "__name__")
        self._visit_var("__module__", ast.Store())
        self.bc.add(opc.LOAD_CONST_STRING, name_interned)
        self._visit_var("__qualname__", ast.Store())
        self._visit_suite(node.body)
        self.bc.add(opc.LOAD_CONST_NONE)
        self.bc.add(opc.RETURN_VALUE)
        co = self.bc.get_codeobj()
        co.co_name = node.name
        co.co_filename = self.filename

        self.bc = prev_bc
        self.symtab = prev_symtab

        self.bc.add(opc.LOAD_BUILD_CLASS)
        self.bc.add(opc.MAKE_FUNCTION, co)
        self.bc.add(opc.LOAD_CONST_STRING, name_interned)
        for b in node.bases:
            self.visit(b)
        self.bc.add(opc.CALL_FUNCTION, 2 + len(node.bases), 0)
        self._visit_var(node.name, ast.Store())

    def _visit_function(self, node):
        args = node.args
        assert not args.kwonlyargs
        assert not args.kw_defaults

        is_lambda = isinstance(node, ast.Lambda)

        prev_symtab = self.symtab
        prev_bc = self.bc
        self.symtab = self.symtab_map[node]
        self.symtab.finalize()
        self.bc = Bytecode()
        if args.vararg:
            self.bc.set_flag(ucodetype.FLAG_VARARGS)
        if args.kwarg:
            self.bc.set_flag(ucodetype.FLAG_VARKEYWORDS)

        # Store arg names in const table, to support calling by keyword
        for a in args.args:
            self.bc.add_const(sys.intern(a.arg))

        if isinstance(node.body, list):
            last_stmt = self._visit_suite(node.body)
            if not isinstance(last_stmt, ast.Return):
                self.bc.add(opc.LOAD_CONST_NONE)
                self.bc.add(opc.RETURN_VALUE)
        else:
            self.visit(node.body)
            self.bc.add(opc.RETURN_VALUE)

        co = self.bc.get_codeobj()
        if is_lambda:
            co.co_name = "<lambda>"
        else:
            co.co_name = node.name
        co.co_filename = self.filename
        co.co_argcount = len(args.args)
        co.mpy_def_pos_args = len(args.defaults)
        # Here mpy_stacksize corresponds to VM stack size, we also need there
        # space for locals.
        co.mpy_stacksize += len(self.symtab.all_locals)

        self.bc = prev_bc
        self.symtab = prev_symtab

        if args.defaults:
            for v in args.defaults:
                self.visit(v)
            self.bc.add(opc.BUILD_TUPLE, len(args.defaults))
            self.bc.add(opc.LOAD_NULL)
            self.bc.add(opc.MAKE_FUNCTION_DEFARGS, co)
        else:
            self.bc.add(opc.MAKE_FUNCTION, co)

        if not is_lambda:
            self._visit_var(node.name, ast.StoreConst())

    def visit_FunctionDef(self, node):
        self._visit_function(node)

    def visit_Lambda(self, node):
        self._visit_function(node)

    def visit_For(self, node):
        test_l = self.bc.get_label()
        end_l = self.bc.get_label()
        self.visit(node.iter)
        self.bc.add(opc.GET_ITER_STACK)
        self.bc.put_label(test_l)
        self.bc.jump(opc.FOR_ITER, end_l)
        self.visit(node.target)
        self.loop_stack.append((test_l, end_l, "for"))
        self._visit_suite(node.body)
        self.loop_stack.pop()
        self.bc.jump(opc.JUMP, test_l)
        self.bc.put_label(end_l)
        self.bc.stk_ptr -= 4
        self._visit_suite(node.orelse)

    def visit_While(self, node):
        test_l = self.bc.get_label()
        body_l = self.bc.get_label()
        end_l = self.bc.get_label()
        self.bc.jump(opc.JUMP, test_l)
        self.bc.put_label(body_l)
        self.loop_stack.append((test_l, end_l, "while"))
        self._visit_suite(node.body)
        self.loop_stack.pop(-1)
        self.bc.put_label(test_l)
        self.visit(node.test)
        self.bc.jump(opc.POP_JUMP_IF_TRUE, body_l)
        self._visit_suite(node.orelse)
        self.bc.put_label(end_l)

    def visit_Continue(self, node):
        assert self.loop_stack
        self.bc.jump(opc.JUMP, self.loop_stack[-1][0])

    def visit_Break(self, node):
        assert self.loop_stack
        if self.loop_stack[-1][2] == "for":
            s = self.bc.stk_ptr
            for _ in range(4):
                self.bc.add(opc.POP_TOP)
            self.bc.stk_ptr = s
        self.bc.jump(opc.JUMP, self.loop_stack[-1][1])

    def visit_If(self, node):
        self.visit(node.test)
        join_l = self.bc.get_label()
        if node.orelse:
            else_l = self.bc.get_label()
            self.bc.jump(opc.POP_JUMP_IF_FALSE, else_l)
            self._visit_suite(node.body)
            self.bc.jump(opc.JUMP, join_l)
            self.bc.put_label(else_l)
            self._visit_suite(node.orelse)
        else:
            self.bc.jump(opc.POP_JUMP_IF_FALSE, join_l)
            self._visit_suite(node.body)
        self.bc.put_label(join_l)

    def visit_ImportFrom(self, node):
        self.bc.load_int(node.level)
        for n in node.names:
            self.bc.add(opc.LOAD_CONST_STRING, n.name)
        self.bc.add(opc.BUILD_TUPLE, len(node.names))
        self.bc.add(opc.IMPORT_NAME, node.module or "")
        if len(node.names) == 1 and node.names[0].name == "*":
            self.bc.add(opc.IMPORT_STAR)
            return
        for n in node.names:
            self.bc.add(opc.IMPORT_FROM, n.name)
            self._visit_var(n.asname or n.name, ast.StoreConst())
        self.bc.add(opc.POP_TOP)

    def visit_Import(self, node):
        for n in node.names:
            self.bc.load_int(0)
            self.bc.add(opc.LOAD_CONST_NONE)
            self.bc.add(opc.IMPORT_NAME, n.name)
            if n.asname:
                comps = n.name.split(".")
                for c in comps[1:]:
                    self.bc.add(opc.LOAD_ATTR, c)
                self._visit_var(n.asname, ast.StoreConst())
            else:
                self._visit_var(n.name.split(".", 1)[0], ast.StoreConst())

    def visit_Yield(self, node):
        self.bc.set_flag(ucodetype.FLAG_GENERATOR)
        if node.value is None:
            self.bc.add(opc.LOAD_CONST_NONE)
        else:
            self.visit(node.value)
        self.bc.add(opc.YIELD_VALUE)

    def visit_YieldFrom(self, node):
        self.bc.set_flag(ucodetype.FLAG_GENERATOR)
        self.visit(node.value)
        self.bc.add(opc.GET_ITER)
        self.bc.add(opc.LOAD_CONST_NONE)
        self.bc.add(opc.YIELD_FROM)

    def visit_Assert(self, node):
        self.visit(node.test)
        true_l = self.bc.get_label()
        self.bc.jump(opc.POP_JUMP_IF_TRUE, true_l)
        self.bc.add(opc.LOAD_GLOBAL, "AssertionError")
        if node.msg is not None:
            self.visit(node.msg)
            self.bc.add(opc.CALL_FUNCTION, 1, 0)
        self.bc.add(opc.RAISE_VARARGS, 1)
        self.bc.put_label(true_l)

    def visit_Raise(self, node):
        arg = 0
        if node.exc is not None:
            self.visit(node.exc)
            arg = 1
            if node.cause is not None:
                self.visit(node.cause)
                arg = 2
        self.bc.add(opc.RAISE_VARARGS, arg)

    def visit_Return(self, node):
        if node.value is None:
            self.bc.add(opc.LOAD_CONST_NONE)
        else:
            self.visit(node.value)
        self.bc.add(opc.RETURN_VALUE)

    def visit_AugAssign(self, node):
        inplaceop_map = {
            ast.Add: opc.INPLACE_ADD,
            ast.Sub: opc.INPLACE_SUBTRACT,
            ast.Mult: opc.INPLACE_MULTIPLY,
            ast.MatMult: opc.INPLACE_MAT_MULTIPLY,
            ast.Div: opc.INPLACE_TRUE_DIVIDE,
            ast.FloorDiv: opc.INPLACE_FLOOR_DIVIDE,
            ast.Mod: opc.INPLACE_MODULO,
            ast.Pow: opc.INPLACE_POWER,
            ast.LShift: opc.INPLACE_LSHIFT,
            ast.RShift: opc.INPLACE_RSHIFT,
            ast.BitAnd: opc.INPLACE_AND,
            ast.BitOr: opc.INPLACE_OR,
            ast.BitXor: opc.INPLACE_XOR,
        }
        self._visit_with_load_ctx(node.target)
        self.visit(node.value)
        self.bc.add(inplaceop_map[type(node.op)])
        self.visit(node.target)

    def visit_Assign(self, node):
        self.visit(node.value)
        for t in node.targets[:-1]:
            self.bc.add(opc.DUP_TOP)
            self.visit(t)
        self.visit(node.targets[-1])

    def visit_Delete(self, node):
        for t in node.targets:
            # Operation is handled by node.ctx
            self.visit(t)

    def visit_Expr(self, node):
        self.visit(node.value)
        self.bc.add(opc.POP_TOP)

    def visit_Pass(self, node):
        pass

    def visit_Call(self, node):
        self.visit(node.func)
        opcode = opc.CALL_FUNCTION
        stararg = None
        dstararg = None

        pos_args = 0
        for arg in node.args:
            if isinstance(arg, ast.Starred):
                opcode = opc.CALL_FUNCTION_VAR_KW
                stararg = arg.value
            else:
                self.visit(arg)
                pos_args += 1

        kw_args = 0
        for kwarg in node.keywords:
            if kwarg.arg is None:
                opcode = opc.CALL_FUNCTION_VAR_KW
                dstararg = kwarg.value
            else:
                self.bc.add(opc.LOAD_CONST_STRING, kwarg.arg)
                self.visit(kwarg.value)
                kw_args += 1

        if opcode == opc.CALL_FUNCTION_VAR_KW:
            if stararg is None:
                self.bc.add(opc.LOAD_NULL)
            else:
                self.visit(stararg)
            if dstararg is None:
                self.bc.add(opc.LOAD_NULL)
            else:
                self.visit(dstararg)

        self.bc.add(opcode, pos_args, kw_args)

    def visit_IfExp(self, node):
        self.visit(node.test)
        join_l = self.bc.get_label()
        else_l = self.bc.get_label()
        self.bc.jump(opc.POP_JUMP_IF_FALSE, else_l)
        self.visit(node.body)
        self.bc.jump(opc.JUMP, join_l)
        self.bc.put_label(else_l)
        # Undo stack effect of the "if" branch.
        self.bc.stk_ptr -= 1
        self.visit(node.orelse)
        self.bc.put_label(join_l)

    def visit_Compare(self, node):
        assert len(node.ops) == 1
        cmpop_map = {
            ast.Eq: opc.BINARY_EQUAL,
            ast.NotEq: opc.BINARY_NOT_EQUAL,
            ast.Lt: opc.BINARY_LESS,
            ast.LtE: opc.BINARY_LESS_EQUAL,
            ast.Gt: opc.BINARY_MORE,
            ast.GtE: opc.BINARY_MORE_EQUAL,
            ast.Is: opc.BINARY_IS,
            ast.IsNot: opc.BINARY_IS,
            ast.In: opc.BINARY_IN,
            ast.NotIn: opc.BINARY_IN,
        }
        self.visit(node.left)
        self.visit(node.comparators[0])
        op_t = type(node.ops[0])
        self.bc.add(cmpop_map[op_t])
        if op_t in (ast.IsNot, ast.NotIn):
            self.bc.add(opc.UNARY_NOT)

    def visit_BoolOp(self, node):
        if isinstance(node.op, ast.And):
            op = opc.JUMP_IF_FALSE_OR_POP
        else:
            op = opc.JUMP_IF_TRUE_OR_POP
        join_l = self.bc.get_label()
        for v in node.values[:-1]:
            self.visit(v)
            self.bc.jump(op, join_l)
        self.visit(node.values[-1])
        self.bc.put_label(join_l)

    def visit_BinOp(self, node):
        binop_map = {
            ast.Add: opc.BINARY_ADD,
            ast.Sub: opc.BINARY_SUBTRACT,
            ast.Mult: opc.BINARY_MULTIPLY,
            ast.MatMult: opc.BINARY_MAT_MULTIPLY,
            ast.Div: opc.BINARY_TRUE_DIVIDE,
            ast.FloorDiv: opc.BINARY_FLOOR_DIVIDE,
            ast.Mod: opc.BINARY_MODULO,
            ast.Pow: opc.BINARY_POWER,
            ast.LShift: opc.BINARY_LSHIFT,
            ast.RShift: opc.BINARY_RSHIFT,
            ast.BitAnd: opc.BINARY_AND,
            ast.BitOr: opc.BINARY_OR,
            ast.BitXor: opc.BINARY_XOR,
        }
        self.visit(node.left)
        self.visit(node.right)
        self.bc.add(binop_map[type(node.op)])

    def visit_UnaryOp(self, node):
        unop_map = {
            ast.UAdd: opc.UNARY_POSITIVE,
            ast.USub: opc.UNARY_NEGATIVE,
            ast.Invert: opc.UNARY_INVERT,
            ast.Not: opc.UNARY_NOT,
        }
        self.visit(node.operand)
        self.bc.add(unop_map[type(node.op)])

    def visit_Subscript(self, node):
        self.visit(node.value)
        self.visit(node.slice)
        if isinstance(node.ctx, ast.Load):
            self.bc.add(opc.LOAD_SUBSCR)
        if isinstance(node.ctx, ast.Store):
            self.bc.add(opc.STORE_SUBSCR)
        elif isinstance(node.ctx, ast.Del):
            self.bc.add(opc.LOAD_NULL)
            self.bc.add(opc.ROT_THREE)
            self.bc.add(opc.STORE_SUBSCR)

    def visit_Slice(self, node):
        def emit_dim(dim):
            if dim is None:
                self.bc.add(opc.LOAD_CONST_NONE)
            else:
                self.visit(dim)
        num = 2
        emit_dim(node.lower)
        emit_dim(node.upper)
        if node.step is not None:
            emit_dim(node.step)
            num = 3
        self.bc.add(opc.BUILD_SLICE, num)

    def visit_Index(self, node):
        self.visit(node.value)

    def visit_Attribute(self, node):
        self.visit(node.value)
        if isinstance(node.ctx, ast.Load):
            self.bc.add(opc.LOAD_ATTR, node.attr)
        elif isinstance(node.ctx, ast.Store):
            self.bc.add(opc.STORE_ATTR, node.attr)
        elif isinstance(node.ctx, ast.Del):
            self.bc.add(opc.LOAD_NULL)
            self.bc.add(opc.ROT_TWO)
            self.bc.add(opc.STORE_ATTR, node.attr)

    def visit_Name(self, node):
        self._visit_var(node.id, node.ctx)

    def _visit_var(self, var, ctx):
        scope = self.symtab.get_scope(var)
        if isinstance(ctx, ast.Load):
            op = (opc.LOAD_NAME, opc.LOAD_GLOBAL, opc.LOAD_FAST_N, opc.LOAD_DEREF)[scope]
        elif isinstance(ctx, ast.Store):
            op = (opc.STORE_NAME, opc.STORE_GLOBAL, opc.STORE_FAST_N, opc.STORE_DEREF)[scope]
        elif isinstance(ctx, ast.StoreConst):
            op = (opc.STORE_NAME_CONST, opc.STORE_GLOBAL_CONST, opc.STORE_FAST_N, opc.STORE_DEREF)[scope]
        elif isinstance(ctx, ast.Del):
            op = (opc.DELETE_NAME, opc.DELETE_GLOBAL, opc.DELETE_FAST, opc.DELETE_DEREF)[scope]
        else:
            assert 0

        if scope in (usymtable.SCOPE_FAST, usymtable.SCOPE_DEREF):
            id = self.symtab.get_fast_local(var)
            self.bc.add(op, id)
        else:
            self.bc.add(op, var)

    def _visit_seq_target(self, t):
        if isinstance(t, (ast.Tuple, ast.List)):
            before_star = 0
            after_star = 0
            star = None
            for el in t.elts:
                if isinstance(el, ast.Starred):
                    star = el
                elif star:
                    after_star += 1
                else:
                    before_star += 1
            if star:
                self.bc.add(opc.UNPACK_EX, after_star << 8 | before_star)
            else:
                self.bc.add(opc.UNPACK_SEQUENCE, len(t.elts))
            for v in t.elts:
                self.visit(v)
        else:
            assert 0

    def visit_Tuple(self, node):
        if isinstance(node.ctx, ast.Store):
            self._visit_seq_target(node)
            return

        for v in node.elts:
            self.visit(v)
        self.bc.add(opc.BUILD_TUPLE, len(node.elts))

    def visit_List(self, node):
        if isinstance(node.ctx, ast.Store):
            self._visit_seq_target(node)
            return

        for v in node.elts:
            self.visit(v)
        self.bc.add(opc.BUILD_LIST, len(node.elts))

    def visit_Set(self, node):
        for v in node.elts:
            self.visit(v)
        self.bc.add(opc.BUILD_SET, len(node.elts))

    def visit_Dict(self, node):
        self.bc.add(opc.BUILD_MAP, len(node.keys))
        for k, v in zip(node.keys, node.values):
            self.visit(v)
            self.visit(k)
            self.bc.add(opc.STORE_MAP)

    def visit_Num(self, node):
        assert isinstance(node.n, int)
        assert -2**30 < node.n < 2**30 - 1
        self.bc.load_int(node.n)

    def visit_Str(self, node):
        self.bc.add(opc.LOAD_CONST_OBJ, node.s)

    def visit_Bytes(self, node):
        self.bc.add(opc.LOAD_CONST_OBJ, node.s)

    def visit_NameConstant(self, node):
        if node.value is None:
            self.bc.add(opc.LOAD_CONST_NONE)
        elif node.value is True:
            self.bc.add(opc.LOAD_CONST_TRUE)
        elif node.value is False:
            self.bc.add(opc.LOAD_CONST_FALSE)
        else:
            assert 0

    def visit_Ellipsis(self, node):
        self.bc.add(opc.LOAD_CONST_OBJ, Ellipsis)

    def generic_visit(self, node):
        log.error("Unsupported AST node: %s", ast.dump(node))
        raise NotImplementedError


def compile_ast(tree, filename="<file>"):
    symtable_b = usymtable.SymbolTableBuilder()
    symtable_b.visit(tree)

    compiler = Compiler(symtable_b.symtab_map, filename)
    compiler.visit(tree)

    co = compiler.bc.get_codeobj()
    co.co_name = "<module>"
    co.co_filename = compiler.filename
    return co
