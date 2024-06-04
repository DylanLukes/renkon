from pydantic import BaseModel

from renkon.core.model.sketch import SketchInfo


class Result(BaseModel):
    """
    Model representing a single trait inference result.
    """

    sketch: SketchInfo
    score: float
    match_mask: bytes
    match_pct: float


class ResultSet(BaseModel):
    """
    Model representing a set of trait inference results.
    """

    results: dict[str, Result]
