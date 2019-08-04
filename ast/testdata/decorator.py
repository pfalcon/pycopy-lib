@decor
def foo():
    pass

@decor()
def foo():
    pass

@decor(1, 2)
def foo():
    pass

@clsdecor(1)
class Foo(Bar):
    pass
