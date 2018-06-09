uasyncio
========

uasyncio is MicroPython's asynchronous sheduling library, roughly
modeled after CPython's asyncio.

uasyncio doesn't use naive always-iterating scheduling algorithm,
but performs a real time-based scheduling, which allows it (and
thus the whole system) to sleep when there is nothing to do (actual
implementation of that depends on I/O scheduling algorithm which
actually performs the wait operation).

Major conceptual differences to asyncio:

* Avoids defining a notion of Future, and especially wrapping coroutines
  in Futures, like CPython asyncio does. uasyncio works directly with
  coroutines (and callbacks).
* Methods provided are more consistently coroutines.
* uasyncio uses wrap-around millisecond timebase (as native to all
  MicroPython ports.)
* Instead of single large package, number of subpackages are provided
  (each installable separately).

Specific differences:

* For millisecond scheduling, ``loop.call_later_ms()`` and
  ``uasyncio.sleep_ms()`` are provided.
* As there's no monotonic time, ``loop.call_at()`` is not provided.
  Instead, there's ``loop.call_at_()`` which is considered an internal
  function and has slightly different signature.
* ``call_*`` funcions don't return Handle and callbacks scheduled by
  them aren't cancellable. If they need to be cancellable, they should
  accept an object as an argument, and a "cancel" flag should be set
  in the object, for a callback to test.
* ``Future`` object is not available.
* ``ensure_future()`` and ``Task()`` perform just scheduling operations
  and return a native coroutine, not Future/Task objects.
* Some other functions are not (yet) implemented.
* StreamWriter method(s) are coroutines. While in CPython asyncio,
  StreamWriter.write() is a normal function (which potentially buffers
  unlimited amount of data), uasyncio offers coroutine StreamWriter.awrite()
  instead. Also, both StreamReader and StreamWriter have .aclose()
  coroutine method.


Advanced topics
---------------

Terminology:

* Task - a top-level coroutine, scheduled in an event loop using its
  create_task() method. (Or, as a uasyncio extension, a couroutine
  object passed to the "yield" statement by another coroutine, this
  is equivalent to the create_task() call). Different tasks run
  concurrently in a cooperative manner. Each task can also call
  another coroutine recursively (in which case calling coroutine
  will "await" (literally) completion of the called coroutine). More
  formally, a task is a coroutine call tree routed in the top-level
  coroutine passed to create_tast(), and identified by it.

Notes on resource sharing between the tasks
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Just as sharing resources between preemptive threads, sharing resources
between uasyncio cooperative tasks has its peculiarities and limitations.
Actually, due to I/O scheduling implementation, there're additional
peculiarities to consider. But let's start with stating that resource
sharing between tasks/threads is usually an error. For example, if both
tasks write to the resource, their would be interspersed, possibly in
an unpredictable way. Reading is even more problematic: different tasks
may get partial input, or one can get all and other none at all. If tasks
implement some protocol, i.e. I/O dialog, that would lead to incorrect
behavior and/or deadlock. Thus, the rule is: don't share the same I/O
objects, in particular StreamReader and StreamWriter objects, among
different tasks. (Of course, they can be passed to subcourotines of the
current task).

An extreme case of the above is trying to use reader part of the same
StreamReader/StreamWriter part in one task, while writer - in another.
This may be only speculative use, and isn't supported either:
StreamReader and StreamWriter represent half-duplex parts of the same
I/O stream, and both must be used within one task. If you need something
like the above, you need to create different StreamReader/Writer pairs
(likely, from different underlying I/O objects).

While StreamReader/StreamWriter are given as examples above, it applies
to other I/O objects too. For example, uasyncio.udp socket just the
same should not be passed to 2 different tasks. If you need this, 2
different sockets should be used.
