def foo():
    yield from 1
    (yield from 1) + 2
    yield from 1 + 2
#    yield from 1, yield from 2
    (yield from 1), (yield from 2)
