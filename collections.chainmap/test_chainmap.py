from collections.chainmap import ChainMap


cm = ChainMap({"k1": "v11", "k2": "v2"}, {"k1": "v12", "k3": "v3"})
assert cm["k1"] == "v11"
assert cm["k2"] == "v2"
assert cm["k3"] == "v3"

items = sorted(list(cm.items()))
assert items == [('k1', 'v11'), ('k2', 'v2'), ('k3', 'v3')]

del cm["k1"]
assert cm["k1"] == "v12"
cm["k1"] = "newv"
assert cm["k1"] == "newv"
del cm["k1"]
assert cm["k1"] == "v12"
