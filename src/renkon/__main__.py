import sys
from pathlib import Path

from loguru import logger
from pyarrow import csv
from rich.console import Console

from renkon.store import get_store

console = Console()

SEMICOLON_WITH_TYPE_ROW = {
    "parse_options": csv.ParseOptions(delimiter=";"),
    "read_options": csv.ReadOptions(skip_rows_after_names=1),
}

DEFAULT = {
    "parse_options": csv.ParseOptions(),
    "read_options": csv.ReadOptions(),
}

SAMPLES = {
    "cars": SEMICOLON_WITH_TYPE_ROW,
    "cereals": SEMICOLON_WITH_TYPE_ROW,
    "cereals-corrupt": SEMICOLON_WITH_TYPE_ROW,
    "factbook": SEMICOLON_WITH_TYPE_ROW,
    "films": SEMICOLON_WITH_TYPE_ROW,
    "gini": DEFAULT,
    "smallwikipedia": SEMICOLON_WITH_TYPE_ROW,
}

# SKETCHES = []

store = get_store()
for name, options in SAMPLES.items():
    data = csv.read_csv(Path.cwd() / "etc/samples" / f"{name}.csv", **options)
    store.put_input_table(name, data)
    logger.info(f"Loaded sample {name} into the store.")

if __name__ == "__main__":
    from renkon.cli import renkon

    for name in ["cereals"]:
        table = store.get_input_dataframe(name)
        console.print(f"[bold]{name}[/bold]")
        console.print(table)
        console.print()

    sys.exit(renkon())
