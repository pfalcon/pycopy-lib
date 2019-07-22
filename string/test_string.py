from string import *

assert translate("foobar", {ord("o"): "foo", ord("b"): 32, ord("r"): None}) == "ffoofoo a"

assert isidentifier("_foo13_1")
assert not isidentifier("_foo13_1-")
assert not isidentifier("1_foo13_1")
