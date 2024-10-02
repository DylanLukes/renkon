# SPDX-FileCopyrightText: 2024-present Dylan Lukes <lukes.dylan@gmail.com>
#
# SPDX-License-Identifier: BSD-3-Clause
from renkon.core.trait import Equal


def test_name_id():
    print(Equal.base_spec.label)
    print(Equal.base_spec.id)
