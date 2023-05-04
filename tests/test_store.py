from pprint import pprint

from renkon.store.store import Store
from tests.conftest import SAMPLES

from pyarrow import compute as pc


def test_store_load_samples(store: Store):
    assert store.base_path.exists()
    assert store.base_path.is_dir()

    for name in SAMPLES:
        path = store.get_input_table_path(name)
        data = store.get_input_table(name)
        assert data is not None
        assert data.num_rows > 0
        assert data.num_columns > 0

        if 'corrupt' in name:
            print(pc.is_null(data['calories'], nan_is_null=True))
            pprint(data.column_names)
