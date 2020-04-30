def update(s, *others):
    for o in others:
        if not isinstance(o, (set, frozenset)):
            o = set(o)
        s |= o


def union(s, *others):
    s = s.copy()
    update(s, *others)
    return s


def intersection_update(s, *others):
    for o in others:
        if not isinstance(o, (set, frozenset)):
            o = set(o)
        s &= o


def intersection(s, *others):
    s = s.copy()
    intersection_update(s, *others)
    return s


def difference_update(s, *others):
    for o in others:
        if not isinstance(o, (set, frozenset)):
            o = set(o)
        s -= o


def difference(s, *others):
    s = s.copy()
    difference_update(s, *others)
    return s
