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


log = ulogging.Logger(__name__)


# Access by name in locals
SCOPE_LOCAL = 0
# Access by name in globals
SCOPE_GLOBAL = 1
# Access by index in function locals
SCOPE_FAST = 2
# Access cell by index in function locals
SCOPE_DEREF = 3


def error(msg):
#    sys.stderr.write(msg + "\n")
    assert 0, msg


class Symbol:

    def __init__(self, var):
        self.var = var
        self.is_def = False
        self.is_use = False
        self.is_use_in_children = False
        self.is_param = False
        self.is_fastlocal = False
        self.is_global = False
        self.is_nonlocal = False

    def is_free(self):
        return not self.is_def or self.is_nonlocal

    def is_cell(self):
        return self.is_fastlocal and self.is_def and self.is_use_in_children

    def __repr__(self):
        return "<Sym %r d=%d p=%d u=%d uch=%d l=%d f=%d c=%d>" % (
            self.var, self.is_def, self.is_param, self.is_use, self.is_use_in_children, self.is_fastlocal,
            self.is_free(), self.is_cell(),
        )


class SymbolTable:

    def __init__(self, defining_node, parent, type):
        self.type = type
        self.defining_node = defining_node
        self.parent = parent
        # All variables in the order they're referenced
        self.var_arr = []
        # Map from var name to Symbol (later its index in .ref_order)
        self.var_map = {}
        # Parameters of a function
        self.params = []
        # Union of free vars of child function scopes
        self.freevars_children = []
        self.free_upvals = None
        # Local vars of this function which should be created as cells, as
        # they're accessed as free in children.
        self.cellvars = []
        # Entire array of (fast) locals, including transitive cells (cells not
        # accessed in this func, but passed down to enclosed funcs).
        self.all_locals = None

    def name(self):
        if isinstance(self.defining_node, ast.Module):
            r = "Module"
        else:
            r = self.defining_node.__class__.__name__ + " " + self.defining_node.name
        return "SymbolTable<%s>" % r

    def is_func_scope(self):
        return self.type == "func"

    def is_method_scope(self):
        return self.parent and self.type == "func" and self.parent.type == "class"

    def get_module_scope(self):
        s = self
        while s.parent:
            s = s.parent
        return s

    def __repr__(self):
        return """%s {
  parent: %s,
  all_locals: %r,
  cells: %r
}""" % (
            self.name(), self.parent and self.parent.name(),
            self.all_locals,
            self.cellvars
        )

    def ref(self, var):
        sym = self.var_map.get(var)
        if sym is not None:
            return sym
        i = len(self.var_arr)
        sym = Symbol(var)
        self.var_arr.append(sym)
        self.var_map[var] = sym
        return sym

    def add_def(self, var, force_local=False):
        sym = self.ref(var)
        sym.is_def = True
        if not sym.is_global and not sym.is_nonlocal:
            if self.type == "func" or force_local:
                sym.is_fastlocal = True
        return sym

    def add_param(self, var):
        sym = self.add_def(var)
        assert not sym.is_param, "dup"
        sym.is_param = True

    def add_use(self, var):
        sym = self.ref(var)
        sym.is_use = True
        return sym

    def check_pristine(self, var):
        if var not in self.var_map:
            return
        sym = self.var_map[var]
        if sym.is_param:
            error("cannot redeclare function parameter as global/nonlocal")
        if sym.is_def or sym.is_use:
            error("global/nonlocal declaration should precede variable definition or usage")

    def add_global(self, var):
        self.check_pristine(var)
        sym = self.ref(var)
        if sym.is_nonlocal:
            error("name '%s' is nonlocal and global" % var)
        sym.is_global = True
        # Both CPython and MicroPython also propagate to top-level scope
        top = self.get_module_scope()
        top.ref(var).is_global = True

    def add_nonlocal(self, var):
        self.check_pristine(var)
        sym = self.ref(var)
        if sym.is_global:
            error("name '%s' is nonlocal and global" % var)
        sym.is_nonlocal = True

    def get_scope(self, var):
        sym = self.var_map[var]
        if sym.is_free():
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
        if sym.is_global:
            return SCOPE_GLOBAL
        if self.is_func_scope() and sym.is_fastlocal:
            return SCOPE_FAST
        return SCOPE_LOCAL

    # Called on parent scope when processing of one of child scopes if finished.
    def handle_child(self, child):
        log.debug("%s handle_child(%s)" % (self.name(), child.name()))

        for sym in child.var_arr:
            if sym.is_free():
                # Uniqueness check isn't really needed
                if sym.var not in self.freevars_children:
                    self.freevars_children.append(sym.var)

            # This potentially would be much more efficient, but leads to locals/cells order not compatible with C compiler
            #sym = self.ref(c)
            #assert not sym.is_global
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
        log.debug("process_children: %s", self.name())

        for v in self.freevars_children:
            sym = self.ref(v)
            sym.is_use_in_children = True

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
        log.debug("finalize: %s" % self)
        assert self.all_locals is None

        for sym in self.var_arr:
            if sym.is_nonlocal:
                v = sym.var
                p = self.parent
                found = False
                while p:
                    if v in p.var_map and p.var_map[v].is_def:
                        found = True
                        break
                    p = p.parent
                if not found:
                    #raise SyntaxError("no binding for nonlocal found: %s: %s" % (self.name(), v))
                    raise SyntaxError("no binding for nonlocal found")

        cellvars = []
        for sym in self.var_arr:
            if sym.is_cell():
                cellvars.append(sym.var)
        self.cellvars = cellvars

        upvals = []
        params = []
        rest = []
        cells = []

        # Calc upvals, these should follow order in parent scope.
        if self.parent and self.parent.type != "module":
            for psym in self.parent.var_arr:
                c = psym.var
                if c in self.var_map and self.var_map[c].is_free() and self.get_scope(c) == SCOPE_DEREF:
                    upvals.append(c)

        for sym in self.var_arr:
