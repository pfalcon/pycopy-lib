import re

m = re.match(r"(?P<int>\d+)\.(?P<frac>\d+)", "24.1632")
assert m.groups() == ("24", "1632")
assert m.group(2, 1) == ("1632", "24")
assert m.group("int") == "24"
assert m.group("frac") == "1632"
assert m.group("frac", "int") == ("1632", "24")

try:
    assert m.group("frac2") == "1632"
    assert False
except IndexError:
    pass
