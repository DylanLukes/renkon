# SPDX-FileCopyrightText: 2023-present Dylan Lukes <lukes.dylan@gmail.com>
#
# SPDX-License-Identifier: BSD-3-Clause
import sys

if __name__ == '__main__':
    from .cli import renkon

    sys.exit(renkon())
