{x: x + 1 for x in y}

(x for x in foo)
(x for x in foo if bar)
(x for x in foo if bar if baz)
any(x for x in foo)
[x for x in foo]
[(x for x in foo)]
[x for x in foo if 2]

(x for x in y for y in foo)
(x for x in y for y in foo if y)
(x for x in y if x for y in foo)
(x for x in y if x for y in foo if y)
[x for x in y if x for y in foo if y]

{x for x in y}

[lambda: None for x in y]

[x for x in s].copy()
