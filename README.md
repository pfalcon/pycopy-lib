micropython-lib
===============
micropython-lib is a project to develop a non-monolothic standard library
for the Pycopy project (https://github.com/pfalcon/micropython), while
where possible, staying compatible with other variants of MicroPython, and
Python in general. The goals of the project are:

* As the main goal, develop Pycopy/MicroPython standard library as close
  as possible matching that of CPython. It thus necessarily targets "Unix"
  port of Pycopy.
* As a side goal, develop individual modules usable/useful on baremetal
  ports of Pycopy/MicroPython. This is oftentimes conflicts with the
  first goal (something as close as possible matching CPython functionality
  is just too big to run on low-memory systems), and necessitates creation
  of additional modules, or special "micro" (aka "u") versions of them.

Each module or package of micropython-lib is available as a separate
distribution package from PyPI. Each module comes from one of the following
sources (and thus each module has its own licensing terms):

* written from scratch specifically for MicroPython
* ported from CPython
* ported from some other Python implementation, e.g. PyPy
* some modules actually aren't implemented yet and are dummy
* some modules are extensions and are not part of CPython's
  standard library

As mentioned above, the main target of micropython-lib is the "Unix" port
of Pycopy (advanced fork of MicroPython). Actual system requirements vary per
module. Majority of modules are compatible with the upstream MicroPython,
though some may require additional functionality/optimizations present in
Pycopy. Modules not related to I/O may also work without problems on
bare-metal ports, not just on "Unix" port (e.g. pyboard).


Usage
-----
micropython-lib packages are published on PyPI (Python Package Index),
the standard Python community package repository: http://pypi.python.org/ .
On PyPI, you can search for MicroPython related packages and read
additional package information. By convention, all micropython-lib package
names are prefixed with "micropython-" (the reverse is not true - some
package starting with "micropython-" aren't part of micropython-lib and
were released by 3rd parties).

Browse available packages
[via this URL](https://pypi.org/search/?q=micropython). (Note: this may
also include 3rd-party modules which are not part of micropython-lib.)

To install packages from PyPI for usage on your local system, use the
`upip` tool, which is MicroPython's native package manager, similar to
`pip`, which is used to install packages for CPython. `upip` is bundled
with MicroPython "Unix" port (i.e. if you build "Unix" port, you
automatically have `upip` tool). Following examples assume that
`micropython` binary is available on your `PATH`:

~~~~
$ micropython -m upip install micropython-pystone
...
$ micropython
>>> import pystone
>>> pystone.main()
Pystone(1.2) time for 50000 passes = 0.534
This machine benchmarks at 93633 pystones/second
~~~~

Run `micropython -m upip --help` for more information about `upip`.


CPython backports
-----------------
While micropython-lib focuses on MicroPython, sometimes it may be beneficial
to run MicroPython code using CPython, e.g. to use code coverage, debugging,
etc. tools available for it. To facilitate such usage, micropython-lib also
provides reimplementations ("backports") of MicroPython modules which run on
CPython. This first of all applies to the builtin MicroPython "u" modules,
but as time goes on, backports of micropython-lib's own modules can be
provided. Backport modules are in the directories named `cpython-*` of
this repository. On PyPI, these named
[micropython-cpython-*](https://pypi.org/search/?q=micropython-cpython-).

These modules should be installed with CPython's pip3 tool. Example session:

~~~
$ pip3 install --user micropython-cpython-uhashlib
...
$ python3
...
>>> import uhashlib
>>> uhashlib.sha1(b"test").hexdigest()
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
AttributeError: 'sha1' object has no attribute 'hexdigest'
# MicroPython's uhashlib doesn't have hexdigest(), use ubinascii.hexlify(.digest())
>>> uhashlib.sha1(b"test").digest()
b'\xa9J\x8f\xe5\xcc\xb1\x9b\xa6\x1cL\x08s\xd3\x91\xe9\x87\x98/\xbb\xd3'
~~~


Development
-----------
To install modules during development, use `make install`. By default, all
available packages will be installed. To install a specific module, add the
`MOD=<module>` parameter to the end of the `make install` command.


Contributing
------------
micropython-lib is a community project and can be implemented "fully" only
by contributions from interested parties. The contributions are expected
to adhere to [Contribution Guidelines](CONTRIBUTING.md).


Links
-----
If you would like to trace evolution of MicroPython packaging support,
you may find following links useful (note that they may contain outdated
information):

 * https://github.com/micropython/micropython/issues/405
 * http://forum.micropython.org/viewtopic.php?f=5&t=70

Guidelines for packaging MicroPython modules for PyPI:

 * https://github.com/micropython/micropython/issues/413

Credits
-------
micropython-lib is developed and maintained by Paul Sokolovsky
([@pfalcon](https://github.com/pfalcon/)) with the help of MicroPython
community.

List of modules specific to micropython-lib
-------------------------------------------

While micropython-lib's primary way is to provide implementation
of Python standard library, micropython-lib goes further and hosts
some extension modules which are deemed to be worth being a part
of "MicroPython standard library". This section lists them to easy
discovery:

* uaiohttpclient - HTTP client for uasyncio
* uargparse - small subset of argparse module
* uasyncio - asynchronous scheduling and I/O, roughly based on CPython's
  asyncio
* uasyncio.core - just a scheduler part of uasyncio
* uasyncio.queues - subset of CPython's asyncio.Queue
* uasyncio.synchro - synchronization primitives for uasyncio (subset
  of asyncio's)
* uasyncio.udp - UDP support for uasyncio
* ucontextlib - subset of contextlib functionality
* uctypelib - higher-level helpers to define structure for the builtin
  uctype module
* uctypeslib2 - pretty printing support for uctypes structure definitions
* ucurses - small subset of curses module
* udnspkt - DNS packet handling (Sans I/O approach)
* ulogging - small subset of logging module
* umqtt.robust
* umqtt.simple
* upip - MicroPython package manager, modelled after "pip" tool
* upysh - minimalistic filesystem shell using Python syntax
* urequests - subset of "requests" module
* urlib.urequest - small subset of urlib.request module
* utarfile - small subset of tarfile module
* utokenize - simple tokenezer for Python source
* uurequests - very small subset of "requests" module
* uwwwauth - HTTP Basic/Digest authentication algorithms
* xmltok2 - small/simple XML tokenizer
