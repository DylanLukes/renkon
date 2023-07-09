from pathlib import Path

import pytest

from renkon.config import Config
from renkon.repo.repo import Repo
from tests.conftest import SAMPLES


def test_get_store(tmp_path: Path, config: Config, repo: Repo, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(tmp_path)
    assert repo.path.resolve() == config.repository.path.resolve() == tmp_path / ".renkon"


def test_get_sample_input_paths(repo: Repo) -> None:
    assert repo.path.exists()
    assert repo.path.is_dir()

    for name in SAMPLES:
        path = repo.get_input_table_path(name)
        assert path is not None
        assert (repo.path / path).exists()
        assert (repo.path / path).is_file()


def test_get_sample_input_tables(repo: Repo) -> None:
    assert repo.path.exists()
    assert repo.path.is_dir()

    for name in SAMPLES:
        data = repo.get_input_table(name)
        assert data is not None
        assert data.num_rows > 0
        assert data.num_columns > 0


def test_get_non_existent(repo: Repo) -> None:
    with pytest.raises(LookupError):
        repo.get_input_table_path("non_existent")

    with pytest.raises(LookupError):
        repo.get_input_table("non_existent")
