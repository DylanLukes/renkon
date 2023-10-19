from pathlib import PurePath

import pyarrow as pa
from polars import Int64, Utf8
from pyarrow import Schema

from renkon.core.repo.registry import Registry
from renkon.core.repo.schema import Schema

DUMMY_SCHEMA: Schema = {"a": Int64, "b": Utf8}


def test_register_table(registry: Registry) -> None:
    entry = Registry.Entry(
        name="df[13]",
        path=PurePath("cells/13/df"),
        filetype="arrow",
        schema=DUMMY_SCHEMA,
        rows=10,
        size=100,  # this is a made up number
    )
    registry.register(entry)

    assert entry == registry.lookup("df[13]", by="name")

    registry.unregister("df[13]")
    assert registry.lookup("df[13]", by="name") is None
    assert registry.lookup(str(entry.path), by="path") is None


def test_list_tables(registry: Registry) -> None:
    entries = [
        Registry.Entry(
            name=name,
            path=PurePath(f"tables/{name}"),
            filetype="arrow",
            schema=DUMMY_SCHEMA,
            rows=10,
            size=100,  # this is a made up number
        )
        for name in ["foo", "bar", "baz", "qux"]
    ]

    for entry in entries:
        registry.register(entry)

    for expected_entry, observed_entry in zip(entries, registry.list_all(), strict=True):
        assert observed_entry == expected_entry


def test_search_tables_by_name(registry: Registry) -> None:
    entries = [
        Registry.Entry(
            name=name,
            path=PurePath(f"tables/{name}.arrow"),
            filetype="arrow",
            schema=DUMMY_SCHEMA,
            rows=10,
            size=100,  # this is a made up number
        )
        for name in ["foo", "foo-too", "also-foo"]
    ]

    for entry in entries:
        registry.register(entry)

    for expected_entry, observed_entry in zip(entries, registry.search("%foo%", by="name"), strict=True):
        assert observed_entry == expected_entry


def test_search_tables_by_path(registry: Registry) -> None:
    entries = [
        Registry.Entry(
            name=name,
            path=PurePath(f"tables/{name}.parquet"),
            filetype="parquet",
            schema=DUMMY_SCHEMA,
            rows=10,
            size=100,  # this is a made up number
        )
        for name in ["foo", "foo-too", "also-foo"]
    ]

    for entry in entries:
        registry.register(entry)

    for expected_entry, observed_entry in zip(entries, registry.search("tables/%", by="path"), strict=True):
        assert observed_entry == expected_entry
