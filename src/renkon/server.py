from typing import Any

from pyarrow.flight import FlightServerBase

from renkon.config import ServerConfig
from renkon.repo import Repository


class RenkonFlightServer(FlightServerBase):  # type: ignore[misc]
    _repo: Repository
    config: ServerConfig

    def __init__(self, repo: Repository, config: ServerConfig, **kwargs: Any):
        super().__init__(f"grpc://{config.hostname}:{config.port}", **kwargs)
        self._repo = repo
        self._config = config
