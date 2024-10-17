# SPDX-FileCopyrightText: 2024-present Dylan Lukes <lukes.dylan@gmail.com>
#
# SPDX-License-Identifier: BSD-3-Clause
from renkon.core.trait import Trait, TraitKind, TraitPattern, TraitSpec

# TODO: implement reusable base
# class _Linear(Trait):
#     n: ClassVar[int]
#
#     # noinspection PyMethodOverriding
#     def __init_subclass__(cls, *, n: int, **kwargs: Any):
#         super().__init_subclass__(**kwargs)
#
#         pattern = TraitPattern(f"{Y} = ")
#
#         cls.n = n
#         cls.base_spec = TraitSpec(
#             id=f"{cls.__module__}.{cls.__qualname__}",
#             label=f"{cls.__qualname__}",
#             kind=TraitKind.MODEL,
#             pattern=TraitPattern("..."),
#        )


class Linear2(Trait):
    base_spec = TraitSpec(
        id="renkon.core.trait.linear.Linear2",
        label="Linear2",
        kind=TraitKind.MODEL,
        pattern=TraitPattern("{Y} = {b_1}*{X_1} + {b_0}"),
        typings={
            "X_1": "numeric",
            "Y": "numeric",
            **{b: "float" for b in ("b_0", "b_1")},
        },
    )


class Linear3(Trait):
    base_spec = TraitSpec(
        id="renkon.core.trait.linear.Linear3",
        label="Linear3",
        kind=TraitKind.MODEL,
        pattern=TraitPattern("{Y} = {b_2}*{X_2} + {b_1}*{X_1} + {b_0}"),
        typings={
            "X_2": "numeric",
            "X_1": "numeric",
            "Y": "numeric",
            **{b: "float" for b in ("b_0", "b_1", "b_2")},
        },
    )
