from typing import Any

from pyarrow.flight import FlightServerBase

from renkon.config import ServerConfig
from renkon.store import Store


class RenkonFlightServer(FlightServerBase):  # type: ignore[misc]
    store: Store
    config: ServerConfig

    def __init__(self, store: Store, config: ServerConfig, **kwargs: Any):
        super().__init__(f"grpc://{config.hostname}:{config.port}", **kwargs)
        self.store = store
        self.config = config
