import uselect
from ucollections import namedtuple


EVENT_READ = uselect.POLLIN
EVENT_WRITE = uselect.POLLOUT


SelectorKey = namedtuple("SelectorKey", ["fileobj", "fd", "events", "data"])


class PollSelector:

    def __init__(self):
        self.poll = uselect.poll()
        self.fmap = {}

    def register(self, fileobj, events, data=None):
        key = SelectorKey(fileobj, fileobj, events, data)
        self.fmap[id(fileobj)] = key
        self.poll.register(fileobj, events)
        return key

    def unregister(self, fileobj):
        self.poll.unregister(fileobj)
        return self.fmap.pop(id(fileobj))

    def modify(self, fileobj, events, data=None):
        self.poll.modify(fileobj, events)
        key = SelectorKey(fileobj, fileobj, events, data)
        self.fmap[id(fileobj)] = key

    def select(self, timeout=None):
        if timeout is None:
            timeout = -1
        elif timeout <= 0:
            timeout = 0
        else:
            timeout = int(timeout * 1000)
        ret = []
        for ready in self.poll.poll(timeout):
            ret.append((self.fmap[id(ready[0])], ready[1]))
        return ret


DefaultSelector = PollSelector
