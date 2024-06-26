from renkon.core.model.trait import TraitForm, TraitInfo, TraitSort
from renkon.core.model.trait.sketch import SketchInfo


def test_sketch_info_round_trip() -> None:
    trait_info = TraitInfo(
        id="renkon.core.trait.linear.Linear2",
        name="Linear Regression (2D)",
        sort=TraitSort.MODEL,
        form=TraitForm(template="{y} = {a}*{x} + {b}", metavars=["x", "y"], params=["a", "b"]),
    )

    sketch_info = expected = SketchInfo(trait=trait_info, substs={"x": "t", "y": "money"})

    json_data = sketch_info.model_dump_json()
    actual = SketchInfo.model_validate_json(json_data)

    assert actual == expected
