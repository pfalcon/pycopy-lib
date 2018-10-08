import re

try:
    re.compile("(")
    assert 0, "Bad syntax not caught"
except re.error as e:
    print("Caught exception as expected:", e)
