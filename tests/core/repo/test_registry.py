from pathlib import PurePath

import pyarrow as pa

from renkon.core.repo.registry import Registry


def test_register_table(registry: Registry) -> None:
    entry = Registry.Entry(
        name="df[13]",
        path=PurePath("cells/13/df"),
        filetype="arrow",
        schema=pa.schema([pa.field("a", pa.int64()), pa.field("b", pa.string())]),
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
            schema=pa.schema([pa.field("a", pa.int64()), pa.field("b", pa.string())]),
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
            schema=pa.schema([pa.field("a", pa.int64()), pa.field("b", pa.string())]),
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
            schema=pa.schema([pa.field("a", pa.int64()), pa.field("b", pa.string())]),
            rows=10,
            size=100,  # this is a made up number
        )
        for name in ["foo", "foo-too", "also-foo"]
    ]

    for entry in entries:
        registry.register(entry)

    for expected_entry, observed_entry in zip(entries, registry.search("tables/%", by="path"), strict=True):
        assert observed_entry == expected_entry
