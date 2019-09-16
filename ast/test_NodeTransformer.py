import sys
import ast
from ast import *
import io


# Based on https://docs.python.org/3/library/ast.html#ast.NodeTransformer
class RewriteName(NodeTransformer):

    # Rewrite all occurrences of name lookups (foo) to data['foo']:
    def visit_Name(self, node):
        return copy_location(Subscript(
            value=Name(id='data', ctx=Load()),
            slice=Index(value=Str(s=node.id)),
            ctx=node.ctx
        ), node)

    def visit_Expr(self, node):
        # Remove bare "bar" expression
        if isinstance(node.value, Name):
            if node.value.id == "bar":
                # Remove
                return None
            elif node.value.id == "baz":
                # Replace one node with two
                # Note: these 2 new won't be rewritten as "data[...]", as we
                # don't explicitly call generic_visit()/visit_Name() on them.
                return [Expr(value=Name(id="baz1")), Expr(value=Name(id="baz2"))]
        # Need to call .generic_visit() for children to be rewritten
        self.generic_visit(node)
        return node


SRC = """\
foo
foo + 1

# To be removed
bar

# To be split in 2
baz

if len(foo) == 2:
    foo = "here"
"""

EXP = """\
Module(body=[Expr(value=Subscript(value=Name(id='data', ctx=Load()), slice=Index(value=Str(s='foo')), ctx=Load())), Expr(value=BinOp(left=Subscript(value=Name(id='data', ctx=Load()), slice=Index(value=Str(s='foo')), ctx=Load()), op=Add(), right=Num(n=1))), Expr(value=Name(id='baz1', ctx=None)), Expr(value=Name(id='baz2', ctx=None)), If(test=Compare(left=Call(func=Subscript(value=Name(id='data', ctx=Load()), slice=Index(value=Str(s='len')), ctx=Load()), args=[Subscript(value=Name(id='data', ctx=Load()), slice=Index(value=Str(s='foo')), ctx=Load())], keywords=[]), ops=[Eq()], comparators=[Num(n=2)]), body=[Assign(targets=[Subscript(value=Name(id='data', ctx=Load()), slice=Index(value=Str(s='foo')), ctx=Store())], value=Str(s='here'))], orelse=[])])"""

t = ast.parse(SRC)

RewriteName().visit(t)

res = ast.dump(t)

assert res == EXP
