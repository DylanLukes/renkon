# import sys
# from pathlib import Path
#
# from loguru import logger
# from pyarrow import csv
# from rich.console import Console
#
# from renkon.repo import get_repo
#
# console = Console()
#
# SEMICOLON_WITH_TYPE_ROW = {
#     "parse_options": csv.ParseOptions(delimiter=";"),
#     "read_options": csv.ReadOptions(skip_rows_after_names=1),
# }
#
# DEFAULT = {
#     "parse_options": csv.ParseOptions(),
#     "read_options": csv.ReadOptions(),
# }
#
# SAMPLES = {
#     "cars": SEMICOLON_WITH_TYPE_ROW,
#     "cereals": SEMICOLON_WITH_TYPE_ROW,
#     "cereals-corrupt": SEMICOLON_WITH_TYPE_ROW,
#     "factbook": SEMICOLON_WITH_TYPE_ROW,
#     "films": SEMICOLON_WITH_TYPE_ROW,
#     "gini": DEFAULT,
#     "smallwikipedia": SEMICOLON_WITH_TYPE_ROW,
# }
#
# # SKETCHES = []
#
# repo = get_repo()
# for name, options in SAMPLES.items():
#     data = csv.read_csv(Path.cwd() / "etc/samples" / f"{name}.csv", **options)
#     repo.put_input_table(name, data)
#     logger.info(f"Loaded sample {name} into the repository.")
#
# if __name__ == "__main__":
#     from renkon.cli import cli
#
#     for name in ["cereals"]:
#         table = repo.get_input_dataframe(name)
#         console.print(f"[bold]{name}[/bold]")
#         console.print(table)
#         console.print()
#
#     sys.exit(cli())
