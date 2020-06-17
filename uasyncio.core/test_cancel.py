# Runs both in Pycopy and CPython.
import time
try:
    import uasyncio.core as asyncio
    is_uasyncio = True
except ImportError:
    import asyncio
    is_uasyncio = False
import logging
#logging.basicConfig(level=logging.DEBUG)
#asyncio.set_debug(True)


BUSY_SLEEP = 0

output = []
cancelled = False

# Can be used to make test run faster/slower and/or avoid floating point
# rounding errors.
def delay(n):
    return n / 10


def print1(msg):
    print(msg)
    output.append(msg)


def looper1(iters):
    global cancelled
    try:
        for i in range(iters):
            print1("ping1")
            if BUSY_SLEEP:
                t = time.time()
                while time.time() - t < delay(1):
                    yield from asyncio.sleep(0)
            else:
                yield from asyncio.sleep(delay(1))
        return 10
    except asyncio.CancelledError:
        print1("cancelled")
        cancelled = True

def looper2(iters):
    for i in range(iters):
        print1("ping2")
        if BUSY_SLEEP:
            t = time.time()
            while time.time() - t < delay(1):
                yield from asyncio.sleep(0)
        else:
            yield from asyncio.sleep(delay(1))
    return 10


def run_to():
    coro = looper1(10)
    task = loop.create_task(coro)
    yield from asyncio.sleep(delay(3))
    if is_uasyncio:
        asyncio.cancel(coro)
    else:
        task.cancel()
    # Need another eventloop iteration for cancellation to be actually
    # processed and to see side effects of the cancellation.
    yield from asyncio.sleep(0)
    assert cancelled

    coro = looper2(10)
    task = loop.create_task(coro)
    yield from asyncio.sleep(delay(2))
    if is_uasyncio:
        asyncio.cancel(coro)
    else:
        task.cancel()
    yield from asyncio.sleep(0)

    # Once saw 3 ping3's output on CPython 3.5.2
    assert output == ['ping1', 'ping1', 'ping1', 'cancelled', 'ping2', 'ping2']


loop = asyncio.get_event_loop()
loop.run_until_complete(run_to())
