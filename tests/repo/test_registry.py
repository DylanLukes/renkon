import pyarrow as pa

from renkon.repo import Registry
from renkon.repo.storage import StoredTableInfo


def test_register_table(registry: Registry):
    store_table_info = StoredTableInfo(
        schema=pa.schema([pa.field("a", pa.int64()), pa.field("b", pa.string())]),
        rows=10,
        size=100,  # this is a made up number
    )

    registry.register("df[13]", "cells/13/df.arrow", store_table_info)

    reg_table_info = registry.lookup("df[13]", by="name")
    assert reg_table_info is not None
    assert reg_table_info.name == "df[13]"
    assert reg_table_info.path == "cells/13/df.arrow"
    assert reg_table_info.schema == store_table_info.schema
    assert reg_table_info.rows == store_table_info.rows
    assert reg_table_info.size == store_table_info.size

    registry.unregister("df[13]")
    assert registry.lookup("df[13]", by="name") is None
    assert registry.lookup("cells/13/df.arrow", by="path") is None
