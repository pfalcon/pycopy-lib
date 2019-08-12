HTTP clients in pycopy-lib
==========================

pycopy-lib currently offers 4 HTTP client modules:

* ``urllib.urequest``
* ``urequests``
* ``uurequests``
* ``uaiohttpclient``

This README is intended to describe differences among them and help
to choose the right module for a particular use.

* ``urllib.urequest`` implements a subset of API CPython standard library
  module urllib.request. This module is intended to be the most minimal
  of all three and provide an efficient, stream-based API. It doesn't
  support automatic redirects or chunked transfer encoding.
* ``urequests`` implements a subset of API of the popular 3rd-party package
  ``requests``. ``requests`` brags itself as "HTTP for Humans", which
  means that its API is not ideal, and implementation is inefficient.
  ``urequests`` implements only a subset of it, and tries to mend some
  poor defaults of the prototype module. Still, it's less efficient
  than ``urllib.urequest``. Redirects are handled, but not chunked
  transfer encoding.
* ``uurequests`` is capture of the version 0.8 of ``urequests``, before
  opening the door for adding more features to the latter. It's provided
  for very small systems which still would like requests-like API.
* ``uaiohttpclient`` is an HTTP client for ``uasyncio`` module. It's
  the only of all 3 which supports chunked transfer encoding.

Thus, the selection guide:

* Whenever possible, use ``urllib.urequest``.
* If you write a once-off, throw-away app where you don't care about
  efficiency, you can use ``urequests``.
* If you wrote that for very small system and above didn't work, can
  give ``uurequests`` a try.
* If you devel an async app, use ``uaiohttpclient``.
* If you need support for more HTTP protocol features, use
  ``uaiohttpclient`` and write an async app.

Future of the modules:

* ``urllib.urequest`` is intended to stay minimal and unlikely will get more
  features (it's suitable for ~80% of possible usage scenarios).
* ``urequests`` has bloat in its DNA, so likely will slowly grow more features
  to match the upstream module, which will make it even less suitable for
  low-memory targets.
* ``uurequests`` was snapshotted to address concern of such low-memory systems
  support. It's static, and only critical bugfixes are intended to be applied.
* ``uaiohttpclient`` may get updated as needed.
