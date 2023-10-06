
from ._sync import Error as ErrorBase
from ._sync import Outcome as OutcomeBase
from ._sync import Value as ValueBase

__all__ = ['Error', 'Outcome', 'Value', 'acapture', 'capture']


def capture(sync_fn, *args, **kwargs):
    """Run ``sync_fn(*args, **kwargs)`` and capture the result.

    Returns:
      Either a :class:`Value` or :class:`Error` as appropriate.

    """
    # _sync.capture references ErrorBase and ValueBase
    try:
        return Value(sync_fn(*args, **kwargs))
    except BaseException as exc:
        return Error(exc)


async def acapture(async_fn, *args, **kwargs):
    """Run ``await async_fn(*args, **kwargs)`` and capture the result.

    Returns:
      Either a :class:`Value` or :class:`Error` as appropriate.

    """
    try:
        return Value(await async_fn(*args, **kwargs))
    except BaseException as exc:
        return Error(exc)


class Outcome(OutcomeBase):
    pass

class Value(Outcome, ValueBase):
    async def asend(self, agen):
        self._set_unwrapped()
        return await agen.asend(self.value)


class Error(Outcome, ErrorBase):
    async def asend(self, agen):
        self._set_unwrapped()
        return await agen.athrow(self.error)


# We don't need this for Sphinx, but do it anyway for IPython, IDEs, etc
Outcome.__doc__ = OutcomeBase.__doc__
Value.__doc__ = ValueBase.__doc__
Error.__doc__ = ErrorBase.__doc__
