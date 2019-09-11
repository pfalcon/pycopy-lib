# Python scope and variable properties resolution
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
from ast import Expr, Assign
import io
import ulogging


log = ulogging.getLogger(__name__)


# Access by name in locals
SCOPE_LOCAL = 0
# Access by name in globals
SCOPE_GLOBAL = 1
# Access by index in function locals
SCOPE_FAST = 2
# Access cell by index in function locals
SCOPE_DEREF = 3


SYM_USE = 0x01
SYM_PARAM = 0x02
SYM_ASSIGN = 0x04
SYM_IMPORT = 0x08
SYM_DECL_GLOBAL = 0x10
SYM_DECL_NONLOCAL = 0x20
SYM_USE_IN_CHILDREN = 0x40
SYM_FUNCLOCAL = 0x80


def error(msg):
#    sys.stderr.write(msg + "\n")
    assert 0, msg


class Symbol:

    def __init__(self, name):
        self.name = name
        self._flags = 0

    def get_name(self):
        return self.name

    def is_use(self):
        return bool(self._flags & SYM_USE)

    is_referenced = is_use

    def is_parameter(self):
        return bool(self._flags & SYM_PARAM)

    def is_assigned(self):
        return bool(self._flags & SYM_ASSIGN)

    def is_def(self):
        return bool(self._flags & (SYM_PARAM | SYM_IMPORT | SYM_ASSIGN))

    def is_declared_global(self):
        return bool(self._flags & SYM_DECL_GLOBAL)

    def is_nonlocal(self):
        return bool(self._flags & SYM_DECL_NONLOCAL)

    def is_local(self):
        return self.is_def() and not (self.is_declared_global() or self.is_nonlocal())

    def is_funclocal(self):
        return bool(self._flags & SYM_FUNCLOCAL)

    def is_use_in_children(self):
        return bool(self._flags & SYM_USE_IN_CHILDREN)

    # A variable is formally free if it's not defined by a function. In Python,
    # definition happens by assignment, but vars declared global or nonlocal
    # are still not defined by function, even if assigned to.
    def is_formal_free(self):
        return not self.is_def() or self.is_declared_global() or self.is_nonlocal()

    def is_funclocal_free(self):
        return not self.is_def() or self.is_nonlocal()

    def is_cell(self):
        return self.is_funclocal() and self.is_def() and self.is_use_in_children()

    def __repr__(self):
        return "<symbol %r d=%d p=%d u=%d uch=%d fl=%d nl=%d f=%d c=%d>" % (
            self.name, self.is_def(), self.is_parameter(), self.is_referenced(), self.is_use_in_children(), self.is_funclocal(),
            self.is_nonlocal(), self.is_funclocal_free(), self.is_cell(),
        )


