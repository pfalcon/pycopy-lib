logging
=======

logging is Pycopy's implementation of a subset of CPythons logging module. This
module defines functions and classes which implement a flexible event logging system for
applications and libraries.

Major differences to CPython logging:

* No event propagation: events logged to a logger will not be passed to the handlers of
  higher level (ancestor) logger. In CPython this matches the behaviour achieved by
  setting ``Logger.propagate = False``.
* Filters are not supported

Requirements
------------

At the time of writing, logging requires the `os <https://pypi.org/project/pycopy-os/>`_
package (installed automatically by the ``upip`` tool).
