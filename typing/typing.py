TYPE_CHECKING = False

class _Subscriptable:

    def __getitem__(self, sub):
        return _SubSingleton

    def __class_getitem__(self, sub):
        return _Subscriptable

_SubSingleton = _Subscriptable()

def TypeVar(new_type, *types, **kw):
    return None

class Any: pass
Text = str
class NoReturn: pass
class ClassVar: pass
Union = _SubSingleton
Optional = _SubSingleton
Generic = _Subscriptable
NamedTuple = _SubSingleton
class Hashable: pass
class Awaitable: pass
class Coroutine: pass
class AsyncIterable: pass
class AsyncIterator: pass
Iterable = _Subscriptable
Iterator = _Subscriptable
Literal = _Subscriptable
Reversible = _Subscriptable
Sized = _Subscriptable
Container = _Subscriptable
Collection = _Subscriptable
Callable = _Subscriptable
AbstractSet = _Subscriptable
MutableSet = _Subscriptable
Mapping = _Subscriptable
MutableMapping = _Subscriptable
Sequence = _Subscriptable
MutableSequence = _Subscriptable
ByteString = _Subscriptable
Tuple = _Subscriptable
List = _Subscriptable
Deque = _Subscriptable
Set = _Subscriptable
FrozenSet = _Subscriptable
MappingView = _Subscriptable
KeysView = _Subscriptable
ItemsView = _Subscriptable
ValuesView = _Subscriptable
ContextManager = _Subscriptable
AsyncContextManager = _Subscriptable
Dict = _Subscriptable
DefaultDict = _Subscriptable
class Counter: pass
class ChainMap: pass
class Generator: pass
class AsyncGenerator: pass
class Type: pass
IO = _SubSingleton
TextIO = IO[str]
BinaryIO = IO[bytes]

AnyStr = TypeVar("AnyStr", str, bytes)


def cast(typ, val):
    return val


def _overload_dummy(*args, **kwds):
    """Helper for @overload to raise when called."""
    raise NotImplementedError(
        "You should not call an overloaded function. "
        "A series of @overload-decorated functions "
        "outside a stub module should always be followed "
        "by an implementation that is not @overload-ed."
    )


def overload(fun):
    return _overload_dummy