class SymbolTable:

    def __init__(self, defining_node, parent, type):
        self.type = type
        self.defining_node = defining_node
        self.parent = parent
        # All symbols in the order they're referenced.
        self.sym_list = []
        # Map from sym name to Symbol (later its index in .ref_order).
        self.sym_map = {}
        # Parameters of a function.
        self.params = []
        # Union of free vars of child function scopes.
        self.freevars_children = []
        self.free_upvals = None
        # Local vars of this function which should be created as cells, as
        # they're accessed as free in children.
        self.cellvars = []
        # Entire array of (fast) locals, including transitive cells (cells not
        # accessed in this func, but passed down to enclosed funcs).
        self.all_locals = None

    def get_name(self):
        if self.type == "module":
            r = "top"
        else:
            r = getattr(self.defining_node, "name", "<lambda>")
        return r

    def get_type(self):
        return self.type

    def get_symbols(self):
        return self.sym_list

    def is_func_scope(self):
        return self.type == "function"

    def is_method_scope(self):
        return self.parent and self.type == "function" and self.parent.type == "class"

    def get_module_scope(self):
        s = self
        while s.parent:
            s = s.parent
        return s

    def __repr__(self):
        return """%s %s {
  parent: %s,
  all_locals: %r,
  cells: %r
}""" % (
            self.type, self.get_name(), self.parent and self.parent.get_name(),
            self.all_locals,
            self.cellvars
        )

    def ref(self, var):
        sym = self.sym_map.get(var)
        if sym is not None:
            return sym
        sym = Symbol(var)
        self.sym_list.append(sym)
        self.sym_map[var] = sym
        return sym

    def add_def(self, var, def_flags=0, force_local=False):
        sym = self.ref(var)
        sym._flags |= def_flags
        if not sym.is_declared_global() and not sym.is_nonlocal():
            if self.type == "function" or force_local:
                sym._flags |= SYM_FUNCLOCAL
        return sym

    def add_param(self, var):
        sym = self.add_def(var)
        assert not sym.is_parameter(), "dup"
        sym._flags |= SYM_PARAM

    def add_assign(self, var):
        self.add_def(var, SYM_ASSIGN)

    def add_use(self, var):
        sym = self.ref(var)
        sym._flags |= SYM_USE
        return sym

    def check_pristine(self, var):
        if var not in self.sym_map:
            return
        sym = self.sym_map[var]
        if sym.is_parameter():
            error("cannot redeclare function parameter as global/nonlocal")
        if sym.is_def() or sym.is_use():
            error("global/nonlocal declaration should precede variable definition or usage")

    def add_global(self, var):
        self.check_pristine(var)
        sym = self.ref(var)
        if sym.is_nonlocal():
            error("name '%s' is nonlocal and global" % var)
        sym._flags |= SYM_DECL_GLOBAL
        # Both CPython and MicroPython also propagate to top-level scope
        top = self.get_module_scope()
        top.ref(var)._flags |= SYM_DECL_GLOBAL

    def add_nonlocal(self, var):
        self.check_pristine(var)
        sym = self.ref(var)
        if sym.is_declared_global():
            error("name '%s' is nonlocal and global" % var)
        sym._flags |= SYM_DECL_NONLOCAL

    def get_scope(self, var):
        sym = self.sym_map[var]
        if sym.is_funclocal_free():
            scope = self.parent
            while scope:
                if var in scope.cellvars:
                    return SCOPE_DEREF
                scope = scope.parent
            if self.is_func_scope():
                return SCOPE_GLOBAL
            else:
                return SCOPE_LOCAL

        if var in self.cellvars:
            return SCOPE_DEREF
        if sym.is_declared_global():
            return SCOPE_GLOBAL
        if self.is_func_scope() and sym.is_funclocal():
            return SCOPE_FAST
        return SCOPE_LOCAL

    # Called on parent scope when processing of one of child scopes is finished.
    def handle_child(self, child):
        log.debug("%s.handle_child(%s)" % (self.get_name(), child.get_name()))

        for sym in child.sym_list:
            if sym.is_funclocal_free():
                # Uniqueness check isn't really needed
                if sym not in self.freevars_children:
                    self.freevars_children.append(sym)

            # This potentially would be much more efficient, but leads to locals/cells order not compatible with C compiler
            #sym = self.ref(c)
            #assert not sym._is_decl_global
            #sym.is_cell = True

    # Calculate partial scope information, based on available children.
    # Called when entire scope is processed (and thus all of its children
    # too). However, we can't calculate complete scope information here,
    # as parent scope(s) aren't fully constructed yet. For example, we may
    # have a situation a-la:
    #
    # def fun1():
    #     def fun2():
    #         def fun3():
    #             return a
    #     a = 10
    #
    # When .process_children() for fun2 will be called, we didn't yet see "a",
    # so we don't know whether it's cellvar or implicit global.
    def process_children(self):
        log.debug("%s.process_children: freevars: %s", self.get_name(), self.freevars_children)

        for child_sym in self.freevars_children:
            sym = self.ref(child_sym.name)
            sym._flags |= SYM_USE_IN_CHILDREN

    # Complete calculation of scoping information. This should be called
    # when processing of parent scopes is finished. In other words,
    # process_children() is called on upward pass thru scopes
    # (children->parent), and process_children() is actually called
    # automatically by SymbolTableBuilder. While finalize() should be
    # called on downward pass (parent->children). This pass is not
    # handled by SymbolTableBuilder (as parent->children relationship
    # is not stored), but should be done by application code explicitly.
    # An obvious way to do that is via traversing the original AST
    # (perhaps, combined with other processing, like codegeneration from
    # AST).
    def finalize(self):
        log.debug("%s.finalize", self.get_name())
        assert self.all_locals is None

        for sym in self.sym_list:
            if sym.is_nonlocal():
                v = sym.name
                p = self.parent
                found = False
                while p:
                    if v in p.sym_map and p.sym_map[v].is_def():
                        found = True
                        break
                    p = p.parent
                if not found:
                    #raise SyntaxError("no binding for nonlocal found: %s: %s" % (self.get_name(), v))
                    raise SyntaxError("no binding for nonlocal found")

        cellvars = []
        for sym in self.sym_list:
            if sym.is_cell():
                cellvars.append(sym.name)
        self.cellvars = cellvars

        upvals = []
        params = []
        rest = []
        cells = []

        # Calc upvals, these should follow order in parent scope.
        if self.parent and self.parent.type != "module":
            for psym in self.parent.sym_list:
                c = psym.name
                if c in self.sym_map and self.sym_map[c].is_funclocal_free() and self.get_scope(c) == SCOPE_DEREF:
                    upvals.append(c)

        for sym in self.sym_list:
#            print(sym)
            var = sym.name
            access = self.get_scope(var)

            if access == SCOPE_DEREF and not sym.is_cell():
                # Already in upvals, calculated above.
                pass
            elif sym.is_funclocal() or access == SCOPE_DEREF:
                if sym.is_parameter():
                    # First go params, regardless of whether they're cell'ed or not.
                    params.append(var)
                else:
                    if var in self.cellvars:
                        # All cells (except param cells) go at the end.
                        cells.append(var)
                    else:
                        # In the middle is all the rest.
                        rest.append(var)

        self.free_upvals = upvals
        self.all_locals = upvals + params + rest + cells
        # For debugging.
        self.all_locals_how = ("upvals:", upvals, "params:", params, "rest:", rest, "cells:", cells)
        self.params = [sym.name for sym in self.sym_list if sym.is_parameter()]

    def get_fast_local(self, var):
        return self.all_locals.index(var)


class SymbolTableBuilder(ast.NodeVisitor):

    def __init__(self):
        self.symtab_map = {}
        self.symtab_list = []
        self.symtab_stack = []
        # Current symtab
        self.symtab = None

    def new_scope(self, node, type):
        scope = SymbolTable(node, self.symtab, type)
        self.symtab_map[node] = scope
        self.symtab_list.append(scope)
        self.symtab_stack.append(scope)
        self.symtab = scope

    def pop_scope(self):
        scope = self.symtab_stack.pop()
        scope.process_children()
        if scope.parent:
            scope.parent.handle_child(scope)
        if self.symtab_stack:
            self.symtab = self.symtab_stack[-1]
        else:
            self.symtab = None

    def _visit_suite(self, lst):
        for s in lst:
            #print("*", ast.dump(s))
            self.visit(s)

    def visit_Module(self, node):
        assert not self.symtab_stack
        self.new_scope(node, "module")
        self._visit_suite(node.body)
        self.pop_scope()

    def _visit_function(self, node):
        if not isinstance(node, ast.Lambda):
            self.symtab.add_assign(node.name)

        args = node.args

        for v in args.defaults:
            self.visit(v)
        for v in args.kw_defaults:
            if v is not None:
                self.visit(v)

        self.new_scope(node, "function")

        for arg in args.args:
            self.symtab.add_param(arg.arg)
        for arg in args.kwonlyargs:
            self.symtab.add_param(arg.arg)
        if args.vararg:
            self.symtab.add_param(args.vararg.arg)
        if args.kwarg:
            self.symtab.add_param(args.kwarg.arg)

        if isinstance(node.body, list):
            self._visit_suite(node.body)
        else:
            self.visit(node.body)
        self.pop_scope()

    def visit_FunctionDef(self, node):
        self._visit_function(node)

    def visit_AsyncFunctionDef(self, node):
        self._visit_function(node)

    def visit_Lambda(self, node):
        self._visit_function(node)

    def visit_ClassDef(self, node):
        self.symtab.add_assign(node.name)
        self.new_scope(node, "class")
        self._visit_suite(node.body)
        self.pop_scope()

    def visit_Name(self, node):
        if isinstance(node.ctx, ast.Load):
            self.symtab.add_use(node.id)
        else:
            # Both Store and Del
            self.symtab.add_assign(node.id)

    def visit_Global(self, node):
        for n in node.names:
            self.symtab.add_global(n)

    def visit_Nonlocal(self, node):
        for n in node.names:
            self.symtab.add_nonlocal(n)
