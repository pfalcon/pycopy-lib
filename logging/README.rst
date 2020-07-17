logging
=======

logging is Pycopy's implementation of a subset of CPythons logging module. This
module defines functions and classes which implement a flexible event logging system for
applications and libraries.

Major differences to CPython logging:

* Simplified event propagation, multilevel logger organization is not handled,
  currently there're just 2 levels: root logger and specific named loggers.
* Filters are not supported.

Requirements
------------

At the time of writing, logging requires the `os <https://pypi.org/project/pycopy-os/>`_
package (installed automatically by the ``upip`` tool).
