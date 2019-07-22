#!/usr/bin/env python3
# Pycopy will pick up glob from the current dir otherwise.
import sys
sys.path.pop(0)

import glob


TEMPLATE = """\
import sys
# Remove current dir from sys.path, otherwise setuptools will peek up our
# module instead of system's.
sys.path.pop(0)
from setuptools import setup
sys.path.append("..")
import sdist_upip

setup(name='pycopy-%(dist_name)s',
      version='%(version)s',
      description=%(desc)r,
      long_description=%(long_desc)s,
      url='https://github.com/pfalcon/pycopy-lib',
      author=%(author)r,
      author_email=%(author_email)r,
      maintainer=%(maintainer)r,
      maintainer_email=%(maintainer_email)r,
      license=%(license)r,
      cmdclass={'sdist': sdist_upip.sdist},
      %(_what_)s=[%(modules)s]%(_inst_req_)s)
"""

TEMPLATE_CPYTHON = """\
import sys
# Remove current dir from sys.path, otherwise setuptools will peek up our
# module instead of system's.
sys.path.pop(0)
from setuptools import setup
sys.path.append("..")

setup(name='pycopy-%(dist_name)s',
      version='%(version)s',
      description=%(desc)r,
      long_description=%(long_desc)s,
      url='https://github.com/pfalcon/pycopy-lib',
      author=%(author)r,
      author_email=%(author_email)r,
      maintainer=%(maintainer)r,
      maintainer_email=%(maintainer_email)r,
      license=%(license)r,
      %(_what_)s=[%(modules)s]%(_inst_req_)s)
"""

DUMMY_DESC = """\
This is a dummy implementation of a module for the standard library of
Pycopy project (https://github.com/pfalcon/pycopy).
It contains zero or very little functionality, and primarily intended to
avoid import errors (using idea that even if an application imports a
module, it may be not using it onevery code path, so may work at least
partially). It is expected that more complete implementation of the module
will be provided later. Please help with the development if you are
interested in this module."""

CPYTHON_DESC = """\
This is a module ported from CPython standard library to be compatible with
Pycopy project (https://github.com/pfalcon/pycopy). Usually, this means
applying small patches for features not supported (yet, or at all) in Pycopy.
Sometimes, heavier changes are required. Note that CPython modules are written
with availability of vast resources in mind, and may not work for Pycopy ports
with limited heap. If you are affected by such a case, please help reimplement
the module from scratch."""

PYPY_DESC = """\
This is a module ported from CPython standard library to be compatible with
Pycopy project (https://github.com/pfalcon/pycopy). Usually, this means
applying small patches for features not supported (yet, or at all) in Pycopy.
Sometimes, heavier changes are required. Note that PyPy modules are written
with availability of vast resources in mind, and may not work for Pycopy ports
with limited heap. If you are affected by such a case, please help reimplement
the module from scratch."""

PYCOPY_LIB_DESC = """\
This is a module for the standard library of Pycopy project:
https://github.com/pfalcon/pycopy . This module was implemented from
scratch specifically to target Pycopy, with efficient and lean design
in mind. Note that this module is likely work in progress and likely
supports just a subset of CPython’s corresponding module. Please help
with the development if you are interested in this module.
"""

BACKPORT_DESC = """\
This is a compatibility module for the standard library of Pycopy project
(https://github.com/pfalcon/pycopy). It allows applications using
Pycopy APIs to run on CPython.
"""

PYCOPY_DEVELS = 'Paul Sokolovsky'
PYCOPY_DEVELS_EMAIL = 'pycopy-dev@googlegroups.com'
CPYTHON_DEVELS = 'CPython Developers'
CPYTHON_DEVELS_EMAIL = 'python-dev@python.org'
PYPY_DEVELS = 'PyPy Developers'
PYPY_DEVELS_EMAIL = 'pypy-dev@python.org'

def parse_metadata(f):
    data = {}
    for l in f:
        l = l.strip()
        if l[0] == "#":
            continue
        k, v = l.split("=", 1)
        data[k.strip()] = v.strip()
    return data


