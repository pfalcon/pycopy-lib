# (c) 2019 Paul Sokolovsky. MIT license.
from .types import *


def dump_to_stream(t, file):
    if isinstance(t, AST):
        file.write(type(t).__name__)
        file.write("(")
        comma = False
        for k in t._fields:
            if k.startswith("_"):
                continue
            res = ""
            if comma:
                res += ", "
            res += k + "="
            file.write(res)
            dump_to_stream(getattr(t, k, None), file)
            comma = True
        file.write(")")
    elif isinstance(t, list):
        file.write("[")
        comma = False
        for v in t:
            if comma:
                file.write(", ")
            dump_to_stream(v, file)
            comma = True
        file.write("]")
    else:
        file.write(repr(t))


def dump(t):
    import io
    buf = io.StringIO()
    dump_to_stream(t, buf)
    return buf.getvalue()


def iter_fields(t):
    for k in t._fields:
        if k.startswith("_"):
            continue
        yield (k, getattr(t, k, None))


def copy_location(new_node, old_node):
    return new_node


def parse_stream(stream, filename="<unknown>", mode="exec"):
    import utokenize as tokenize
    from . import parser
    tstream = tokenize.tokenize(stream.readline)
    p = parser.Parser(tstream)
    p.match(tokenize.ENCODING)
    if mode == "exec":
        t = p.match_mod()
    elif mode == "eval":
        t = Expression(body=p.require_expr())
    elif mode == "single":
        t = Interactive(body=p.match_stmt())
    else:
        raise ValueError
    return t


def parse(source, filename="<unknown>", mode="exec"):
    import io
    return parse_stream(io.StringIO(source), filename, mode)


class NodeVisitor:

    def visit(self, node):
        n = node.__class__.__name__
        m = getattr(self, "visit_" + n, None)
        if m:
            return m(node)
        else:
            return self.generic_visit(node)

    def generic_visit(self, node):
        for f in node._fields:
            val = getattr(node, f)
            if isinstance(val, list):
                for v in val:
                    if isinstance(v, AST):
                        self.visit(v)
            elif isinstance(val, AST):
                self.visit(val)


class NodeTransformer(NodeVisitor):

    def generic_visit(self, node):
        for f in node._fields:
            val = getattr(node, f)
            if isinstance(val, list):
                newl = []
                for v in val:
                    newv = self.visit(v)
                    if newv is None:
                        pass
                    elif isinstance(newv, list):
                        newl.extend(newv)
                    else:
                        newl.append(newv)
                setattr(node, f, newl)
            elif isinstance(val, AST):
                newv = self.visit(val)
                setattr(node, f, newv)

        return node
