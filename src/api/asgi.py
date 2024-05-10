"""Module to startup the server."""

from . import dependencies, factory

app = factory.create_app(dependencies.create_container())
