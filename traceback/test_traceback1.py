import traceback


def f(e):
    return traceback.format_exception_only(type(e), e)


assert f(ValueError()) == ["ValueError\n"]
assert f(ValueError(1)) == ["ValueError: 1\n"]
assert f(ValueError(1, 2)) == ["ValueError: (1, 2)\n"]
