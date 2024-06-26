# SPDX-FileCopyrightText: 2024-present Dylan Lukes <lukes.dylan@gmail.com>
#
# SPDX-License-Identifier: BSD-3-Clause

class TraitSketchError(Exception):
    pass


class UnsubstitutedMetavariableError(TraitSketchError):
    def __init__(self, missing_metavars: set[str]):
        super().__init__(f"TraitSketch has unsubstituted metavariables: {missing_metavars}", missing_metavars)
        self.missing_metavars = missing_metavars


class UnknownMetavariableError(TraitSketchError):
    def __init__(self, invalid_substs: set[str]):
        super().__init__(f"TraitSketch's schema has unknown metavariables: {invalid_substs}", invalid_substs)
        self.invalid_substs = invalid_substs
