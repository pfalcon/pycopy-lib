import os


res = []
for t in os.walk("testdata/walk"):
    #print(t)
    t[2].sort()
    res.append(t)

assert res == [
    ('testdata/walk', ['subdir'], ['bar', 'foo']),
    ('testdata/walk/subdir', [], []),
]

res = []
for t in os.walk("testdata/walk", False):
    #print(t)
    t[2].sort()
    res.append(t)

assert res == [
    ('testdata/walk/subdir', [], []),
    ('testdata/walk', ['subdir'], ['bar', 'foo']),
]
