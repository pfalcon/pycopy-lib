# Runs both in Pycopy and CPython.
try:
    import uasyncio.core as asyncio
except ImportError:
    import asyncio
import logging
#logging.basicConfig(level=logging.DEBUG)
#asyncio.set_debug(True)


# Can be used to make test run faster/slower and/or avoid floating point
# rounding errors.
def delay(n):
    return n / 10


def looper(iters):
    for i in range(iters):
        print("ping")
        yield from asyncio.sleep(delay(1))
    return 10


def run_to():
    # Should time out
    try:
        ret = yield from asyncio.wait_for(looper(2), delay(1))
        print("result #1:", ret)
        assert False
    except asyncio.TimeoutError:
        print("Coro #1 timed out")

    print("=================")

    # The expected run time of coro == timeout, should still time out
    try:
        ret = yield from asyncio.wait_for(looper(2), delay(2))
        print("result #2:", ret)
        assert False
    except asyncio.TimeoutError:
        print("Coro #2 timed out")

    print("=================")

    # Should not time out
    try:
        ret = yield from asyncio.wait_for(looper(2), delay(3))
        print("result #3:", ret)
    except asyncio.TimeoutError:
        print("Coro #3 timed out")
        assert False


loop = asyncio.get_event_loop()
loop.run_until_complete(run_to())
# Catch any coros which may still run (due to bugs)
loop.run_until_complete(asyncio.sleep(delay(1)))
