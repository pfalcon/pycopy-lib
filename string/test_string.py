import string

assert string.translate("foobar", {ord("o"): "foo", ord("b"): 32, ord("r"): None}) == "ffoofoo a"

assert string.isidentifier("_foo13_1")
assert not string.isidentifier("_foo13_1-")
assert not string.isidentifier("1_foo13_1")
