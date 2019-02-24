# coding: utf-8
from __future__ import absolute_import, division, print_function

import abc
import sys


class AlreadyUsedError(RuntimeError):
    """An Outcome can only be unwrapped once."""
    pass


def fixup_module_metadata(module_name, namespace):
    def fix_one(obj):
        mod = getattr(obj, "__module__", None)
        if mod is not None and mod.startswith("outcome."):
            obj.__module__ = module_name
            if isinstance(obj, type):
                for k in dir(obj):
                    attr_value = getattr(obj, k)
                    fix_one(attr_value)

    for objname in namespace["__all__"]:
        obj = namespace[objname]
        fix_one(obj)


