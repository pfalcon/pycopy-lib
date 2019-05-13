import sys
import io
import os
import unittest
import gc
import contextlib


TESTFN = '@test'

def run_unittest(*classes):
    suite = unittest.TestSuite()
    for c in classes:
        if isinstance(c, str):
            c = __import__(c)
            for name in dir(c):
                obj = getattr(c, name)
                if isinstance(obj, type) and issubclass(obj, unittest.TestCase):
                    suite.addTest(obj)
        else:
            suite.addTest(c)
    runner = unittest.TestRunner()
    result = runner.run(suite)

def can_symlink():
    return False

def skip_unless_symlink(test):
    """Skip decorator for tests that require functional symlink"""
    ok = can_symlink()
    msg = "Requires functional symlink implementation"
    return test if ok else unittest.skip(msg)(test)

def create_empty_file(name):
    open(name, "w").close()

@contextlib.contextmanager
def disable_gc():
    have_gc = gc.isenabled()
    gc.disable()
    try:
        yield
    finally:
        if have_gc:
            gc.enable()

def gc_collect():
    gc.collect()
    gc.collect()
    gc.collect()

@contextlib.contextmanager
def captured_output(stream_name):
    org = getattr(sys, stream_name)
    buf = io.StringIO()
    setattr(sys, stream_name, buf)
    try:
        yield buf
    finally:
        setattr(sys, stream_name, org)

def captured_stderr():
    return captured_output("stderr")

def requires_IEEE_754(f):
    return f

@contextlib.contextmanager
def change_cwd(path, quiet=False):
    """Return a context manager that changes the current working directory.

    Arguments:

      path: the directory to use as the temporary current working directory.

      quiet: if False (the default), the context manager raises an exception
        on error.  Otherwise, it issues only a warning and keeps the current
        working directory the same.

    """
    saved_dir = os.getcwd()
    try:
        os.chdir(path)
    except OSError:
        if not quiet:
            raise
        warnings.warn('tests may fail, unable to change CWD to: ' + path,
                      RuntimeWarning, stacklevel=3)
    try:
        yield os.getcwd()
    finally:
        os.chdir(saved_dir)
