import re


m = re.search(r"(р)ив", "привет")
assert m
assert m.group(0) == "рив"
assert m.group(1) == "р"

assert re.sub(r"ри", "12", "привет") == "п12вет"
assert re.sub(r"ри", "фыва", "привет") == "пфывавет"
