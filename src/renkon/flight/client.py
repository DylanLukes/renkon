import pyarrow as pa
from pyarrow.flight import FlightClient


class RenkonFlightClient(FlightClient):  # type: ignore[misc]
    def upload(self, name: str, table: pa.Table) -> None:
        descriptor = pa.flight.FlightDescriptor.for_path(name)
        writer, _ = self.do_put(descriptor, table.schema)
        writer.write(table)
        writer.close()

    def download(self, name: str) -> pa.Table:
        descriptor = pa.flight.FlightDescriptor.for_path(name)
        flight = self.get_flight_info(descriptor)
        reader = self.do_get(flight.endpoints[0].ticket)
        return reader.read_all()
