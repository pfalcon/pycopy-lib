import traceback


def f(e):
    return traceback.format_exception_only(type(e), e)


assert f(ValueError()) == ["ValueError\n"]
assert f(ValueError(1)) == ["ValueError: 1\n"]
assert f(ValueError(1, 2)) == ["ValueError: (1, 2)\n"]


class MyExc(Exception):
    pass


assert f(MyExc()) == ["MyExc\n"]


from test_traceback2 import MyExc2


assert f(MyExc2()) == ["test_traceback2.MyExc2\n"]
