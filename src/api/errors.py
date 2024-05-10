"""Module containing known errors."""

import typing


class BaseError(Exception):
    """Base error for custom exceptions."""

    output: dict[str, typing.Any]


class NotFound(BaseError):
    """Error to be returned when a resource is not found."""

    def __init__(self, entity: str | None = None) -> None:
        self.output = {
            "status_code": 404,
            "message": (
                "The entity was not found."
                if not entity
                else f"The entity {entity.capitalize()} was not found."
            ),
            "code": "not_found" if not entity else f"{entity}_not_found",
        }
