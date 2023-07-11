from ipaddress import IPv4Address
from pathlib import Path

import pytest

from renkon.config import load_config


def test_load_toml_config(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    # Monkeypatch the current working directory.
    monkeypatch.chdir(tmp_path)

    # Create a renkon.toml file.
    toml_path = tmp_path / "renkon.toml"
    toml_path.write_text(
        """
        [server]
        hostname = "1.2.3.4"
        port = 1234

        [repository]
        path = "foo/bar/baz"
        """
    )

    # Load the configuration.
    config = load_config()

    # Check that the configuration has been loaded correctly.
    assert config.server.hostname == IPv4Address("1.2.3.4")
    assert config.server.port == 1234
    assert config.repository.path.resolve() == tmp_path / "foo" / "bar" / "baz"
