"""Module containing factory to build app."""

import functools
import logging

import fastapi
import fastapi_injector
import injector
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware

from api import errors, routers, typings

from .middleware import (
    default_error_handler,
    error_handler,
    logging_middleware,
)

logger = logging.getLogger(__name__)


def create_app(container: injector.Injector) -> fastapi.FastAPI:
    """Creates fastapi app."""
    setts = container.get(typings.Settings)
    app = fastapi.FastAPI(title="XES-UFF")

    app.add_middleware(fastapi_injector.InjectorMiddleware, injector=container)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=setts.get("origin", "*").split(","),
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    logging_func = functools.partial(
        logging_middleware, project_id=setts.get("project_id")
    )
    app.add_middleware(BaseHTTPMiddleware, dispatch=logging_func)

    app.include_router(routers.base_router, prefix="/api/v1")

    app.add_exception_handler(
        errors.BaseError,
        handler=error_handler,  # type: ignore[arg-type]
    )
    app.add_exception_handler(Exception, handler=default_error_handler)

    fastapi_injector.attach_injector(app, container)

    return app
