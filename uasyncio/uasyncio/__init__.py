# (c) 2014-2020 Paul Sokolovsky. MIT license.
from micropython import const
import uerrno
import uselect as select
import usocket as _socket
import uio
from uasyncio.core import *


DEBUG = 0
log = None

def set_debug(val):
    global DEBUG, log
    DEBUG = val
    if val:
        import ulogging
        log = ulogging.getLogger("uasyncio")


class PollEventLoop(EventLoop):

    def __init__(self, runq_len=16, waitq_len=16):
        EventLoop.__init__(self, runq_len, waitq_len)
        self.poller = select.poll()

    def add_reader(self, sock, cb, *args):
        if DEBUG and __debug__:
            log.debug("add_reader%s", (sock, cb, args))
        if args:
            self.poller.register(sock, select.POLLIN, (cb, args))
        else:
            self.poller.register(sock, select.POLLIN, cb)

    def remove_reader(self, sock):
        if DEBUG and __debug__:
            log.debug("remove_reader(%s)", sock)
        self.poller.unregister(sock, False)

    def add_writer(self, sock, cb, *args):
        if DEBUG and __debug__:
            log.debug("add_writer%s", (sock, cb, args))
        if args:
            self.poller.register(sock, select.POLLOUT, (cb, args))
        else:
            self.poller.register(sock, select.POLLOUT, cb)

    def remove_writer(self, sock):
        if DEBUG and __debug__:
            log.debug("remove_writer(%s)", sock)
        # StreamWriter.awrite() first tries to write to a socket,
        # and if that succeeds, yield IOWrite may never be called
        # for that socket, and it will never be added to poller. So,
        # ignore such error.
        self.poller.unregister(sock, False)

    def cancel_io(self, sock):
        if DEBUG and __debug__:
            log.debug("cancel_io(%s)", sock)
        # Cancel both reader and writer
        # Don't remove, in the hope that it will be used again, though
        # this call is usually used for timeouts, and timeouts are
        # usually handled as fatal errors (but then underlying stream
        # should be closed by user).
        # Use modify() deliberately, to catch a case when we cancel
        # a socket which was never pended, what shouldn't happen.
        self.poller.modify(sock, 0)

    def wait(self, delay):
        if DEBUG and __debug__:
            log.debug("poll.wait(%d)", delay)
        # We need one-shot behavior (second arg of 1 to .poll())
        res = self.poller.ipoll(delay, 1)
        #log.debug("poll result: %s", res)
        for sock, ev, cb in res:
            if ev & (select.POLLHUP | select.POLLERR):
                # These events are returned even if not requested, and
                # are sticky, i.e. will be returned again and again.
                # If the caller doesn't do proper error handling and
                # unregistering this sock, we'll busy-loop on it, so we
                # as well can unregister it now "just in case".
                self.remove_reader(sock)
            if DEBUG and __debug__:
                log.debug("Calling IO callback: %r", cb)
            if isinstance(cb, tuple):
                cb[0](*cb[1])
            else:
                cb.pend_throw(None)
                self.call_soon(cb)


