import builtins
import sys


# In case it will be overriden later.
org_import = builtins.__import__


def new_module(name):
    mod = org_import("_imp_empty_mod")
    del sys.modules["_imp_empty_mod"]
    mod.__name__ = name
    return mod
