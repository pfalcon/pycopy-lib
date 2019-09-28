def itemgetter(*args):
    def _itemgetter(obj):
        return obj[args[0]]
    def _itemsgetter(obj):
        return tuple([obj[i] for i in args])
    if len(args) == 1:
        return _itemgetter
    return _itemsgetter


def attrgetter(attr):
    assert "." not in attr
    def _attrgetter(obj):
        return getattr(obj, attr)
    return _attrgetter


def methodcaller(name, *args, **kwargs):
    def _methodcaller(obj):
        return getattr(obj, name)(*args, **kwargs)
    return _methodcaller


def lt(a, b):
    return a < b

def le(a, b):
    return a <= b

def gt(a, b):
    return a > b

def ge(a, b):
    return a >= b

def eq(a, b):
    return a == b

def ne(a, b):
    return a != b

def mod(a, b):
    return a % b

def truediv(a, b):
    return a / b

def floordiv(a, b):
    return a // b

def getitem(a, b):
    return a[b]
