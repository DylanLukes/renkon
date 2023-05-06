from abc import ABC, abstractmethod


class Property(ABC):
    """
    Base class for an inferred property.
    """

    __slots__ = ()

    @abstractmethod
    def __str__(self) -> str:
        ...


class Equal(Property):
    pass
