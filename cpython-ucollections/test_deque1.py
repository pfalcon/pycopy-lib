from ucollections import deque


d = deque((), 2)
assert len(d) == 0
assert not bool(d)

try:
    d.popleft()
    assert False
except IndexError:
    pass

assert d.append(1) is None
assert len(d) == 1
assert bool(d)
assert d.popleft() == 1
assert len(d) == 0

d.append(2)
assert d.popleft() == 2

d.append(3)
d.append(4)
assert len(d) == 2
assert (d.popleft(), d.popleft()) == (3, 4)
try:
    d.popleft()
    assert False
except IndexError:
    pass

d.append(5)
d.append(6)
d.append(7)
assert len(d) == 2
assert (d.popleft(), d.popleft()) == (6, 7)
assert len(d) == 0
try:
    d.popleft()
    assert False
except IndexError:
    pass

# Case where get index wraps around when appending to full deque
d = deque((), 2)
d.append(1)
d.append(2)
d.append(3)
d.append(4)
d.append(5)
assert (d.popleft(), d.popleft()) == (4, 5)

# Negative maxlen is not allowed
try:
    deque((), -1)
    assert False
except ValueError:
    pass

# Unsupported unary op
try:
    ~d
    assert False
except TypeError:
    pass
