# SPDX-FileCopyrightText: 2024-present Dylan Lukes <lukes.dylan@gmail.com>
#
# SPDX-License-Identifier: BSD-3-Clause
from renkon.core.model.schema import Schema


def test_schema():
    schema = Schema({})
    print(schema)

def test_schema_as_model_field():
    pass