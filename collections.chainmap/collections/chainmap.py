class ChainMap:

    def __init__(self, *maps):
        if maps:
            self.maps = list(maps)
        else:
            self.maps = [{}]

    def __getitem__(self, k):
        for m in self.maps:
            if k in m:
                return m[k]
        raise KeyError(k)

    def __setitem__(self, k, v):
        self.maps[0][k] = v

    def __delitem__(self, k):
        del self.maps[0][k]

    def items(self):
        seen = set()
        for m in self.maps:
            for k, v in m.items():
                if k not in seen:
                    yield k, v
                    seen.add(k)
