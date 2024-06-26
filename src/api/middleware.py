"""Middleware file for the connector runtime."""

# pylint: disable=import-private-name
import collections.abc
import logging
import time
import typing

import fastapi
import pydantic
import starlette.responses

from api import errors

NextCall = collections.abc.Callable[
    [fastapi.Request], collections.abc.Awaitable[starlette.responses.Response]
]

logger = logging.getLogger(__name__)


# pylint: disable=unused-argument
async def logging_middleware(
    request: fastapi.Request,
    call_next: NextCall,
    project_id: str | None = None,
) -> fastapi.Response:
    """Log data from request and response.

    Intercepts the request and starts a timer,
    calls back the endpoint and then logs the request,
    response and latency.

    :returns: the response back to the app.
    """
    start_time = time.perf_counter()

    try:
        response: starlette.responses.Response = await call_next(request)
    except Exception as exc:
        response = await handle_handlers(request, exc)

    process_time = time.perf_counter() - start_time
    request_url = request.url.path

    http_request = {
        "requestMethod": request.method,
        "requestUrl": request_url,
        "requestSize": request.headers.get("content-length"),
        "status": response.status_code,
        "responseSize": response.headers.get("content-length"),
        "userAgent": request.headers.get("user-agent"),
        "remoteIp": request.client.host if request.client else None,
        "latency": process_time,
    }

    if response.status_code >= 500:
        level = logging.ERROR
    elif response.status_code >= 400:
        level = logging.WARNING
    else:
        level = logging.INFO
    extra: dict[str, typing.Any] = {}
    if "x-cloud-trace-context" in request.headers:
        trace_id = request.headers.get("x-cloud-trace-context", "").split("/")[0]
        extra["logging.googleapis.com/trace"] = (
            f"project/{project_id}/traces/{trace_id}"
        )
    extra["httpRequest"] = http_request
    logger.log(level, "response", extra=extra)
    return response


async def error_handler(
    request: fastapi.Request, exc: errors.BaseError
) -> fastapi.responses.Response:
    """Error handler for custom errors."""
    return fastapi.responses.JSONResponse(
        status_code=exc.output.get("status_code", 400), content=exc.output
    )


async def default_error_handler(
    request: fastapi.Request, exc: Exception
) -> fastapi.responses.Response:
    """Handler for unexpected errors."""
    resp: list[dict[str, typing.Any]] | dict[str, typing.Any] | None = None
    match exc:
        case pydantic.ValidationError():
            status_code = fastapi.status.HTTP_422_UNPROCESSABLE_ENTITY
            resp = [dict(error) for error in exc.errors()]
        case _:
            logger.exception(exc)
            status_code = fastapi.status.HTTP_500_INTERNAL_SERVER_ERROR
            resp = {
                "status_code": 500,
                "code": "unexpected_server_error",
                "message": "There was an unexpected server error.",
            }

    return fastapi.responses.JSONResponse(
        status_code=status_code,
        content=resp,
    )


async def handle_handlers(
    request: fastapi.Request, exc: Exception
) -> fastapi.responses.Response:
    """Function to handle the different error handlers."""
    match exc:
        case errors.BaseError():
            return await error_handler(request, exc)
        case _:
            return await default_error_handler(request, exc)
