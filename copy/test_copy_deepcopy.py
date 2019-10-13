# So far just copy of test_copy_copy.py, but need to add more tests.
import copy


class Foo:
    clsvar = 1


o1 = Foo()
o1.val = 10

c1 = copy.deepcopy(o1)
assert id(o1) != id(c1)

o1.val = 11
assert c1.val == 10

Foo.clsvar = 2

assert o1.clsvar == 2
assert c1.clsvar == 2
