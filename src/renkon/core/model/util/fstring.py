from string import Formatter
from typing import Annotated

from annotated_types import Predicate


def is_valid_fstring(s: str) -> bool:
    """
    Check if the given string is a valid f-string.

    >>> is_valid_fstring("{x}")
    True
    >>> is_valid_fstring("{x")
    False
    >>> is_valid_fstring("{x} {y}")
    True
    >>> is_valid_fstring("{x} {y")
    False

    :param s: The string to check.
    :return: True if the string parses as a valid f-string, False otherwise.
    """
    try:
        fmt = Formatter()
        list(fmt.parse(s))
    except ValueError:
        return False
    return True


type FString = Annotated[str, Predicate(is_valid_fstring)]
