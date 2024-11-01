# SPDX-FileCopyrightText: 2024-present Dylan Lukes <lukes.dylan@gmail.com>
#
# SPDX-License-Identifier: BSD-3-Clause
import pytest
from renkon.core.schema import Schema


def test_schema_init_empty():
    _ = Schema({})
