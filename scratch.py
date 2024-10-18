# SPDX-FileCopyrightText: 2024-present Dylan Lukes <lukes.dylan@gmail.com>
#
# SPDX-License-Identifier: BSD-3-Clause

from pydantic import BaseModel


class BaseA(BaseModel):
    def __eq__(self, other: object) -> bool:
        return isinstance(other, self.__class__)

    def __hash__(self) -> int:
        return hash(self.__class__)


class A(BaseA):
    pass


class BaseB:
    def __eq__(self, other: object) -> bool:
        return isinstance(other, self.__class__)

    def __hash__(self) -> int:
        return hash(self.__class__)


class B(BaseB):
    pass


_1 = {BaseA()}  # OK
_2 = {BaseB()}  # OK
_3 = {A()}  # Pyright: Set entry must be hashable. Type "A" is not hashable (reportUnhashable)
_4 = {B()}  # OK
