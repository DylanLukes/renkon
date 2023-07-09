from typing import Any

from pyarrow.flight import FlightServerBase

from renkon.config import ServerConfig
from renkon.repo import Repo


class RenkonFlightServer(FlightServerBase):  # type: ignore[misc]
    store: Repo
    config: ServerConfig

    def __init__(self, store: Repo, config: ServerConfig, **kwargs: Any):
        super().__init__(f"grpc://{config.hostname}:{config.port}", **kwargs)
        self.store = store
        self.config = config
