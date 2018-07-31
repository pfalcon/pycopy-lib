import xmltok

dir = "."
if "/" in __file__:
    dir = __file__.rsplit("/", 1)[0]

tokenizer = xmltok.tokenize(open(dir + "/test_text_of.xml"))

text = xmltok.text_of(tokenizer, "val")
assert text == "foo"

text = xmltok.text_of(tokenizer, "val")
assert text == "bar"

# Will match even namespaced tag
text = xmltok.text_of(tokenizer, "val")
assert text == "kaboom"

# Match specifically namespaced tag
text = xmltok.text_of(tokenizer, ("ns", "val"))
assert text == "kaboom2"

try:
    text = xmltok.text_of(tokenizer, "val")
    assert False
except StopIteration:
    pass

