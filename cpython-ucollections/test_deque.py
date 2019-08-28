from ucollections import deque


d = deque((), 1)
d.append(1)
d.append(2)
assert d.popleft() == 2

d = deque((), 1, 1)
d.append(1)
try:
    d.append(2)
    assert False
except IndexError:
    pass
