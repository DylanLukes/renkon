from renkon.store.store import Store
from tests.conftest import SAMPLES


def test_store_load_samples(store: Store) -> None:
    assert store.base_path.exists()
    assert store.base_path.is_dir()

    for name in SAMPLES:
        store.get_input_table_path(name)
        data = store.get_input_table(name)
        assert data is not None
        assert data.num_rows > 0
        assert data.num_columns > 0
