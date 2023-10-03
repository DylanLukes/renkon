from typing import Protocol


class Engine(Protocol):
    """
    Core inference engine (protocol) for Renkon.
    """

    pass


class SimpleEngine(Engine):
    """
    Simple inference engine for Renkon. Does not support any advanced features such as:
      - Task graphs.
      - Dependent inference.
      - Multi-processing.

    Appropriate for small-scale inference, or for testing.
    """

    pass