#            print(sym)
            var = sym.var
            access = self.get_scope(var)

            if access == SCOPE_DEREF and not sym.is_cell():
                # Already in upvals, calculated above.
                pass
            elif sym.is_fastlocal or access == SCOPE_DEREF:
                if sym.is_param:
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
        self.all_locals_how = (upvals, params, rest, cells)
        self.params = [sym.var for sym in self.var_arr if sym.is_param]


class SymbolTableBuilder(ast.NodeVisitor):

    def __init__(self):
        self.symtab_map = {}
        self.symtab_stack = []
        # Current symtab
        self.symtab = None
        # Current function scope symtab (i.e. bypassing class scopes)
        self.func_symtab = None

    def new_scope(self, node, parent, type):
        scope = SymbolTable(node, parent, type)
        self.symtab_map[node] = scope
        self.symtab_stack.append(scope)
        self.symtab = scope
        if scope.is_func_scope():
            self.func_symtab = scope

    def pop_scope(self):
        scope = self.symtab_stack.pop()
        scope.process_children()
        if scope.parent:
            scope.parent.handle_child(scope)
        if self.symtab_stack:
            self.symtab = self.symtab_stack[-1]
        else:
            self.symtab = None
        if scope.is_func_scope():
            self.func_symtab = scope.parent

    def list_visit(self, lst):
        for s in lst:
#            print("*", ast.dump(s))
            self.visit(s)

    def visit_Module(self, node):
        assert not self.symtab_stack
        self.new_scope(node, None, "module")
        self.list_visit(node.body)
        self.pop_scope()

    def visit_FunctionDef(self, node):
        self.symtab.add_def(node.name)
        self.new_scope(node, self.func_symtab, "func")

        args = node.args
        for arg in args.args:
            self.symtab.add_param(arg.arg)

        self.list_visit(node.body)
        self.pop_scope()

    def visit_ClassDef(self, node):
        self.symtab.add_def(node.name)
        self.new_scope(node, self.func_symtab, "class")
        self.list_visit(node.body)
        self.pop_scope()

    def visit_Name(self, node):
        if isinstance(node.ctx, ast.Load):
            self.symtab.add_use(node.id)
        else:
            # Both Store and Del
            self.symtab.add_def(node.id)

    def visit_Global(self, node):
        for n in node.names:
            self.symtab.add_global(n)

    def visit_Nonlocal(self, node):
        for n in node.names:
            self.symtab.add_nonlocal(n)