def write_setup(fname, template, substs):
    with open(fname, "w") as f:
        f.write(template % substs)


def main():
    for fname in glob.iglob("*/metadata.txt"):
        print(fname)
        with open(fname) as f:
            data = parse_metadata(f)

        dirname = fname.split("/")[0]
        module = dirname
        template = TEMPLATE

        if data["type"] == "module":
            data["_what_"] = "py_modules"
        elif data["type"] == "package":
            data["_what_"] = "packages"
        else:
            raise ValueError

        data["maintainer_email"] = PYCOPY_DEVELS_EMAIL

        if data["srctype"] == "dummy":
            data["author"] = PYCOPY_DEVELS
            data["author_email"] = PYCOPY_DEVELS_EMAIL
            data["maintainer"] = PYCOPY_DEVELS
            data["license"] = "MIT"
            data["desc"] = "Dummy %s module for Pycopy" % module
            data["long_desc"] = DUMMY_DESC
        elif data["srctype"] == "cpython":
            data["author"] = CPYTHON_DEVELS
            data["author_email"] = CPYTHON_DEVELS_EMAIL
            data["maintainer"] = PYCOPY_DEVELS
            data["license"] = "Python"
            data["desc"] = "CPython %s module ported to Pycopy" % module
            data["long_desc"] = CPYTHON_DESC
        elif data["srctype"] == "pypy":
            data["author"] = PYPY_DEVELS
            data["author_email"] = PYPY_DEVELS_EMAIL
            data["maintainer"] = PYCOPY_DEVELS
            data["license"] = "MIT"
            data["desc"] = "PyPy %s module ported to Pycopy" % module
            data["long_desc"] = PYPY_DESC
        elif data["srctype"] in ("micropython-lib", "pycopy-lib"):
            if "author" not in data:
                data["author"] = PYCOPY_DEVELS
            if "author_email" not in data:
                data["author_email"] = PYCOPY_DEVELS_EMAIL
            if "maintainer" not in data:
                data["maintainer"] = PYCOPY_DEVELS
            if "desc" not in data:
                data["desc"] = "%s module for Pycopy" % module
            if "long_desc" not in data:
                data["long_desc"] = PYCOPY_LIB_DESC
            if "license" not in data:
                data["license"] = "MIT"
        elif data["srctype"] == "cpython-backport":
            assert module.startswith("cpython-")
            template = TEMPLATE_CPYTHON
            module = module[len("cpython-"):]
            data["author"] = PYCOPY_DEVELS
            data["author_email"] = PYCOPY_DEVELS_EMAIL
            data["maintainer"] = PYCOPY_DEVELS
            data["license"] = "Python"
            data["desc"] = "Pycopy module %s ported to CPython" % module
            data["long_desc"] = BACKPORT_DESC
        else:
            raise ValueError

        if "dist_name" not in data:
            data["dist_name"] = dirname
        if "name" not in data:
            data["name"] = module
        if data["long_desc"] in ("README", "README.rst"):
            data["long_desc"] = "open(%r).read()" % data["long_desc"]
        else:
            data["long_desc"] = repr(data["long_desc"])

        data["modules"] = "'" + data["name"].rsplit(".", 1)[0] + "'"
        if "extra_modules" in data:
            extra_modules = ["'" + x.strip() + "'" for x in data["extra_modules"].split(",")]
            if any(" " in d for d in extra_modules):
                raise ValueError("extra_modules should be comma separated")
            data["modules"] += ", " + ", ".join(extra_modules)

        if "depends" in data:
            deps = ["pycopy-" + x.strip() for x in data["depends"].split(",")]
            if any(" " in d for d in deps):
                raise ValueError("depends should be comma separated")
            data["_inst_req_"] = ",\n      install_requires=['" + "', '".join(deps) + "']"
        else:
            data["_inst_req_"] = ""

        write_setup(dirname + "/setup.py", template, data)


if __name__ == "__main__":
    main()
