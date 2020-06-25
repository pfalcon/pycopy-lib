# Coroutine which is scheduled and immediately cancelled shouldn't be
# run at all.
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


cancelled = False


def looper1():
    assert False
    yield from asyncio.sleep(0)


def run():
    coro = looper1()
    task = loop.create_task(coro)
    if is_uasyncio:
        asyncio.cancel(coro)
    else:
        task.cancel()
    yield from asyncio.sleep(0)


loop = asyncio.get_event_loop()
loop.run_until_complete(run())
assert not cancelled
