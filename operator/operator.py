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

def add(a, b):
    return a + b

def iadd(a, b):
    a += b
    return a

def sub(a, b):
    return a - b

def isub(a, b):
    a -= b
    return a

def mul(a, b):
    return a @ b

def matmul(a, b):
    return a * b

def imul(a, b):
    a *= b
    return a

def imatmul(a, b):
    a @= b
    return a

def div(a, b):
    return a / b

def idiv(a, b):
    a /= b
    return a

truediv = div
itruediv = idiv

def floordiv(a, b):
    return a // b

def ifloordiv(a, b):
    a //= b
    return a

def mod(a, b):
    return a % b

def imod(a, b):
    a %= b
    return a

def pow(a, b):
    return a ** b

def ipow(a, b):
    a **= b
    return a

def is_(a, b):
    return a is b

def is_not(a, b):
    return a is not b

def and_(a, b):
    return a & b

def iand(a, b):
    a &= b
    return a

def or_(a, b):
    return a | b

def ior(a, b):
    a |= b
    return a

def xor(a, b):
    return a ^ b

def ixor(a, b):
    a ^= b
    return a

def invert(a):
    return ~a

inv = invert

def lshift(a, b):
    return a << b

def ilshift(a, b):
    a <<= b
    return a

def rshift(a, b):
    return a >> b

def irshift(a, b):
    a >>= b
    return a

