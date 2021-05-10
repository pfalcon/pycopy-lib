import sys
from contextvars import ContextVar

current_async_library_cvar = ContextVar(
    "current_async_library_cvar", default=None
)


class AsyncLibraryNotFoundError(RuntimeError):
    pass


def current_async_library():
    """Detect which async library is currently running.

    The following libraries are currently supported:

    ================   ===========  ============================
    Library             Requires     Magic string
    ================   ===========  ============================
    **Trio**            Trio v0.6+   ``"trio"``
    **Curio**           -            ``"curio"``
    **asyncio**                      ``"asyncio"``
    **uasyncio**       MicroPython   ``"uasyncio"``
    **Trio-asyncio**    v0.8.2+     ``"trio"`` or ``"asyncio"``,
                                    depending on current mode
    ================   ===========  ============================

    Returns:
      A string like ``"trio"``.

    Raises:
      AsyncLibraryNotFoundError: if called from synchronous context,
        or if the current async library was not recognized.

    Examples:

        .. code-block:: python3

           from sniffio import current_async_library

           async def generic_sleep(seconds):
               library = current_async_library()
               if library == "trio":
                   import trio
                   await trio.sleep(seconds)
               elif library == "asyncio":
                   import asyncio
                   await asyncio.sleep(seconds)
               # ... and so on ...
               else:
                   raise RuntimeError(f"Unsupported library {library!r}")

    """
    value = current_async_library_cvar.get()
    if value is not None:
        return value

    # Sniff for curio (for now)
    if 'curio' in sys.modules:
        from curio.meta import curio_running
        if curio_running():
            return 'curio'

    # Need to sniff for asyncio
    if "asyncio" in sys.modules:
        import asyncio
        try:
            current_task = asyncio.current_task
        except AttributeError:
            current_task = asyncio.Task.current_task
        try:
            if current_task() is not None:
                if (3, 7) <= sys.version_info:
                    # asyncio has contextvars support, and we're in a task, so
                    # we can safely cache the sniffed value
                    current_async_library_cvar.set("asyncio")
                return "asyncio"
        except RuntimeError:
            pass

    # Need to sniff for uasyncio
    if "uasyncio" in sys.modules:
        import uasyncio
        current_task = uasyncio.get_event_loop().cur_task
        if current_task is not None:
            print("CT",current_task)
            return "uasyncio"

    raise AsyncLibraryNotFoundError(
        "unknown async library, or not in async context"
    )

__all__ = [
    "current_async_library", "UnknownAsyncLibraryError",
    "current_async_library_cvar"
]
