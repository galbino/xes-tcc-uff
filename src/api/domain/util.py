"""
Module for utility functions.
"""

import json
import typing
import uuid


class UUIDEncoder(json.JSONEncoder):
    """
    Class for uuid encoding when dumping
    """

    def default(self, o: typing.Any) -> typing.Any:
        """
        Method to correctly handle uuid.
        """
        if isinstance(o, uuid.UUID):
            return str(o)
        if isinstance(o, list):
            return [self.default(item) for item in o]
        if isinstance(o, bytes):
            return o.decode("utf-8")
        return json.JSONEncoder.default(self, o)
