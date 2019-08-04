def foo():
    yield
    (yield) + 1
    yield 1
    (yield 1) + 2
    yield 1 + 2
#    yield 1, yield 2
    (yield 1), (yield 2)
    yield 1, 2
