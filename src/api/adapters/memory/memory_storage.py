"""
Module containing memory storage implementation.
"""

import typing
import uuid

from api import ports


class MemoryStorage(ports.MemoryStorage):
    """
    Memory Storage implementation.
    """

    def __init__(self) -> None:
        self._storage: dict[str | uuid.UUID, typing.Any] = {}

    def get(self, key: str | uuid.UUID) -> typing.Any:
        """
        Get a value from the storage.
        """
        return self._storage.get(key, "")

    def set(self, key: str | uuid.UUID, value: typing.Any) -> None:
        """
        Set a value on the storage.
        """
        self._storage[key] = value
