import re


m = re.search(r"(р)ив", "привет")
assert m
assert m.group(0) == "рив"
assert m.group(1) == "р"

assert re.sub(r"ри", "12", "привет") == "п12вет"
assert re.sub(r"ри", "фыва", "привет") == "пфывавет"

assert re.split(r"и", "привет") == ["пр", "вет"]
assert re.split(r"ив", "привет") == ["пр", "ет"]

assert re.findall(r"и.", "и1и22иф45") == ["и1", "и2", "иф"]
