# SPDX-FileCopyrightText: 2024-present Dylan Lukes <lukes.dylan@gmail.com>
#
# SPDX-License-Identifier: BSD-3-Clause
from typing import final

from renkon.core.model import TraitSpec
from renkon.core.model.type import Type
from renkon.core.traits.base import Trait

@final
class Equal(Trait):
    spec = TraitSpec.model_validate({
        "id": f"{__package__}.Equal",
        "name": "Equal",
        "kind": "logical",
        "pattern": "{A} = {B}",
        "commutors": [{"A", "B"}],
        "typevars": {
            "T": "equatable",
        },
        "typings": {
            "A": "T",
            "B": "T"
        }
    })


def test_equal():
    eq = Equal()
    print(eq.sketch(A=Type.int(), B=Type.int()))
