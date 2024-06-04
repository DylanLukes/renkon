from typing import Self

from pydantic import BaseModel, model_validator

from renkon.core.model.trait import TraitInfo


class SketchInfo(BaseModel):
    """
    Represents a sketch of a trait.

    :param trait: the trait being sketched.
    :param substs: the assignments of column names to metavariable names in the trait form.
    """

    trait: TraitInfo
    substs: dict[str, str]

    @model_validator(mode="after")
    def check_all_metavars_subst(self) -> Self:
        """
        Ensure that all metavars are substituted.
        """
        missing_substs = set(self.trait.form.metavars) - set(self.substs.keys())
        if missing_substs:
            raise MissingSubstitutionsError(missing_substs)
        return self

    @model_validator(mode="after")
    def check_no_subst_not_metavar(self) -> Self:
        """
        Ensure that all substitutions are for actual metavariable in the trait form.
        """
        invalid_substs = set(self.substs.keys()) - set(self.trait.form.metavars)
        if invalid_substs:
            raise InvalidSubstitutionsError(invalid_substs)
        return self


class MissingSubstitutionsError(Exception):
    def __init__(self, missing_substs: set[str]):
        super().__init__(f"Missing substitutions for holes: {missing_substs}", missing_substs)
        self.missing_substs = missing_substs


class InvalidSubstitutionsError(Exception):
    def __init__(self, invalid_substs: set[str]):
        super().__init__(f"Invalid substitutions: {invalid_substs}", invalid_substs)
        self.invalid_substs = invalid_substs
