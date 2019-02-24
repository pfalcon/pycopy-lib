class partial:
    def __init__(self, func, *args, **kwargs):
        self.func = func
        self.args = args
        self.kwargs = kwargs

    def __call__(self, *more_args, **more_kwargs):
        kw = self.kwargs.copy()
        kw.update(more_kwargs)
        return self.func(*(self.args + more_args), **kw)


def update_wrapper(wrapper, wrapped, assigned=None, updated=None):
    # Dummy impl
    return wrapper


def wraps(wrapped, assigned=None, updated=None):
    # Dummy impl
    return lambda x: x


def reduce(function, iterable, initializer=None):
    it = iter(iterable)
    if initializer is None:
        value = next(it)
    else:
        value = initializer
    for element in it:
        value = function(value, element)
    return value
