from collections.abc import Generator
from typing import Any

from loguru import logger
from pyarrow.flight import (
    Action,
    FlightDataStream,
    FlightDescriptor,
    FlightEndpoint,
    FlightInfo,
    FlightMetadataWriter,
    FlightServerBase,
    MetadataRecordBatchReader,
    RecordBatchStream,
    ServerCallContext,
    Ticket,
)

from renkon.config import ServerConfig
from renkon.repo import Repository
from renkon.repo.info import TableInfo


class RenkonFlightServer(FlightServerBase):  # type: ignore[misc]
    _location: str
    _repo: Repository
    _config: ServerConfig

    def __init__(self, repo: Repository, config: ServerConfig, **kwargs: Any):
        location = f"grpc://{config.hostname}:{config.port}"
        super().__init__(location, **kwargs)
        self._location = location
        self._repo = repo
        self._config = config

    def _make_flight_info(self, table_info: TableInfo) -> FlightInfo:
        name = table_info.name
        descriptor = FlightDescriptor.for_path(name.encode("utf-8"))
        endpoints = [FlightEndpoint(name, [self._location])]
        return FlightInfo(table_info.schema, descriptor, endpoints, table_info.rows, table_info.size)

    def list_flights(self, _context: ServerCallContext, _criteria: bytes) -> Generator[FlightInfo, None, None]:
        for table_info in self._repo.list_info():
            yield self._make_flight_info(table_info)

    def get_flight_info(self, _context: ServerCallContext, descriptor: FlightDescriptor) -> FlightInfo:
        name = descriptor.path[0].decode("utf-8")
        table_info = self._repo.get_info(name)
        if table_info is None:
            msg = f"Table {name} not found."
            raise KeyError(msg)
        return self._make_flight_info(table_info)

    def do_put(
        self,
        _context: ServerCallContext,
        descriptor: FlightDescriptor,
        reader: MetadataRecordBatchReader,
        _writer: FlightMetadataWriter,
    ) -> None:
        name = descriptor.path[0].decode("utf-8")
        table = reader.read_all()
        self._repo.put(name, table)

    def do_get(
        self,
        _context: ServerCallContext,
        ticket: Ticket,
    ) -> FlightDataStream:
        name = ticket.ticket.decode("utf-8")
        table = self._repo.get(name)
        return RecordBatchStream(table)

    def list_actions(self, _context: ServerCallContext) -> list[tuple[str, str]]:
        return [("dummy", "Dummy action, does nothing.")]

    def do_action(self, _context: ServerCallContext, action: Action) -> None:
        if action.type == "dummy":
            logger.info("Dummy action received, doing nothing.")
            pass
        else:
            msg = f"Action type {action.type} is not supported."
            raise NotImplementedError(msg)
