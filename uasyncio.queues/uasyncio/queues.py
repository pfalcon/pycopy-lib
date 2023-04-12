from collections.deque import deque

from uasyncio import core


class QueueEmpty(Exception):
    """Exception raised by get_nowait()."""


class QueueFull(Exception):
    """Exception raised by put_nowait()."""


class Queue:
    """A queue, useful for coordinating producer and consumer coroutines.

    If maxsize is less than or equal to zero, the queue size is infinite. If it
    is an integer greater than 0, then "yield from put()" will block when the
    queue reaches maxsize, until an item is removed by get().

    Unlike the standard library Queue, you can reliably know this Queue's size
    with qsize(), since your single-threaded uasyncio application won't be
    interrupted between calling qsize() and doing an operation on the Queue.
    """

    def __init__(self, maxsize=0):
        self.maxsize = maxsize
        self._queue = deque()
        self._full = core.TaskQueue()
        self._empty = core.TaskQueue()

    def _get(self):
        res = self._queue.popleft()
        if self._full.peek():
            core._task_queue.push(self._full.pop())
        return res

    def get(self):
        """Returns generator, which can be used for getting (and removing)
        an item from a queue.

        Usage::

            item = await queue.get()
        """
        if not self._queue:
            self._empty.push(core.cur_task)
            core.cur_task.data = self._empty
            yield

        return self._get()

    def get_nowait(self):
        """Remove and return an item from the queue.

        Return an item if one is immediately available, else raise QueueEmpty.
        """
        if not self._queue:
            raise QueueEmpty()
        return self._get()

    def _put(self, val):
        if self._empty.peek():
            core._task_queue.push(self._empty.pop())
        self._queue.append(val)

    def put(self, val):
        """Returns generator which can be used for putting item in a queue.

        Usage::

            await queue.put(item)
        """
        if self.maxsize and self.qsize() >= self.maxsize:
            self._full.push(core.cur_task)
            core.cur_task.data = self._full
            yield
        self._put(val)

    def put_nowait(self, val):
        """Put an item into the queue without blocking.

        If no free slot is immediately available, raise QueueFull.
        """
        if self.maxsize and self.qsize() >= self.maxsize:
            raise QueueFull()
        self._put(val)

    def qsize(self):
        """Number of items in the queue."""
        return len(self._queue)

    def empty(self):
        """Return True if the queue is empty, False otherwise."""
        return not self._queue

    def full(self):
        """Return True if there are maxsize items in the queue.

        Note: if the Queue was initialized with maxsize=0 (the default),
        then full() is never True.
        """
        if self.maxsize <= 0:
            return False
        else:
            return self.qsize() >= self.maxsize
