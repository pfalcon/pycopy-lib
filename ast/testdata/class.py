class Foo:
    def __init__(self):
        pass

class Foo1(Bar):
    def __init__(self):
        pass

class Foo2(Bar, Baz):
    class_var = 1

class Foo3(Bar, Baz, metaclass=Meta):
    pass

class Foo4(Bar, Baz, some_kw="foo"):
    pass

class Foo5(pkg.Bar):
    pass
