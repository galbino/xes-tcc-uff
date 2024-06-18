"""
Module containing schemas for endpoint.
"""

import dataclasses
import typing
import uuid

import pydantic

from api import typings


class ConvertXES(pydantic.BaseModel):
    """
    Base schema related to XES converting.
    """

    file: str
    email_address: pydantic.EmailStr
    keys: dict[str, str]
    delimiter: str = ";"


class ConvertXESResponse(pydantic.BaseModel):
    """
    Base schema related to XES converting response.
    """

    task_id: uuid.UUID
    status: typing.Literal["processing", "done", "error"]


class GetSignedUrl(pydantic.BaseModel):
    """
    Base schema related to the get signed url endpoint.
    """

    file_name: str
    mimetype: str
    is_handshake: bool = False


@dataclasses.dataclass(frozen=True, kw_only=True)
class ConvertAsyncTask(typings.Message):
    """
    Base schema related to the convert async task.
    """

    task_id: uuid.UUID
    url: str
    email_address: str
    keys: dict[str, str]
    delimiter: str = ";"


class PubsubMessage(pydantic.BaseModel, extra=pydantic.Extra.allow):
    """
    Defines required pubsub message.
    """

    data: bytes
    message_id: str = pydantic.Field(alias="messageId")


class PubsubRequest(pydantic.BaseModel, extra=pydantic.Extra.allow):
    """
    Defines required pubsub request.
    """

    message: PubsubMessage
    subscription: str


class AsyncTaskRequest(pydantic.BaseModel):
    """
    Base schema related to the convert async task.
    """

    task_id: uuid.UUID
    url: str
    email_address: str
    keys: dict[str, str]
    delimiter: str
