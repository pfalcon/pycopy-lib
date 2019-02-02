import utime
try:
    import uasyncio.core as asyncio
except ImportError:
    import asyncio


requested = None

async def coro():
    try:
        await asyncio.sleep(1)
        assert False, "sleep wasn't cancelled"
    except asyncio.CancelledError:
        now = utime.ticks_ms()
        diff = utime.ticks_diff(now, requested)
        print("cancelled at: %s, delay: %s" % (now, diff))
        assert diff < 10


async def canceller(task):
    global requested
    asyncio.cancel(task)
    requested = utime.ticks_ms()
    print("requested cancel at:", requested)
    await asyncio.sleep(1)


loop = asyncio.get_event_loop()

task = coro()
loop.create_task(task)
loop.run_until_complete(canceller(task))
