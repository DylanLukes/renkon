from functools import lru_cache


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
    print(global_config().DATA_DIR)
