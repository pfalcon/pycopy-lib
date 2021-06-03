import json

inp = ['foo', {'bar': ('baz', None, 1, 2)}]
print(inp)

s = json.dumps(inp)
print(s)
assert s == '["foo", {"bar": ["baz", null, 1, 2]}]'

outp = json.loads(s)
print(outp)
assert outp == ['foo', {'bar': ['baz', None, 1, 2]}]
