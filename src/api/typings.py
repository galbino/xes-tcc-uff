"""
Module containing custom typings.
"""

from __future__ import annotations

import typing

Settings = typing.NewType("Settings", dict[str, str])


class Message:
    """
    Publisher abstract messages.
    """
