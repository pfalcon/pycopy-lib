# We mostly test that we don't error on annotation syntax here
from typing import *


def greeting(name: str) -> str:
    return 'Hello ' + name


def listfunc() -> List:
    return [1, 2]


Vector = List[float]

def scale(scalar: float, vector: Vector) -> Vector:
    return [scalar * num for num in vector]

new_vector = scale(2.0, [1.0, -4.2, 5.4])
assert new_vector == [2.0, -8.4, 10.8]

assert NewType("Id", int) == int

ConnectionOptions = Dict[str, str]
Address = Tuple[str, int]
Server = Tuple[Address, ConnectionOptions]
Tuple[int, ...]
Name: TypeAlias = str


def broadcast_message(message: str, servers: List[Server]) -> None:
    ...


Optional[int]

Union[int, float, None]


@overload
def process(response: None) -> None:
    ...

try:
    process()
    assert False, "Calling function defined with 'overload' decorator should result in NotImplementedError"
except NotImplementedError:
    pass
