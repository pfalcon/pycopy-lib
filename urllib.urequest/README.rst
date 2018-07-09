HTTP clients in micropython-lib
===============================

micropython-lib currently offers 3 HTTP client modules:

* ``urllib.urequest``
* ``urequests``
* ``uaiohttpclient``

This README is intended to describe differences among them and help
to choose the right module for a particular use.

* ``urllib.urequest`` implements a subset of API CPython standard library
  module urllib.request. This module is intended to be the most minimal
  of all three and provide the efficient, stream-based API.
* ``urequests`` implements a subset of API of the popular 3rd-party package
  ``requests``. ``requests`` brags itself as "HTTP for Humans", which
  means that its API is not ideal, and implementation is inefficient.
  ``urequests`` implements only a subset of it, and tries to mend some
  poor defaults of the prototype module. Still, it's less efficient
  than ``urllib.urequest``.
* ``uaiohttpclient`` is an HTTP client for ``uasyncio`` module. It's
  the only of all 3 which supports chunked transfer encoding and redirects.

Thus, the selection guide:

* Whenever possible, use ``urllib.urequest``.
* If you write a once-off, throw-away app where you don't care about
  efficiency, you can use ``urequests``.
* If you devel an async app, use ``uaiohttpclient``.
* If you need support for more HTTP protocol features, use
  ``uaiohttpclient`` and write an async app.

Future of the modules:

``urllib.urequest`` is intended to stay minimal and unlikely will get more
features (it's suitable for ~80% of possible usage scenarios). ``urequests``
has bloat in its DNA, so likely will slowly grow more features to match the
upstream module, which will make it even less suitable for low-memory targets.
``uaiohttpclient`` may get updated as need.
