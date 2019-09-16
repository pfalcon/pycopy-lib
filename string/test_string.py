from string import *

assert translate("foobar", {ord("o"): "foo", ord("b"): 32, ord("r"): None}) == "ffoofoo a"

assert isidentifier("_foo13_1")
assert not isidentifier("_foo13_1-")
assert not isidentifier("1_foo13_1")
assert not isidentifier("")

# expandtabs
assert expandtabs("\t") == '        '
assert expandtabs("123\t") == '123     '
assert expandtabs("12345678\t") == '12345678        '
assert expandtabs("123\n\t") == '123\n        '

assert ljust("foo", 5) == "foo  "
assert ljust("foo", 2) == "foo"
assert ljust("foo", 5, "-") == "foo--"
