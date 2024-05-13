"""
Module containing memory storage abstract.
"""

import abc
import typing
import uuid


class MemoryStorage(abc.ABC):
    """
    Memory Storage abstract.
    """

    @abc.abstractmethod
    def get(self, key: str | uuid.UUID) -> typing.Any:
        """
        Get a value from the storage.
        """

    @abc.abstractmethod
    def set(self, key: str | uuid.UUID, value: typing.Any) -> None:
        """
        Set a value on the storage.
        """
