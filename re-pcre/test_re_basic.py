import re

assert re.escape(r"1243*&[]_dsfAd") == r"1243\*\&\[\]_dsfAd"

# search

m = re.search(r"a+", "caaab")
assert m.group(0) == "aaa"
assert m.group() == "aaa"

# match

m = re.match(r"(?ms)foo.*\Z", "foo\nbar")
assert m.group(0) == "foo\nbar"

assert re.match(r"a+", "caaab") is None
m = re.match(r"a+", "aaaab")
assert m.group(0) == "aaaa"

m = re.match(r"(\d+)\.(\d+)", "24.1632")
assert m.groups() == ('24', '1632')
assert m.group(2, 1) == ('1632', '24')

m = re.match("(b)|(:+)", ":a")
assert m.groups() == (None, ":")

# sub

assert re.sub("a", "z", "caaab") == "czzzb"
assert re.sub("a+", "z", "caaab") == "czb"
assert re.sub("a", "z", "caaab", 1) == "czaab"
assert re.sub("a", "z", "caaab", 2) == "czzab"
assert re.sub("a", "z", "caaab", 10) == "czzzb"
assert re.sub(r"[ :/?&]", "_", "http://foo.ua/bar/?a=1&b=baz/") == "http___foo.ua_bar__a=1_b=baz_"
assert re.sub("a", lambda m: m.group(0) * 2, "caaab") == "caaaaaab"
# Callback should receive the same type as org string
assert re.sub("a", lambda m: str(int(isinstance(m.group(0), str))), "caaab") == "c111b"
assert re.sub(b"a", lambda m: str(int(isinstance(m.group(0), bytes))).encode(), b"abcda") == b"1bcd1"

# subn

assert re.subn("b*", "x", "xyz") == ('xxxyxzx', 4)

# zero-length matches
assert re.sub('(?m)^(?!$)', '--', 'foo') == '--foo'
assert re.sub('(?m)^(?!$)', '--', 'foo\n') == '--foo\n'
assert re.sub('(?m)^(?!$)', '--', 'foo\na') == '--foo\n--a'
assert re.sub('(?m)^(?!$)', '--', 'foo\n\na') == '--foo\n\n--a'
assert re.sub('(?m)^(?!$)', '--', 'foo\n\na', 1) == '--foo\n\na'
assert re.sub('(?m)^(?!$)', '--', 'foo\n  \na', 2) == '--foo\n--  \na'

# split

# Splitting on potentially empty matches is currently disabled.
#assert re.split('x*', 'foo') == ['foo']
#assert re.split("(?m)^$", "foo\n\nbar\n") == ["foo\n\nbar\n"]

assert re.split('\W+', 'Words, words, words.') == ['Words', 'words', 'words', '']
assert re.split('(\W+)', 'Words, words, words.') == ['Words', ', ', 'words', ', ', 'words', '.', '']
assert re.split('\W+', 'Words, words, words.', 1) == ['Words', 'words, words.']
assert re.split('[a-f]+', '0a3B9', flags=re.IGNORECASE) == ['0', '3', '9']
assert re.split('(\W+)', '...words, words...') == ['', '...', 'words', ', ', 'words', '...', '']
assert re.split("(b)|(:+)", ":abc") == ['', None, ':', 'a', 'b', None, 'c']

# findall

text = "He was carefully disguised but captured quickly by police."
assert re.findall(r"\w+ly", text) == ['carefully', 'quickly']

text = "He was carefully disguised but captured quickly by police."
assert re.findall(r"(\w+)(ly)", text) == [('careful', 'ly'), ('quick', 'ly')]

text = "He was carefully disguised but captured quickly by police."
assert re.findall(r"(\w+)ly", text) == ['careful', 'quick']

r = re.compile(r"\w+ly")
text = "carefully disguised but captured quickly by police."
assert r.findall(text, 1) == ['arefully', 'quickly']

_leading_whitespace_re = re.compile('(^[ \t]*)(?:[^ \t\n])', re.MULTILINE)
text = "\tfoo\n\tbar"
indents = _leading_whitespace_re.findall(text)
assert indents == ['\t', '\t']

text = "  \thello there\n  \t  how are you?"
indents = _leading_whitespace_re.findall(text)
assert indents == ['  \t', '  \t  ']

assert re.findall(r"\b", "a") == ['', '']

# handling of empty matches
indent_re = re.compile('^([ ]*)(?=\S)', re.MULTILINE)
s = "line number one\nline number two"
assert indent_re.findall(s) == ['', '']

# finditer
# based on CPython's test_re.py
iter = re.finditer(r":+", "a:b::c:::d")
assert [item.group(0) for item in iter] == [":", "::", ":::"]

pat = re.compile(r":+")
iter = pat.finditer("a:b::c:::d", 3, 8)
assert [item.group(0) for item in iter] == ["::", "::"]

s = "line one\nline two\n   3"
iter = re.finditer(r"^ *", s, re.MULTILINE)
assert [m.group() for m in iter] == ["", "", "   "]

assert [m.group() for m in re.finditer(r".*", "asdf")] == ["asdf", ""]
