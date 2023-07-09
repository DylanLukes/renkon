from pathlib import Path

import pytest
from pyarrow import csv

from renkon.config import Config, load_config
from renkon.repo.repo import Repo, get_repo

TESTS_DIR = Path(__file__).parent

SEMICOLON_WITH_TYPE_ROW = {
    "parse_options": csv.ParseOptions(delimiter=";"),
    "read_options": csv.ReadOptions(skip_rows_after_names=1),
}

DEFAULT = {
    "parse_options": csv.ParseOptions(),
    "read_options": csv.ReadOptions(),
}

"""
List of sample datasets. Each key corresponds to a CSV file in the
`data` directory. Each contains the parse and read options needed
to read the file.
"""
SAMPLES = {
    "cars": SEMICOLON_WITH_TYPE_ROW,
    "cereals": SEMICOLON_WITH_TYPE_ROW,
    "cereals-corrupt": SEMICOLON_WITH_TYPE_ROW,
    "factbook": SEMICOLON_WITH_TYPE_ROW,
    "films": SEMICOLON_WITH_TYPE_ROW,
    "gini": DEFAULT,
    "smallwikipedia": SEMICOLON_WITH_TYPE_ROW,
}


@pytest.fixture
def config(tmp_path: Path) -> Config:
    return load_config(store={"path": tmp_path / ".renkon"})


@pytest.fixture
def repo(config: Config) -> Repo:
    store = get_repo(config)
    for name, options in SAMPLES.items():
        data = csv.read_csv(TESTS_DIR / "samples" / f"{name}.csv", **options)
        store.put_input_table(name, data)
    return store
