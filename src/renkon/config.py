from functools import lru_cache

from loguru import logger


class Config:
    """
    Renkon configuration class.
    """

    # Location to store data on disk.
    DATA_DIR = ".renkon"


@lru_cache(1)
def global_config() -> Config:
    """
    Return the Renkon configuration.
    """
    return Config()


if __name__ == "__main__":
    logger.info(global_config().DATA_DIR)
