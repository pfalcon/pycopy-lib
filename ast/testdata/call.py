foo(kw1=1)
foo(1, bar, kw1=1, kw2=(1, 2))
foo(*args)
foo(1, 2, *args)
foo(**kwargs)
foo(1, 2, foo="bar", **kwargs)

foo(1, 2,)
