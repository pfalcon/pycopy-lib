import random


# Test degenerate behavior, when return value is not random, but a constant
for i in range(100):
    assert random.randrange(1) == 0
    assert random.randrange(0, 1) == 0
    assert random.randrange(100, 101) == 100
    assert random.randint(0, 0) == 0
