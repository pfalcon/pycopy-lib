from collections import namedtuple


Tuple1 = namedtuple("Tuple1", "a b c")
assert repr(Tuple1) == "<class 'Tuple1'>"

t = Tuple1._make([1, 2, 3])
assert t[0] == 1 and t[1] == 2 and t[2] == 3
assert t.a == 1 and t.b == 2 and t.c == 3

assert issubclass(Tuple1, tuple)
