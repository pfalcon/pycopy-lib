from . import foo
from .. import foo
from bar import foo
from .bar import foo
from bar.baz import foo
from . import foo as foo1, bar, baz as baz2

from bar import (one, two)
from bar import (one, two,)
