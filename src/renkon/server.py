from typing import Any

import pyarrow.flight as pa_fl

from renkon.config import ServerConfig
from renkon.repo import Repository


class RenkonFlightServer(pa_fl.FlightServerBase):  # type: ignore[misc]
    _repo: Repository
    config: ServerConfig

    def __init__(self, repo: Repository, config: ServerConfig, **kwargs: Any):
        super().__init__(f"grpc://{config.hostname}:{config.port}", **kwargs)
        self._repo = repo
        self._config = config

    def list_flights(self, context: pa_fl.ServerCallContext, criteria: bytes):
        # tables = self._repo.
        pass
