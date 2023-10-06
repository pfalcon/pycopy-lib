# coding: utf-8

class AlreadyUsedError(RuntimeError):
    """An Outcome can only be unwrapped once."""
    pass


