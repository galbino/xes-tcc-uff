"""Module containing schemas for endpoint."""

import pydantic


class ConvertXES(pydantic.BaseModel):
    """Base schema related to the User."""

    file: str
    email_address: pydantic.EmailStr
    keys: dict[str, str]
    delimiter: str = ";"
