from pathlib import Path

from renkon.settings import Settings


def test_load_packaged_default_settings(working_dir: Path) -> None:
    settings = Settings()
    assert settings.data_dir == working_dir / ".renkon/"


def test_load_tests_settings(settings: Settings, working_dir: Path) -> None:
    assert settings.data_dir == working_dir / ".renkon/"
