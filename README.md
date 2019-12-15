pycopy-lib
==========
pycopy-lib is a project to develop a non-monolothic standard library
for the Pycopy project (https://github.com/pfalcon/pycopy), while
where possible, staying compatible with other variants and implementations
of Python. The goals of the project are:

* As the main goal, develop Pycopy standard library as close as possible
  matching that of CPython. It thus necessarily targets "Unix" port of
  Pycopy.
* As a side goal, develop individual modules usable/useful on baremetal
  ports of Pycopy. This is oftentimes conflicts with the first goal
  (something as close as possible matching CPython functionality is just
  too big to run on low-memory systems), and necessitates creation
  of additional modules, or special "micro" (aka "u") versions of them.

Each module or package of `pycopy-lib` is available as a separate
distribution package from PyPI. Each module comes from one of the following
sources (and thus each module has its own licensing terms):

* written from scratch specifically for Pycopy
* ported from CPython
* ported from some other Python implementation, e.g. PyPy
* some modules actually aren't implemented yet and are dummy
* some modules are extensions and are not part of CPython's
  standard library

As mentioned above, the main target of pycopy-lib is the "Unix" port
of Pycopy.Actual system requirements vary per module. Modules not
related to I/O may also work without problems on bare-metal ports, not
just on "Unix" port (e.g. esp8266).


Usage
-----
pycopy-lib packages are published on PyPI (Python Package Index),
the standard Python community package repository: http://pypi.python.org/ .
On PyPI, you can search for Pycopy related packages and read
additional package information. All pycopy-lib package names are prefixed
with "pycopy-".

Browse available packages
[via this URL](https://pypi.org/search/?q=pycopy-). (Note: this may
also include 3rd-party modules which are not part of pycopy-lib.)

To install packages from PyPI for usage on your local system, use the
`upip` tool, which is Pycopy's native package manager, similar to
`pip`, which is used to install packages for CPython. `upip` is bundled
with Pycopy "Unix" port (i.e. if you build "Unix" port, you
automatically have `upip` tool). Following examples assume that
`pycopy` binary is available on your `PATH`:

~~~~
$ pycopy -m upip install pycopy-pystone
...
$ pycopy
>>> import pystone
>>> pystone.main()
Pystone(1.2) time for 50000 passes = 0.534
This machine benchmarks at 93633 pystones/second
~~~~

Run `pycopy -m upip --help` for more information about `upip`.


CPython backports
-----------------
While pycopy-lib focuses on Pycopy, sometimes it may be beneficial
to run Pycopy code using CPython, e.g. to use code coverage, debugging,
etc. tools available for it. To facilitate such usage, pycopy-lib also
provides reimplementations ("backports") of Pycopy modules, which
run on CPython. This first of all applies to the builtin Pycopy "u"
modules, but as time goes on, backports of pycopy-lib's own modules can
be provided. Backport modules are in the directories named `cpython-*` of
this repository. On PyPI, these named
[pycopy-cpython-*](https://pypi.org/search/?q=pycopy-cpython-).

These modules should be installed with CPython's pip3 tool. Example session:

~~~
$ pip3 install --user pycopy-cpython-uhashlib
...
$ python3
...
>>> import uhashlib
>>> uhashlib.sha1(b"test").hexdigest()
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
AttributeError: 'sha1' object has no attribute 'hexdigest'
# Pycopy's uhashlib doesn't have hexdigest(), use ubinascii.hexlify(.digest())
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
pycopy-lib is a community project and can be implemented "fully" only
by contributions from interested parties. The contributions are expected
to adhere to [Contribution Guidelines](CONTRIBUTING.md).


Credits
-------
pycopy-lib is developed and maintained by Paul Sokolovsky
([@pfalcon](https://github.com/pfalcon/)) with the help of
Pycopy community.

List of modules specific to pycopy-lib
--------------------------------------

While pycopy-lib's primary way is to provide implementation
of Python standard library, pycopy-lib goes further and hosts
some extension modules which are deemed to be worth being a part
of "Pycopy standard library". This section lists them to easy
discovery:

* byteslib - similar to `string`, function variants of `bytes` methods.
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
* upip - Pycopy package manager, modelled after "pip" tool
* upysh - minimalistic filesystem shell using Python syntax
* urequests - subset of "requests" module
* urlib.urequest - small subset of urlib.request module
* utarfile - small subset of tarfile module
* utokenize - simple tokenizer for Python source
* uurequests - very small subset of "requests" module
* uwwwauth - HTTP Basic/Digest authentication algorithms
* xmltok2 - small/simple XML tokenizer