class Stream:

    def __init__(self, polls, ios=None, extra=None):
        if ios is None:
            ios = polls
        self.polls = polls
        self.ios = ios
        self.extra = extra

    def read(self, n=-1):
        while True:
            res = self.ios.read(n)
            if res is None:
                yield IORead(self.polls)
            elif res is uio.WANT_WRITE:
                yield IOWrite(self.polls)
            else:
                break
        if not res:
            yield IOReadDone(self.polls)
        return res

    def readexactly(self, n):
        buf = b""
        while n:
            res = self.ios.read(n)
            if res is None:
                yield IORead(self.polls)
            elif res is uio.WANT_WRITE:
                yield IOWrite(self.polls)
            elif not res:
                yield IOReadDone(self.polls)
                break
            else:
                buf += res
                n -= len(res)
                # Give other tasks a chance to run
                yield
        return buf

    def readline(self):
        if DEBUG and __debug__:
            log.debug("StreamReader.readline()")
        buf = b""
        while True:
            res = self.ios.readline()
            if res is None:
                yield IORead(self.polls)
            elif res is uio.WANT_WRITE:
                yield IOWrite(self.polls)
            elif not res:
                yield IOReadDone(self.polls)
                break
            else:
                buf += res
                if buf[-1] == 0x0a:
                    break
                # Give other tasks a chance to run
                yield
        if DEBUG and __debug__:
            log.debug("StreamReader.readline(): %s", buf)
        return buf

    def awrite(self, buf, off=0, sz=-1):
        # This method is called awrite (async write) to not proliferate
        # incompatibility with original asyncio. Unlike original asyncio
        # whose .write() method is both not a coroutine and guaranteed
        # to return immediately (which means it has to buffer all the
        # data), this method is a coroutine.
        if sz == -1:
            sz = len(buf) - off
        if DEBUG and __debug__:
            log.debug("StreamWriter.awrite(): spooling %d bytes", sz)
        while sz:
            res = self.ios.write(buf, off, sz)
            # If we spooled everything, fast return
            if res == sz:
                if DEBUG and __debug__:
                    log.debug("StreamWriter.awrite(): completed spooling %d bytes", res)
                return
            elif res is None:
                yield IOWrite(self.polls)
            elif res is uio.WANT_READ:
                yield IORead(self.polls)
            else:
                if DEBUG and __debug__:
                    log.debug("StreamWriter.awrite(): spooled partial %d bytes", res)
                assert res != 0 and res < sz
                off += res
                sz -= res
                # Give other tasks a chance to run
                yield

    # This function is tentative, subject to change
    def awritestr(self, s):
        yield from self.awrite(s.encode())

    # Write piecewise content from iterable (usually, a generator)
    def awriteiter(self, iterable):
        for buf in iterable:
            yield from self.awrite(buf)

    def aclose(self):
        yield IOWriteDone(self.polls)
        self.ios.close()
        self.polls.close()

    def get_extra_info(self, name, default=None):
        return self.extra.get(name, default)

    def __repr__(self):
        return "<Stream %r %r>" % (self.polls, self.ios)


StreamReader = StreamWriter = const(Stream)


def open_connection(host, port, ssl=False, server_hostname=None):
    if DEBUG and __debug__:
        log.debug("open_connection(%s, %s)", host, port)
    ai = _socket.getaddrinfo(host, port, 0, _socket.SOCK_STREAM)
    ai = ai[0]
    s = _socket.socket(ai[0], ai[1], ai[2])
    s.setblocking(False)
    try:
        s.connect(ai[-1])
    except OSError as e:
        if e.args[0] != uerrno.EINPROGRESS:
            s.close()
            raise
    if DEBUG and __debug__:
        log.debug("open_connection: After connect")
    yield IOWrite(s)
    if DEBUG and __debug__:
        log.debug("open_connection: After iowait: %s", s)
    s2 = s
    if ssl:
        if ssl is True:
            import ussl
            ssl = ussl.SSLContext()
        s2 = ssl.wrap_socket(s, server_hostname=server_hostname, do_handshake=False)
        s2.setblocking(False)
    return StreamReader(s, s2), StreamWriter(s, s2)


def start_server(client_coro, host, port, backlog=10, ssl=None):
    if DEBUG and __debug__:
        log.debug("start_server(%s, %s)", host, port)
    ai = _socket.getaddrinfo(host, port, 0, _socket.SOCK_STREAM)
    ai = ai[0]
    s = _socket.socket(ai[0], ai[1], ai[2])
    s2 = None
    try:
        s.setblocking(False)
        s.setsockopt(_socket.SOL_SOCKET, _socket.SO_REUSEADDR, 1)
        s.bind(ai[-1])
        s.listen(backlog)
        while True:
            if DEBUG and __debug__:
                log.debug("start_server: Before accept")
            yield IORead(s)
            if DEBUG and __debug__:
                log.debug("start_server: After iowait")
            s2, client_addr = s.accept()
            s3 = s2
            if ssl:
                s3 = ssl.wrap_socket(s2, server_side=True, do_handshake=False)
            s3.setblocking(False)
            if DEBUG and __debug__:
                log.debug("start_server: After accept: %s", s2)
            extra = {"peername": client_addr}
            yield client_coro(StreamReader(s2, s3), StreamWriter(s2, s3, extra))
            s2 = s3 = None
    finally:
        if s2:
            s2.close()
        s.close()


import uasyncio.core
uasyncio.core._event_loop_class = PollEventLoop
