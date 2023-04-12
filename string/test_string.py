from string import *

assert translate("foobar", {ord("o"): "foo", ord("b"): 32, ord("r"): None}) == "ffoofoo a"

assert isalnum("898dsdsd")
assert isalnum("sdsd64645")
assert not isalnum("")
assert not isalnum("sdsd_64645")
assert not isalnum("<EOF>")

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

assert encode("foo", "utf-8", "strict") == b"foo"

assert capitalize("fOOBar_123") == "Foobar_123"
