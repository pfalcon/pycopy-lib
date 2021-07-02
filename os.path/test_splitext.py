from os.path import splitext


assert splitext("foo") == ("foo", "")
assert splitext(".foo") == (".foo", "")
assert splitext("foo.bar") == ("foo", ".bar")
assert splitext(".foo.bar") == (".foo", ".bar")
