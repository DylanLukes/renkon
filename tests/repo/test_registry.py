from pathlib import PurePath

import pyarrow as pa

from renkon.repo import Registry
from renkon.repo.info import TableStat


def test_register_table(registry: Registry) -> None:
    store_table_info = TableStat(
        path=PurePath("tables/foo.arrow"),
        filetype="arrow",
        schema=pa.schema([pa.field("a", pa.int64()), pa.field("b", pa.string())]),
        rows=10,
        size=100,  # this is a made up number
    )

    path = PurePath("cells/13/df.arrow")
    registry.register("df[13]", path, store_table_info)

    reg_table_info = registry.lookup("df[13]", by="name")
    assert reg_table_info is not None
    assert reg_table_info.name == "df[13]"
    assert reg_table_info.path == path
    assert reg_table_info.schema == store_table_info.schema
    assert reg_table_info.rows == store_table_info.rows
    assert reg_table_info.size == store_table_info.size

    registry.unregister("df[13]")
    assert registry.lookup("df[13]", by="name") is None
    assert registry.lookup(str(path), by="path") is None


def test_list_tables(registry: Registry) -> None:
    named_table_infos = [
        (
            name,
            TableStat(
                path=PurePath(f"tables/{i}.{('arrow', 'parquet')[i % 2]}"),
                filetype=("arrow", "parquet")[i % 2],
                schema=pa.schema([pa.field("a", pa.int64()), pa.field("b", pa.string())]),
                rows=10,
                size=100,  # this is a made up number
            ),
        )
        for i, name in enumerate(["foo", "bar", "baz", "qux"])
    ]

    for name, table_info in named_table_infos:
        registry.register(name, PurePath(f"tables/{name}.{table_info.filetype}"), table_info)

    reg_table_infos = registry.list_all()
    assert len(reg_table_infos) == len(named_table_infos)
    for (name, table_info), reg_info in zip(named_table_infos, reg_table_infos, strict=True):
        assert reg_info.name == name
        assert reg_info.path == PurePath(f"tables/{name}.{table_info.filetype}")
        assert reg_info.schema == table_info.schema
        assert reg_info.rows == table_info.rows
        assert reg_info.size == table_info.size
