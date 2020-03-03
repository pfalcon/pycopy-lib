def update(s, *others):
    for o in others:
        s.update(o)
    return s


def union(s, *others):
    s = s.copy()
    update(s, *others)
    return s


def intersection_update(s, *others):
    for o in others:
        s.intersection_update(o)
    return s


def intersection(s, *others):
    s = s.copy()
    intersection_update(s, *others)
    return s


def difference_update(s, *others):
    for o in others:
        s.difference_update(o)
    return s


def difference(s, *others):
    s = s.copy()
    difference_update(s, *others)
    return s
