import pycopy
from pycopy import const

FOO = const(1)

@pycopy.native
def func1():
    return 2

@pycopy.viper
def func2() -> int:
    return 3


assert FOO == 1
assert func1() == 2
assert func2() == 3
