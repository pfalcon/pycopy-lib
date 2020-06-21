# Runs both in Pycopy and CPython.
import time
try:
    import uasyncio.core as asyncio
    is_uasyncio = True
except ImportError:
    import asyncio
    is_uasyncio = False


requested = None
cancelled = False

async def coro():
    global cancelled
    try:
        await asyncio.sleep(1)
        assert False, "sleep wasn't cancelled"
    except asyncio.CancelledError:
        now = time.time()
        diff = now - requested
        print("cancelled at: %s, delay: %s" % (now, diff))
        assert diff < 0.01
        cancelled = True


async def canceller(task):
    global requested
    if is_uasyncio:
        asyncio.cancel(task)
    else:
        task.cancel()
    requested = time.time()
    print("requested cancel at:", requested)
    await asyncio.sleep(0)


loop = asyncio.get_event_loop()

task = coro()
if is_uasyncio:
    loop.create_task(task)
else:
    task = loop.create_task(task)
loop.run_until_complete(canceller(task))
assert cancelled
