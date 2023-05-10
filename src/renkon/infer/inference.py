from typing import Generic, TypeVar

import pyarrow as pa

from renkon.core.sketch import Sketch

_SK = TypeVar("_SK", bound=Sketch)


class Inference(Generic[_SK]):
    sketch: _SK

    def __init__(self, sketch: _SK) -> None:
        self.sketch = sketch


def infer(sketch: Sketch, _data: pa.Table) -> Inference[Sketch]:
    return Inference(sketch)
