# SPDX-FileCopyrightText: 2024-present Dylan Lukes <lukes.dylan@gmail.com>
#
# SPDX-License-Identifier: BSD-3-Clause
from typing import Protocol

from bitarray import bitarray


class TraitRenderer[R]: ...


class SketchRenderer[R]: ...


class ResultRenderer[R](Protocol):
    """

    :param R: the type of the rendered result.
    """

    def render(self) -> R: ...

    def render_score(self, score: float) -> R: ...

    def render_mask(self, mask: bitarray) -> R: ...


class RendererFactory[R](Protocol):
    """
    Abstract factory that produces a family of compatible renderers
    for various Renkon models.

    Examples of renderer families include:

    - Plain Text
    - Rich TTY
    - JSON
    - HTML

    :param R: the type of the rendered result.
    """

    def make_trait_renderer(self) -> TraitRenderer[R]: ...

    def make_sketch_renderer(self) -> SketchRenderer[R]: ...

    def make_result_renderer(self) -> ResultRenderer[R]: ...
