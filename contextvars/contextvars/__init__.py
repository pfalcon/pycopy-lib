import collections.abc

import immutables


__all__ = ('ContextVar', 'Context', 'Token', 'copy_context')


_NO_DEFAULT = object()


class Context(collections.abc.Mapping):

    def __init__(self):
        self._data = immutables.Map()
        self._prev_context = None

    def run(self, callable, *args, **kwargs):
        if self._prev_context is not None:
            raise RuntimeError(
                'cannot enter context: {} is already entered'.format(self))

        self._prev_context = _get_context()
        try:
            _set_context(self)
            return callable(*args, **kwargs)
        finally:
            _set_context(self._prev_context)
            self._prev_context = None

    def copy(self):
        new = Context()
        new._data = self._data
        return new

    def __getitem__(self, var):
        if not isinstance(var, ContextVar):
            raise TypeError(
                "a ContextVar key was expected, got {!r}".format(var))
        return self._data[var]

    def __contains__(self, var):
        if not isinstance(var, ContextVar):
            raise TypeError(
                "a ContextVar key was expected, got {!r}".format(var))
        return var in self._data

    def __len__(self):
        return len(self._data)

    def __iter__(self):
        return iter(self._data)


class ContextVar:

    def __init__(self, name, *, default=_NO_DEFAULT):
        if not isinstance(name, str):
            raise TypeError("context variable name must be a str")
        self.name = name
        self.default = default

    def get(self, default=_NO_DEFAULT):
        ctx = _get_context()
        try:
            return ctx[self]
        except KeyError:
            pass

        if default is not _NO_DEFAULT:
            return default

        if self.default is not _NO_DEFAULT:
            return self.default

        raise LookupError

    def set(self, value):
        ctx = _get_context()
        data = ctx._data
        try:
            old_value = data[self]
        except KeyError:
            old_value = Token.MISSING

        updated_data = data.set(self, value)
        ctx._data = updated_data
        return Token(ctx, self, old_value)

    def reset(self, token):
        if token._used:
            raise RuntimeError("Token has already been used once")

        if token._var is not self:
            raise ValueError(
                "Token was created by a different ContextVar")

        if token._context is not _get_context():
            raise ValueError(
                "Token was created in a different Context")

        ctx = token._context
        if token._old_value is Token.MISSING:
            ctx._data = ctx._data.delete(token._var)
        else:
            ctx._data = ctx._data.set(token._var, token._old_value)

        token._used = True

    def __repr__(self):
        r = '<ContextVar name=' + repr(self.name)
        if self.default is not _NO_DEFAULT:
            r += ' default=' +repr(self.default)
        return r + ' at %x>' % id(self)


class Token:

    MISSING = object()

    def __init__(self, context, var, old_value):
        self._context = context
        self._var = var
        self._old_value = old_value
        self._used = False

    @property
    def var(self):
        return self._var

    @property
    def old_value(self):
        return self._old_value

    def __repr__(self):
        r = '<Token '
        if self._used:
            r += ' used'
        r += ' var={!r} at {:0x}>'.format(self._var, id(self))
        return r


def copy_context():
    return _get_context().copy()


def _get_context():
    ctx = getattr(_state, 'context', None)
    if ctx is None:
        ctx = Context()
        _state.context = ctx
    return ctx


def _set_context(ctx):
    _state.context = ctx


class _State:
    context = None
_state = _State()
