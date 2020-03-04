import setlib


s1 = {1, 2}

res = setlib.union(s1, {2, 3}, {3, 4})
assert res == {1, 2, 3, 4}
assert s1 == {1, 2}

res = setlib.intersection(s1, {2, 3}, {2, 4})
assert res == {2}
assert s1 == {1, 2}

s1 = {1, 2, 3, 4}
res = setlib.difference(s1, {2, 3}, {2, 4})
assert res == {1}
assert s1 == {1, 2, 3, 4}

res = setlib.intersection(set('abc'), 'cbs')
assert res == {'b', 'c'}
