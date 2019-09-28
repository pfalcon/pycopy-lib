import operator

class A:

    def method(self, *args, **kwargs):
        return (args, kwargs)


a = A()

a.name = "foo"
f = operator.attrgetter('name')
assert f(a) == "foo"

fm = operator.methodcaller("method")
assert fm(a) == ((), {})

fm = operator.methodcaller("method", 1, 2, 3, kw1="foo", kw2=10)
assert fm(a) == ((1, 2, 3), {"kw1": "foo", "kw2": 10})

im = operator.itemgetter(1)
assert im([1, 2, 3]) == 2

im = operator.itemgetter(0, 2)
assert im([1, 2, 3]) == (1, 3)
