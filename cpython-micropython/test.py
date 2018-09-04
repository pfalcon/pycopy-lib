import micropython
from micropython import const

FOO = const(1)

@micropython.native
def func1():
    return 2

@micropython.viper
def func2() -> int:
    return 3


assert FOO == 1
assert func1() == 2
assert func2() == 3
