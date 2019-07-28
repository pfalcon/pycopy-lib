# (c) 2019 Paul Sokolovsky. MIT license.
from .types import *


def dump(t):
    if isinstance(t, AST):
        res = type(t).__name__
        res += "("
        comma = False
        for k in t._fields:
            if k.startswith("_"):
                continue
            if comma:
                res += ", "
            res += k + "=" + dump(getattr(t, k, None))
            comma = True
        res += ")"
        return res
    elif isinstance(t, list):
        res = "["
        comma = False
        for v in t:
            if comma:
                res += ", "
            res += dump(v)
            comma = True
        res += "]"
        return res
    else:
        return repr(t)


def iter_fields(t):
    for k in t._fields:
        if k.startswith("_"):
            continue
        yield (k, getattr(t, k, None))


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
