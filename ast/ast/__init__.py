from .types import *


def dump(t):
    if isinstance(t, AST):
        res = type(t).__name__
        res += "("
        comma = False
        for k in dir(t):
            if k.startswith("_"):
                continue
            if comma:
                res += ", "
            res += k + "=" + dump(getattr(t, k))
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
