"""
This file contains utilities related to pretty printing results when output is a TTY.
"""
import polars as pl

SHADE_BLOCKS = [" ", "░", "▒", "▓", "█"]
H_BLOCK_CHARS = [" ", "▏", "▎", "▍", "▌", "▋", "▊", "▉", "█"]
V_BLOCK_CHARS = [" ", "▁", "▂", "▃", "▄", "▅", "▆", "▇", "█"]
MIN_SCORE_GREEN = 0.75
MIN_MATCH_GREEN = 0.85


def pct_to_block(pct: float, blocks: list[str] | None = None) -> str:
    """
    Convert a percentage to a Unicode block character, where the block height is
    proportional to the percentage.
    """
    blocks = blocks or V_BLOCK_CHARS
    return blocks[int(pct * (len(blocks) - 1))]


def mask_to_blocks(mask: pl.Series, n_chunks: int = 25) -> str:
    """
    Convert a Boolean series to a string of n_chunks Unicode block characters,
    where each character's block height is proportional to the percentage of
    True values in that chunk of the series.
    """
    chunk_pcts = (
        (
            pl.LazyFrame({"idx": pl.int_range(0, len(mask), eager=True), "mask": mask})
            .group_by_dynamic("idx", every=f"{len(mask) // n_chunks}i")
            .agg((pl.sum("mask") / pl.count("mask")).alias("pct"))
        )
        .select("pct")
        .collect()
    )["pct"].to_list()
    return "".join(map(pct_to_block, chunk_pcts))
